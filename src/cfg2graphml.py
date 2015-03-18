import sys

from xml.etree import ElementTree as ET
from xml.dom import minidom

from cfg_nodes import CFGNodeType
from cfg_nodes import CFGEntryNode
from cfg_nodes import CFGNode
from cfg import CFG


class CFG2Graphml(object):

    def make_graphml(self, cfg, file_name='', yed_output=False):
        self._yed_output = yed_output

        root = self._start_graphml()
        self._define_header(root)
        self._write_graph(root, cfg)
        self._save_graphml(file_name, root)

    def _save_graphml(self, file_name, root):
        try:
            with open(file_name, 'w') as f:
                f.write(self._pretty_print(root))
        except IOError:
            sys.stdout.write(self._pretty_print(root))

    def _pretty_print(self, root):
        rough_string = ET.tostring(root)
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent='  ', encoding='UTF-8')

    def _start_graphml(self):
        root = ET.Element('graphml')
        root.set('xmlns', 'http://graphml.graphdrawing.org/xmlns')
        root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')

        if self._yed_output:
            root.set('xmlns:y', 'http://www.yworks.com/xml/graphml')
            root.set('xsi:schemaLocation',
                    'http://graphml.graphdrawing.org/xmlns'
                    + ' http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd'
                    + ' http://www.yworks.com/xml/schema/graphml/1.0/ygraphml.xsd')
        else:
            root.set('xsi:schemaLocation',
                    'http://graphml.graphdrawing.org/xmlns'
                    + ' http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd')

        return root

    def _define_header(self, root):
        self._define_yed_keys(root)
        self._define_node_keys(root)
        self._define_edge_keys(root)

    def _define_yed_keys(self, root):
        """ Define header tags for graphical view
        """
        if not self._yed_output: return

        for key in self._yed_keys:
            xml_key = ET.SubElement(root, 'key')
            for attr, v in key.iteritems():
                xml_key.set(attr, v)

    def _define_node_keys(self, root):
        for key in self._node_keys:
            xml_key = ET.SubElement(root, 'key')
            for attr, v in key.iteritems():
                if attr == 'default':
                    xml_default = ET.SubElement(xml_key, 'default')
                    xml_default.text = v
                elif attr != 'get_data':
                    xml_key.set(attr, v)

    def _define_edge_keys(self, root):
        pass

    def _write_graph(self, root, cfg):
        """ Write graph tag and add CFG nodes and edges
        """
        if not isinstance(cfg, CFG): return

        xml_graph = ET.SubElement(root, 'graph')
        edges = 0
        func_id = 0
        for entry in cfg.get_entry_nodes():
            func_id += 1
            if isinstance(entry, CFGEntryNode):
                # write nodes
                self._node_ids = {} # to control visited nodes
                self._write_node(xml_graph, entry.get_func_name(), func_id,
                        entry.get_func_first_node(), 0)

                # write edges
                self._node_ids = {} # to control visited nodes
                edges = self._write_edge(xml_graph, func_id,
                            entry.get_func_first_node(), 0, 0)

        xml_graph.set('id', 'graph')
        xml_graph.set('parse.nodes', str(len(self._node_ids)))
        xml_graph.set('parse.edges', str(edges))
        xml_graph.set('parse.order', 'free')
        xml_graph.set('edgedefault', 'directed')

    def _write_node(self, xml_graph, fname, fid, n, nid):
        """ Write node attributes to graphml file.
        """
        if not isinstance(n, CFGNode): return

        # node is visited
        self._node_ids[id(n)] = 'g%sn%s' % (fid, nid)

        # write node xml data
        self._write_node_xml(xml_graph, fid, n, nid)

        # explore loop if current node is PSEUDO
        if n.get_type() == CFGNodeType.PSEUDO:
            self._write_node(xml_graph, fname, fid, n.get_ref_node(),
                    len(self._node_ids))

        # explore node children that were not visit yet
        for child in n.get_children():
            if id(child) not in self._node_ids:
                self._write_node(xml_graph, fname, fid, child,
                        len(self._node_ids))

    def _write_node_xml(self, xml_graph, fid, n, nid):
        # create node tag
        xml_node = ET.SubElement(xml_graph, 'node')
        xml_node.set('id', self._node_ids[id(n)])

        # add data based on node keys
        for key in self._node_keys:
            xml_data = ET.SubElement(xml_node, 'data')
            xml_data.set('key', key['id'])
            try:
                method_name = key['get_data']
                method = getattr(n, method_name)
                xml_data.text = str(method()).lower()
            except AttributeError:
                xml_data.text = key['default']

        # add graphical information
        if self._yed_output:
            self._write_node_yed(n, nid, xml_node)


    def _write_node_yed(self, n, nid, xml_node):
        """ Define node shape and position for graphical view
        """
        if not isinstance(n, CFGNode): return

        for key in self._yed_keys:
            if key['for'] == 'node':
                break

        if key == {} or key['for'] != 'node': return

        xml_data = ET.SubElement(xml_node, 'data')
        xml_data.set('key', key['id'])

        xml_shape_node = ET.SubElement(xml_data, 'y:ShapeNode')
        xml_shape = ET.SubElement(xml_shape_node, 'y:Shape')
        xml_shape.set('type', 'ellipse')

        xml_geometry = ET.SubElement(xml_shape_node, 'y:Geometry')
        xml_geometry.set('height', '30.0')
        xml_geometry.set('width', '30.0')

        xml_fill = ET.SubElement(xml_shape_node, 'y:Fill')
        xml_fill.set('color', '#FFCC00')

        xml_label = ET.SubElement(xml_shape_node, 'y:NodeLabel')
        xml_label.set('modelName', 'internal')
        xml_label.set('modelPosition', 'c')
        xml_label.text = ('%d' % nid)

        xml_label = ET.SubElement(xml_shape_node, 'y:NodeLabel')
        xml_label.set('modelName', 'sides')
        xml_label.set('modelPosition', 'e')
        xml_label.text = ('W.%d' % n.get_wcec())

    def _write_edge(self, xml_graph, fid, n, nid, eid):
        """ Write edge attributes to graphml file by first discovering
            all nodes, then create edges in preorder.

            Return the number of edges.
        """
        if not isinstance(n, CFGNode): return

        # node is visited
        self._node_ids[id(n)] = 'g%sn%s' % (fid, nid)

        # explore loop if current one is PSEUDO
        if n.get_type() == CFGNodeType.PSEUDO:
            loop_node = n.get_ref_node()
            eid = self._write_edge(xml_graph, fid, loop_node,
                    len(self._node_ids), eid)
            self._write_edge_xml(xml_graph, fid, eid, n, nid, loop_node)
            eid += 1

        # write node children that were not visit yet
        for child in n.get_children():
            if id(child) not in self._node_ids:
                eid = self._write_edge(xml_graph, fid, child,
                        len(self._node_ids), eid)
            self._write_edge_xml(xml_graph, fid, eid, n, nid, child)
            eid += 1

        return eid

    def _write_edge_xml(self, xml_graph, fid, eid, n, nid, child):
        # create edge tag
        xml_edge = ET.SubElement(xml_graph, 'edge')
        xml_edge.set('id', 'g%se%s' % (fid, eid))
        xml_edge.set('source', self._node_ids[id(n)])
        xml_edge.set('target', self._node_ids[id(child)])

        # add only rwcec key tag
        for key in self._node_keys:
            if key['attr.name'] == 'rwcec':
                xml_data = ET.SubElement(xml_edge, 'data')
                xml_data.set('key', key['id'])
                try:
                    method_name = key['get_data']
                    method = getattr(n, method_name)
                    xml_data.text = str(method()).lower()
                except AttributeError:
                    xml_data.text = key['default']
                finally:
                    break

        # add graphical information
        if self._yed_output:
            self._write_edge_yed(xml_edge, child.get_rwcec())

    def _write_edge_yed(self, xml_edge, rwcec):
        """ Define edge shape and position for graphical view
        """
        for key in self._yed_keys:
            if key['for'] == 'edge':
                break

        if key == {} or key['for'] != 'edge': return

        xml_data = ET.SubElement(xml_edge, 'data')
        xml_data.set('key', key['id'])

        xml_poly_line = ET.SubElement(xml_data, 'y:PolyLineEdge')

        xml_arrows = ET.SubElement(xml_poly_line, 'y:Arrows')
        xml_arrows.set('source', 'none')
        xml_arrows.set('target', 'short')

        xml_label = ET.SubElement(xml_poly_line, 'y:EdgeLabel')
        xml_label.set('alignment', 'center')
        xml_label.text = str(rwcec)

    def __init__(self):
        self._node_ids = {} # to control visited nodes
        self._yed_output = False
        self._yed_keys = [
            {
                'id': 'nyed',
                'yfiles.type': 'nodegraphics',
                'for': 'node'
            },
            {
                'id': 'eyed',
                'yfiles.type': 'edgegraphics',
                'for': 'edge'
            },
        ]
        self._node_keys = [
            {
                'for': 'node',
                'id': 'k0',
                'attr.name': 'node_type',
                'attr.type': 'string',
                'default': 'common',
                'get_data': CFGNode.get_type.__name__
            },
            {
                'for': 'node',
                'id': 'k1',
                'attr.name': 'start_line',
                'attr.type': 'int',
                'default': '0',
                'get_data': CFGNode.get_start_line.__name__
            },
            {
                'for': 'node',
                'id': 'k2',
                'attr.name': 'last_line',
                'attr.type': 'int',
                'default': '0',
                'get_data': CFGNode.get_end_line.__name__
            },
            {
                'for': 'node',
                'id': 'k3',
                'attr.name': 'function_owner',
                'attr.type': 'string',
                'default': 'none',
                'get_data': CFGNode.get_func_owner.__name__
            },
            {
                'for': 'node',
                'id': 'k4',
                'attr.name': 'call',
                'attr.type': 'string',
                'default': 'none',
                'get_data': CFGNode.get_call_func_name.__name__
            },
            {
                'for': 'node',
                'id': 'k5',
                'attr.name': 'loop_wcec',
                'attr.type': 'int',
                'default': '0',
                'get_data': CFGNode.get_loop_wcec.__name__
            },
            {
                'for': 'node',
                'id': 'k6',
                'attr.name': 'iterations',
                'attr.type': 'int',
                'default': '0',
                'get_data': CFGNode.get_loop_iters.__name__
            },
            {
                'for': 'node',
                'id': 'k7',
                'attr.name': 'wcec',
                'attr.type': 'int',
                'default': '0',
                'get_data': CFGNode.get_wcec.__name__
            },
            {
                'for': 'node',
                'id': 'k8',
                'attr.name': 'rwcec',
                'attr.type': 'int',
                'default': '0',
                'get_data': CFGNode.get_rwcec.__name__
            }
        ]


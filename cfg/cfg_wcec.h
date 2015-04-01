/*
 * cfg/cfg_wcec.h
 *
 * It defines how the new frequency should be computed when a type-B or type-L
 * edges are found.
 *
 * By default, the new frequency is always 100. So, __cfg_get_curfreq() should
 * be changed to return the right frequency when testing it in a real
 * environment. Moreover, __cfg_typeB_freq() and __cfg_typeL_freq() should also
 * be changed to set the new frequency.
 *
 * At the user side, only __cfg_change_freq() must be called with the right
 * parameters to change the frequency if it is possible.
 *
 * Note: type-B and type-L overheads are zero by default.
 */

#ifndef __CFG_WCEC__
#define __CFG_WCEC__

typedef enum {
    __CFG_TYPE_UNKOWN = 0,
    __CFG_TYPE_B,
    __CFG_TYPE_L
} __cfg_edge_type;


/* Utils */
float __cfg_get_curfreq(void);
int __cfg_ceil(float freq);
void __cfg_change_freq(__cfg_edge_type *type, float rwcec_bi, float rwcec_bj,
        int loop_max_iter, int loop_iter);

/* For Type-B Edges */
float __cfg_typeB_sur(float rwcec_wsbi, float rwcec_bj);
void __cfg_typeB_freq(float rwcec_wsbi, float rwcec_bj);

/* For Type-L Edges */
float __cfg_typeL_cycles_saved(float loop_wcec, int loop_max_iter,
        int loop_iter);
float __cfg_typeL_sur(float loop_wcec, float rwcec_bout, int loop_max_iter,
        int loop_iter);
void __cfg_typeL_freq(float loop_wcec, float rwcec_bout, int loop_max_iter,
        int loop_iter);


/* __cfg_get_curfreq: get processor current frequency
 * @returns: processor current frequency
 */
float __cfg_get_curfreq(void) {
    return 100; // default frequency
}

/* __cfg_ceil: implements ceil operation without using external libraries
 * @parameter freq: number that ceil operation should be applied
 * @returns: result of ceil operation
 */
int __cfg_ceil(float freq) {
    return (freq == (int)freq) ? freq : (int)(freq + 1);
}

/* __cfg_change_freq: change processor frequency according to the edge type
 * @parameter type: cfg edge type which can be B or L
 * @parameter rwcec_bi: if edge is of type-B, so it is RWCEC of the worst
 *  successor of bi. However, if it is of type-L, so it is WCEC of one loop
 *  execution
 * @parameter rwcec_bj: if edge is of type-B, so it is RWCEC of bj. However, if
 *  it is of type-L, so it is RWCEC of bout - first node after loop execution
 * @parameter loop_max_iter: maximum number of loop iterations
 * @parameter loop_iter: how many loop iterations were done at runtime
 */
void __cfg_change_freq(__cfg_edge_type *type, float rwcec_bi, float rwcec_bj,
        int loop_max_iter, int loop_iter) {

    switch(*type) {
    case(__CFG_TYPE_B):
        __cfg_typeB_freq(rwcec_bi, rwcec_bj);
        break;
    case(__CFG_TYPE_L):
        __cfg_typeL_freq(rwcec_bi, rwcec_bj, loop_max_iter, loop_iter);
        break;
    case(__CFG_TYPE_UNKOWN):
        break;
    }

    *type = __CFG_TYPE_UNKOWN;
}


/* ========================
 * Type-B edges definitions
 * ========================
 */
float __cfg_typeB_overhead = 0;  /* overhead of type-B operations */

/* __cfg_typeB_sur: compute speed update ratio from type-B edge
 *      r(bi, bj) = RWCEC(bj) / (RWCEC(WORST_SUCC(bi)) - typeB_overhead)
 * @parameter rwcec_wsbi: RWCEC of the worst successor of bi
 * @parameter rwcec_bj: RWCEC of bj
 * @returns: speed update ratio from a type-B edge
 */
float __cfg_typeB_sur(float rwcec_wsbi, float rwcec_bj) {
    if (rwcec_wsbi - __cfg_typeB_overhead <= 0)
        return 1;

    return rwcec_bj / (rwcec_wsbi - __cfg_typeB_overhead);
}

/* __cfg_typeB_freq: compute the new frequency of a type-B edge and apply it if
 * the ratio is less than one. If it is equal or greater than one, the new
 * frequency will be greater than the current one and so it will be the energy
 * consumption.
 * @parameter rwcec_wsbi: RWCEC of the worst successor of bi
 * @parameter rwcec_bj: RWCEC of bj
 */
void __cfg_typeB_freq(float rwcec_wsbi, float rwcec_bj) {
    float ratio, curfreq;
    int newfreq;

    ratio = __cfg_typeB_sur(rwcec_wsbi, rwcec_bj);
    if (ratio < 1) {
        curfreq = __cfg_get_curfreq();
        curfreq = curfreq * ratio;
        newfreq = __cfg_ceil(curfreq);

        /* change_processor_frequency(newfreq) */
    }
}


/* ========================
 * Type-L edges definitions
 * ========================
 */
float __cfg_typeL_overhead = 0;  /* overhead of type-B operations */

/*
 * __cfg_typeL_cycles_saved: compute how many cycles were not executed
 *      r(bi, bout) = RWCEC(bout) / (RWCEC(bout) + SAVED(bi) - typeB_overhead)
 * where bi is loop condition node.
 * @parameter loop_wcec: WCEC of one loop execution
 * @parameter loop_max_iter: maximum number of loop iterations
 * @parameter loop_iter: how many loop iterations were done at runtime
 * @returns: cycles that were not executed from a type-L edge
 */
float __cfg_typeL_cycles_saved(float loop_wcec, int loop_max_iter,
        int loop_iter) {
    return (float)(loop_wcec * (loop_max_iter - loop_iter));
}

/*
 * __cfg_typeL_sur: compute speed update ratio from type-L edge
 *      r(bi, bout) = RWCEC(bout) / (RWCEC(bout) + SAVED(bi) - typeB_overhead)
 * where bi is loop condition node.
 * @parameter loop_wcec: WCEC of one loop execution
 * @parameter rwcec_bout: RWCEC of bout - first node after loop execution
 * @parameter loop_max_iter: maximum number of loop iterations
 * @parameter loop_iter: how many loop iterations were done at runtime
 * @returns: speed update ratio from a type-L edge
 */
float __cfg_typeL_sur(float loop_wcec, float rwcec_bout, int loop_max_iter,
        int loop_iter) {
    float saved = __cfg_typeL_cycles_saved(loop_wcec, loop_max_iter, loop_iter);
    if (rwcec_bout + saved - __cfg_typeL_overhead <= 0)
        return 1;

    return rwcec_bout / (rwcec_bout + saved - __cfg_typeL_overhead);
}

/*
 * __cfg_typeL_freq: compute the new frequency of a type-L edge and apply it if
 * the ratio is less than one. If it is equal or greater than one, the new
 * frequency will be greater than the current one and so it will be the energy
 * consumption.
 * @parameter loop_wcec: WCEC of one loop execution
 * @parameter rwcec_bout: RWCEC of bout - first node after loop execution
 * @parameter loop_max_iter: maximum number of loop iterations
 * @parameter loop_iter: how many loop iterations were done at runtime
 */
void __cfg_typeL_freq(float loop_wcec, float rwcec_bout, int loop_max_iter,
        int loop_iter) {
    float ratio, curfreq;
    int newfreq;

    ratio = __cfg_typeL_sur(loop_wcec, rwcec_bout, loop_max_iter, loop_iter);
    if (ratio < 1) {
        curfreq = __cfg_get_curfreq();
        curfreq = curfreq * ratio;
        newfreq = __cfg_ceil(curfreq);

        /* change_processor_frequency(newfreq) */
    }
}

#endif /* __CFG_WCEC__ */

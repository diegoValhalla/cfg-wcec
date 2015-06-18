int main() {

    int a, b, c;

    a = 2;
    b = c = 3;

    if (b < a) {
        if (b < a) {
            a = c;
            c = b;
            while(a < b) { // @LOOP 10
                a = 3;
                b = c;
                a += b + c;
            }
        }
        a = c;
        c = b;
    } else {
        if (c < a) {
            c = a;
        } else {
            if (b < a) {
                while(a < b) { // @LOOP 10
                    a = 3;
                    b = c;
                    a += b + c;
                }
                a = c;
                if (b < a) {
                    a = c;
                    c = b;
                }
                c = b;
                while(a < b) { // @LOOP 10
                    if (b < a) {
                        a = c;
                    }
                    a = 3;
                    b = c;
                    a += b + c;
                }
            } else {
                if (c < b) {
                    c = a;
                } else {
                    a = c;
                    c = b;
                    while(a < b) { // @LOOP 10
                        a = 3;
                        b = c;
                        a += b + c;
                    }
                    if (b < a) {
                        a = c;
                        c = b;
                    }
                }
            }
        }
    }

    while(a < b) { // @LOOP 10
        a = 3;
        if (a > b) {
            a = 2;
        }
        b = c;
        a += b + c;
    }

    while(a < b) { // @LOOP 10
        if (a < c) {
            a = 3;
        } else {
            b = c;
        }
        a += b + c;
    }

    while(a < b) { // @LOOP 10
        if (a < c) {
            a = 3;
        } else {
            b = c;
        }
    }


    while(a < b) { // @LOOP 10
        a += b + c;
        if (a < c) {
            a = 3;
        } else {
            b = c;
        }
        a += b + c;
    }

    return 0;
}

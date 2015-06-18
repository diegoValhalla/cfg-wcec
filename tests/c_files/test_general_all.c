void foo() {
    int a, b;

    a = b = 3;
    if (a < b) {
        a++;
        b--;
    }
}

int main() {

    int a, b, c;

    a = 2;
    foo();
    b = c = 3;

    if (b < a) {
        if (b < a) {
            foo();
            a = c;
            c = b;
            while(a < b) { // @LOOP 10
                a = 3;
                b = c;
                a += b + c;
                foo();
            }
        }
        a = c;
        c = b;
    } else {
        if (c < a) {
            c = a;
            foo();
        } else {
            if (b < a) {
                foo();
                while(a < b) { // @LOOP 10
                    a = 3;
                    b = c;
                    foo();
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
                        foo();
                        a = c;
                    }
                    a = 3;
                    b = c;
                    a += b + c;
                    foo();
                }
            } else {
                if (c < b) {
                    c = a;
                    foo();
                } else {
                    a = c;
                    c = b;
                    while(a < b) { // @LOOP 10
                        a = 3;
                        foo();
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
            foo();
        } else {
            b = c;
        }
        a += b + c;
    }

    while(a < b) { // @LOOP 10
        if (a < c) {
            foo();
        } else {
            foo();
        }
    }


    while(a < b) { // @LOOP 10
        a += b + c;
        if (a < c) {
            a = 3;
        } else {
            foo();
        }
        a += b + c;
    }

    return 0;
}

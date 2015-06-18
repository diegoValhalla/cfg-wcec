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
    b = c = 3;

    if (b < a) {
        if (b < a) {
            a = c;
            foo();
            c = b;
        }
        a = c;
        c = b;
    } else {
        if (c < a) {
            foo();
            c = a;
        } else {
            if (b < a) {
                a = c;
                if (b < a) {
                    a = c;
                    c = b;
                    foo();
                }
                c = b;
            } else {
                if (c < b) {
                    c = a;
                    foo();
                } else {
                    foo();
                    a = c;
                    c = b;
                    if (b < a) {
                        a = c;
                        c = b;
                    }
                }
            }
        }
    }

    foo();
    if (a > b) {
        a = 2;
    }

    return 0;
}

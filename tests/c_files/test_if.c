int main() {

    int a, b, c;

    a = 2;
    b = c = 3;

    if (b < a) {
        if (b < a) {
            a = c;
            c = b;
        }
        a = c;
        c = b;
    } else {
        if (c < a) {
            c = a;
        } else {
            if (b < a) {
                a = c;
                if (b < a) {
                    a = c;
                    c = b;
                }
                c = b;
            } else {
                if (c < b) {
                    c = a;
                } else {
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

    if (a > b) {
        a = 2;
    }

    return 0;
}

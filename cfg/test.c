int main() {
    int a, b, c;

    a = 2;
    b = c = 3;

    while(a < b) { // @LOOP 10
        a = 3;
        b = c;
        a += b + c;
    }

    while(a < b) { // @LOOP 3
        while(a < b) { // @LOOP 20
            a = 3;
            b = c;
            a += b + c;
        }
        a = 3;
        b = c;
        a += b + c;
    }

    a = c;

    while(a < b) { // @LOOP 2
        a = 3;
        b = c;
        while(a < b) { // @LOOP 1
            a = 3;
            b = c;
            a += b + c;
        }
        a += b + c;
    }

    a = c + a;

    while(a < b) { // @LOOP 1
        a = 3;
        b = c;
        a += b + c;
        while(a < b) { // @LOOP 12
            a = 3;
            b = c;
            a += b + c;
        }
    }

    return 0;
}

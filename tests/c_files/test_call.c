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
    foo();

    if (a < b) {
        a = 3;
        foo();
    }

    if (c < b) {
        foo();
        a = 3;
    } else {
        foo();
    }

    return 0;
}

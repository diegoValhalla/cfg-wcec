int main() {
    int a, b;

    a = 2;
    b = 3;

    if (a < b) {
        a *= 5;
        a += b;
        a /= 10;
    } else {
        a--;
    }

    return 0;
}

gcc --version

cat > test.c << 'EOF'
int g;

void foo(int a, int b) {
    if (a) {
        g++;
        if (b) {
            g++;
        } // C_else_2
    } // C_else_1

    // g++; // Uncommenting this changes the behavior

L1: // C_else_1 + C_else_2

    if (a) {
        g++;
        if (b) {
            g++;
        } else {
            g--; // C_else_2
        }
    } // C_else_1

    // g++; // Uncommenting this changes the behavior

L2: // C_else_1

    return;
}

int main(void) {
    for (int i = 0; i < 1; i++)
        foo(0, 0);
    for (int i = 0; i < 20; i++)
        foo(1, 0);
    for (int i = 0; i < 300; i++)
        foo(0, 1);
    for (int i = 0; i < 4000; i++)
        foo(1, 1);
}
EOF

gcc --coverage test.c -o test
./test
gcov test
cat test.c.gcov

echo ---------------------------------------------------------------------------
if ! grep &>/dev/null -e '      321:   13:L1: // C_else_1 + C_else_2' -e '     4642:   13:L1: // C_else_1 + C_else_2' test.c.gcov; then
    echo $0 NOT REPRODUCING 1
    exit 1
fi
if ! grep &>/dev/null -e '      301:   26:L2: // C_else_1' -e '     4622:   26:L2: // C_else_1' test.c.gcov; then
    echo $0 NOT REPRODUCING 2
    exit 1
fi
echo $0 OK

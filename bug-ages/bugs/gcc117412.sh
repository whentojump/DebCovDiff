gcc --version

cat > test.c << 'EOF'
int foo(long a) {
    return 0;
};

struct Bar { int b; };

int main(void) {
    int        x[100];
    struct Bar y;
    int        z;

    int           a1;
    unsigned long a2;
    long long     a3;

    *x = foo(
             a1*2);

    x[1] = foo(
             a2+1);

    y.b = foo(
             a3-3);

    return 0;
}
EOF

gcc --coverage test.c -o test
./test
gcov test
cat test.c.gcov

echo ---------------------------------------------------------------------------
if ! grep &>/dev/null '        2:   16:    \*x = foo(' test.c.gcov; then
    echo $0 NOT REPRODUCING 1
    exit 1
fi
if ! grep &>/dev/null '        2:   19:    x\[1\] = foo(' test.c.gcov; then
    echo $0 NOT REPRODUCING 2
    exit 1
fi
if ! grep &>/dev/null '        2:   22:    y.b = foo(' test.c.gcov; then
    echo $0 NOT REPRODUCING 3
    exit 1
fi
echo $0 OK

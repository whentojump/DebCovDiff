gcc --version

cat > test.c << 'EOF'
int g;

int foo(int a, int b) {
    g++;
    if (a && b) { // (1)
        g++;
        int dummy; // (2)
        for(int i = 0; i < 1; i++) {} // (3)
    }
    else {
        g++; // (4)
    }
}

int main(void) {
    for (int i = 0; i < 3; i++)
        foo(0, 1);
    for (int i = 0; i < 5; i++)
        foo(1, 1);
}
EOF

gcc --coverage test.c -o test
./test
gcov test
cat test.c.gcov

echo ---------------------------------------------------------------------------
if ! grep &>/dev/null '       13:    5:    if (a && b) { // (1)' test.c.gcov; then
    echo $0 NOT REPRODUCING 1
    exit 1
fi
echo $0 OK

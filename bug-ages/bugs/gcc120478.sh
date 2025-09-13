gcc --version

cat > test.c << 'EOF'
__inline__ __attribute__((__always_inline__))
int foo() { return 0; }

int main(void) {
    int x = 0, y = 0;
    for (int i = 0; i < 42; i++) {
        x++; y += foo();
        // x++;
    }
}
EOF

gcc --coverage test.c -o test
./test
gcov test
cat test.c.gcov

echo ---------------------------------------------------------------------------
if ! grep &>/dev/null '       84:    7:        x++; y += foo();' test.c.gcov; then
    echo $0 NOT REPRODUCING 1
    exit 1
fi
echo $0 OK

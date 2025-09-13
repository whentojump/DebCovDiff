gcc --version

cat > test.c << 'EOF'
int g;

static inline __attribute__((always_inline))
int foo() { return 0; }

#define PROCESS g = foo()

int main(void) {
    int x = 1;
    switch(x) {
    case 1:       g++;
                  PROCESS;
    case 2:       PROCESS;
    case 3:       PROCESS;
                  g++;
    case 4:       g++;
    }
}
EOF

gcc --coverage test.c -o test
./test
gcov test
cat test.c.gcov

echo ---------------------------------------------------------------------------
if ! grep &>/dev/null '        2:   13:    case 2:       PROCESS;' test.c.gcov; then
    echo $0 NOT REPRODUCING 1
    exit 1
fi
echo $0 OK

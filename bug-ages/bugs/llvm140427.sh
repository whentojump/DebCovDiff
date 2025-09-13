clang --version

cat > test.c << 'EOF'
#include <stdio.h>

// (1) "return" in macro
#define FOO \
    if (b) \
        return;

int g, cnt;

void foo(int a, int b) {
    do { // (2) inside an "if", "while" etc
        if (a)
            return; // (3) "return", "goto" etc
        // g++; // inserting a statement here eliminates the abnormal behavior
        FOO;
        cnt++; // <= wrong line coverage
    } while (0);
}

int main(void) {
    for (int i = 0; i < 10; i++)
        foo(0, 0);
    for (int i = 0; i < 200; i++)
        foo(1, 0);
    for (int i = 0; i < 3000; i++)
        foo(0, 1);
    for (int i = 0; i < 40000; i++)
        foo(1, 1);
    printf("cnt = %d\n", cnt);
}
EOF

clang -fprofile-instr-generate -fcoverage-mapping test.c -o test
./test
llvm-profdata merge default.profraw -o default.profdata
llvm-cov show -instr-profile default.profdata ./test |& tee report.txt

echo ---------------------------------------------------------------------------
if ! grep &>/dev/null '   16|  3.02k|        cnt++; // <= wrong line coverage' report.txt; then
    echo $0 NOT REPRODUCING 1
    exit 1
fi
echo $0 OK

clang --version

cat > test.h << EOF
#define FOO x++
EOF
cat > test.c << EOF
#include <test.h>
int main(void)
{
    int x;
    for (int i=0; i<10; i++) {
        if (i==5)
            break;
        FOO;
        x++;
    }
    return 0;
}
EOF
clang -fprofile-instr-generate -fcoverage-mapping -isystem. test.c -o test
./test
llvm-profdata merge default.profraw -o default.profdata
llvm-cov show -instr-profile default.profdata test |& tee report.txt

echo ---------------------------------------------------------------------------
if ! grep &>/dev/null '    8|      6|        FOO;' report.txt; then
    echo $0 NOT REPRODUCING 1
    exit 1
fi
echo $0 OK

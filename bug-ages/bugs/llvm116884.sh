clang --version

cat > test.c << EOF
int main(){
    int x = 0;
    for (int i=0; ; i++)
    {
        if (x == 2){
            break;
        }
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
if ! grep &>/dev/null '    3|      2|    for (int i=0; ; i++)' report.txt; then
    echo $0 NOT REPRODUCING 1
    exit 1
fi
echo $0 OK

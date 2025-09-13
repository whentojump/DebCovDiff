gcc --version

cat > test.c << 'EOF'
int g;

int main(void) {
    for(int i = 1; i < 2; i++) {
        // (1) it has to be declared in this scope
        int loop_local = 1;

        g++;
        if (i > 100) {
            g++;
            continue;
        }
        g++;

        // (2) the variable is referenced in some way
        &loop_local;

        // (3) there is a "continue" that's in an "if else" block that's
        // executed at least once
        if (1) {
            continue;
        }
    }
}
EOF

gcc --coverage test.c -o test
./test
gcov test
cat test.c.gcov

echo ---------------------------------------------------------------------------
if ! grep &>/dev/null -e '       1\*:   11:            continue;' -e '        1:   11:            continue;' test.c.gcov; then
    echo $0 NOT REPRODUCING 1
    exit 1
fi
echo $0 OK

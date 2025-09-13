gcc --version

cat > test.c << 'EOF'
int arr[10];

int *foo() {
    return arr;
}

int bar() {
    return 0;
}

int main(void) {
    int *a = arr;
    int zero = 0;

    if (zero) {} else {
        // Variant 1 triggering conditions:
        //
        // 1. RHS of assignment is a function call
        // 2. The first function name and assignment are put in one line;
        //    the second function name is put in the other line
        // 3. Inside if(){...}, else{...}, for(){...} etc
        *foo()=
            bar();
    }

    // Variant 2 triggering conditions:
    //
    // 1. RHS of assignment is a dereference
    // 2. The function name and assignment are put in one line; the second
    //    dereference is put in the other line
    // 3. The operand of dereference is referenced elsewhere
    *foo()=
        *a;
    &a;

    return 0;
}
EOF

gcc --coverage test.c -o test
./test
gcov test
cat test.c.gcov

echo ---------------------------------------------------------------------------
if ! grep &>/dev/null '        2:   22:        \*foo()=' test.c.gcov; then
    echo $0 NOT REPRODUCING 1
    exit 1
fi
if ! grep &>/dev/null '        2:   32:    \*foo()=' test.c.gcov; then
    echo $0 NOT REPRODUCING 2
    exit 1
fi
echo $0 OK

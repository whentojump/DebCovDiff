gcc --version

cat > test.c << 'EOF'
int g, h;

int one = 1;

void foo() {
    g = 0;
    while(1) {         // C1 - C2 ?
        g++;           // C1
        int dummy;
        if (g >= 7)
            break;     // C2
        h++;           // C1 - C2
    }

    g = 0;
    while(1) {         // No code ?
        g++;           // C1
        // int dummy;
        if (g >= 7)
            break;     // C2
        h++;           // C1 - C2
    }

    g = 0;
    while(one) {       // C1      ?
        g++;           // C1
        int dummy;
        if (g >= 7)
            break;     // C2
        h++;           // C1 - C2
    }
}

int main(void) {
    for (int i = 0; i < 5; i++)
        foo();
}
EOF

gcc --coverage test.c -o test
./test
gcov test
cat test.c.gcov

echo ---------------------------------------------------------------------------
if ! grep &>/dev/null '       30:    7:    while(1) {         // C1 - C2 ?' test.c.gcov; then
    echo $0 NOT REPRODUCING 1
    exit 1
fi
if ! grep &>/dev/null '        -:   16:    while(1) {         // No code ?' test.c.gcov; then
    echo $0 NOT REPRODUCING 2
    exit 1
fi
if ! grep &>/dev/null -e '       35:   25:    while(one) {       // C1      ?' -e '       40:   25:    while(one) {       // C1      ?' test.c.gcov; then
    echo $0 NOT REPRODUCING 3
    exit 1
fi
echo $0 OK

gcc --version

cat > src1.cc << 'EOF'
int g;

extern "C" {
    int foo(int *x);
}

int never;

void bar() {
    int j = 0;
    while (1)
    {
        g++;
        if (never) {
            g++;
            return;
        }

        int l; // has to be local and in this scope
        foo(&l);

        j++;
        if (j == 11)
            return;
    }
}

int main() {
    for (int i = 0; i < 7; i++)
        bar();
    return 0;
}
EOF

cat > src2.c << 'EOF'
int foo(int *x) {
    return 0;
}
EOF

g++ -c --coverage src1.cc
gcc -c --coverage src2.c
g++ --coverage  src1.o src2.o -o prog
./prog
gcov src1
cat src1.cc.gcov

echo ---------------------------------------------------------------------------
if ! grep &>/dev/null -e '       7\*:   16:            return;' -e '        7:   16:            return;' src1.cc.gcov; then
    echo $0 NOT REPRODUCING 1
    exit 1
fi
echo $0 OK

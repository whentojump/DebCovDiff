gcc --version

cat > test_cpp2.cc << 'EOF'
int a, b;

int foo (int x) { return 1; }

int main(void) {
    if (a
            && foo(b))
        return 1;
    return 0;
}
EOF

g++ --coverage test_cpp2.cc -o test_cpp2
./test_cpp2
gcov -b -c test_cpp2
cat test_cpp2.cc.gcov

echo ---------------------------------------------------------------------------
if ! grep &>/dev/null '        2:    6:    if (a' test_cpp2.cc.gcov; then
    echo $0 NOT REPRODUCING 1
    exit 1
fi
echo $0 OK

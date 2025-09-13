gcc --version

cat > test.cc << 'EOF'
int g;

class C1 {
    int x;
    int y;
public:
    C1() {}
    C1(int x, int y) : x(x),
        y(y)
    { g++; }
};

class C2 : public C1 {
    int a;
    int b;
public:
    C2(int a, int b) : a(a),
        b(b)
    { g++; }
};

int main() {
    C1 c1(2, 3);
    C2 c2(11, 13);
}
EOF

g++ --coverage test.cc -o test
./test
gcov test
cat test.cc.gcov

echo ---------------------------------------------------------------------------
if ! grep &>/dev/null '        2:   17:    C2(int a, int b) : a(a),' test.cc.gcov; then
    echo $0 NOT REPRODUCING 1
    exit 1
fi
echo $0 OK

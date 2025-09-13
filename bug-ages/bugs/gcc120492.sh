gcc --version

cat > test.cc << 'EOF'
#include <vector>
#include <string>

int main() {
    int one = 1;
    std::vector<std::string> v;
    std::string s = "hello";

    if (one)
        v.push_back("hello");

    if (one)
        v.push_back(s);

    if (1)
        v.push_back("hello");

    return 0;
}
EOF

g++ --coverage test.cc -o test
./test
gcov test
cat test.cc.gcov

echo ---------------------------------------------------------------------------
if ! grep &>/dev/null '        2:   10:        v.push_back("hello");' test.cc.gcov; then
    echo $0 NOT REPRODUCING 1
    exit 1
fi
echo $0 OK

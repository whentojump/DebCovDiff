gcc --version

cat > test1.c << 'EOF'
int g;
int foo(int a, int b) {
#include "header.h"
    return g;
}

int main(void) {
    for (int i = 0; i < 1; i++)
        foo(0, 0);
    for (int i = 0; i < 20; i++)
        foo(1, 0);
    for (int i = 0; i < 300; i++)
        foo(0, 1);
    for (int i = 0; i < 4000; i++)
        foo(1, 1);
}
EOF

cat > header.h << EOF
    if (a && b)
        g++;
EOF

gcc --coverage -fcondition-coverage test1.c -o test1
./test1
gcov -b -c --condition test1
cat header.h.gcov
echo ==
cat test1.c.gcov

echo ---------------------------------------------------------------------------
cat test1.c.gcov | head -7 | tail -1 > line7.txt
cat test1.c.gcov | head -8 | tail -1 > line8.txt
cat test1.c.gcov | head -9 | tail -1 > line9.txt
cat test1.c.gcov | head -10 | tail -1 > line10.txt
cat test1.c.gcov | head -11 | tail -1 > line11.txt

if ! grep &>/dev/null '     4321:    2:int foo(int a, int b) {' line7.txt; then
    echo $0 NOT REPRODUCING 1
    exit 1
fi
if ! grep &>/dev/null 'branch  0 taken 4020 (fallthrough)' line8.txt; then
    echo $0 NOT REPRODUCING 2
    exit 1
fi
if ! grep &>/dev/null 'branch  1 taken 301' line9.txt; then
    echo $0 NOT REPRODUCING 3
    exit 1
fi
if ! grep &>/dev/null 'condition outcomes covered 4/4' line10.txt; then
    echo $0 NOT REPRODUCING 4
    exit 1
fi
if ! grep &>/dev/null '        -:    3:#include "header.h"' line11.txt; then
    echo $0 NOT REPRODUCING 5
    exit 1
fi
echo $0 OK

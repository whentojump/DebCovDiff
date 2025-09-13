gcc --version

cat > test.c << 'EOF'
int g;

#define INLINE __inline__ __attribute__((__always_inline__))

INLINE int innermost(int x) { return 0; }

INLINE int inner1(void) {
    g++;
    return 0; // -> 1 x direct
}

INLINE int inner2(void) {
    g++;
    return innermost(g); // -> (direct x 2) + indirect
}

// "const" or not also affects the behavior
INLINE int inner3(int const x) {
    g++;                 // -> 1 x direct
    if (x != 3)          // -> 1 x indirect
        return 0;
    return innermost(g); // -> (direct + indirect) x 2
}

// Outer functions for indirectly calling inner functions
void outer1(void) { inner1(); }
void outer2(void) { inner2(); }
void outer3(int x) { inner3(x); }

int main(void) {
    for (int i = 0; i < 22; i++) { // indirect invocation
        outer1();
        outer2();
        outer3(3);
    }
    for (int i = 0; i < 4400; i++) { // direct invocation
        inner1();
        inner2();
        inner3(3);
    }
}
EOF

gcc --coverage test.c -o test
./test
gcov test
cat test.c.gcov

echo ---------------------------------------------------------------------------
# Behavior in the paper's experiments:
#
#        -:    7:INLINE int inner1(void) {
#     4422:    8:    g++;
#     4400:    9:    return 0; // -> 1 x direct
#        -:   10:}
#        -:   11:
#        -:   12:INLINE int inner2(void) {
#     4422:   13:    g++;
#     8822:   14:    return innermost(g); // -> (direct x 2) + indirect
#        -:   15:}
#        -:   16:
#        -:   17:// "const" or not also affects the behavior
#        -:   18:INLINE int inner3(int const x) {
#     4400:   19:    g++;                 // -> 1 x direct
#       22:   20:    if (x != 3)          // -> 1 x indirect
#    #####:   21:        return 0;
#     8844:   22:    return innermost(g); // -> (direct + indirect) x 2
#        -:   23:}

# Behavior of old toolchain
#
#        -:    7:INLINE int inner1(void) {
#     4422:    8:    g++;
#     4400:    9:    return 0; // -> 1 x direct (BUGGY)
#        -:   10:}
#        -:   11:
#        -:   12:INLINE int inner2(void) {
#     4422:   13:    g++;
#     4422:   14:    return innermost(g); // -> direct + indirect
#        -:   15:}
#        -:   16:
#        -:   17:// "const" or not also affects the behavior
#        -:   18:INLINE int inner3(int const x) {
#     4422:   19:    g++;                 // -> direct + indirect
#       22:   20:    if (x != 3)          // -> 1 x indirect (BUGGY)
#    #####:   21:        return 0;
#     4422:   22:    return innermost(g); // -> direct + indirect
#        -:   23:}
if grep 7.5.0 <<< "$(gcc --version | head -1)" >& /dev/null; then
    if ! grep &>/dev/null '       22:   20:    if (x != 3)          //' test.c.gcov; then
        echo $0 NOT REPRODUCING 3
        exit 1
    fi
    if ! grep &>/dev/null '     8844:   14:    return innermost(g); //' test.c.gcov; then
        echo $0 NOT REPRODUCING 4
        exit 1
    fi
    if ! grep &>/dev/null '     8844:   22:    return innermost(g); //' test.c.gcov; then
        echo $0 NOT REPRODUCING 5
        exit 1
    fi
elif grep 16.0.0 <<< "$(gcc --version | head -1)" >& /dev/null; then
    if ! grep &>/dev/null '       22:   20:    if (x != 3)          //' test.c.gcov; then
        echo $0 NOT REPRODUCING 6
        exit 1
    fi
    if ! grep &>/dev/null '     8822:   14:    return innermost(g); //' test.c.gcov; then
        echo $0 NOT REPRODUCING 7
        exit 1
    fi
    if ! grep &>/dev/null '     8844:   22:    return innermost(g); //' test.c.gcov; then
        echo $0 NOT REPRODUCING 8
        exit 1
    fi
else
    if ! grep &>/dev/null '       22:   20:    if (x != 3)          //' test.c.gcov; then
        echo $0 NOT REPRODUCING 1
        exit 1
    fi
    if ! grep &>/dev/null '     4400:    9:    return 0; //' test.c.gcov; then
        echo $0 NOT REPRODUCING 2
        exit 1
    fi
fi
echo $0 OK

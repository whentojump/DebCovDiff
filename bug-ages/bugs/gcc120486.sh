gcc --version

cat > test.c << 'EOF'
int foo(int a, int b) {
   return
      (a
       ? (b
          ? 1
          : 2)
       : 3);
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

gcc --coverage test.c -o test
./test
gcov test
cat test.c.gcov

echo ---------------------------------------------------------------------------
if ! grep &>/dev/null '     8341:    7:       : 3);' test.c.gcov; then
    echo $0 NOT REPRODUCING 1
    exit 1
fi
echo $0 OK

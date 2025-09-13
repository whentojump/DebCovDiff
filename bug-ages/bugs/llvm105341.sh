clang --version

cat > test.c << 'EOF'
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

#define NUM_THREADS 10000

int x;
int y;

void g() {
    if (x % 10000)
        ++y;
    else
        --y;
}

void* f(void* thread_id) {
    x++;
    for (int i = 0; i < 100; i ++)
        g();
    pthread_exit(NULL);
}

int main() {
    pthread_t threads[NUM_THREADS];
    long t;

    for(t = 0; t < NUM_THREADS; t++)
        pthread_create(&threads[t], NULL, f, (void*)t);

    for(t = 0; t < NUM_THREADS; t++)
        pthread_join(threads[t], NULL);

    return 0;
}
EOF

clang -pthread -fprofile-instr-generate -fcoverage-mapping test.c -o test

echo ---------------------------------------------------------------------------
for i in `seq 100`; do
    echo "attempting $i time(s)"
    rm -f report.txt *.prof*
    ./test
    llvm-profdata merge default.profraw -o default.profdata
    llvm-cov show -instr-profile default.profdata ./test >& report.txt

    if grep &>/dev/null '14|  18.4E|        --y;' report.txt; then
        cat report.txt
        echo $0 OK
        exit 0
    fi
done

echo $0 NOT REPRODUCING 1
exit 1

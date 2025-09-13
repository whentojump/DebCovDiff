for i in `seq 0 999`; do
    if ! diff default/$i.c default-1000-serial/$i.c > /dev/null; then
        echo "diff found at $i"
    fi
done

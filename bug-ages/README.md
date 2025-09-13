```shell
docker build -t old-compilers-env .
docker run -it --rm -v $PWD:/usr/src/app old-compilers-env
```

```shell
# In container
bash bugs/setup-links.sh
bash bugs/run.sh |& tee log.txt
```

GCC 7.5.0

```
root@98e9b0fa4923:/usr/src/app# grep 'NOT REPRODUCING' log.txt
/usr/src/app/bugs/gcc117412.sh NOT REPRODUCING 1
/usr/src/app/bugs/gcc120491.sh NOT REPRODUCING 1
/usr/src/app/bugs/gcc120492.sh NOT REPRODUCING 1
/usr/src/app/bugs/gcc120319.sh NOT REPRODUCING 1
/usr/src/app/bugs/llvm114622.sh NOT REPRODUCING 1
root@98e9b0fa4923:/usr/src/app# grep ' OK' log.txt
/usr/src/app/bugs/gcc120321.sh OK
/usr/src/app/bugs/gcc120478.sh OK
/usr/src/app/bugs/gcc120482.sh OK
/usr/src/app/bugs/gcc120490.sh OK
/usr/src/app/bugs/gcc117415.sh OK
/usr/src/app/bugs/gcc120348.sh OK
/usr/src/app/bugs/gcc120484.sh OK
/usr/src/app/bugs/gcc120489.sh OK
/usr/src/app/bugs/gcc120486.sh OK
/usr/src/app/bugs/gcc120332.sh OK
/usr/src/app/bugs/llvm140427.sh OK
/usr/src/app/bugs/llvm116884.sh OK
/usr/src/app/bugs/llvm105341.sh OK
```

GCC 8.4.0

```
root@98e9b0fa4923:/usr/src/app# grep 'NOT REPRODUCING' log.txt
/usr/src/app/bugs/gcc120478.sh NOT REPRODUCING 1
/usr/src/app/bugs/gcc120490.sh NOT REPRODUCING 1
/usr/src/app/bugs/gcc120491.sh NOT REPRODUCING 1
/usr/src/app/bugs/gcc120492.sh NOT REPRODUCING 1
/usr/src/app/bugs/gcc120319.sh NOT REPRODUCING 1
/usr/src/app/bugs/llvm114622.sh NOT REPRODUCING 1
root@98e9b0fa4923:/usr/src/app# grep ' OK' log.txt
/usr/src/app/bugs/gcc120321.sh OK
/usr/src/app/bugs/gcc117412.sh OK
/usr/src/app/bugs/gcc120482.sh OK
/usr/src/app/bugs/gcc117415.sh OK
/usr/src/app/bugs/gcc120348.sh OK
/usr/src/app/bugs/gcc120484.sh OK
/usr/src/app/bugs/gcc120489.sh OK
/usr/src/app/bugs/gcc120486.sh OK
/usr/src/app/bugs/gcc120332.sh OK
/usr/src/app/bugs/llvm140427.sh OK
/usr/src/app/bugs/llvm116884.sh OK
/usr/src/app/bugs/llvm105341.sh OK
```

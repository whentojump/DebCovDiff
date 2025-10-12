FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    bzip2 \
    gcc \
    g++ \
    git \
    flex \
    bison \
    file \
    clang-7 \
    clang++-7 \
    lld-7 \
    && apt-get clean

RUN ln -sf /usr/bin/clang-7 /usr/bin/clang && \
    ln -sf /usr/bin/clang++-7 /usr/bin/clang++ && \
    ln -sf /usr/bin/llvm-profdata-7 /usr/bin/llvm-profdata && \
    ln -sf /usr/bin/llvm-cov-7 /usr/bin/llvm-cov

WORKDIR /usr/src

# Ubuntu 18.04 distribution only has GCC 7.5.0 or 8.4.0 but we want 8.0.
# Thus build from source. We checkout a few commits before releases/gcc-8.1.0
# where gcc/BASE-VER lastly stayed 8.0.1.

RUN git clone --depth 10 --branch releases/gcc-8.1.0 git://gcc.gnu.org/git/gcc.git gcc-source && \
    cd gcc-source && \
    git checkout 9b646cb298fa7159c600f040daa7dbc2ea96504d

WORKDIR /usr/src/gcc-source

RUN ./contrib/download_prerequisites

WORKDIR /usr/src
RUN mkdir gcc-build && \
    cd gcc-build && \
    ../gcc-source/configure \
      --enable-languages=c,c++ \
      --disable-multilib \
      --disable-bootstrap && \
    make -j$(nproc) && \
    make install

RUN rm -rf /usr/src/gcc-source /usr/src/gcc-build

WORKDIR /usr/src/app

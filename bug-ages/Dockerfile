# Use Ubuntu 18.04 as the base image
FROM ubuntu:18.04

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Update package lists and install compilers and build tools
# Added gfortran-8 to the list of packages
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    software-properties-common \
    gcc-8 \
    g++-8 \
    gfortran-8 \
    clang-7 \
    clang++-7 \
    lld-7 \
    make \
    vim \
    && apt-get clean

# --- Configure Alternatives ---
# Set priorities to easily switch between compilers.
# Priority 80 for GCC 8 and 70 for Clang 7. The highest priority is the default.
RUN update-alternatives --install /usr/bin/cc cc /usr/bin/gcc-8 80
RUN update-alternatives --install /usr/bin/c++ c++ /usr/bin/g++-8 80
RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-8 80
RUN update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-8 80
RUN update-alternatives --install /usr/bin/gfortran gfortran /usr/bin/gfortran-8 80

RUN update-alternatives --install /usr/bin/cc cc /usr/bin/clang-7 70
RUN update-alternatives --install /usr/bin/c++ c++ /usr/bin/clang++-7 70
RUN update-alternatives --install /usr/bin/clang clang /usr/bin/clang-7 70
RUN update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-7 70

# Create a directory for source code inside the container
WORKDIR /usr/src/app

# Set the default command to bash
CMD ["/bin/bash"]

mkdir -p /tmp/patches
cd /tmp/patches

wget https://github.com/gcc-mirror/gcc/commit/08a52331803f66a4aaeaedd278436ca8eac57b50.diff -O gcc-mcdc.all.diff

grep -E '^\+\s*(gcc_assert|gcc_unreachable|gcc_checking_assert|internal_error|fatal_error|debug_[a-z_]+)' gcc-mcdc.all.diff
grep -E '^\+\s*(gcc_assert|gcc_unreachable|gcc_checking_assert|internal_error|fatal_error|debug_[a-z_]+)' gcc-mcdc.all.diff | wc -l

wget https://github.com/llvm/llvm-project/commit/8b2bdfbca7c1db272e4e703445f5626b4bc4b9d3.diff -O llvm-mcdc.clang.diff
wget https://github.com/llvm/llvm-project/commit/618a22144db5e45da8c95dc22064103e1b5e5b71.diff -O llvm-mcdc.llvm-cov.diff
wget https://github.com/llvm/llvm-project/commit/a50486fd736ab2fe03fcacaf8b98876db77217a7.diff -O llvm-mcdc.compiler-rt.diff

grep -E '^\+\s*(llvm_unreachable|report_fatal_error|assert|LLVM_DEBUG|verify(Function|Module)|errs\(\)|dbgs\(\))' llvm-mcdc.*.diff
grep -E '^\+\s*(llvm_unreachable|report_fatal_error|assert|LLVM_DEBUG|verify(Function|Module)|errs\(\)|dbgs\(\))' llvm-mcdc.*.diff | wc -l

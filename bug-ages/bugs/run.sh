THIS_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

BUG_IDS=(
    "gcc120321"
    "gcc117412"
    "gcc120478"
    "gcc120482"
    "gcc120490"
    "gcc117415"
    "gcc120348"
    "gcc120484"
    "gcc120489"
    "gcc120491"
    "gcc120492"
    "gcc120486"
    "gcc120319"
    "gcc120332"
    "llvm140427"
    "llvm114622"
    "llvm116884"
    "llvm105341"
)

for BUG_ID in "${BUG_IDS[@]}"; do
    TMPDIR=$(mktemp -d)
    pushd $TMPDIR

    bash $THIS_DIR/$BUG_ID.sh

    popd
    echo $TMPDIR
done

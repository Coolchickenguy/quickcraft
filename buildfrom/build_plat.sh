# Check if the script has received three arguments
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <win/linux/macos>"
    exit 1
fi
platform=$1
shdir=$(dirname $0)
builddir="build/build-$platform"
rm -rf "$builddir"
mkdir -p "$builddir"
mkdir "$builddir/assets"
cp $shdir/sources/assets-all/* "$builddir/assets"
if [ "$1" = "win" ]; then
    cp $shdir/sources/assets-win/* "$builddir/assets"
    cp $shdir/sources/main-win/* "$builddir"
fi
build_unix() {
    cp $shdir/sources/assets-unix/* "$builddir/assets"
    cp $shdir/sources/main-unix/* "$builddir"
}
if [ "$1" = "linux" ]; then
    build_unix
    cp $shdir/sources/assets-linux/* "$builddir/assets"
    cp $shdir/sources/main-linux/* "$builddir"
fi
if [ "$1" = "macos" ]; then
    build_unix
    #cp "$shdir/sources/assets-macos/*" "$builddir/assets" || true
    #cp "$shdir/sources/main-macos/*" "$builddir" || true
fi
buildzip="build/build-$platform.zip"
zip -q -r "$buildzip" "$builddir" 
echo "$buildzip"

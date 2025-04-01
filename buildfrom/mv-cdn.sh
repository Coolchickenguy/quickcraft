echo "Moving $1 to cdn" >&2

sum=$(cat $1 | md5sum | cut -d' ' -f1)
ext=${1##*.}
path="./cdn/$sum.$ext"
mv $1 $path
echo $path
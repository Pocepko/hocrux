cp copy_map.png map.png

python3 ../code/hocrux.py split map.png -n 5 3

rm map.png
rm map2.png
rm map4.png

python3 ../code/hocrux.py bind map 3

rm map?.png

if diff "map.png" "copy_map.png" > /dev/null; then
    rm map.png
    exit 0
else
    rm map.png
    exit 1
fi

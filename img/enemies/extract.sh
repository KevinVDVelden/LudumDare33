#!/bin/bash
rm *.png

for i in `echo "1|lines 2|head 3|torso 4|legs 5|hands 6|arms"`
do
    index=$(echo $i|cut -f1 -d\|)
    file=$(echo $i|cut -f2 -d\|)

    convert enemy.psd[0] enemy.psd[$index] \( -clone 0 -alpha transparent \) -swap 0 +delete -coalesce -compose src-over -composite enemy_"$file".png
done

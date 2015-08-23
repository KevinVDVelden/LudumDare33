#!/bin/bash
echo include target_list.mk
echo

echo -n 'BUILDING_NAMES=' > target_list.mk

cat buildings.txt | grep \| | while read line
do
    file=$(echo $line|cut -f1 -d\|)
    base=$(echo $line|cut -f2 -d\|)
    top=$(echo $line|cut -f3 -d\|)

    echo -n $file' ' >> target_list.mk

    echo 'combined/'$file'_0.png: $(BRIDGES) parts/'$top'.png '$base'_base.png'
    echo '	bash combine.sh '$file' parts/'$top.png' '$base'_base.png'
done
echo
echo

cat hues.txt | while read line
do
    hue=$(echo $line|cut -f1 -d\|)
    file=$(echo $line|cut -f2 -d\|)

    echo parts/$file:
    echo '	bash buildHue.sh $@ '$hue
done

#!/bin/bash
hue_file=$2
name=$1

if [ ! -d combined ]
then
    mkdir combined
fi

echo -n $name: 
for bridgeI in `seq 0 15`
do
    bridge_file=parts/bridge_"$bridgeI".png

    composite -gravity center $bridge_file ziggurat_base.png tmp/ziggurat.png
    composite -gravity center $hue_file tmp/ziggurat.png combined/building_"$name"_"$bridgeI".png
    echo -n .

    composite -gravity center $bridge_file pylon_base.png tmp/pylon.png
    composite -gravity center $hue_file tmp/pylon.png combined/pylon_"$name"_"$bridgeI".png
    echo -n .
done
echo

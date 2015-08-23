#!/bin/bash
name=$1
top_file=$2
bottom_file=$3

if [ ! -d combined ]
then
    mkdir combined
fi

echo -n $name: 
for bridgeI in `seq 0 15`
do
    bridge_file=parts/bridge_"$bridgeI".png

    composite -gravity center $bridge_file $bottom_file tmp/"$bottom_file"
    composite -gravity center $top_file tmp/"$bottom_file" combined/"$name"_"$bridgeI".png
    echo -n .
done
echo

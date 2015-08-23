#!/bin/bash
rm tmp/*
for rot_all in 0,down 90,left 180,up 270,right
do
    rot=$(echo $rot_all|cut -f1 -d,)
    rot_name=$(echo $rot_all|cut -f2 -d,)

    convert -rotate $rot bridge_down.png tmp/bridge_"$rot_name".png
done

for bridgeI in `seq 0 15`
do
    cp empty.png tmp/cur_bridge.png

    for bridge in 1,down 2,left 4,up 8,right
    do
        mask=$(echo $bridge|cut -f1 -d,)
        bridge=$(echo $bridge|cut -f2 -d,)

        temp=$((bridgeI&mask))

        if [ $temp -gt 0 ]
        then
            echo $bridgeI
            mv tmp/cur_bridge.png tmp/tmp_bridge.png
            composite tmp/bridge_"$bridge".png tmp/tmp_bridge.png tmp/cur_bridge.png
        fi
    done

    for hue_all in `cat files.txt|grep -v '#'|grep ,`
    do
        hue=$(echo $hue_all|cut -f1 -d\|)
        hue_name=$(echo $hue_all|cut -f2 -d\|)

        echo $hue
        echo $hue_name

        convert -modulate $hue effect_red.png tmp/effect_curHue.png


        composite -gravity center tmp/cur_bridge.png ziggurat_base.png tmp/ziggurat.png
        composite -gravity center tmp/effect_curHue.png tmp/ziggurat.png combined/building_"$hue_name"_"$bridgeI".png

        composite -gravity center tmp/cur_bridge.png pylon_base.png tmp/pylon.png
        composite -gravity center tmp/effect_curHue.png tmp/pylon.png combined/pylon_"$hue_name"_"$bridgeI".png
    done
done

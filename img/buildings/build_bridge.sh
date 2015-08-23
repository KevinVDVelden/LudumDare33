#!/bin/bash
if [ $# == 0 ]
then
    for rot_all in 0,down 90,left 180,up 270,right
    do
        rot=$(echo $rot_all|cut -f1 -d,)
        rot_name=$(echo $rot_all|cut -f2 -d,)

        convert -rotate $rot bridge_down.png tmp/bridge_"$rot_name".png
    done
else
    bridgeI=$1

    cp empty.png tmp/cur_bridge.png

    for bridge in 1,down 2,left 4,up 8,right
    do
        mask=$(echo $bridge|cut -f1 -d,)
        bridge=$(echo $bridge|cut -f2 -d,)

        temp=$((bridgeI&mask))

        if [ $temp -gt 0 ]
        then
            mv tmp/cur_bridge.png tmp/tmp_bridge.png
            composite tmp/bridge_"$bridge".png tmp/tmp_bridge.png tmp/cur_bridge.png
        fi
    done

    mv tmp/cur_bridge.png parts/bridge_"$bridgeI".png
fi

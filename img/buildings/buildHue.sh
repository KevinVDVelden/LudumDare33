#!/bin/bash
output="$1"
shift

hue="$1"
shift

convert -modulate $hue effect_red.png tmp/effect_curHue.png

cp tmp/effect_curHue.png "$output"

if [ $# -gt 0 ]
then
    for i in `seq 2 $1`
    do
        composite tmp/effect_curHue.png "$output" "$output"
    done
fi

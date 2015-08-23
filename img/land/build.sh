#!/bin/bash
rm *_night.png

for a in *.png
do
    convert "$a" -modulate 60,80 "`echo $a|sed 's/\.png/_night.png/'`"
done

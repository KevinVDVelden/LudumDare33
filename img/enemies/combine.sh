#!/bin/bash
output=$1
shift

cp "$1" "$output"
shift

while [ $# -ge 1 ]
do
    echo $1
    composite "$1" "$output" "$output"
    shift
done

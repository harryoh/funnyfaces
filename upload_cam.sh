#!/bin/bash

S3URL=s3://funnyfaces

for (( ; ; ))
do
    IMG=/tmp/$(date +%s).jpg
    fswebcam -r 640x480 -S 7 \
             --set "Backlight Compensation"=1 \
             --set brightness=50% \
             --set contrast=40% \
             --set gamma=50% \
             --set saturation=50% \
             --set hue=50% \
             --set sharpness=50% \
             --no-banner $IMG \
             >/dev/null 2>&1 \
        && aws s3 cp $IMG $S3URL \
        && rm -f $IMG
    sleep 5
done

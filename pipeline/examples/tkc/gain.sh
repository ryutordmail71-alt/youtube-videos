#!/bin/bash
# $1 file, $2 dB
ffmpeg -v error -y -i "$1" -c:v copy -af "volume=$2dB,alimiter=limit=0.79:level=false" -ar 48000 -c:a aac -b:a 160k -movflags +faststart "${1%.mp4}_g.mp4" && mv "${1%.mp4}_g.mp4" "$1"
ffmpeg -nostats -i "$1" -af ebur128=peak=true -f null - 2>&1 | grep -A14 Summary | grep -E "I:|Peak"

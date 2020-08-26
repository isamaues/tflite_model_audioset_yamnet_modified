#!/bin/bash
import os

echo "Checking RFCOMM."
sh ./set_rfcomm.sh
#except
echo "$RFCOMM OK"

while True
do
  echo "Press <CTRL+C> to exit."
  os.system("arecord -D hw:1,0 -f S16_LE -c1 -r44100 -s 43000 temp.wav")
  os.system("python3 inference_bt.py temp.wav")
  #sleep 1
  #if [[ "$i" == '2' ]]; then # IF KEYBOARD INTERRUPT?
    #break
  #fi
done

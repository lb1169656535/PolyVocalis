#!/bin/bash
conda init
conda activate polyVocalis

python app.py \
  -i /home/liub/project/data/test.m4a \
  -o ./output \
  -w 60 \
  -t 4 \
  --gpu 0


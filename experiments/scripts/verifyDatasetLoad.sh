#!/bin/bash
# Usage:
# ./experiments/scripts/verifyDatasetLoad.sh GPU DATASET IMAGE_SET

set -e

GPU_ID=$1
DATASET=$2
IMAGE_SET=$3
NET_lc=${NET,,}

array=( $@ )
len=${#array[@]}
EXTRA_ARGS=${array[@]:3:$len}
EXTRA_ARGS_SLUG=${EXTRA_ARGS// /_}

time ./tools/train_net.py --gpu ${GPU_ID} \
  --solver models/VGG16/faster_rcnn_end2end/solver.prototxt \
  --weights /home/gauenk/Documents/other/py-faster-rcnn/data/faster_rcnn_models/downloaded_imagenet/VGG16.v2.caffemodel \
  --imdb ${DATASET}"-"${IMAGE_SET}"-default" \
  --cfg experiments/cfgs/faster_rcnn_end2end.yml
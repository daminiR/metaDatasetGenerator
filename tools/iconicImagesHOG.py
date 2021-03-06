#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 13 21:32:08 2018

@author: zkapach
"""

import _init_paths
from core.train import get_training_roidb
from core.config import cfg, cfg_from_file, cfg_from_list, get_output_dir, loadDatasetIndexDict
from datasets.factory import get_repo_imdb
from datasets.ds_utils import load_mixture_set,print_each_size,computeTotalAnnosFromAnnoCount,cropImageToAnnoRegion
import os.path as osp
import datasets.imdb
import argparse
import pprint
import numpy as np
import sys,os,cv2
# pytorch imports
from datasets.pytorch_roidb_loader import RoidbDataset
from ntd.hog_svm import plot_confusion_matrix, extract_pyroidb_features


def parse_args():
    """
    Parse input arguments
    """
    parser = argparse.ArgumentParser(description='Test loading a mixture dataset')
    parser.add_argument('--cfg', dest='cfg_file',
                        help='optional config file',
                        default=None, type=str)
    parser.add_argument('--setID', dest='setID',
                        help='which 8 digit ID to read from',
                        default='11111111', type=str)
    parser.add_argument('--repetition', dest='repetition',
                        help='which repetition to read from',
                        default='1', type=str)
    parser.add_argument('--size', dest='size',
                        help='which size to read from',
                        default=1000, type=int)
    parser.add_argument('--save', dest='save',
                        help='save some samples with bboxes visualized?',
                        action='store_true')
    parser.add_argument('--rand', dest='randomize',
                        help='randomize (do not use a fixed seed)',
                        action='store_true')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    return args

def get_bbox_info(roidb,size):
    areas = np.zeros((size))
    widths = np.zeros((size))
    heights = np.zeros((size))
    actualSize = 0
    idx = 0
    for image in roidb:
        if image['flipped'] is True: continue
        bbox = image['boxes']
        for box in bbox:
            actualSize += 1
            widths[idx] = box[2] - box[0]
            heights[idx] = box[3] - box[1]
            assert widths[idx] >= 0,"widths[{}] = {}".format(idx,widths[idx])
            assert heights[idx] >= 0
            areas[idx] = widths[idx] * heights[idx]
            idx += 1
    return areas,widths,heights


if __name__ == '__main__':
    args = parse_args()

    print('Called with args:')
    print(args)

    if args.cfg_file is not None:
        cfg_from_file(args.cfg_file)

    print('Using config:')
    pprint.pprint(cfg)

    if not args.randomize:
        np.random.seed(cfg.RNG_SEED)

    setID = args.setID
    repetition = args.repetition
    size = args.size
    
    roidb,annoCount = load_mixture_set(setID,repetition,size)
    numAnnos = computeTotalAnnosFromAnnoCount(annoCount)

    print("\n\n-=-=-=-=-=-=-=-=-\n\n")
    print("Report:\n\n")
    print("Mixture Dataset: {} {} {}\n\n".format(setID,repetition,size))

    print("number of images: {}".format(len(roidb)))
    print("number of annotations: {}".format(numAnnos))
    print("size of roidb in memory: {}kB".format(len(roidb) * sys.getsizeof(roidb[0])/1024.))
    print("example roidb:")
    for k,v in roidb[0].items():
        print("\t==> {},{}".format(k,type(v)))
        print("\t\t{}".format(v))

    print("computing bbox info...")
    areas, widths, heights = get_bbox_info(roidb,numAnnos)

    print("ave area: {} | std. area: {}".format(np.mean(areas),np.std(areas,dtype=np.float64)))
    print("ave width: {} | std. width: {}".format(np.mean(widths),np.std(widths,dtype=np.float64)))
    print("ave height: {} | std. height: {}".format(np.mean(heights),np.std(heights,dtype=np.float64)))
    prefix_path = cfg.IMDB_REPORT_OUTPUT_PATH
    if osp.exists(prefix_path) is False:
        os.makedirs(prefix_path)

    path = osp.join(prefix_path,"areas.dat")
    np.savetxt(path,areas,fmt='%.18e',delimiter=' ')
    path = osp.join(prefix_path,"widths.dat")
    np.savetxt(path,widths,fmt='%.18e',delimiter=' ')
    path = osp.join(prefix_path,"heights.dat")
    np.savetxt(path,heights,fmt='%.18e',delimiter=' ')

        
    print("-=-=-=-=-=-")

    clsToSet = loadDatasetIndexDict()

    print("as pytorch friendly ")

    pyroidb = RoidbDataset(roidb,[1,2,3,4,5,6,7,8],loader=cv2.imread,transform=cropImageToAnnoRegion)
    

    print('fdsggrfdsgsdfgdsgdsfgdsgfdsgfsdgdfsgsgsd')
    
    print(type(pyroidb))
    print(type(pyroidb[0]))
    print(type(pyroidb[0][0]))
    print(type(pyroidb[0][1]))

    print(pyroidb.__len__())


    # X, y, X_idx = extract_pyroidb_features(pyroidb, feat_type = 'hog')

    
    # print(pyroidb.roidb[872])
    # print(pyroidb[872])
    # errors = 0
    # counter = 0
    # try: 
    #     for file_p in pyroidb:
    #         print(file_p[1])
    #         counter = counter + 1
    # except:
    #     errors = errors + 1
    # print('num of errors', errors)
    # print(counter)

    # for i in range(pyroidb.__len__()):
    #     try:
    #         # print(i)
    #         print(pyroidb[i][1])
    #     except:
    #         errors = errors + 1



    # for i in range(pyroidb.__len__()):
    #     print(pyroidb[i][1])


    # print(errors)
    # print(errors)


    if args.save:
       print("save 30 cropped annos in output folder.")
       saveDir = "./output/mixedDataReport/"
       if not osp.exists(saveDir):
           print("making directory: {}".format(saveDir))
           os.makedirs(saveDir)

       for i in range(30):
           cls = roidb[i]['set']
           ds = clsToSet[cls]
           fn = osp.join(saveDir,"{}_{}.jpg".format(i,ds))
           print(fn)
           cv2.imwrite(fn,pyroidb[i][0])



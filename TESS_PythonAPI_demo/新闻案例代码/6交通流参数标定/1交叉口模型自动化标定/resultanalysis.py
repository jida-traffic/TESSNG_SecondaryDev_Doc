# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 01:23:19 2023

@author: 11917
"""
import pandas as pd
import numpy as np
import os

# 本脚本功能为：交叉口评价指标计算

# 真实数据
# 东进口	直行  97.5
# 	        左转  58.5
# 西进口	直行  78
# 	        左转  19.5
# 南进口	直行  71.5
# 	        左转  65
# 北进口	直行  169
# 	        左转  110.5

## 仿真结果文件夹路径
file_path_simu = "C:\\Users\\ZDH\\OneDrive - tongji.edu.cn\\TESS教材\\交叉口自动化标定\\SimuResult\\芜湖-初始模型_ver2.tess\\20231120152647_end"



def resultanalysis(file_path_simu):
    # 检测器ID列表
    queue_detector = {"东直": ["排队计数器_集计数据_东直1(ID11).csv", "排队计数器_集计数据_东直2(ID10).csv", "排队计数器_集计数据_东直3(ID9).csv"],
                      "东左": ["排队计数器_集计数据_东左1(ID29).csv", "排队计数器_集计数据_东左2(ID28).csv"],
                      "西直": ["排队计数器_集计数据_西直1(ID1).csv", "排队计数器_集计数据_西直2(ID3).csv"],
                      "西左": ["排队计数器_集计数据_西左1(ID101).csv", "排队计数器_集计数据_西左2(ID2).csv"],
                      "南直": ["排队计数器_集计数据_南直1(ID21).csv", "排队计数器_集计数据_南直2(ID22).csv", "排队计数器_集计数据_南直3(ID23).csv"],
                      "南左": ["排队计数器_集计数据_南左(ID20).csv"],
                      "北直": ["排队计数器_集计数据_北直1(ID16).csv", "排队计数器_集计数据_北直2(ID15).csv", "排队计数器_集计数据_北直3(ID14).csv"],
                      "北左": ["排队计数器_集计数据_北左1(ID19).csv", "排队计数器_集计数据_北左2(ID18).csv", "排队计数器_集计数据_北左3(ID17).csv"]
                      }

    queue_real = {"东直": 97.5,
                  "东左": 58.5,
                  "西直": 78,
                  "西左": 19.5,
                  "南直": 71.5,
                  "南左": 65,
                  "北直": 169,
                  "北左": 110.5
                  }

    RE = {"东直": 0,
          "东左": 0,
          "西直": 0,
          "西左": 0,
          "南直": 0,
          "南左": 0,
          "北直": 0,
          "北左": 0
          }

    for direction in queue_detector:
        max_queue = []
        for id in queue_detector[direction]:
            ## 找到文件夹下记录集计数据的文件位置
            path = os.path.join(file_path_simu,id)
            queue_length = pd.read_csv(path,skiprows = 1,usecols=[3],header=None)
            max_queue.append(np.mean(queue_length))
        real = queue_real[direction]
        simu = np.mean(max_queue)
        re = abs(real - simu)/real * 100
        RE[direction] = re

    return RE

if __name__ == '__main__':
    RE = resultanalysis(file_path_simu)
    print(RE)


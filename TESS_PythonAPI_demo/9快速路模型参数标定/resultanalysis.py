# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 01:23:19 2023

@author: 11917
"""
import pandas as pd
import numpy as np
import os

# 本脚本功能为：快速路评价指标计算

## 仿真结果文件夹路径
file_path_simu = "C:\\Users\\ZDH\\OneDrive - tongji.edu.cn\\TESS教材\\快速路自动化标定\\SimuResult\\武宁路09323.tess\\20231114130939"
## 现实路况线圈数据
file_path_real = "C:\\Users\\ZDH\\OneDrive - tongji.edu.cn\\TESS教材\\武宁路20090323\\real.csv"

def resultanalysis(file_path_simu,file_path_real):
    ## 找到文件夹下记录集计数据的文件位置
    paths = os.listdir(file_path_simu)
    ## 找到线圈集计数据
    paths = paths[12:23]

    ## 读取现实路况中的速度矩阵和流量矩阵
    real = pd.read_csv(file_path_real, header=None)
    SCM_r = np.array(real.loc[0:47, 5:9]).transpose()  # 5-9列为速度
    V = np.array(real.loc[0:47, 0:4]).transpose()  # 0-4列为流量

    # In[0]
    ## 初始化SCM和E矩阵
    SCM_s = np.zeros([5, 48])
    E = np.zeros([5, 48])

    ##  五个线圈所对应断面的仿真模型中的检测器编号（tips：仿真模型中一个检测器只能检测一个车道）
    ##  车道数3，2，2，2，2
    No_cluster = [[0, 3, 4], [5, 6], [7, 8], [9, 10], [1, 2]]
    ## 统计每个断面的流量
    for number in range(5):
        ## 过渡矩阵temp
        temp = pd.DataFrame(np.zeros([48, 3]), columns=['speed', 'flow', 's*f'])
        for collector in No_cluster[number]:  ##

            ## 读数据并进行简单删减
            data = pd.read_csv(os.path.join(file_path_simu, paths[collector]), header=0, encoding='gbk')
            data = data[["平均车速(km/h)", "车辆数"]]
            data = data.loc[2:, :]  # 去掉0，1预热，计算9个小时的
            data = data.reset_index(drop=True)

            temp['flow'] += data["车辆数"]
            temp['s*f'] += data["平均车速(km/h)"] * data["车辆数"]

        SCM_s[number, :] = pd.Series(temp['s*f'] / temp['flow'])
        E[number, :] = pd.Series(temp['flow'])

    # In[1] 指标运算
    BSCM_s = SCM_s <= 45
    BSCM_s = BSCM_s * 1
    BSCM_r = SCM_r <= 45
    BSCM_r = BSCM_r * 1
    ## C1
    C1_up = sum(sum(1 * ((BSCM_s + BSCM_r) == 2)))
    C1_down = sum(sum(BSCM_s + BSCM_r) / 2)
    C1 = C1_up / C1_down

    ##C2
    C2_up = sum(sum(((BSCM_s + BSCM_r) > 0) * abs(SCM_s - SCM_r)))
    C2_down = sum(sum(((BSCM_s + BSCM_r) > 0) * (SCM_s + SCM_r) / 2))
    C2 = C2_up / C2_down

    ##GEH
    GEH_matrix = np.sqrt((E - V) * (E - V) / (E + V) * 2)
    GEH = np.percentile(GEH_matrix, 85)

    ##DevS
    DevS_matrix = abs(SCM_s - SCM_r) / SCM_r
    DevS = np.average(DevS_matrix)

    print('C1:', C1)
    print('C2:', C2)
    print('GEH:', GEH)
    print('DevS:', DevS)
    return [C1,C2,GEH,DevS]

if __name__ == '__main__':
    result = resultanalysis(file_path_simu,file_path_real)
    print(result)
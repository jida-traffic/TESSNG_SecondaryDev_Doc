# -*- coding: utf-8 -*-
import os
from pathlib import Path
import sys

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import time
from Tessng import *
from MyPlugin import *
from multiprocessing import Process
import matplotlib.pyplot as plt
from resultanalysis import *
import os
from sko.GA import GA

def tess_run(Params):
    # 该函数多加了一个Params参数，传递4个跟驰模型参数给MySimulator
    app = QApplication()

    workspace = os.fspath(Path(__file__).resolve().parent)
    config = {'__workspace':workspace,
              '__netfilepath':"./武宁路0932313_17.tess",
              '__simuafterload': True,
              '__custsimubysteps': True
              }
    plugin = MyPlugin(Params)
    factory = TessngFactory()
    tessng = factory.build(plugin, config)
    if tessng is None:
        sys.exit(0)
    else:
        sys.exit(app.exec_())



def evaluation():
    # 仿真文件和真实数据文件路径
    # 真实传感器数据路径
    file_path_real = ".\\real.csv"
    # 仿真输出文件路径
    dir_path_simu = ".\\SimuResult\\武宁路0932313_17.tess"
    # 默认最新的仿真结果为本次tess仿真结果
    dirs = os.listdir(dir_path_simu)
    dir = dirs[-1]
    file_path_simu = os.path.join(dir_path_simu,dir)
    # 结果评价，返回四个评价指标C1，C2，GEH，DevS
    result = resultanalysis(file_path_simu,file_path_real)
    # 返回值
    return cateria(result)

def cateria(result):
    # 仿真精度阈值
    C1 =  result[0] - 0.7
    C2 =  result[1] - 0.65
    GEH = (5 - result[2]) * 0.1  #归一化
    DevS = 0.15 - result[3]
    return C1 + C2 + GEH + DevS

def optfunc(p):
    # 遗传算法参数
    alpha, beit, safedistance, safeinterval = p
    # 仿真计数器
    global count
    count += 1
    print(f"第{count}次仿真已开始")
    # 创建子进程来实现tess仿真
    t = Process(target=tess_run,args=([alpha, round(beit, 0), safedistance, safeinterval],)) #实例化进程对象
    t.start()
    # 等待TESS仿真结束，即子进程结束
    t.join()
    # TESS仿真结果计算
    x = evaluation()
    print("Result:",x)
    return -1 * x



if __name__ == '__main__':
    # 遗传算法
    count = 0
    ga = GA(func=optfunc, n_dim=4, size_pop=10, max_iter=10, prob_mut=0.05, lb=[1.0, 1.0, 1.0, 1.0], ub=[3.5, 3.5, 2.2, 2.2], precision=0.01)
    best_x, best_y = ga.run()
    print('best_Params:', best_x,"best_result:",best_y)
    print('结束测试')

    # 绘制结果
    Y_history = pd.DataFrame(ga.all_history_Y)
    fig, ax = plt.subplots(2, 1)
    ax[0].plot(Y_history.index, Y_history.values, '.', color='red')
    Y_history.min(axis=1).cummin().plot(kind='line')
    plt.show()

    # 结果分析
    # # 真实传感器数据路径
    # file_path_real = "C:\\Users\\ZDH\\OneDrive - tongji.edu.cn\\TESS教材\\武宁路20090323\\real.csv"
    # # 仿真输出文件路径
    # file_path_simu = "C:\\Users\\ZDH\\OneDrive - tongji.edu.cn\\TESS教材\\快速路自动化标定\\SimuResult\\武宁路0932313_17.tess\\20231117180545end"
    # # 结果评价，返回四个评价指标C1，C2，GEH，DevS
    # result = resultanalysis(file_path_simu,file_path_real)
    # print(result)




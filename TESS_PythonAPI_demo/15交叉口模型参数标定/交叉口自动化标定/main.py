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
from multiprocessing import Process,Manager
from resultanalysis import *
import os
from sko.GA import GA
import matplotlib.pyplot as plt

def tess_run(Params):
    # 该函数多加了一个Params参数，传递4个跟驰模型参数给MySimulator
    app = QApplication()

    workspace = os.fspath(Path(__file__).resolve().parent)
    config = {'__workspace':workspace,
              '__netfilepath':"./芜湖-初始模型_ver2.tess",
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
    # 仿真输出文件路径
    dir_path_simu = "C:\\Users\\ZDH\\OneDrive - tongji.edu.cn\\TESS教材\\交叉口自动化标定\\SimuResult\\芜湖-初始模型_ver2.tess"
    # 默认最新的仿真结果为本次tess仿真结果
    dirs = os.listdir(dir_path_simu)
    dir = dirs[-1]
    file_path_simu = os.path.join(dir_path_simu,dir)
    # 结果评价，返回四个评价指标C1，C2，GEH，DevS
    results = resultanalysis(file_path_simu)
    # 返回所有进口道平均最大排队长度相对误差
    max_queue = []
    for result in results:
        max_queue.append(results[result])
    return np.mean(max_queue)


def optfunc(p):
    # 遗传算法参数
    alpha, beit, safedistance, safeinterval = p
    # 仿真计数器
    global count
    count += 1
    print(f"第{count}次仿真已开始")
    # 创建子进程来实现tess仿真
    t = Process(target=tess_run,args=([alpha, beit, safedistance, safeinterval],)) #实例化进程对象
    t.start()
    # 等待TESS仿真结束，即子进程结束
    t.join()
    # TESS仿真结果计算
    x = evaluation()
    print("RE：",x)
    return x



if __name__ == '__main__':
    # 遗传算法
    count = 0
    ga = GA(func=optfunc, n_dim=4, size_pop=10, max_iter=10, prob_mut=0.05, lb=[2.0, 1.0, 1.0, 1.0], ub=[5.0, 2.0, 2.0, 2.0], precision=0.1)
    best_x, best_y = ga.run()
    print('best_Params:', best_x,"best_RE:",best_y)

    # 绘制结果
    Y_history = pd.DataFrame(ga.all_history_Y)
    fig, ax = plt.subplots(2, 1)
    ax[0].plot(Y_history.index, Y_history.values, '.', color='red')
    Y_history.min(axis=1).cummin().plot(kind='line')
    plt.show()

    print('结束测试')




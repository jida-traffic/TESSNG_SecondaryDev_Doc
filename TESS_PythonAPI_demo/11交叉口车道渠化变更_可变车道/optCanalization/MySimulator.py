import json
import math
import random
from PySide2.QtCore import *
from shiboken2.shiboken2 import wrapInstance

from Tessng import TessInterface, SimuInterface, PyCustomerSimulator, IVehicle, ILink
from Tessng import m2p, p2m, tessngIFace, tessngPlugin
from Tessng import *
import random
from datetime import datetime

from SecondaryDevelopmentCases import SecondaryDevCases



# 用户插件子类，代表用户自定义与仿真相关的实现逻辑，继承自PyCustomerSimulator
#     多重继承中的父类QObject，在此目的是要能够自定义信号signlRunInfo
class MySimulator(QObject, PyCustomerSimulator):
    signalRunInfo = Signal(str)
    forStopSimu = Signal()
    forReStartSimu = Signal()

    def __init__(self):
        QObject.__init__(self)
        PyCustomerSimulator.__init__(self)
        # 车辆方阵的车辆数
        self.mrSquareVehiCount = 28
        # 飞机速度，飞机后面的车辆速度会被设定为此数据
        self.mrSpeedOfPlane = 0
        # 当前正在仿真计算的路网名称
        self.mNetPath = None
        # 相同路网连续仿真次数
        self.mSimuCount = 0
        # 初始化二次开发对象
        self.secondary_dev = SecondaryDevCases(2)



    # 过载父类方法，动态修改决策点不同路径流量比
    def calcDynaFlowRatioParameters(self):
        # TESSNG 顶层接口
        iface = tessngIFace()
        # 当前仿真计算批次
        batchNum = iface.simuInterface().batchNumber()
        # 在计算第20批次时修改某决策点各路径流量比
        if batchNum  == 20:
            # 一个决策点某个时段各路径车辆分配比
            dfi = Online.DecipointFlowRatioByInterval()
            # 决策点编号
            dfi.deciPointID = 1
            # 起始时间 单位秒
            dfi.startDateTime = 1
            # 结束时间 单位秒
            dfi.endDateTime = 84000
            rfr1 = Online.RoutingFlowRatio(10, 3)
            rfr2 = Online.RoutingFlowRatio(11, 4)
            rfr3 = Online.RoutingFlowRatio(12, 3)
            dfi.mlRoutingFlowRatio = [rfr1, rfr2, rfr3]
            return [dfi]
        return []
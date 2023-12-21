from PySide2.QtCore import *
from shiboken2.shiboken2 import wrapInstance
import sys
from Tessng import TessInterface, SimuInterface, PyCustomerSimulator, IVehicle, ILink
from Tessng import m2p, p2m, tessngIFace, tngPlugin
from Tessng import *
import random
from datetime import datetime

# 用户插件子类，代表用户自定义与仿真相关的实现逻辑，继承自PyCustomerSimulator
#     多重继承中的父类QObject，在此目的是要能够自定义信号signlRunInfo
class MySimulator(QObject, PyCustomerSimulator):
    signalRunInfo = Signal(str)
    forReStartSimu = Signal()

    def __init__(self):
        QObject.__init__(self)
        PyCustomerSimulator.__init__(self)

    def __init__(self,Params):
        QObject.__init__(self)
        PyCustomerSimulator.__init__(self)

        self.Params = Params
        # # 自动启动仿真仿真次数
        # self.mAutoStartSimuCount = 1

        # 跟驰模型参数
        self.followingmodel_alpha = 5
        self.followingmodel_beit = 3
        self.followingmodel_safedistance = 15
        self.followingmodel_safeinterval = 1.5

    def ref_beforeStart(self, ref_keepOn):
        # 可在此设置本次仿真参数
        ref_keepOn.value = True
        # 跟驰模型参数
        # 正交实验法
        # global FollowingModelParams
        # self.followingmodel_alpha = FollowingModelParams["alpha"][int(self.index/3)]
        # self.followingmodel_beit = FollowingModelParams["beit"][int(self.index%3)]
        # self.followingmodel_safedistance = FollowingModelParams["safedistance"][int(self.index%3)]
        # self.followingmodel_safeinterval = FollowingModelParams["safeinterval"][int(self.index%3)]
        # 启发式算法
        self.followingmodel_alpha = self.Params[0]
        self.followingmodel_beit = self.Params[1]
        self.followingmodel_safedistance = self.Params[2]
        self.followingmodel_safeinterval = self.Params[3]

        print(f"仿真跟驰参数列表：",[self.followingmodel_alpha,
                                        self.followingmodel_beit,
                                        self.followingmodel_safedistance,
                                        self.followingmodel_safeinterval])
    # 过载的父类方法，重新计算跟驰参数：时距及安全距离
    def reSetFollowingParams(self):
        """重设跟驰模型参数
        :return: 返回Tessng.Online.FollowingModelParam'的列表
        # 机动车
        """
        # TESSNG 顶层接口
        iface = tessngIFace()
        # TESSNG 仿真子接口
        simuiface = iface.simuInterface()
        # TESSNG 路网子接口
        netiface = iface.netInterface()
        # 当前仿真计算批次
        batchNum = simuiface.batchNumber()
        # 对跟驰模型参数的修改只操作一次
        if batchNum < 2:
            followingModelParam_motor = Online.FollowingModelParam()
            followingModelParam_motor.vtype = Online.Motor
            followingModelParam_motor.alfa = self.followingmodel_alpha
            followingModelParam_motor.beit = self.followingmodel_beit
            followingModelParam_motor.safeDistance = self.followingmodel_safedistance       #单位：像素
            followingModelParam_motor.safeInterval = self.followingmodel_safeinterval          #单位：m

            # 非机动车
            followingModelParam_Nonmotor = Online.FollowingModelParam()
            followingModelParam_Nonmotor.vtype = Online.Nonmotor
            followingModelParam_Nonmotor.alfa = 4
            followingModelParam_Nonmotor.beit = 2
            followingModelParam_Nonmotor.safeDistance = 0.5
            followingModelParam_Nonmotor.safeInterval = 1.5

            followingModelParam_Ist = []
            followingModelParam_Ist.append(followingModelParam_motor)
            followingModelParam_Ist.append(followingModelParam_Nonmotor)
            return followingModelParam_Ist
        else:
            return []

    def afterStop(self):
        # 仿真结束后自动退出子进程
        sys.exit(0)


























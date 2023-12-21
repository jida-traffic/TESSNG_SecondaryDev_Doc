###################################################
# 模拟CV从匝道汇入主线时，不同接受间隙下的交通流特征
# 基本思路，首先通过车道限行完全禁止TESS底层所做的换道决策计算
# 根据前后车车头时距对换道决策进行重计算——此处可以对不同接受间隙做设置
# 通过取消车道限行的方式，使换道决策生效，具体换道过程由TESS控制
#################################################### 
from PySide2.QtCore import *
from shiboken2.shiboken2 import wrapInstance

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
        self.getPermission = set()  # 记录获得换道允许的CV车ID

    def ref_beforeStart(self, ref_keepOn):
        #可在此设置本次仿真参数
        ref_keepOn.value = True

    # 过载的父类方法，计算是否要左自由变道
    # TODO: 对于进入加速车道的CV，由外部接口对换道决策进行计算
    def reCalcToLeftFreely(self, vehi):
        # 对于获得换道允许的车辆，进行左变道
        if vehi.id() in self.getPermission and vehi.vehicleDriving().laneNumber() == 0:
            return True
        return False

    # 过载父类方法， 计算车辆当前限制车道序号列表
    # TODO: 对于进入加速车道的CV，禁止其由TESS的换道决策执行汇入
    def calcLimitedLaneNumber(self, vehi):
        if vehi.vehicleTypeCode() == 8 and vehi.roadId() == 5 and vehi.vehicleDriving().laneNumber() == 0:
            # 对于获得换道允许的车辆或距离加速车道终点不足10m的，解除车道限制
            if vehi.id() in self.getPermission or (vehi.vehicleDriving().distToEndpoint() - vehi.length() / 2 < m2p(10)):
                return []
            return [1, 2, 3]
        return []

    # 过载的父类方法，TESS NG 在每个计算周期结束后调用此方法，大量用户逻辑在此实现，注意耗时大的计算要尽可能优化，否则影响运行效率
    def afterOneStep(self):
        #= == == == == == =以下是获取一些仿真过程数据的方法 == == == == == ==
        # TESSNG 顶层接口
        iface = tessngIFace()
        # TESSNG 仿真子接口
        simuiface = iface.simuInterface()
        # 当前仿真计算批次
        batchNum = simuiface.batchNumber()
        # 当前正在运行车辆列表
        lAllVehi = simuiface.allVehiStarted()
        
        '''自定义换道决策方式——基于与目标车道前后车的车头时距
        1. 目标车道无前车/后车——执行左换道
        2. 目标车道间隙大于4.5s（前向间隙大于2s，后向间隙大于2.5s）——执行换道
        '''
        # 获取加速车道内侧的主线1号车道上的所有车辆对象
        lVehisPre = simuiface.vehisInLink(5)
        targetLane = []
        for vehi in lVehisPre:
            if vehi.vehicleDriving().laneNumber() == 1:
                targetLane.append(vehi)
        
        # 获取上游主线对应1号车道上的所有车辆对象
        lVehisPost = simuiface.vehisInLink(1)
        postLane = []
        for vehi in lVehisPost:
            if vehi.vehicleDriving().laneNumber() == 1:
                postLane.append(vehi)
        
        # 寻找执行换道决策车辆在目标车道上的前后车
        for vehi in lAllVehi:
            
            if vehi.vehicleTypeCode() == 10 and vehi.roadId() == 5 and vehi.vehicleDriving().laneNumber() == 0:
                leftFront, leftRear = None, None
                for vehiInTL in targetLane:  # 加速车道内侧的主线1号车道上寻找可能的前后车
                    if vehi.vehicleDriving().currDistanceInRoad() < vehiInTL.vehicleDriving().currDistanceInRoad():
                        if not leftFront or (leftFront.vehicleDriving().currDistanceInRoad() > vehiInTL.vehicleDriving().currDistanceInRoad()):
                            leftFront = vehiInTL
                    elif vehi.vehicleDriving().currDistanceInRoad() > vehiInTL.vehicleDriving().currDistanceInRoad():
                        if not leftRear or (leftRear.vehicleDriving().currDistanceInRoad() < vehiInTL.vehicleDriving().currDistanceInRoad()):
                            leftRear = vehiInTL
                if not leftRear and postLane:  # 若未找到后车，寻找范围扩大至上游主线
                    temp = postLane[0]
                    for vehiInPL in postLane[1:]:
                        if vehiInPL.vehicleDriving().distToEndpoint() < temp.vehicleDriving().distToEndpoint():
                            temp = vehiInPL
                    leftRear = temp
                # 计算可接受间隙（与目标车道前车的车头时距 + 与目标车道后车的车头时距）    
                #leftFrontTHW, leftRearTHW = 0.5, 0.5
                leftFrontTHW, leftRearTHW = float('inf'), float('inf')
                if leftFront and p2m(vehi.currSpeed()) > p2m(leftFront.currSpeed()):
                    leftFrontTHW = (p2m(leftFront.vehicleDriving().currDistanceInRoad()) - p2m(vehi.vehicleDriving().currDistanceInRoad())) /(p2m(vehi.currSpeed()) - p2m(leftFront.currSpeed()))
                if leftRear and p2m(vehi.currSpeed()) < p2m(leftRear.currSpeed()):
                    leftRearTHW = (p2m(vehi.vehicleDriving().currDistanceInRoad()) - p2m(leftRear.vehicleDriving().currDistanceInRoad())) / (p2m(vehi.currSpeed()) - p2m(leftRear.currSpeed()))
                print(batchNum, vehi.id(), leftFront.id(), leftRear.id(), leftFrontTHW, leftRearTHW)
                if leftFrontTHW >= 0.9 and leftRearTHW >= 1.5:  # 满足可接受间隙的车辆，获得换道允许
                    print("ke")
                    self.getPermission.add(vehi.id())
            
























#########################################
# 模拟不同渗透率条件下，CV自编队行驶的场景
# 自编队逻辑：CV在行驶过程中会扫描内侧车道是否存在相邻的CV
# 若存在目标CV，则执行换道与其形成编队
# 完成编队后，修改对应CV的驾驶行为参数，体现编队行驶优势
#########################################
from PySide2.QtCore import *
from shiboken2.shiboken2 import wrapInstance

from Tessng import TessInterface, SimuInterface, PyCustomerSimulator, IVehicle, ILink
from Tessng import m2p, p2m, tessngIFace, tngPlugin
from Tessng import *
import random

# 用户插件子类，代表用户自定义与仿真相关的实现逻辑，继承自PyCustomerSimulator
#     多重继承中的父类QObject，在此目的是要能够自定义信号signlRunInfo
class MySimulator(QObject, PyCustomerSimulator):
    signalRunInfo = Signal(str)
    forReStartSimu = Signal()

    def __init__(self):
        QObject.__init__(self)
        PyCustomerSimulator.__init__(self)
        self.platoon = {}  # 记录CV是否已经加入编队

    def ref_beforeStart(self, ref_keepOn):
        #可在此设置本次仿真参数
        ref_keepOn.value = True

    # 过载的父类方法，重新计算跟驰参数：时距及安全距离
    # vehi:车辆
    # ref_inOutSi，安全时距，ref_inOutSi.value是TESS NG已计算好的值，此方法可以改变它
    # ref_inOutSd，安全距离，ref_inOutSd.value是TESS NG已计算好的值，此方法可以改变它
    # return结果：False：TESS NG忽略此方法作的修改，True：TESS NG采用此方法所作修改
    def ref_reSetFollowingParam(self, vehi, ref_inOutSi, ref_inOutSd):
        front = vehi.vehicleFront()
        # 若当前车与其前车均为CV，则修改其安全时距至0.8s
        if vehi.vehicleTypeCode() == 13 and front and front.vehicleTypeCode() == 13:
            ref_inOutSi.value = 0.8
            return True
        return False

    # TODO: 对网联车CV的驾驶行为进行自定义
    '''自定义的CV驾驶行为
    1. 前方无车，期望速度提升至120
    2. 前方为CV并且车头时距>1s，期望速度提升至前车+20
    3. 前方为CV并且车头时距<1s，期望速度与前车保持一致
    4. 前方非CV并且车头时距>2s，期望速度提升至前车+20
    5. 前方非CV并且车头时距<2s，期望速度与前车保持一致
    '''
    def ref_reCalcdesirSpeed(self, vehi, ref_desirSpeed):
        if vehi.vehicleTypeCode() == 13:
            front = vehi.vehicleFront()
            if not front:
                ref_desirSpeed.value = m2p(120 / 3.6)
                return True
            elif front.vehicleTypeCode() == 13:
                if vehi.vehiHeadwayFront() > 1:
                    ref_desirSpeed.value = (front.currSpeed() + m2p(20 / 3.6))
                    return True
                else:
                    ref_desirSpeed.value = front.currSpeed()
                    return True
            else:
                if vehi.vehiHeadwayFront() > 2:
                    ref_desirSpeed.value = (front.currSpeed() + m2p(20 / 3.6))
                    return True
                else:
                    ref_desirSpeed.value = front.currSpeed()
                    return True      
        return False

    # 过载的父类方法，计算是否要左自由变道
    # vehi:车辆
    # return结果，True：变道、False：不变道
    # TODO: 对右侧车道的单独CV施加变道动机，使其与内侧CV形成编队
    def reCalcToLeftFreely(self, vehi):
        leftFront, leftRear = vehi.vehicleLFront(), vehi.vehicleLRear()
        # 若当前车为CV，且左前车/左后车为CV，则执行左变道
        if vehi.vehicleTypeCode() == 13 and ((leftFront and leftFront.vehicleTypeCode() == 13) or (leftRear and leftRear.vehicleTypeCode() == 13)):
            self.platoon[vehi.id()] = 1  # 更新platoon字典，表示该车已经处于编队中
            if leftFront and leftFront.vehicleTypeCode() == 13:
                self.platoon[leftFront.id()] = 1
            if leftRear and leftRear.vehicleTypeCode() == 13:
                self.platoon[leftRear.id()] = 1
            return True
        #车辆到路段终点距离小于20米不变道
        if vehi.vehicleDriving().distToEndpoint() - vehi.length() / 2 < m2p(20):
            return False
        return False

    # 过载父类方法， 计算车辆当前限制车道序号列表
    # TODO: 限制已经向左换道完成编队的CV执行右换道驶离编队
    def calcLimitedLaneNumber(self, vehi):
        if vehi.vehicleTypeCode() == 13 and self.platoon[vehi.id()]:
            if vehi.vehicleDriving().laneNumber() == 1:  # 1号车道的编队，限制其右变道，驶离编队进入外侧车道（但允许编队继续向内侧车道变道）
                return [0]
            elif vehi.vehicleDriving().laneNumber() == 2:  # 2号车道的编队，限制其右变道驶离编队
                return [0, 1]
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

        # TODO: 为实现MV与CV不同颜色显示，直接通过API在路段生成车辆，控制颜色
        if not batchNum % 3:  # 每0.4秒发一辆，9000veh/h
            second = batchNum // 3  # 归一化，用于控制渗透率
            if second % 10 < 5:  # 控制CV渗透率（30%
                r = hex(255)[3:].upper()
                g = hex(105)[3:].upper()
                b = hex(180)[3:].upper()
                color = f"#{r}{g}{b}"
                dvp = Online.DynaVehiParam()
                dvp.vehiTypeCode = 13  # CV编号13
                dvp.roadId = 1
                dvp.laneNumber = random.randint(0, 3)
                dvp.dist = 0.01
                dvp.speed = m2p(80 / 3.6)
                dvp.color = color
                vehi1 = simuiface.createGVehicle(dvp)  # 生成新的TESS接管车辆
                if vehi1:
                    self.platoon[vehi1.id()] = 0
            else:
                r = hex(135)[3:].upper()
                g = hex(206)[3:].upper()
                b = hex(235)[3:].upper()
                color = f"#{r}{g}{b}"
                dvp = Online.DynaVehiParam()
                dvp.vehiTypeCode = 1  # 普通车MV，编号1
                dvp.roadId = 1
                dvp.laneNumber = random.randint(0, 3)
                dvp.dist = 0.01
                dvp.speed = m2p(60 / 3.6)
                dvp.color = color
                vehi1 = simuiface.createGVehicle(dvp)  # 生成新的TESS接管车辆
                if not vehi1:
                    pass

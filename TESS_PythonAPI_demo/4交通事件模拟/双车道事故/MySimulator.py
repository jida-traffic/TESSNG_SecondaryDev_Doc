from PySide2.QtCore import *
from Tessng import *

class AccidentCar(object):
    laneNum1 = 0
    laneNum2 = 0
    carPos = 0
    accidentStart = 0
    accidentCarNum = 0
    accidentCar2 = 0
    accidentPos = None
    lock = 0

accidentCar = AccidentCar()


# 用户插件子类，代表用户自定义与仿真相关的实现逻辑，继承自PyCustomerSimulator
#     多重继承中的父类QObject，在此目的是要能够自定义信号signlRunInfo
class MySimulator(QObject, PyCustomerSimulator):
    signalRunInfo = Signal(str)
    def __init__(self):
        QObject.__init__(self)
        PyCustomerSimulator.__init__(self)

    # 过载的父类方法， 初始化车辆，在车辆启动上路时被TESS NG调用一次
    def initVehicle(self, vehi):
        # 车辆ID，不含首位数，首位数与车辆来源有关，如发车点、公交线路
        return True

    # 过载的父类方法重新计算加速度
    def ref_calcAcce(self, vehi, acce):
        return False

    def ref_reCalcAngle(self, vehi, ref_outAngle):
        global accidentCar2_Id
        if accidentCar.accidentStart:
            if vehi.id() == accidentCar.accidentCarNum:
                ref_outAngle.value = 120
                return True
            try:
                if vehi.id() == accidentCar2_Id:
                    ref_outAngle.value = 30
                    return True
            except:
                pass
        else:
            return False

    # 过载的父类方法，重新计算期望速度
    # vehi：车辆
    # ref_esirSpeed：返回结果,ref_desirSpeed.value是TESS NG计算好的期望速度，可以在此方法改变它
    # return结果：False：TESS NG忽略此方法作的修改，True：TESS NG采用此方法所作修改
    def ref_reCalcdesirSpeed(self, vehi, ref_desirSpeed):
        global accidentCar2_Id
        # TESSNG 顶层接口
        iface = tngIFace()
        # TESSNG 仿真子接口
        simuiface = iface.simuInterface()
        # 当前已仿真时间，单位：毫秒
        simuTime = simuiface.simuTimeIntervalWithAcceMutiples()

        currDistance = p2m(vehi.vehicleDriving().currDistanceInRoad())
        if vehi.id() == 100015 and currDistance >= 200:
            ref_desirSpeed.value = 0
            accidentCar.laneNum1 = vehi.vehicleDriving().laneNumber()
            accidentCar.accidentStart = 1
            accidentCar.accidentCarNum = vehi.id()
            accidentCar.accidentPos = (p2m(vehi.pos().x()), p2m(vehi.pos().y()))
            return True
        if accidentCar.accidentStart:
            try:
                if vehi.id() == accidentCar2_Id:
                    ref_desirSpeed.value = 0
                    accidentCar.laneNum2 = vehi.vehicleDriving().laneNumber()
                    return True
            except:
                pass
        else:
            return False

    # 过载的父类方法，重新计算跟驰参数：时距及安全距离
    # vehi:车辆
    # ref_inOutSi，安全时距，ref_inOutSi.value是TESS NG已计算好的值，此方法可以改变它
    # ref_inOutSd，安全距离，ref_inOutSd.value是TESS NG已计算好的值，此方法可以改变它
    # return结果：False：TESS NG忽略此方法作的修改，True：TESS NG采用此方法所作修改
    def ref_reSetFollowingParam(self, vehi, ref_inOutSi, ref_inOutSd):
        return False

    # 过载的父类方法，重新计算加速度
    # vehi：车辆
    # inOutAce：加速度，inOutAcce.value是TESS NG已计算的车辆加速度，此方法可以改变它
    # return结果：False：TESS NG忽略此方法作的修改，True：TESS NG采用此方法所作修改
    def ref_reSetAcce(self, vehi, inOutAcce):
        return False

    # 过载的父类方法，重新计算当前速度
    # vehi:车辆
    # ref_inOutSpeed，速度ref_inOutSpeed.value，是已计算好的车辆速度，此方法可以改变它
    # return结果：False：TESS NG忽略此方法作的修改，True：TESS NG采用此方法所作修改
    def ref_reSetSpeed(self, vehi, ref_inOutSpeed):
        global accidentCar2_Id
        if accidentCar.accidentStart and vehi.id() == accidentCar.accidentCarNum and not accidentCar.lock:
            accidentCar2 = vehi.vehicleRRear()
            if accidentCar.accidentPos[0] - 15 <= p2m(accidentCar2.pos().x()) <= accidentCar.accidentPos[0] - 10:
                ref_inOutSpeed.value = 0
                accidentCar.lock = 1
                accidentCar2_Id = accidentCar2.id()
                return True
        else:
            return False

    # 过载的父类方法，计算是否要左自由变道
    # vehi:车辆
    # return结果，True：变道、False：不变道
    def reCalcToLeftFreely(self, vehi):
        return False

    # 过载的父类方法，计算是否要右自由变道
    # vehi:车辆
    # return结果，True：变道、False：不变道
    def reCalcToRightFreely(self, vehi):
        return False

    # 过载父类方法， 计算车辆当前限制车道序号列表
    def calcLimitedLaneNumber(self, vehi):
        if accidentCar.accidentStart:
            if 50 <= p2m(vehi.vehicleDriving().currDistanceInRoad()):
                return [accidentCar.laneNum1, accidentCar.laneNum2]
        else:
            return False


    # 过载父类方法，车道限速
    def ref_calcSpeedLimitByLane(self, link, laneNumber, ref_outSpeed):
        return False

    # 过载父类方法，动态修改决策点不同路径流量比
    def calcDynaFlowRatioParameters(self):
        return []

    def calcDynaSignalContralParameters(self):
        return []

    # 过载父类方法，停止指定车辆运行，退出路网，但不会从内存删除，会参数各种统计
    #  范例车辆进入ID等于2的路段或连接段，路离终点小于100米，则驰出路网
    def isStopDriving(self, vehi):
        return False

    # 过载的父类方法，TESS NG 在每个计算周期结束后调用此方法，大量用户逻辑在此实现，注意耗时大的计算要尽可能优化，否则影响运行效率
    def afterOneStep(self):
        #= == == == == == =以下是获取一些仿真过程数据的方法 == == == == == ==
        # TESSNG 顶层接口
        iface = tngIFace()
        # TESSNG 仿真子接口
        simuiface = iface.simuInterface()
        # TESSNG 路网子接口
        netiface = iface.netInterface()
        # 当前仿真计算批次
        batchNum = simuiface.batchNumber()
        # 当前已仿真时间，单位：毫秒
        simuTime = simuiface.simuTimeIntervalWithAcceMutiples()
        # 开始仿真的现实时间
        startRealtime = simuiface.startMSecsSinceEpoch()
        # 当前正在运行车辆列表
        lAllVehi = simuiface.allVehiStarted()
        # 打印当前在运行车辆ID列表
        # print([item.id() for item in lAllVehi])
        # 当前在ID为1的路段上车辆
        lVehis = simuiface.vehisInLink(1)






























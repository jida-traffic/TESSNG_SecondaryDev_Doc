from PySide2.QtCore import *
from shiboken2.shiboken2 import wrapInstance

from Tessng import TessInterface, SimuInterface, PyCustomerSimulator, IVehicle, ILink
from Tessng import m2p, p2m, tngIFace, tngPlugin
from Tessng import *
import random
from datetime import datetime

# 用户插件子类，代表用户自定义与仿真相关的实现逻辑，继承自PyCustomerSimulator
#     多重继承中的父类QObject，在此目的是要能够自定义信号signlRunInfo
class MySimulator(QObject, PyCustomerSimulator, SimuInterface):
    signalRunInfo = Signal(str)
    def __init__(self):
        QObject.__init__(self)
        PyCustomerSimulator.__init__(self)


    # 过载的父类方法， 初始化车辆，在车辆启动上路时被TESS NG调用一次
    def initVehicle(self, vehi):
        # 车辆ID，不含首位数，首位数与车辆来源有关，如发车点、公交线路
        global tmpId
        global simuTime
        iface = tngIFace()
        simuIFace = iface.simuInterface()
        simuTime = simuIFace.simuTimeIntervalWithAcceMutiples()
        #     roadName = vehi.roadName()
        tmpId = vehi.id() % 100000
        # 车辆所在路段名或连接段名
        roadName = vehi.roadName()

        # 车辆所在路段ID或连接段ID
        roadId = vehi.roadId()
        if roadName == '路段1':
            vehi.initSpeed(m2p(150))

            if tmpId == 1:
                vehi.setVehiType(2)

            elif tmpId >= 2 and tmpId <= 4:
                vehi.setVehiType(8)

            elif tmpId >= 5 and tmpId <= 6:
                vehi.setVehiType(9)

            elif tmpId >= 7 and tmpId <= 9:
                vehi.setVehiType(10)

            elif 12 >= tmpId >= 9:
                vehi.setVehiType(8)

            elif 22 >= tmpId >= 12:
                vehi.setVehiType(1)

            elif 24 >= tmpId >= 22:
                vehi.setVehiType(9)

            elif 50 >= tmpId >= 25:
                vehi.setVehiType(1)

            elif tmpId >= 54 and tmpId <= 51:
                vehi.setVehiType(10)

            elif tmpId >= 55 and tmpId <= 56:
                vehi.setVehiType(8)

            else:
                vehi.setVehiType(1)

        return True

    # #前方车辆停车后，后方车辆期望速度设置为10
    # def ref_reCalcdesirSpeed(self, vehi, ref_desirSpeed):
    #     tmpId = vehi.id() % 100000
    #     roadName = vehi.roadName()
    #     if roadName == '路段1':
    #         iface = tngIFace()
    #         simuIFace = iface.simuInterface()
    #         simuTime = simuIFace.simuTimeIntervalWithAcceMutiples()
    #         if simuTime >= 28000:
    #             ref_desirSpeed.value = m2p(10)
    #             return True
    #     return False


    #设置连接段1的安全距离
    def ref_reSetFollowingParam(self, vehi, ref_inOutSi, ref_inOutSd):
        roadName = vehi.roadName()
        if roadName == "连接段1":
            ref_inOutSd.value = m2p(5)
            return True
        return False


    #     # 过载的父类方法，计算是否要左自由变道
    #     # vehi:车辆
    #     # return结果，True：变道、False：不变道
    # def reCalcToLeftFreely(self, vehi):
    #     # 车辆到路段终点距离小于20米不变道
    #     # 车辆到路段终点距离小于20米不变道
    #     if vehi.vehicleDriving().distToEndpoint() - vehi.length() / 2 < m2p(20):
    #         return False
    #     roadName = vehi.roadName()
    #     if roadName == "路段1":
    #         if simuTime >= 26000 and vehi.vehicleTypeCode() < 2:
    #             return True
    #     return False
    #
    # 
    #     # 过载的父类方法，计算是否要右自由变道
    #     # vehi:车辆
    #     # return结果，True：变道、False：不变道
    # def reCalcToRightFreely(self, vehi):
    #     # 车辆到路段终点距离小于20米不变道
    #     if vehi.vehicleDriving().distToEndpoint() - vehi.length() / 2 < m2p(20):
    #         return False
    #     roadName = vehi.roadName()
    #     if roadName == "路段1":
    #         if simuTime >= 26000 and vehi.vehicleTypeCode() > 2:
    #             return True
    #     return False

    #车辆故障停车
    def ref_reSetSpeed(self, vehi, ref_inOutSpeed):
        link = wrapInstance(vehi.road().__int__(), ILink)
        tmpId = vehi.id() % 100000

        if tmpId == 11 and simuTime >= 78000 and simuTime <= 108000:
            # print(tmpId, vehi.vehicleTypeCode())
            # if tmpId == 11 and vehi.vehicleTypeCode() == 2:
            if vehi.vehicleTypeCode() != 12:
                ref_inOutSpeed.value = m2p(0)

                return True
        return False

    # 过载父类方法， 计算车辆当前限制车道序号列表
    def calcLimitedLaneNumber(self, vehi):
        # 如果当前车辆在路段上，且路段ID等于3，则小车走内侧，大车走外侧
        if vehi.vehicleTypeCode() == 1:
            if vehi.roadIsLink():
                # IVehicle.road()方法获取的是车辆当前所路段或连接段的void指针，需要将它转换成路段或连接段
                link = wrapInstance(vehi.road().__int__(), ILink)
                if link is not None and link.id() == 3 and simuTime >= 25000:
                    # 小车走内侧，大车走外侧，设长度小于6米为小车
                    return []
        return []



    # 过载父类方法，动态修改决策点不同路径流量比
    def calcDynaFlowRatioParameters(self):
        # TESSNG 顶层接口
        iface = tngIFace()
        # 当前仿真计算批次
        batchNum = iface.simuInterface().batchNumber()
        # 在计算第20批次时修改某决策点各路径流量比
        if batchNum == 20:
            # 一个决策点某个时段各路径车辆分配比
            dfi = TESSNG.DecipointFlowRatioByInterval()
            #决策点编号
            dfi.deciPointID = 5
            #起始时间 单位秒
            dfi.startDateTime = 1
            #结束时间 单位秒
            dfi.endDateTime = 84000
            rfr1 = TESSNG.RoutingFlowRatio(10, 3)
            rfr2 = TESSNG.RoutingFlowRatio(11, 4)
            rfr3 = TESSNG.RoutingFlowRatio(12, 3)
            dfi.mlRoutingFlowRatio = [rfr1, rfr2, rfr3]
            return [dfi]
        return []


    def isStopDriving(self, vehi):
        if vehi.roadId() == 2:
            # 车头到当前路段或连接段终点距离
            dist = vehi.vehicleDriving().distToEndpoint(True)
            # 如果距终点距离小于100米，车辆停止运行退出路网
            if dist < m2p(5):
                return False
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
        #每20个计算批次做一次小计，将结果通过信号发送出云
        if batchNum % 20 == 0:
            strLinkCount = str(netiface.linkCount())
            strVehiCount = str(len(lAllVehi))
            strSimuTime = str(simuTime)
            runInfo = f"路段数：{strLinkCount}\n运行车辆数：{strVehiCount}\n仿真时间：{strSimuTime}(毫秒)"
            self.signalRunInfo.emit(runInfo)

        # 动态发车，不通过发车点发送，直接在路段和连接段中间某位置创建并发送，每50个计算批次发送一次
        if batchNum % 50 == 1:
            r = hex(256 + random.randint(0,256))[3:].upper()
            g = hex(256 + random.randint(0,256))[3:].upper()
            b = hex(256 + random.randint(0,256))[3:].upper()
            color = f"#{r}{g}{b}"
            # 路段上发车
            dvp = TESSNG.DynaVehiParam()
            dvp.vehiTypeCode = random.randint(0, 4) + 1
            dvp.roadId = 6
            dvp.laneNumber = random.randint(0, 3)
            dvp.dist = 50
            dvp.speed = 20
            dvp.color = color
            vehi1 = simuiface.createGVehicle(dvp)
            if vehi1 != None:
                pass
    #
    #         # 连接段上发车
    #         dvp2 = TESSNG.DynaVehiParam()
    #         dvp2.vehiTypeCode = random.randint(0, 4) + 1
    #         dvp2.roadId = 3
    #         dvp2.laneNumber = random.randint(0, 3)
    #         dvp2.toLaneNumber = dvp2.laneNumber # 默认为 - 1，如果大于等于0, 在连接段上发车
    #         dvp2.dist = 50
    #         dvp2.speed = 20
    #         dvp2.color = color
    #         vehi2 = simuiface.createGVehicle(dvp2)
    #         if vehi2 != None:
    #             pass

        # 获取车辆状态，含位置
        lVehiStatus = simuiface.getVehisStatus()
        #print("车辆位置：", [(status.vehiId, status.mPoint.x(), status.mPoint.y()) for status in lVehiStatus])
        # 信号灯组相位颜色
        lPhoneColor = simuiface.getSignalPhasesColor()
        #print("信号灯组相位颜色", [(pcolor.signalGroupId, pcolor.phaseNumber, pcolor.color, pcolor.mrIntervalSetted, pcolor.mrIntervalByNow) for pcolor in lPhoneColor])
        # 获取当前仿真时间完成穿越采集器的所有车辆信息
        lVehiInfo = simuiface.getVehisInfoCollected()
        #if len(lVehiInfo) > 0:
        #    print("车辆信息采集器采集信息：", [(vinfo.collectorId, vinfo.vehiId) for vinfo in lVehiInfo])
        # 获取最近集计时间段内采集器采集的所有车辆集计信息
        lVehisInfoAggr = simuiface.getVehisInfoAggregated()
        #if len(lVehisInfoAggr) > 0:
        #    print("车辆信息采集集计数据：", [(vinfo.collectorId, vinfo.vehiCount) for vinfo in lVehisInfoAggr])
        # 获取当前仿真时间排队计数器计数的车辆排队信息
        lVehiQueue = simuiface.getVehisQueueCounted()
        #if len(lVehiQueue) > 0:
        #    print("车辆排队计数器计数：", [(vq.counterId, vq.queueLength) for vq in lVehiQueue])
        # 获取最近集计时间段内排队计数器集计数据
        lVehiQueueAggr = simuiface.getVehisQueueAggregated()
        #if len(lVehiQueueAggr) > 0:
        #    print("车辆排队集计数据：", [(vqAggr.counterId, vqAggr.avgQueueLength) for vqAggr in lVehiQueueAggr])
        # 获取当前仿真时间行程时间检测器完成的行程时间检测信息
        lVehiTravel = simuiface.getVehisTravelDetected()
        #if len(lVehiTravel) > 0:
        #    print("车辆行程时间检测信息：", [(vtrav.detectedId, vtrav.travelDistance) for vtrav in lVehiTravel])
        # 获取最近集计时间段内行程时间检测器集计数据
        lVehiTravAggr = simuiface.getVehisTravelAggregated()
        #if len(lVehiTravAggr) > 0:
        #    print("车辆行程时间集计数据：", [(vTravAggr.detectedId, vTravAggr.vehiCount, vTravAggr.avgTravelDistance) for vTravAggr in lVehiTravAggr])

























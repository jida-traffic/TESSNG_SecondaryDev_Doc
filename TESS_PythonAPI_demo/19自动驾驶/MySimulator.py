from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtCore import Qt
from shiboken2.shiboken2 import wrapInstance

from Tessng import TessInterface, SimuInterface, PyCustomerSimulator, IVehicle, ILink
from Tessng import m2p, p2m, tngIFace, tngPlugin
from Tessng import *
import random
from datetime import datetime

# 用户插件子类，代表用户自定义与仿真相关的实现逻辑，继承自PyCustomerSimulator
#     多重继承中的父类QObject，在此目的是要能够自定义信号signlRunInfo
class MySimulator(QObject, PyCustomerSimulator):
    signalRunInfo = Signal(str)
    def __init__(self):
        QObject.__init__(self)
        PyCustomerSimulator.__init__(self)
        # 车辆方阵的车辆数
        self.mrSquareVehiCount = 28

    # 过载的父类方法， 初始化车辆，在车辆启动上路时被TESS NG调用一次
    def initVehicle(self, vehi):

        # 为了使paintVehicle方法有效
        vehi.setIsPermitForVehicleDraw(True)
        # 车辆ID，不含首位数，首位数与车辆来源有关，如发车点、公交线路
        tmpId = vehi.id() % 100000
        # 车辆所在路段名或连接段名
        roadName = vehi.roadName()
        # 车辆所在路段ID或连接段ID
        roadId = vehi.roadId()
        if roadName == '公路1':

            if tmpId == 4:
                vehi.setVehiType(9)
                vehi.initLane(1, m2p(47), 4)
                vehi.initSpeed(0)

            elif tmpId == 5:
                vehi.setVehiType(1)
                vehi.initLane(1, m2p(10), 9)

            elif tmpId == 1:
                vehi.setVehiType(2)
                vehi.initLane(1, m2p(10), 7)

            elif tmpId == 2:
                vehi.setVehiType(3)
                vehi.initLane(0, m2p(10), 8)

            elif tmpId == 3:
                vehi.setVehiType(2)
                vehi.initLane(1, m2p(30), 6)

            elif tmpId == 6:
                vehi.setVehiType(2)
                vehi.initLane(1, m2p(10), 5)
 
            elif tmpId == 7:
                vehi.setVehiType(2)
                vehi.initLane(0, m2p(10), 5)

            elif tmpId == 8:
                vehi.setVehiType(2)
                vehi.initLane(1, m2p(10), 5)
 
            elif tmpId == 9:
                vehi.setVehiType(2)
                vehi.initLane(0, m2p(10), 5)

        return True

    # 过载的父类方法重新计算加速度
    def ref_calcAcce(self, vehi, acce):
        return False


    # 过载的父类方法，重新计算期望速度
    # vehi：车辆
    # ref_esirSpeed：返回结果,ref_desirSpeed.value是TESS NG计算好的期望速度，可以在此方法改变它
    # return结果：False：TESS NG忽略此方法作的修改，True：TESS NG采用此方法所作修改
    def ref_reCalcdesirSpeed(self, vehi, ref_desirSpeed):
        global simuTime
        iface = tngIFace()
        simuIFace = iface.simuInterface()
        simuTime = simuIFace.simuTimeIntervalWithAcceMutiples()
        tmpId = vehi.id() % 100000
        roadName = vehi.roadName()
        if roadName == '公路1' and simuTime >= 6000:
            if vehi.vehicleTypeCode() == 9:
                ref_desirSpeed.value = m2p(50)
                return True
            else:
                ref_desirSpeed.value = m2p(60)
                return True
        return False

    # 过载的父类方法，重新计算加速度
    # vehi：车辆
    # inOutAce：加速度，inOutAcce.value是TESS NG已计算的车辆加速度，此方法可以改变它
    # return结果：False：TESS NG忽略此方法作的修改，True：TESS NG采用此方法所作修改
    def ref_reSetAcce(self, vehi, inOutAcce):
        roadName = vehi.roadName()
        if roadName == "公路1" and simuTime >= 6000:
            #  重设加速度实现超车
            if vehi.vehicleTypeCode() == 1:
                inOutAcce.value = m2p(8)
                return True
            else:
                inOutAcce.value = m2p(3)
                return True
        return False

    # 过载的父类方法，重新计算当前速度
    # vehi:车辆
    # ref_inOutSpeed，速度ref_inOutSpeed.value，是已计算好的车辆速度，此方法可以改变它
    # return结果：False：TESS NG忽略此方法作的修改，True：TESS NG采用此方法所作修改
    def ref_reSetSpeed(self, vehi, ref_inOutSpeed):
        tmpId = vehi.id() % 100000
        roadName = vehi.roadName()
        #  重设期望速度实现超车
        if roadName == "公路1" and simuTime >= 6000:
            if vehi.vehicleTypeCode() == 1:
                ref_inOutSpeed.value = m2p(32)
                return True
            else:
                ref_inOutSpeed.value = m2p(30)
                return True
        return False

    # # 过载的父类方法，计算是否要右自由变道
    # # vehi:车辆
    # # return结果，True：变道、False：不变道
    def reCalcToRightFreely(self, vehi):
        tmpId = vehi.id() % 100000
        #车辆到路段终点距离小于20米不变道
        if vehi.vehicleDriving().distToEndpoint() - vehi.length() / 2 < m2p(20):
            return False
        roadName = vehi.roadName()
        if roadName == "公路1" and simuTime >= 6000:
            print("15")
            #  小于雷达探测距离，变道，开始超车
            if vehi.vehicleTypeCode() == 1 or tmpId == 5:
                print("25")
                print(p2m(vehi.vehiDistFront()))
                if vehi.vehiDistFront() <= m2p(50):

                    print("35")
                    return True
        else:
            return False

    # 过载父类方法，停止指定车辆运行，退出路网，但不会从内存删除，会参数各种统计
    #  范例车辆进入ID等于2的路段或连接段，路离终点小于100米，则驰出路网
    def isStopDriving(self, vehi):
        if vehi.roadId() == 2:
            # 车头到当前路段或连接段终点距离
            dist = vehi.vehicleDriving().distToEndpoint(True)
            # 如果距终点距离小于10米，车辆停止运行退出路网
            if dist < m2p(10):
                return True
        return False

    #  调整车辆角度
    def boundingRect(self, vehi, outRect) -> bool:
        if vehi.vehicleTypeCode() == 1:
            if vehi:
                length = vehi.length() + 200
                w = length * 2
                outRect.setLeft(m2p(-w/2))
                outRect.setTop(m2p(-w/2))
                outRect.setWidth(m2p(w))
                outRect.setHeight(m2p(w))
                return True
        return False

    #  画扇形雷达探测区域
    def paintVehicle(self, vehi, painter):
        if vehi.vehicleTypeCode() == 1:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(254, 174, 165, 200), Qt.SolidPattern))
            painter.drawPie(-70, -70, 140, 143, 70 * 16, 40 * 16)
            painter.setBrush(QBrush(QColor(180, 180, 180, 200), Qt.SolidPattern))
            painter.drawRoundRect(-2, 2, 4, 8, 30, 30)
            painter.setBrush(QBrush(QColor(225, 225, 225, 200), Qt.SolidPattern))
            painter.drawRoundRect(-2, 4, 4, 5, 30, 30)
            return True

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
            dvp = Online.DynaVehiParam()
            dvp.vehiTypeCode = random.randint(0, 4) + 1
            dvp.roadId = 6
            dvp.laneNumber = random.randint(0, 3)
            dvp.dist = 50
            dvp.speed = 20
            dvp.color = color
            vehi1 = simuiface.createGVehicle(dvp)
            if vehi1 != None:
                pass

            # 连接段上发车
            dvp2 = Online.DynaVehiParam()
            dvp2.vehiTypeCode = random.randint(0, 4) + 1
            dvp2.roadId = 3
            dvp2.laneNumber = random.randint(0, 3)
            dvp2.toLaneNumber = dvp2.laneNumber # 默认为 - 1，如果大于等于0, 在连接段上发车
            dvp2.dist = 50
            dvp2.speed = 20
            dvp2.color = color
            vehi2 = simuiface.createGVehicle(dvp2)
            if vehi2 != None:
                pass

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








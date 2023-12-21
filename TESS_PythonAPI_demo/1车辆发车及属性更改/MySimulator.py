from PySide2.QtCore import *
from shiboken2.shiboken2 import wrapInstance

from Tessng import TessInterface, SimuInterface, PyCustomerSimulator, IVehicle, ILink
from Tessng import m2p, p2m, tessngIFace, tessngPlugin
from Tessng import *
import random
from datetime import datetime

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

    def ref_beforeStart(self, ref_keepOn):
        iface = tessngIFace()
        # 当前路网名
        tmpNetPath = iface.netInterface().netFilePath()
        if tmpNetPath != self.mNetPath:
            self.mNetPath = tmpNetPath
            self.mSimuCount = 1;
        else:
            self.mSimuCount += 1
        #可在此设置本次仿真参数
        ref_keepOn.value = True

    #设置本类实现的过载方法被调用频次，即多少个计算周期调用一次。过多的不必要调用会影响运行效率
    def setStepsPerCall(self, vehi):
        #设置当前车辆及其驾驶行为过载方法被TESSNG调用频次，即多少个计算周调用一次指定方法。如果对运行效率有极高要求，可以精确控制具体车辆或车辆类型及具体场景相关参数
        iface = tessngIFace()
        netface = iface.netInterface()
        netFileName = netface.netFilePath()
        #范例打开临时路段会会创建车辆方阵，需要进行一些仿真过程控制
        if "Temp" in netFileName:
            #允许对车辆重绘方法的调用
            vehi.setIsPermitForVehicleDraw(True)
            #计算限制车道方法每10个计算周期被调用一次
            vehi.setSteps_calcLimitedLaneNumber(10)
            #计算安全变道距离方法每10个计算周期被调用一次
            vehi.setSteps_calcChangeLaneSafeDist(10)
            #重新计算车辆期望速度方法每一个计算周期被调用一次
            vehi.setSteps_reCalcdesirSpeed(1)
            #重新设置车速方法每一个计算周期被调用一次
            vehi.setSteps_reSetSpeed(1)
        else:
            simuface = iface.simuInterface()
            #仿真精度，即每秒计算次数
            steps = simuface.simuAccuracy()
            # #======设置本类过载方法被TESSNG调用频次，以下是默认设置，可以修改======
            # #======车辆相关方法调用频次======
            # #是否允许对车辆重绘方法的调用
            # vehi.setIsPermitForVehicleDraw(False)
            # #计算下一位置前处理方法被调用频次
            # vehi.setSteps_beforeNextPoint(steps * 300)
            # #计算下一位置方法方法被调用频次
            # vehi.setSteps_nextPoint(steps * 300)
            # #计算下一位置完成后处理方法被调用频次
            # vehi.setSteps_afterStep(steps * 300)
            # #确定是否停止车辆运行便移出路网方法调用频次
            # vehi.setSteps_isStopDriving(steps * 300)
            #
            # #======驾驶行为相关方法调用频次======
            # #重新设置期望速度方法被调用频次
            # vehi.setSteps_reCalcdesirSpeed(steps * 300)
            # #计算最大限速方法被调用频次
            # vehi.setSteps_calcMaxLimitedSpeed(steps * 300)
            # #计算限制车道方法被调用频次
            # vehi.setSteps_calcLimitedLaneNumber(steps)
            # #计算车道限速方法被调用频次
            # vehi.setSteps_calcSpeedLimitByLane(steps)
            # #计算安全变道方法被调用频次
            # vehi.setSteps_calcChangeLaneSafeDist(steps)
            # #重新计算是否可以左强制变道方法被调用频次
            # vehi.setSteps_reCalcToLeftLane(steps)
            # #重新计算是否可以右强制变道方法被调用频次
            # vehi.setSteps_reCalcToRightLane(steps)
            # #重新计算是否可以左自由变道方法被调用频次
            # vehi.setSteps_reCalcToLeftFreely(steps)
            # # 重新计算是否可以右自由变道方法被调用频次
            # vehi.setSteps_reCalcToRightFreely(steps)
            # #计算跟驰类型后处理方法被调用频次
            # vehi.setSteps_afterCalcTracingType(steps * 300)
            # #连接段上汇入到车道前处理方法被调用频次
            # vehi.setSteps_beforeMergingToLane(steps * 300)
            # #重新跟驰状态参数方法被调用频次
            # vehi.setSteps_reSetFollowingType(steps * 300)
            # #计算加速度方法被调用频次
            # vehi.setSteps_calcAcce(steps * 300)
            # #重新计算加速度方法被调用频次
            # vehi.setSteps_reSetAcce(steps * 300)
            # #重置车速方法被调用频次
            # vehi.setSteps_reSetSpeed(steps * 300)
            # #重新计算角度方法被调用频次
            # vehi.setSteps_reCalcAngle(steps * 300)
            # vehi.setSteps_recentTimeOfSpeedAndPos(steps * 300)
            # vehi.setSteps_travelOnChangingTrace(steps * 300)
            # vehi.setSteps_leaveOffChangingTrace(steps * 300)
            # #计算后续道路前处理方法被调用频次
            # vehi.setSteps_beforeNextRoad(steps * 300)
            pass

    # 过载的父类方法， 初始化车辆，在车辆启动上路时被TESS NG调用一次
    def initVehicle(self, vehi):
        #设置当前车辆及其驾驶行为过载方法被TESSNG调用频次，即多少个计算周调用一次指定方法。如果对运行效率有极高要求，可以精确控制具体车辆或车辆类型及具体场景相关参数
        self.setStepsPerCall(vehi)
        # 车辆ID，不含首位数，首位数与车辆来源有关，如发车点、公交线路
        tmpId = vehi.id() % 100000
        # 车辆所在路段名或连接段名
        roadName = vehi.roadName()
        # 车辆所在路段ID或连接段ID
        roadId = vehi.roadId()
        if roadName == '曹安公路':
            #飞机
            if tmpId == 1:
                vehi.setVehiType(12)
                vehi.initLane(3, m2p(105), 0)
            #工程车
            elif tmpId >=2 and tmpId <=8:
                vehi.setVehiType(8)
                vehi.initLane((tmpId - 2) % 7, m2p(80), 0)
            #消防车
            elif tmpId >=9 and tmpId <=15:
                vehi.setVehiType(9)
                vehi.initLane((tmpId - 2) % 7, m2p(65), 0)
            #消防车
            elif tmpId >=16 and tmpId <=22:
                vehi.setVehiType(10)
                vehi.initLane((tmpId - 2) % 7, m2p(50), 0)
            #最后两队列小车
            elif tmpId == 23:
                vehi.setVehiType(1)
                vehi.initLane(1, m2p(35), 0)
            elif tmpId == 24:
                vehi.setVehiType(1)
                vehi.initLane(5, m2p(35), 0)
            elif tmpId == 25:
                vehi.setVehiType(1)
                vehi.initLane(1, m2p(20), 0)
            elif tmpId == 26:
                vehi.setVehiType(1)
                vehi.initLane(5, m2p(20), 0)
            elif tmpId == 27:
                vehi.setVehiType(1)
                vehi.initLane(1, m2p(5), 0)
            elif tmpId == 28:
                vehi.setVehiType(1)
                vehi.initLane(5, m2p(5), 0)
            # 最后两列小车的长度设为一样长，这个很重要，如果车长不一样长，加上导致的前车距就不一样，会使它们变道轨迹长度不一样，就会乱掉
            if tmpId >= 23 and tmpId <= 28:
                vehi.setLength(m2p(4.5), True)
        return True

    # 过载的父类方法重新计算加速度
    def ref_calcAcce(self, vehi, acce):
        return False
        # if vehi.vehiDistFront() < m2p(5):
        #     #前车距小于5米，让TESSNG计算加速度
        #     return False
        # elif vehi.currSpeed() > m2p(10):
        #     acce.value = m2p(-2)
        # elif vehi.currSpeed() < m2p(1):
        #     acce.value = m2p(2)
        # return False

    # 过载的父类方法，重新计算期望速度
    # vehi：车辆
    # ref_esirSpeed：返回结果,ref_desirSpeed.value是TESS NG计算好的期望速度，可以在此方法改变它
    # return结果：False：TESS NG忽略此方法作的修改，True：TESS NG采用此方法所作修改
    def ref_reCalcdesirSpeed(self, vehi, ref_desirSpeed):
        tmpId = vehi.id() % 100000
        roadName = vehi.roadName()
        if roadName == '曹安公路':
            if tmpId <= self.mrSquareVehiCount:
                iface = tessngIFace()
                simuIFace = iface.simuInterface()
                simuTime = simuIFace.simuTimeIntervalWithAcceMutiples()
                if simuTime < 5 * 1000:
                    ref_desirSpeed.value = 0
                elif simuTime < 10 * 1000:
                    ref_desirSpeed.value = m2p(20 / 3.6)
                else:
                    ref_desirSpeed.value = m2p(40 / 3.6)
            return True
        return False

    # 过载的父类方法，重新计算跟驰参数：时距及安全距离
    # vehi:车辆
    # ref_inOutSi，安全时距，ref_inOutSi.value是TESS NG已计算好的值，此方法可以改变它
    # ref_inOutSd，安全距离，ref_inOutSd.value是TESS NG已计算好的值，此方法可以改变它
    # return结果：False：TESS NG忽略此方法作的修改，True：TESS NG采用此方法所作修改
    def ref_reSetFollowingParam(self, vehi, ref_inOutSi, ref_inOutSd):
        roadName = vehi.roadName()
        if roadName == "连接段2":
            ref_inOutSd.value = m2p(30);
            return True
        return False

    # 过载的父类方法，重新计算加速度
    # vehi：车辆
    # inOutAce：加速度，inOutAcce.value是TESS NG已计算的车辆加速度，此方法可以改变它
    # return结果：False：TESS NG忽略此方法作的修改，True：TESS NG采用此方法所作修改
    def ref_reSetAcce(self, vehi, inOutAcce):
        roadName = vehi.roadName()
        if roadName == "连接段1":
            if vehi.currSpeed() > m2p(20 / 3.6):
                inOutAcce.value = m2p(-5)
                return True
            elif vehi.currSpeed() > m2p(20 / 3.6):
                inOutAcce.value = m2p(-1)
                return True
        return False

    # 过载的父类方法，重新计算当前速度
    # vehi:车辆
    # ref_inOutSpeed，速度ref_inOutSpeed.value，是已计算好的车辆速度，此方法可以改变它
    # return结果：False：TESS NG忽略此方法作的修改，True：TESS NG采用此方法所作修改
    def ref_reSetSpeed(self, vehi, ref_inOutSpeed):
        tmpId = vehi.id() % 100000
        roadName = vehi.roadName()
        if roadName == "曹安公路":
            if tmpId == 1:
                self.mrSpeedOfPlane = vehi.currSpeed()
            elif tmpId >= 2 and tmpId <= self.mrSquareVehiCount:
                ref_inOutSpeed.value = self.mrSpeedOfPlane
            return True
        return False

    # 过载的父类方法，计算是否要左自由变道
    # vehi:车辆
    # return结果，True：变道、False：不变道
    def reCalcToLeftFreely(self, vehi):
        #车辆到路段终点距离小于20米不变道
        if vehi.vehicleDriving().distToEndpoint() - vehi.length() / 2 < m2p(20):
            return False
        tmpId = vehi.id() % 100000
        roadName = vehi.roadName()
        if roadName == "曹安公路":
            if tmpId >= 23 and tmpId <= 28:
                laneNumber = vehi.vehicleDriving().laneNumber()
                if laneNumber == 1 or laneNumber == 4:
                    return True
        return False

    # 过载的父类方法，计算是否要右自由变道
    # vehi:车辆
    # return结果，True：变道、False：不变道
    def reCalcToRightFreely(self, vehi):
        tmpId = vehi.id() % 100000;
        #车辆到路段终点距离小于20米不变道
        if vehi.vehicleDriving().distToEndpoint() - vehi.length() / 2 < m2p(20):
            return False
        roadName = vehi.roadName();
        if roadName == "曹安公路":
            if tmpId >= 23 and tmpId <= 28:
                laneNumber = vehi.vehicleDriving().laneNumber()
                if laneNumber == 2 or laneNumber == 5:
                    return True
        return False

    # 过载父类方法，设置信号灯色。此例设置ID为5的信号灯色为红色，此方法在每个计算周被调用，所以这个信号灯一直是红色
    # 本次自动创建的路网没有信号灯，在此实现该方法只为说明如何运用
    def calcLampColor(self, signalLamp):
        if signalLamp.id() == 5:
            signalLamp.setLampColor('红')
            return True
        return False

    # 过载父类方法， 计算车辆当前限制车道序号列表
    def calcLimitedLaneNumber(self, vehi):
        # 如果当前车辆在路段上，且路段ID等于2，则小车走内侧，大车走外侧
        if vehi.roadIsLink():
            # IVehicle.road()方法获取的是车辆当前所路段或连接段的void指针，需要将它转换成路段或连接段
            link = wrapInstance(vehi.road().__int__(), ILink)
            if link is not None and link.id() == 2:
                laneCount = link.laneCount()
                # 小车走内侧，大车走外侧，设长度小于8米为小车
                if(vehi.length() < m2p(8)):
                    return [num for num in range(laneCount // 2 - 1)]
                else:
                    return [num for num in range(laneCount // 2 - 1, laneCount)]
        return []

    # 过载父类方法，车道限速
    def ref_calcSpeedLimitByLane(self, link, laneNumber, ref_outSpeed):
        # ID为2路段，车道序号为0，速度不大于30千米/小时
        if link.id() == 2 and laneNumber <= 1:
            ref_outSpeed.value = 30
            return True
        return False

    # 过载父类方法 对发车点一增加发车时间段
    #   此范例展示了以飞机打头的方阵全部驰出路段后为这条路段的发车点增加发车间隔
    def calcDynaDispatchParameters(self):
        # TESSNG 顶层接口
        iface = tessngIFace()
        currSimuTime = iface.simuInterface().simuTimeIntervalWithAcceMutiples()
        # ID等于1路段上车辆
        lVehi = iface.simuInterface().vehisInLink(1)
        if currSimuTime < 1000 * 10 or len(lVehi) > 0:
            return []
        now = datetime.now()
        # 当前时间秒
        currSecs = now.hour * 3600 + now.minute * 60 + now.second
        # 仿真10秒后且ID等于1的路段上车辆数为0，则为ID等于1的发车点增加发车间隔
        di = Online.DispatchInterval()
        di.dispatchId = 1
        di.fromTime = currSecs
        di.toTime = di.fromTime + 300 - 1
        di.vehiCount = 300
        di.mlVehicleConsDetail = [Online.VehiComposition(1, 60), Online.VehiComposition(2, 40)]
        return [di]

    # 过载父类方法，动态修改决策点不同路径流量比
    def calcDynaFlowRatioParameters(self):
        # TESSNG 顶层接口
        iface = tessngIFace()
        # 当前仿真计算批次
        batchNum = iface.simuInterface().batchNumber()
        # 在计算第20批次时修改某决策点各路径流量比
        if batchNum == 20:
            # 一个决策点某个时段各路径车辆分配比
            dfi = Online.DecipointFlowRatioByInterval()
            #决策点编号
            dfi.deciPointID = 5
            #起始时间 单位秒
            dfi.startDateTime = 1
            #结束时间 单位秒
            dfi.endDateTime = 84000
            rfr1 = Online.RoutingFlowRatio(10, 3)
            rfr2 = Online.RoutingFlowRatio(11, 4)
            rfr3 = Online.RoutingFlowRatio(12, 3)
            dfi.mlRoutingFlowRatio = [rfr1, rfr2, rfr3]
            return [dfi]
        return []

    def calcDynaSignalContralParameters(self):
        return []

    # 过载父类方法，停止指定车辆运行，退出路网，但不会从内存删除，会参数各种统计
    #  范例车辆进入ID等于2的路段或连接段，路离终点小于100米，则驰出路网
    def isStopDriving(self, vehi):
        # if vehi.roadId() == 2:
        #     # 车头到当前路段或连接段终点距离
        #     dist = vehi.vehicleDriving().distToEndpoint(True)
        #     # 如果距终点距离小于100米，车辆停止运行退出路网
        #     if dist < m2p(100):
        #         return True
        return False

    # 过载的父类方法，TESS NG 在每个计算周期结束后调用此方法，大量用户逻辑在此实现，注意耗时大的计算要尽可能优化，否则影响运行效率
    def afterOneStep(self):
        #= == == == == == =以下是获取一些仿真过程数据的方法 == == == == == ==
        # TESSNG 顶层接口
        iface = tessngIFace()
        # TESSNG 仿真子接口
        simuiface = iface.simuInterface()
        # TESSNG 路网子接口
        netiface = iface.netInterface()
        # 当前仿真计算批次
        batchNum = simuiface.batchNumber()
        # 当前已仿真时间，单位：毫秒
        simuTime = simuiface.simuTimeIntervalWithAcceMutiples()
        # 如果仿真时间大于等于600秒，通知主窗体停止仿真
        if(simuTime >= 600 * 1000):
            self.forStopSimu.emit()
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

    def afterStop(self):
        #最多连续仿真2次
        if self.mSimuCount >= 2:
            return
        else:
            self.forReStartSimu.emit()
























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
import functions


# 用户插件子类，代表用户自定义与仿真相关的实现逻辑，继承自PyCustomerSimulator
#     多重继承中的父类QObject，在此目的是要能够自定义信号signlRunInfo
class MySimulator(QObject, PyCustomerSimulator):
    signalRunInfo = Signal(str)
    forStopSimu = Signal()
    forReStartSimu = Signal()

    def __init__(self, secondary_dev):
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
        self.secondary_dev = secondary_dev
        # 初始化信号灯方案起始时间
        self.init_signal_groups_startTime()
        # 设置跟驰模型函数标志
        self.reSetFollowingParamsFlag = False
        # 设置换道模型函数标志
        self.ref_reSetChangeLaneFreelyParamFlag = False
        # 设置信号灯颜色标志位
        self.calcLampColorFlag = False

    # 初始化信号灯方案起始时间
    def init_signal_groups_startTime(self):
        # 读取方案数据
        with open('./Data/Signal_Plan_Data_1109.json', 'r', encoding='utf-8') as json_file:
            signal_groups_dict = json.load(json_file)
        # 所有灯组的起始时间
        self.signal_groups_startTime_lst = []
        for group in signal_groups_dict.values():
            for startTime in group.keys():
                self.signal_groups_startTime_lst.append(functions.time_to_seconds(startTime) * 1000)

    # 设置本类实现的过载方法被调用频次，即多少个计算周期调用一次。过多的不必要调用会影响运行效率
    def setStepsPerCall(self, vehi):
        # 设置当前车辆及其驾驶行为过载方法被TESSNG调用频次，即多少个计算周调用一次指定方法。如果对运行效率有极高要求，可以精确控制具体车辆或车辆类型及具体场景相关参数
        iface = tessngIFace()
        netface = iface.netInterface()
        netFileName = netface.netFilePath()
        # 范例打开临时路段会会创建车辆方阵，需要进行一些仿真过程控制
        if "Temp" in netFileName:
            # 允许对车辆重绘方法的调用
            vehi.setIsPermitForVehicleDraw(True)
            # 计算限制车道方法每10个计算周期被调用一次
            vehi.setSteps_calcLimitedLaneNumber(10)
            # 计算安全变道距离方法每10个计算周期被调用一次
            vehi.setSteps_calcChangeLaneSafeDist(10)
            # 重新计算车辆期望速度方法每一个计算周期被调用一次
            vehi.setSteps_reCalcdesirSpeed(1)
            # 重新设置车速方法每一个计算周期被调用一次
            vehi.setSteps_reSetSpeed(1)
        else:
            simuface = iface.simuInterface()
            # 仿真精度，即每秒计算次数
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
        # # 设置当前车辆及其驾驶行为过载方法被TESSNG调用频次，即多少个计算周调用一次指定方法。如果对运行效率有极高要求，可以精确控制具体车辆或车辆类型及具体场景相关参数
        # self.setStepsPerCall(vehi)
        return True

    # 过载的父类方法重新计算加速度
    def ref_calcAcce(self, vehi, acce):
        return False

    # 过载的父类方法，重新计算期望速度
    # vehi：车辆
    # ref_esirSpeed：返回结果,ref_desirSpeed.value是TESS NG计算好的期望速度，可以在此方法改变它
    # return结果：False：TESS NG忽略此方法作的修改，True：TESS NG采用此方法所作修改
    def ref_reCalcdesirSpeed(self, vehi, ref_desirSpeed):
        roadId = vehi.roadId()
        # 以动作控制案例 - 机动车交叉口路网的L5路段为例
        if roadId == 5:
            # L5离路段起点50-150m处为减速区
            distToStart = vehi.vehicleDriving().distToStartPoint()
            if m2p(50) < distToStart < m2p(100) and functions.action_control_methodNumber == 3:
                if vehi.vehicleTypeCode() == 1:
                    ref_desirSpeed.value = m2p(10)
                    print(vehi.id(), "的小客车进入减速区，减速为10，当前速度为", vehi.currSpeed())
                elif vehi.vehicleTypeCode() == 2:
                    print(vehi.id(), "的大客车进入减速区，减速为5，当前速度为", vehi.currSpeed())
                    ref_desirSpeed.value = m2p(5)
                return True
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
        # 尝试让L12等待的车辆强制闯红灯
        if functions.action_control_methodNumber == 7:
            if vehi.roadId() == 12:
                vehi_currentSpeed = vehi.currSpeed()
                vehi_currentDistToEnd = vehi.vehicleDriving().distToEndpoint(True)
                if m2p(vehi_currentSpeed) < 20 and p2m(vehi_currentDistToEnd) < 3:
                    random_number = random.random()
                    if random_number < 0.8:
                        ref_inOutSpeed.value = m2p(15)
                        print(vehi.id(), vehi.currSpeed())
                        return True
        # 强制L5路段车辆停车
        if vehi.roadId() == 5:
            if functions.action_control_methodNumber == 10:
                ref_inOutSpeed.value = m2p(0)
                return True
        return False

    # 过载的父类方法，计算是否要左自由变道
    # vehi:车辆
    # return结果，True：变道、False：不变道
    def reCalcToLeftFreely(self, vehi):
        # 最右侧车道左变道，需开启不变道到最右侧车道
        if functions.action_control_methodNumber == 6:
            if vehi.lane().number() == 0:
                return True
        return False

    # 过载的父类方法，计算是否要右自由变道
    # vehi:车辆
    # return结果，True：变道、False：不变道
    def reCalcToRightFreely(self, vehi):
        return False

    # 过载父类方法，设置信号灯色。此例设置ID为5的信号灯色为红色，此方法在每个计算周被调用，所以这个信号灯一直是红色
    # 本次自动创建的路网没有信号灯，在此实现该方法只为说明如何运用
    def calcLampColor(self, signalLamp):
        # 默认设置函数为关闭状态，开启需将MySimulator的该函数标志为设置为True
        if signalLamp.id() == 5 and self.calcLampColorFlag:
            signalLamp.setLampColor('红')
            return True
        return False

    # 过载父类方法， 计算车辆当前限制车道序号列表
    def calcLimitedLaneNumber(self, vehi):
        return []

    # 过载父类方法 对发车点一增加发车时间段
    def calcDynaDispatchParameters(self):
        if functions.action_control_methodNumber == 1:
            # TESSNG 顶层接口
            iface = tessngIFace()
            # ID等于5路段上车辆
            lVehi = iface.simuInterface().vehisInLink(5)
            now = datetime.now()
            # 当前时间秒
            currSecs = now.hour * 3600 + now.minute * 60 + now.second
            # 仿真10秒后且ID等于1的路段上车辆数为0，则为ID等于1的发车点增加发车间隔
            di = Online.DispatchInterval()
            # 动作控制案例-机动车交叉口L5路段发车点ID为11
            di.dispatchId = 11
            di.fromTime = currSecs
            di.toTime = di.fromTime + 300 - 1
            di.vehiCount = 300
            di.mlVehicleConsDetail = [Online.VehiComposition(1, 60), Online.VehiComposition(2, 40)]
            functions.action_control_methodNumber = 0
            return [di]
        return []

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
            # 决策点编号
            dfi.deciPointID = 5
            # 起始时间 单位秒
            dfi.startDateTime = 1
            # 结束时间 单位秒
            dfi.endDateTime = 84000
            rfr1 = Online.RoutingFlowRatio(10, 1)
            rfr2 = Online.RoutingFlowRatio(11, 2)
            rfr3 = Online.RoutingFlowRatio(12, 3)
            dfi.mlRoutingFlowRatio = [rfr1, rfr2, rfr3]
            return [dfi]
        return []

    def calcDynaSignalContralParameters(self):
        return []

    # 过载父类方法，停止指定车辆运行，退出路网，但不会从内存删除，会参数各种统计
    #  范例车辆进入ID等于2的路段或连接段，路离终点小于100米，则驰出路网
    def isStopDriving(self, vehi):
        return False

    # Add 插件方法将添加到对应MySimulator类和MyNet类中
    # 修改跟驰模型参数
    def reSetFollowingParams(self):
        """ 重设跟驰模型参数
        :return: 返回 'Tessng.Online.FollowingModelParam' 的列表
        """
        # 默认设置函数为关闭状态，如开启需将MySimulator中的函数标志位设置为True
        if self.reSetFollowingParamsFlag:
            # 机动车
            followingModelParam_motor = Online.FollowingModelParam()
            followingModelParam_motor.vtype = Online.Motor
            followingModelParam_motor.alfa = 5
            followingModelParam_motor.beit = 3
            followingModelParam_motor.safeDistance = 15
            followingModelParam_motor.safeInterval = 10

            # 非机动车
            followingModelParam_Nonmotor = Online.FollowingModelParam()
            followingModelParam_Nonmotor.vtype = Online.Nonmotor
            followingModelParam_Nonmotor.alfa = 3
            followingModelParam_Nonmotor.beit = 1
            followingModelParam_Nonmotor.safeDistance = 5
            followingModelParam_Nonmotor.safeInterval = 6

            followingModelParam_lst = []
            followingModelParam_lst.append(followingModelParam_motor)
            followingModelParam_lst.append(followingModelParam_Nonmotor)

            return followingModelParam_lst
        return []

    # 重新设置自由变道参数
    def ref_reSetChangeLaneFreelyParam(self, vehi, safeTime, ultimateDist, targetRParam):
        # 默认设置函数为关闭状态，如开启需将MySimulator中的函数标志位设置为True
        if self.ref_reSetChangeLaneFreelyParamFlag:
            # 安全操作时间，从驾驶员反应到实施变道(完成变道前半段)所需时间，默认4秒
            safeTime.value = 100
            # 安全变道(完成变道前半段)后距前车距离，小于此距离压迫感增强，触发驾驶员寻求变道
            ultimateDist.value = 50
            # 目标车道后车影响系数，大于等于0小于等于1，此值越大目标车道后车距影响越大，反之则越小
            targetRParam.value = 0.9
            return True
        return False

    # 撤销变道，可用于强制车辆不变道
    def reCalcDismissChangeLane(self, vehi):
        if functions.action_control_methodNumber == 5:
            # 禁止车辆变道到最右侧车道
            lane = vehi.lane()
            if lane.number() == 1:
                if self.secondary_dev.judge_vehicle_laneChange_direction(vehi) == "right":
                    return True
        return False

    def afterStep(self, vehi):
        # = == == == == == =以下是获取一些仿真过程数据的方法 == == == == == ==
        # TESSNG 顶层接口
        iface = tessngIFace()
        # TESSNG 仿真子接口
        simuiface = iface.simuInterface()
        # TESSNG 路网子接口
        netiface = iface.netInterface()
        # 当前已仿真时间，单位：毫秒
        simuTime = simuiface.simuTimeIntervalWithAcceMutiples()

        # L5路段车辆行驶至离路段终点50m处被移出路网
        if functions.action_control_methodNumber == 8:
            if vehi.roadId() == 12:
                simuiface.stopVehicleDriving(vehi)

        # L5路段车辆行驶至离路段终点50m处航向角修改
        if functions.action_control_methodNumber == 9:
            if vehi.roadId() == 5:
                vehi.vehicleDriving().setAngle(vehi.angle() + 45.0)

    def afterOneStep(self):
        # = == == == == == =以下是获取一些仿真过程数据的方法 == == == == == ==
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
        # 仿真速度调整
        # simuiface.setAcceMultiples(1)
        # 正在运行的所有车辆
        allVehiStarted_lst = simuiface.allVehiStarted()

        # 车辆位置移动（以L5路段上的车辆为例，在3秒时直接将该车移动过路口）
        if functions.action_control_methodNumber == 2:
            for index, vehi in enumerate(allVehiStarted_lst):
                print(index, vehi.id())
                if vehi.roadId() == 5:
                    next_link = netiface.findLink(9)
                    laneObjs_next_link_lst = next_link.laneObjects()
                    if (vehi.vehicleDriving().move(laneObjs_next_link_lst[index % len(laneObjs_next_link_lst)],
                                                   float(index % 100))):
                        print("{}车辆移动成功。".format(vehi.id()))
                        functions.action_control_methodNumber = 0

        # 修改路径（L1所有车辆均修改为右转路径）
        if functions.action_control_methodNumber == 4:
            for vehi in allVehiStarted_lst:
                if vehi.roadId() == 1:
                    # 修改车辆路径
                    decisionPoints_lst = netiface.decisionPoints()
                    decisionPoint_link1 = None
                    for decisionPoint in decisionPoints_lst:
                        if decisionPoint.link().id() == 1:
                            decisionPoint_link1 = decisionPoint
                            break
                    decisionPoint_link1_routings_lst = []
                    if decisionPoint_link1:
                        decisionPoint_link1_routings_lst = decisionPoint_link1.routings()
                    if len(decisionPoint_link1_routings_lst) > 0:
                        if vehi.routing() != decisionPoint_link1_routings_lst[-1]:
                            if (vehi.vehicleDriving().setRouting(decisionPoint_link1_routings_lst[-1])):
                                print("{}车辆修改路径成功。".format(vehi.id()))

        # # 创建施工区
        # if simuTime == 10 * 1000:
        #     self.secondary_dev.createworkZone()
        # if simuTime % 60000 == 0:
        #     self.secondary_dev.flow_loading_section(simuTime / 1000)
        # if simuTime == 60 * 1000:
        #     waitForRemove_dispatchPoint = netiface.findDispatchPoint(11)
        #     if waitForRemove_dispatchPoint:
        #         if netiface.removeDispatchPoint(waitForRemove_dispatchPoint):
        #             print("发车点{}已移除。".format(11))

        # # 获取车辆状态，含位置
        # lVehiStatus = simuiface.getVehisStatus()
        # # print("车辆位置：", [(status.vehiId, status.mPoint.x(), status.mPoint.y()) for status in lVehiStatus])
        # # 信号灯组相位颜色
        # lPhoneColor = simuiface.getSignalPhasesColor()
        # # print("信号灯组相位颜色", [(pcolor.signalGroupId, pcolor.phaseNumber, pcolor.color, pcolor.mrIntervalSetted, pcolor.mrIntervalByNow) for pcolor in lPhoneColor])
        # # 获取当前仿真时间完成穿越采集器的所有车辆信息
        # lVehiInfo = simuiface.getVehisInfoCollected()
        # # if len(lVehiInfo) > 0:
        # #    print("车辆信息采集器采集信息：", [(vinfo.collectorId, vinfo.vehiId) for vinfo in lVehiInfo])
        # # 获取最近集计时间段内采集器采集的所有车辆集计信息
        # lVehisInfoAggr = simuiface.getVehisInfoAggregated()
        # # if len(lVehisInfoAggr) > 0:
        # #    print("车辆信息采集集计数据：", [(vinfo.collectorId, vinfo.vehiCount) for vinfo in lVehisInfoAggr])
        # # 获取当前仿真时间排队计数器计数的车辆排队信息
        # lVehiQueue = simuiface.getVehisQueueCounted()
        # # if len(lVehiQueue) > 0:
        # #    print("车辆排队计数器计数：", [(vq.counterId, vq.queueLength) for vq in lVehiQueue])
        # # 获取最近集计时间段内排队计数器集计数据
        # lVehiQueueAggr = simuiface.getVehisQueueAggregated()
        # # if len(lVehiQueueAggr) > 0:
        # #    print("车辆排队集计数据：", [(vqAggr.counterId, vqAggr.avgQueueLength) for vqAggr in lVehiQueueAggr])
        # # 获取当前仿真时间行程时间检测器完成的行程时间检测信息
        # lVehiTravel = simuiface.getVehisTravelDetected()
        # # if len(lVehiTravel) > 0:
        # #    print("车辆行程时间检测信息：", [(vtrav.detectedId, vtrav.travelDistance) for vtrav in lVehiTravel])
        # # 获取最近集计时间段内行程时间检测器集计数据
        # lVehiTravAggr = simuiface.getVehisTravelAggregated()
        # # if len(lVehiTravAggr) > 0:
        # #    print("车辆行程时间集计数据：", [(vTravAggr.detectedId, vTravAggr.vehiCount, vTravAggr.avgTravelDistance) for vTravAggr in lVehiTravAggr])

    def afterStop(self):
        pass

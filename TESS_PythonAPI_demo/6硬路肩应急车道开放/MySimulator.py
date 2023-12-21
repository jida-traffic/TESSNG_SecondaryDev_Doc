from PySide2.QtCore import *
from shiboken2.shiboken2 import wrapInstance
from Tessng import *
import random
import json
from datetime import datetime
from functions import *


# 用户插件子类，代表用户自定义与仿真相关的实现逻辑，继承自PyCustomerSimulator
#     多重继承中的父类QObject，在此目的是要能够自定义信号signlRunInfo
class MySimulator(QObject, PyCustomerSimulator):
    signalRunInfo = Signal(str)
    forStopSimu = Signal()
    forReStartSimu = Signal()

    def __init__(self):
        QObject.__init__(self)
        PyCustomerSimulator.__init__(self)
        self.openEmergencyLaneFlag = False

    # 动态创建事故区
    def dynaCreateAccidentZone(self, roadId, location, zoneLength, lFromLaneNumber, duration):
        '''
        # 动态创建事故区
        :param roadId:事故区所在的道路ID
        :param location: 事故区位置，事故区起点距路段起点的距离
        :param zoneLength: 事故区长度
        :param lFromLaneNumber: 事故区所在车道列表
        :param duration: 事故区持续时间，默认单位秒
        :return:
        '''
        accidentZoneObj = Online.DynaAccidentZoneParam()
        # 道路ID
        accidentZoneObj.roadId = roadId
        # 事故区名称
        accidentZoneObj.name = f"{roadId}路段事故区"
        # 位置，距离路段或连接段起点距离，单位米
        accidentZoneObj.location = m2p(location)
        # 事故区长度，单位米
        accidentZoneObj.length = m2p(zoneLength)
        # 事故区起始车道序号列表
        accidentZoneObj.mlFromLaneNumber = lFromLaneNumber
        # 事故持续时间
        accidentZoneObj.duration = duration
        # 创建事故区
        zone = tessngIFace().netInterface().createAccidentZone(accidentZoneObj)

    # 强制车辆不变道可用
    def judge_vehicle_laneChange_direction(self, vehi):
        '''
        判断车辆是左变道还是右变道。
        :param vehi: 运行车辆
        :return:
        '''
        lane = vehi.lane()
        vehi_currPos = vehi.pos()
        vehi_currDistToStart = lane.distToStartPoint(vehi_currPos)
        lane_centerBreakPoints = lane.centerBreakPoints()
        vehi_segmentIndex = -1
        # 获取车辆所在的道路分段号
        for index, centerBreakPoint in enumerate(lane_centerBreakPoints):
            lane_centerBreakPoints_distToStart = lane.distToStartPoint(centerBreakPoint)
            if vehi_currDistToStart < lane_centerBreakPoints_distToStart:
                vehi_segmentIndex = index
                break
        if 0 < vehi_segmentIndex < len(lane_centerBreakPoints):
            start_breakPoint = lane_centerBreakPoints[vehi_segmentIndex - 1]
            end_breakPoint = lane_centerBreakPoints[vehi_segmentIndex]
            # 以点积判断车辆处于中心线左侧还是右侧
            vehi_direction = car_position_road(start_breakPoint, end_breakPoint, vehi_currPos)
            # 判断车头角度偏度
            breakLane_angle = calculate_angle(start_breakPoint, end_breakPoint)
            # 若车辆处于中心线右侧且车头右偏，则判定为右变道意图
            if vehi_direction == "right" and vehi.angle() > breakLane_angle:
                return "right"
            # 若车辆处于中心线左侧且车头左偏，则判定为左变道意图
            elif vehi_direction == "left" and vehi.angle() < breakLane_angle:
                return "left"
            else:
                return "noChange"
        else:
            print("FindError:can't find the segment,relevant info:", vehi_segmentIndex, vehi_currDistToStart,
                  vehi_currPos)

    # 过载父类方法，撤销变道，可用于强制车辆不变道
    def reCalcDismissChangeLane(self, vehi):
        if not self.openEmergencyLaneFlag:
            # 封闭应急车道
            if vehi.roadId() == 1044:
                lane = vehi.lane()
                if lane.number() == 1:
                    if self.judge_vehicle_laneChange_direction(vehi) == "right":
                        return True
        return False

    # 过载的父类方法，TESS NG 在每个计算周期结束后调用此方法，大量用户逻辑在此实现，注意耗时大的计算要尽可能优化，否则影响运行效率
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
        # 当前正在运行车辆列表
        lAllVehi = simuiface.allVehiStarted()

        '''应急事件2-应急车道开放'''
        # 应急车道开放时设置为Ture，并删除路段决策点
        self.openEmergencyLaneFlag = True
        if self.openEmergencyLaneFlag:
            runInfo = "提示：\nL1033路段发生事故，车辆拥堵加剧，应急车道开放！\nL1044路段发生事故，车辆拥堵加剧，应急车道开放！"
            self.signalRunInfo.emit(runInfo)
            decisionPoints_lst = netiface.decisionPoints()
            for decisionPoint in decisionPoints_lst:
                routings_lst = decisionPoint.routings()
                for routing in routings_lst:
                    if netiface.removeDeciRouting(decisionPoint, routing):
                        print("应急车道开放，删除路段决策点！")
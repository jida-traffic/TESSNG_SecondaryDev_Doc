from PySide2.QtCore import *
from shiboken2.shiboken2 import wrapInstance
from Tessng import *
import random
import json
from datetime import datetime

from Plot import *


# 用户插件子类，代表用户自定义与仿真相关的实现逻辑，继承自PyCustomerSimulator
#     多重继承中的父类QObject，在此目的是要能够自定义信号signlRunInfo
class MySimulator(QObject, PyCustomerSimulator):
    signalRunInfo = Signal(str)
    forStopSimu = Signal()
    forReStartSimu = Signal()

    def __init__(self):
        QObject.__init__(self)
        PyCustomerSimulator.__init__(self)
        # 示例路段排队计数器列表
        self.VehiQueueAggregationDict = {}
        # 示例决策点当前流量，初始流量依次为右转(3802)，左转(3901,3902,3903,3904)，直行(3905,3907,3908,6109,6110)
        self.decisionPointCurrentFlowRation = {}
        # 示例决策点右左直流量比例
        self.decisionPointFlowRatio = []
        # 加载示例决策点初始流量
        with open('./JsonData/DecisionPoint3801_FlowRation.json', 'r', encoding='utf-8') as json_file:
            self.decisionPointCurrentFlowRation = json.load(json_file)
        # 排队计数器统计标志
        self.vehiQueueAggregateFlag = False
        # 排队计数器集计时间间隔列表
        self.lVehiQueueAggrInterval = []

    # 过载父类方法，动态修改决策点不同路径流量比，以L21为例，默认流量比例为：右0（11），直1（10+10+26+23+4），左（2+2+10+2）
    def calcDynaFlowRatioParameters(self):
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
        if self.vehiQueueAggregateFlag:
            # 调整示例决策点的路径流量比
            print("L21起点路段路口直行车道排队过长，降低直行流量比！", simuTime)
            # 路径流量分配比时间段
            decipointInterval = list(self.decisionPointCurrentFlowRation.keys())[0]
            # 一个决策点某个时段各路径车辆分配比
            decipointFlowRatioByInterval = Online.DecipointFlowRatioByInterval()
            # 决策点编号
            decipointFlowRatioByInterval.deciPointID = 3801
            # 起始时间 单位秒
            decipointFlowRatioByInterval.startDateTime = int(decipointInterval.split("-")[0])
            # 结束时间 单位秒
            decipointFlowRatioByInterval.endDateTime = int(decipointInterval.split("-")[1])
            lRoutingFlowRatio = []
            lRoutingFlowRatioAfterUpdate = []
            for index, (routingId, routingFlowRatio) in enumerate(
                    list(self.decisionPointCurrentFlowRation.values())[0].items()):
                # 右转
                if index <= 0:
                    CurrentFlowRation = int(routingFlowRatio) + 3
                    lRoutingFlowRatio.append(Online.RoutingFlowRatio(int(routingId), float(CurrentFlowRation)))
                    lRoutingFlowRatioAfterUpdate.append(CurrentFlowRation)
                    self.decisionPointCurrentFlowRation[decipointInterval][routingId] = str(
                        CurrentFlowRation)
                # 左转
                elif 0 < index <= 4:
                    CurrentFlowRation = int(routingFlowRatio)
                    lRoutingFlowRatio.append(Online.RoutingFlowRatio(int(routingId), float(CurrentFlowRation)))
                    lRoutingFlowRatioAfterUpdate.append(CurrentFlowRation)
                # 直行 3905 3907 3908
                elif 4 < index < 8:
                    CurrentFlowRation = int(routingFlowRatio) + 3
                    lRoutingFlowRatio.append(Online.RoutingFlowRatio(int(routingId), float(CurrentFlowRation)))
                    lRoutingFlowRatioAfterUpdate.append(CurrentFlowRation)
                # 直行 6109 6110
                else:
                    CurrentFlowRation = int(routingFlowRatio) if int(routingFlowRatio) < 6 else int(
                        routingFlowRatio) - 6
                    lRoutingFlowRatio.append(Online.RoutingFlowRatio(int(routingId), float(CurrentFlowRation)))
                    lRoutingFlowRatioAfterUpdate.append(CurrentFlowRation)
                if index == 9:
                    rightRatio = round(lRoutingFlowRatioAfterUpdate[0] / sum(lRoutingFlowRatioAfterUpdate) * 100, 1)
                    leftRatio = round(sum(lRoutingFlowRatioAfterUpdate[1:5]) / sum(lRoutingFlowRatioAfterUpdate) * 100,
                                      1)
                    straightRatio = round(
                        sum(lRoutingFlowRatioAfterUpdate[6:10]) / sum(lRoutingFlowRatioAfterUpdate) * 100, 1)
                    runInfo = f"L21起点路段路口直行车道排队过长，动态调整左转、右转和直行的流量比！\n\n修改后右转比例为: " \
                              f"{rightRatio}\n左转比例为: {leftRatio}\n直行比例为: {straightRatio}\n"
                    self.signalRunInfo.emit(runInfo)
                    self.decisionPointFlowRatio.append([rightRatio, leftRatio, straightRatio])
            decipointFlowRatioByInterval.mlRoutingFlowRatio = lRoutingFlowRatio
            self.vehiQueueAggregateFlag = False
            return [decipointFlowRatioByInterval]
        return []

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
        # 获取最近集计时间段内排队计数器集计数据
        lVehiQueueAggr = simuiface.getVehisQueueAggregated()
        if len(lVehiQueueAggr) > 0 and simuTime > (300 + 20) * 1000:
            print(simuTime)
            self.lVehiQueueAggrInterval.append((simuTime / 1000) - 300)
            for vqAggr in lVehiQueueAggr:
                vehiCounterId = vqAggr.counterId
                # 定位到示例路段上的排队计数器
                if vehiCounterId in [4501, 4502, 4503, 4504]:
                    if vehiCounterId not in self.VehiQueueAggregationDict:
                        self.VehiQueueAggregationDict[vehiCounterId] = []
                    self.VehiQueueAggregationDict[vehiCounterId].append(vqAggr.avgQueueLength)
                    print("车辆排队集计数据：", vqAggr.counterId, vqAggr.avgQueueLength, vqAggr.maxQueueLength)
                    self.vehiQueueAggregateFlag = True

    def afterStop(self):
        print(self.decisionPointFlowRatio)
        print(self.VehiQueueAggregationDict)
        print(self.lVehiQueueAggrInterval)
        plot_queue_lengths(self.lVehiQueueAggrInterval, self.VehiQueueAggregationDict)
        plot_traffic_ratios(self.lVehiQueueAggrInterval, self.decisionPointFlowRatio)

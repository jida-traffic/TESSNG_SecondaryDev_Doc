import json
import random

from PySide2.QtCore import *
from Tessng import tessngPlugin, tessngIFace, m2p, p2m
from Tessng import Online
from Tessng import _RoutingFLowRatio, _DecisionPoint

import functions

class SecondaryDevCases:
    """ 定义二次开发案例类 SecondaryDevCases
        Attributes:
            id: 二次开发案例对象编号
    """

    def __init__(self, _id):
        self.id = _id

    # 信控编辑案例
    def edit_signal_controller(self):
        """ 信控编辑
        :return:
        """
        # 代表TESS NG的接口
        iface = tessngIFace()
        # 代表TESS NG的路网子接口
        netiface = iface.netInterface()

        # 创建两条新路段和一条连接段作为示例
        startPoint1 = QPointF(m2p(-300), m2p(-200))
        endPoint1 = QPointF(m2p(-50), m2p(-200))
        lPoint1 = [startPoint1, endPoint1]
        link1 = netiface.createLink(lPoint1, 3, "信控编辑路段1")

        startPoint2 = QPointF(m2p(50), m2p(-200))
        endPoint2 = QPointF(m2p(300), m2p(-200))
        lPoint2 = [startPoint2, endPoint2]
        link2 = netiface.createLink(lPoint2, 3, "信控编辑路段2")

        # 连接段车道连接列表
        lLaneObjects = []
        if link1 and link2:
            lFromLaneNumber = [1, 2, 3]
            lToLaneNumber = [1, 2, 3]
            connector = netiface.createConnector(link1.id(), link2.id(), lFromLaneNumber, lToLaneNumber,
                                                 "信控编辑连接段", True)
            if connector:
                lLaneObjects = connector.laneObjects()
                for laneObj in lLaneObjects:
                    print("上游车道ID", laneObj.fromLane().id(), "下游车道ID", laneObj.toLane().id())
        # 创建发车点
        if link1:
            dp = netiface.createDispatchPoint(link1)
            if dp:
                dp.addDispatchInterval(1, 3600, 3600)

        # 创建信号灯组
        signalGroup = netiface.createSignalGroup("信号灯组1", 60, 1, 3600)
        # 创建相位,40秒绿灯，黄灯3秒，全红3秒
        red = Online.ColorInterval("G", 40)
        green = Online.ColorInterval("Y", 3)
        yellow = Online.ColorInterval("R", 3)
        signalPhase = netiface.createSignalPhase(signalGroup, "信号灯组1相位1",
                                                 [green, yellow, red])
        # 创建信号灯
        for index, laneObj in enumerate(lLaneObjects):
            signalLamp = netiface.createSignalLamp(signalPhase, "信号灯{}".format(index + 1), laneObj.fromLane().id(),
                                                   laneObj.toLane().id(), m2p(2.0))

    # 双环信控方案下发
    def double_ring_signal_control(self, current_simuTime):
        """ 双环信控方案下发
        :param current_simuTime: 当前仿真时间
        :return:
        """

        # 代表TESS NG的接口
        iface = tessngIFace()
        # 代表TESS NG的路网子接口
        netiface = iface.netInterface()

        # 读取方案数据
        with open('./Data/Signal_Plan_Data_1109.json', 'r', encoding='utf-8') as json_file:
            signal_groups_dict = json.load(json_file)

        # 创建信号灯组和相位
        for group_name, group in signal_groups_dict.items():
            # 当前灯组
            current_signal_group = None
            # 通过灯组名称查询到灯组
            all_signal_groups_lst = netiface.signalGroups()
            for signal_group in all_signal_groups_lst:
                if signal_group.groupName() == group_name:
                    current_signal_group = signal_group
                    break
            if current_signal_group:
                current_signal_group_phases_lst = current_signal_group.phases()
            else:
                print("FindError: The signalGroup not in current net.")
                break

            # 获取所有灯组的起始时间
            signal_group_startTime_lst = list(group.keys())
            for index, group_data in enumerate(group.values()):
                start_time = signal_group_startTime_lst[index]
                end_time = signal_group_startTime_lst[index + 1] if index != len(
                    signal_group_startTime_lst) - 1 else "24:00"
                # 起始时间和结束时间的秒数表示
                start_time_seconds = functions.time_to_seconds(start_time)
                end_time_seconds = functions.time_to_seconds(end_time)
                # 若当前仿真时间位于当前时段内，修改当前时段信号灯组的相位
                if start_time_seconds <= current_simuTime < end_time_seconds:
                    period_time = group_data['cycle_time']
                    phases = group_data['phases']
                    # 修改周期
                    current_signal_group.setPeriodTime(int(period_time))
                    for phase in phases:
                        phase_name = phase['phase_name']
                        phase_number = int(phase['phase_number'])
                        color_list = []  # 按照红灯、绿灯、黄灯、红灯顺序计算
                        color_list.append(Online.ColorInterval('红', int(phase['start_time'])))
                        color_list.append(Online.ColorInterval('绿', int(phase['green_time'])))
                        color_list.append(Online.ColorInterval('黄', 3))
                        if int(period_time - phase['start_time'] - phase['green_time'] - 3) > 0:
                            color_list.append(
                                Online.ColorInterval('红',
                                                     int(period_time - phase['start_time'] - phase['green_time'] - 3)))

                        # 当前灯组包含的相位序号
                        current_phase = None
                        for current_signal_group_phase in current_signal_group_phases_lst:
                            if phase_number == int(current_signal_group_phase.number()):
                                current_phase = current_signal_group_phase
                                break

                        # 若已存在该相位，修改相位灯色顺序，否则添加相位
                        if current_phase:
                            # 修改相位
                            current_phase.setColorList(color_list)
                        else:
                            signal_phase = netiface.createSignalPhase(current_signal_group, phase_name, color_list)
                            # 设置相位序号
                            signal_phase.setNumber(phase_number)
                        # 设置相位包含的信号灯
                        for lampId in phase["lamp_lst"]:
                            lamp = netiface.findSignalLamp(int(lampId))
                            if lamp:
                                '''
                                目前一个信号灯属于多个相位，相位间不交叉。因此如果要实际下发方案时，应按照仿真时间实时管理相位序号。
                                '''
                                lamp.setPhaseNumber(phase_number)
                            else:
                                print("FindError:未查找到信号灯:", lampId)

    # 双环信控方案下发测试
    def double_ring_signal_control_test(self, planNumber):
        """ 双环信控方案下发测试
        :param planNumber: 方案序号
        :return:
        """
        # 读取方案数据
        with open('./Data/Signal_Plan_Data_1109.json', 'r', encoding='utf-8') as json_file:
            signal_groups_dict = json.load(json_file)
        # 所有灯组的起始时间
        signal_groups_startTime_lst = []
        for group in signal_groups_dict.values():
            for startTime in group.keys():
                signal_groups_startTime_lst.append(functions.time_to_seconds(startTime))
        # 当前方案序号
        current_planNumber = planNumber % len(signal_groups_startTime_lst)
        print(signal_groups_startTime_lst[current_planNumber], ":双环信控方案更改。")
        self.double_ring_signal_control((signal_groups_startTime_lst[current_planNumber]))

    # 流量加载
    def traffic_loading(self):
        """ 流量加载
        :return:
        """
        # 代表TESS NG的接口
        iface = tessngIFace()
        # 代表TESS NG的路网子接口
        netiface = iface.netInterface()
        # 代表TESS NG的仿真子接口
        simuiface = iface.simuInterface()

        '''1.新建发车点'''
        # 创建两条新路段和一条连接段作为示例
        startPoint1 = QPointF(m2p(-300), m2p(-180))
        endPoint1 = QPointF(m2p(-50), m2p(-180))
        lPoint1 = [startPoint1, endPoint1]
        link1 = netiface.createLink(lPoint1, 3, "流量加载路段1")

        startPoint2 = QPointF(m2p(50), m2p(-180))
        endPoint2 = QPointF(m2p(300), m2p(-180))
        lPoint2 = [startPoint2, endPoint2]
        link2 = netiface.createLink(lPoint2, 3, "流量加载路段2")

        # 连接段车道连接列表
        lLaneObjects = []
        if link1 and link2:
            lFromLaneNumber = [1, 2, 3]
            lToLaneNumber = [1, 2, 3]
            connector = netiface.createConnector(link1.id(), link2.id(), lFromLaneNumber, lToLaneNumber,
                                                 "流量加载连接段", True)
            if connector:
                lLaneObjects = connector.laneObjects()
                for laneObj in lLaneObjects:
                    print("上游车道ID", laneObj.fromLane().id(), "下游车道ID", laneObj.toLane().id())

            # 创建车辆组成及指定车辆类型
            vehiType_proportion_lst = []
            # 车型组成：小客车0.3，大客车0.2，公交车0.1，货车0.4
            vehiType_proportion_lst.append(Online.VehiComposition(1, 0.3))
            vehiType_proportion_lst.append(Online.VehiComposition(2, 0.2))
            vehiType_proportion_lst.append(Online.VehiComposition(3, 0.1))
            vehiType_proportion_lst.append(Online.VehiComposition(4, 0.4))
            vehiCompositionID = netiface.createVehicleComposition("动态创建车型组成", vehiType_proportion_lst)
            if vehiCompositionID != -1:
                print("车型组成创建成功，id为：", vehiCompositionID)
                # 新建发车点,车型组成ID为动态创建的，600秒发300辆车
                if link1:
                    dp = netiface.createDispatchPoint(link1)
                    if dp:
                        dp.addDispatchInterval(vehiCompositionID, 600, 300)

            '''2.动态发车'''
            # 创建两条新路段和一条连接段作为示例
            startPoint3 = QPointF(m2p(-300), m2p(-160))
            endPoint3 = QPointF(m2p(-50), m2p(-160))
            lPoint3 = [startPoint3, endPoint3]
            link3 = netiface.createLink(lPoint3, 3, "动态加载车辆段")

            startPoint4 = QPointF(m2p(50), m2p(-160))
            endPoint4 = QPointF(m2p(300), m2p(-160))
            lPoint4 = [startPoint4, endPoint4]
            link4 = netiface.createLink(lPoint4, 3, "动态加载车辆段")

            # 连接段车道连接列表
            lLaneObjects = []
            if link3 and link4:
                lFromLaneNumber = [1, 2, 3]
                lToLaneNumber = [1, 2, 3]
                connector = netiface.createConnector(link3.id(), link4.id(), lFromLaneNumber, lToLaneNumber,
                                                     "动态加载加载连接段", True)
                if connector:
                    lLaneObjects = connector.laneObjects()
                    for laneObj in lLaneObjects:
                        print("上游车道ID", laneObj.fromLane().id(), "下游车道ID", laneObj.toLane().id())

            # 在指定车道和位置动态加载车辆(示例：在0,1,2车道不同位置动态加载车辆)
            dvp_lane0 = Online.DynaVehiParam()
            dvp_lane1 = Online.DynaVehiParam()
            dvp_lane2 = Online.DynaVehiParam()
            dvp_lane0.vehiTypeCode = 1
            dvp_lane1.vehiTypeCode = 2
            dvp_lane2.vehiTypeCode = 3
            dvp_lane0.roadId = link3.id()
            dvp_lane1.roadId = link3.id()
            dvp_lane2.roadId = link4.id()
            dvp_lane0.laneNumber = 0
            dvp_lane1.laneNumber = 1
            dvp_lane2.laneNumber = 2
            dvp_lane0.dist = m2p(50)
            dvp_lane1.dist = m2p(100)
            dvp_lane2.dist = m2p(50)
            dvp_lane0.speed = 20
            dvp_lane0.speed = 30
            dvp_lane0.speed = 40
            dvp_lane0.color = "#FF0000"
            dvp_lane1.color = "#008000"
            dvp_lane2.color = "#0000FF"
            vehi_lane0 = simuiface.createGVehicle(dvp_lane0)
            vehi_lane1 = simuiface.createGVehicle(dvp_lane1)
            vehi_lane2 = simuiface.createGVehicle(dvp_lane2)

    # 路径加载
    def flow_loading(self):
        """ 路径加载
        :return:
        """
        # 代表TESS NG的接口
        iface = tessngIFace()
        # 代表TESS NG的路网子接口
        netiface = iface.netInterface()
        # 代表TESS NG的仿真子接口
        simuiface = iface.simuInterface()

        # 以标准四岔路口为例 (L3-C2-L10)
        link3 = netiface.findLink(3)
        link10 = netiface.findLink(10)
        link6 = netiface.findLink(6)
        link7 = netiface.findLink(7)
        link8 = netiface.findLink(8)
        # 新建发车点
        if link3:
            dp = netiface.createDispatchPoint(link3)
            if dp:
                dp.addDispatchInterval(1, 1800, 900)
        # 创建决策点
        decisionPoint = netiface.createDecisionPoint(link3, m2p(30))
        # 创建路径(左，直，右)
        decisionRouting1 = tessngIFace().netInterface().createDeciRouting(decisionPoint, [link3, link10, link6])
        decisionRouting2 = tessngIFace().netInterface().createDeciRouting(decisionPoint, [link3, link10, link8])
        decisionRouting3 = tessngIFace().netInterface().createDeciRouting(decisionPoint, [link3, link10, link7])

        # 分配左、直、右流量比
        flowRatio_left = _RoutingFLowRatio()
        flowRatio_left.RoutingFLowRatioID = 1
        flowRatio_left.routingID = decisionRouting1.id()
        flowRatio_left.startDateTime = 0
        flowRatio_left.endDateTime = 999999
        flowRatio_left.ratio = 2.0
        flowRatio_straight = _RoutingFLowRatio()
        flowRatio_straight.RoutingFLowRatioID = 2
        flowRatio_straight.routingID = decisionRouting2.id()
        flowRatio_straight.startDateTime = 0
        flowRatio_straight.endDateTime = 999999
        flowRatio_straight.ratio = 3.0
        flowRatio_right = _RoutingFLowRatio()
        flowRatio_right.RoutingFLowRatioID = 3
        flowRatio_right.routingID = decisionRouting3.id()
        flowRatio_right.startDateTime = 0
        flowRatio_right.endDateTime = 999999
        flowRatio_right.ratio = 1.0

        # 决策点数据
        decisionPointData = _DecisionPoint()
        decisionPointData.deciPointID = decisionPoint.id()
        decisionPointData.deciPointName = decisionPoint.name()
        decisionPointPos = QPointF()
        if decisionPoint.link().getPointByDist(decisionPoint.distance(), decisionPointPos):
            decisionPointData.X = decisionPointPos.x()
            decisionPointData.Y = decisionPointPos.y()
            decisionPointData.Z = decisionPoint.link().z()
        # 更新决策点及其各路径不同时间段流量比
        updated_decision_point = netiface.updateDecipointPoint(
            decisionPointData, [flowRatio_left, flowRatio_straight, flowRatio_right]
        )
        if updated_decision_point:
            print("决策点创建成功。")
            # 删除右转路径
            if (netiface.removeDeciRouting(decisionPoint, decisionRouting3)):
                print("删除右转路径成功。")

    # 路径断面流量加载
    def flow_loading_section(self, current_time):
        """ 路径断面流量加载
        :param current_time: 当前仿真时间
        :return:
        """
        # 代表TESS NG的接口
        iface = tessngIFace()
        # 代表TESS NG的路网子接口
        netiface = iface.netInterface()
        # 代表TESS NG的仿真子接口
        simuiface = iface.simuInterface()
        # 读取方案数据
        with open('./Data/flow_ratio_quarter.json', 'r', encoding='utf-8') as json_file:
            flow_ratio_quarter_dict = json.load(json_file)
        for linkId, quarter_ratios in flow_ratio_quarter_dict.items():
            decisionPoint = None
            # 查找到决策点
            decisionPoints_lst = netiface.decisionPoints()
            for _decisionPoint in decisionPoints_lst:
                if _decisionPoint.link().id() == int(linkId):
                    decisionPoint = _decisionPoint
                    break
            if decisionPoint:
                quarter_startTime_lst = list(quarter_ratios.keys())
                for index, quarter_ratio in enumerate(quarter_ratios.values()):
                    quarter_time_seconds = functions.time_to_seconds(quarter_startTime_lst[index])
                    if index != len(quarter_startTime_lst) - 1:
                        quarter_time_seconds_next = functions.time_to_seconds(quarter_startTime_lst[index + 1])
                    else:
                        quarter_time_seconds_next = quarter_time_seconds + 1
                    if quarter_time_seconds <= current_time < quarter_time_seconds_next:
                        # 获取决策点现有路径
                        decision_routings_lst = decisionPoint.routings()
                        if (len(decision_routings_lst) == 3):
                            # 分配左、直、右流量比
                            flowRatio_left = _RoutingFLowRatio()
                            flowRatio_left.RoutingFLowRatioID = decision_routings_lst[0].id()
                            flowRatio_left.routingID = decision_routings_lst[0].id()
                            flowRatio_left.startDateTime = 0
                            flowRatio_left.endDateTime = 999999
                            flowRatio_left.ratio = quarter_ratio["left"]
                            flowRatio_straight = _RoutingFLowRatio()
                            flowRatio_straight.RoutingFLowRatioID = decision_routings_lst[1].id()
                            flowRatio_straight.routingID = decision_routings_lst[1].id()
                            flowRatio_straight.startDateTime = 0
                            flowRatio_straight.endDateTime = 999999
                            flowRatio_straight.ratio = quarter_ratio["straight"]
                            flowRatio_right = _RoutingFLowRatio()
                            flowRatio_right.RoutingFLowRatioID = decision_routings_lst[2].id()
                            flowRatio_right.routingID = decision_routings_lst[2].id()
                            flowRatio_right.startDateTime = 0
                            flowRatio_right.endDateTime = 999999
                            flowRatio_right.ratio = quarter_ratio["right"]
                            # 决策点数据
                            decisionPointData = _DecisionPoint()
                            decisionPointData.deciPointID = decisionPoint.id()
                            decisionPointData.deciPointName = decisionPoint.name()
                            decisionPointPos = QPointF()
                            if decisionPoint.link().getPointByDist(decisionPoint.distance(), decisionPointPos):
                                decisionPointData.X = decisionPointPos.x()
                                decisionPointData.Y = decisionPointPos.y()
                                decisionPointData.Z = decisionPoint.link().z()
                            # 更新决策点及其各路径不同时间段流量比
                            updated_decision_point = netiface.updateDecipointPoint(
                                decisionPointData, [flowRatio_left, flowRatio_straight, flowRatio_right]
                            )
                            if updated_decision_point:
                                print("{}流量更新成功。".format(quarter_startTime_lst[index]))
                        else:
                            print("DecisionRoutingsError:决策点{}需要包含左、直、右三条路径。".format(decisionPoint.id()))
            else:
                # 需路段存在决策点，才可更新，因此可用flow_loading函数新建决策点
                print("FindError:ID为{}的路段不存在决策点".format(linkId))

    # 动作控制
    def action_control(self, planNumber):
        """ 动作控制
        :param planNumber: 方案序号
        :return:
        """
        # 以动作控制案例-机动车交叉口路网的L5路段为例
        '''1. 修改发车流量信息，删除发车点'''
        # 修改发车流量信息需在MySimulator中的calcDynaDispatchParameters函数,删除发车点位于afterOneStep函数中
        '''2. 修改决策路径的属性，删除决策路径'''
        # 见路径加载/路径管理模块
        '''3. 修改减速区，施工区，事故区信息；删除减速区，施工区，事故区'''
        # 减速区见MySimulator中的ref_reCalcdesirSpeed函数
        '''4. 车辆位置移动'''
        # 见afterOneStep函数
        '''5. 修改车辆速度'''
        # 同3减速区
        '''6. 修改车辆路径'''
        # 以L1路段上的路径为例，见afterOneStep
        '''7. 强制车辆不变道'''
        # 见MySimulator中的reCalcDismissChangeLane函数
        '''8. 强制车辆变道'''
        # MySimulator中的reCalcToLeftFreely和reCalcToRightFreely,return true即可
        '''9. 强制车辆闯红灯'''
        # 见MySimulator的ref_reSetSpeed函数
        '''10. 强制车辆停车'''
        # 见MySimulator的ref_reSetSpeed函数
        '''11. 强制清除车辆（车辆消失）'''
        # 以L5路段上的路径为例，见afterStep
        '''12. 修改车辆航向角'''
        # 以L5路段上的路径为例，见afterStep
        '''13. 修改车辆速度，加速度'''
        # 同5，修改加速度函数为MySimulator的ref_reSetAcce，用法与设置速度相同
        '''14. 车道关闭，恢复'''
        # 几种方法都可以实现：1.设置事件区。2.MySimulator中的自由变道，以L5路段50-100m处最右侧封闭30秒为例

        functions.action_control_methodNumber = planNumber
        print(functions.action_control_methodNumber)

    # 创建施工区和删除施工区示例,施工区和事故区的删除有两种方式，duration结束后自动删除以及主动删除(removeRoadWorkZone)，此处初始化前者
    def createworkZone(self):
        """ 创建施工区
        :param :
        :return:
        """
        # 创建施工区
        workZone = Online.DynaRoadWorkZoneParam()
        # 道路ID
        workZone.roadId = int(5)
        # 施工区名称
        workZone.name = "施工区，限速40,持续20秒"
        # 位置，距离路段或连接段起点距离，单位米
        workZone.location = 50
        # 施工区长度，单位米
        workZone.length = 50
        # 车辆经过施工区的最大车速，单位千米/小时
        workZone.limitSpeed = 40
        # 施工区施工时长，单位秒
        workZone.duration = 20
        # 施工区起始车道
        workZone.mlFromLaneNumber = [0]
        # 创建施工区
        zone = tessngIFace().netInterface().createRoadWorkZone(workZone)

    # 管控手段控制
    def control_Measures(self, method_number):
        """ 管控手段控制
        :param method_number:调用的方法序号
        :return:
        """
        # TESSNG 顶层接口
        iface = tessngIFace()
        # TESSNG 仿真子接口
        simuiface = iface.simuInterface()
        # TESSNG 路网子接口
        netiface = iface.netInterface()
        '''1. 修改信号灯灯色'''
        # 见MySimulator的afterOneStep函数，L5路段信号灯第10秒红灯变绿灯，持续20秒。
        '''2. 修改信号灯组方案'''
        # 见双环管控方案下发。
        '''3. 修改相位绿灯时间长度'''
        # 除双环管控方案下所包含方法外，还有相位类自带的修改方法,以L12路段相位直行信号灯相位为例（ID为7），由红90绿32黄3红25改为红10绿110黄3红28
        if method_number == 3:
            signalPhase_L12_7 = netiface.findSignalPhase(7)
            color_list = []  # 按照红灯、绿灯、黄灯、红灯顺序计算
            color_list.append(Online.ColorInterval('红', 10))
            color_list.append(Online.ColorInterval('绿', 110))
            color_list.append(Online.ColorInterval('黄', 3))
            color_list.append(Online.ColorInterval('红', 28))
            signalPhase_L12_7.setColorList(color_list)
        '''5. 修改link, connector 限速'''
        # 以L5路段最高限速由80调整至20，连接段无法修改限速。
        if method_number == 5:
            link5 = netiface.findLink(5)
            link5.setLimitSpeed(20)

    # 换道模型
    def lane_changing_model(self, method_number):
        """ 换道模型
        :param method_number：调用的方法序号
        :return:
        """
        # TESSNG 顶层接口
        iface = tessngIFace()
        # TESSNG 仿真子接口
        simuiface = iface.simuInterface()
        # TESSNG 路网子接口
        netiface = iface.netInterface()
        '''1. 选择变道类型：强制变道，压迫变道，自由变道'''
        '''2. 设置强制变道，压迫变道参数'''
        # 目前仅有MySimulator中的ref_reSetChangeLaneFreelyParam函数设置安全操作时间、安全变道(完成变道前半段)后距前车距离、目标车道后车影响系数
        # 以L5路段两侧车道往中间变道为例

    # 流程控制
    def process_control(self, method_number):
        """ 流程控制
              :param method_number：调用的方法序号
              :return:
              """
        # TESSNG 顶层接口
        iface = tessngIFace()
        # TESSNG 仿真子接口
        simuiface = iface.simuInterface()
        # TESSNG 路网子接口
        netiface = iface.netInterface()
        '''1. 启动、暂停、恢复、停止仿真'''
        if method_number == 1:
            simuiface.startSimu()
        elif method_number == 2:
            simuiface.pauseSimu()
        elif method_number == 3:
            simuiface.stopSimu()
        elif method_number == 4:
            simuiface.pauseSimuOrNot()
        '''8. 获取运动信息'''
        # 8.1 获取路网在途车辆，见MySimulator中afterOneStep的simuiface.allVehiStarted()
        # 8.2 根据路段|车道获取车辆list
        if method_number == 8.2:
            vehiOnRoad5_lst = simuiface.vehisInLink(5)
            vehiOnLane20_lst = simuiface.vehisInLane(20)
            print("L5路段车辆id：")
            for vehi in vehiOnRoad5_lst:
                print(vehi.id())
            print("lane20车道车辆id：")
            for vehi in vehiOnLane20_lst:
                print(vehi.id())
        # 8.3 根据车辆id获取具体的车辆信息,以id为300001的车辆为例
        if method_number == 8.3:
            vehi_300001 = simuiface.getVehicle(300001)
            print("300001车辆的具体信息：")
            print("所在路段:", vehi_300001.roadId())
            print("所在车道:", vehi_300001.lane().id())
            print("当前车速:", vehi_300001.currSpeed())
            print("当前加速度:", vehi_300001.acce())
            print("当前角度:", vehi_300001.angle())
            print("当前位置:", vehi_300001.pos())
            print("其它:", "......")
        '''10. 设置仿真精度'''
        if method_number == 10:
            simuiface.setSimuAccuracy(10)
        '''11. 设置仿真开始结束时间'''
        # 可以设置仿真时长，无法设置仿真开始的时间，不过可以由定时器定时启动和结束仿真实现设置仿真开始结束时间，此处仅展示二次开发的设置仿真时长方法
        if method_number == 11:
            simuiface.setSimuIntervalScheming(30)
        '''12. 设置仿真加速比'''
        if method_number == 12:
            simuiface.setAcceMultiples(10)

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
            vehi_direction = functions.car_position_road(start_breakPoint, end_breakPoint, vehi_currPos)
            # 判断车头角度偏度
            breakLane_angle = functions.calculate_angle(start_breakPoint, end_breakPoint)
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


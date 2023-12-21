import json
import random

from PySide2.QtCore import *
from Tessng import tessngPlugin, tessngIFace, m2p, p2m
from Tessng import Online
from Tessng import _RoutingFLowRatio, _DecisionPoint


class SecondaryDevCases:
    """ 定义二次开发案例类 SecondaryDevCases
        Attributes:
            id: 二次开发案例对象编号
    """

    def __init__(self, _id):
        self.id = _id


    def opt_traffic_canalization(self):
        # 修改交叉口道路渠化，注意：需同时关注是否需要同步修改路径
        # 假定需要将芜湖交叉口的东进口一条直行改左转，则进行如下操作：

        # TESSNG 顶层接口
        iface = tessngIFace()
        # TESSNG 仿真子接口
        simuiface = iface.simuInterface()
        # TESSNG 路网子接口
        netiface = iface.netInterface()

        link1 = netiface.findLink(1) # 东进口link
        link2 = netiface.findLink(2) # 西出口link
        link7 = netiface.findLink(7) # 北出口link

        # step1: 新建connector，laneconnector：
        #创建第三条连接段
        if link1 is not None and link2 is not None:
            lFromLaneNumber = [3, 4]
            lToLaneNumber = [3, 4]
            # 移除laneConnector,新增laneConnector 但是要保证connecotId要允许用户设置，不然基于connectorId的路径之类的全部都得动了
            old_left_connector = netiface.findConnector(3)
            netiface.removeConnector(old_left_connector)
            new_conn_left = netiface.createConnector(link1.id(), link7.id(), lFromLaneNumber, lToLaneNumber, "优化后左转连接器", True)

            # step2:  按需求修改,保证路径和渠化一致
            decisionPoint =  netiface.findDecisionPoint(1)# 可以先查找所有决策点，再根据路径经过link2且link7的，决策点，决策路径,这里直接指定了
            decisionRouting_left = netiface.findRouting(3)
            netiface.removeDeciRouting(decisionPoint, decisionRouting_left)
            # routing = netiface.createRouting([link1, link2, link8]) # 默认全选laneconnecor.
            decisionRouting_left_new = tessngIFace().netInterface().createDeciRouting(decisionPoint, [link1, link7])

            decisionRouting_right = netiface.findRouting(1)
            decisionRouting_straight = netiface.findRouting(2)


            # 分配左、直、右流量比
            flowRatio_left = _RoutingFLowRatio()
            flowRatio_left.RoutingFLowRatioID = 1
            flowRatio_left.routingID = decisionRouting_left_new.id()
            flowRatio_left.startDateTime = 0
            flowRatio_left.endDateTime = 999999
            flowRatio_left.ratio = 2.0
            flowRatio_straight = _RoutingFLowRatio()
            flowRatio_straight.RoutingFLowRatioID = 2
            flowRatio_straight.routingID = decisionRouting_straight.id()
            flowRatio_straight.startDateTime = 0
            flowRatio_straight.endDateTime = 999999
            flowRatio_straight.ratio = 3.0
            flowRatio_right = _RoutingFLowRatio()
            flowRatio_right.RoutingFLowRatioID = 3
            flowRatio_right.routingID = decisionRouting_right.id()
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

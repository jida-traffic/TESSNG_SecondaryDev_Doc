# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from Tessng import PyCustomerNet, TessInterface, TessPlugin, NetInterface, tngPlugin, tngIFace, m2p
from Tessng import NetItemType, GraphicsItemPropName

def Creat(netiface, flow):
    # 发车路段
    startPoint = QPointF(m2p(-3500), m2p(-1.75))
    endPoint = QPointF(m2p(-2500 - 20), m2p(-1.75))
    lPoint = [startPoint, endPoint]
    link1 = netiface.createLink(lPoint, 3, "发车路段")
    link1.setLimitSpeed(120)
    
    dp = netiface.createDispatchPoint(link1)
    dp.addDispatchInterval(1, 3600, 3500)
    
    # 上游路段
    startPoint = QPointF(m2p(-2500 + 20), 0)
    endPoint = QPointF(m2p(-500 - 10), 0)
    lPoint = [startPoint, endPoint]
    link2 = netiface.createLink(lPoint, 4, "上游路段")
    link2.setLimitSpeed(120)
    
    # 事故路段
    startPoint = QPointF(m2p(-500 + 10), 0)
    endPoint = QPointF(m2p(0 - 10), 0)
    lPoint = [startPoint, endPoint]
    link3 = netiface.createLink(lPoint, 4, "事故路段1")
    link3.setLimitSpeed(120)
    
    startPoint = QPointF(m2p(-0 + 10), 0)
    endPoint = QPointF(m2p(500 - 10), 0)
    lPoint = [startPoint, endPoint]
    link4 = netiface.createLink(lPoint, 4, "事故路段2")
    link4.setLimitSpeed(120)
    
    startPoint = QPointF(m2p(500 + 10), 0)
    endPoint = QPointF(m2p(1000 - 10), 0)
    lPoint = [startPoint, endPoint]
    link5 = netiface.createLink(lPoint, 4, "事故路段3")
    link5.setLimitSpeed(120)
    
    startPoint = QPointF(m2p(1000 + 10), 0)
    endPoint = QPointF(m2p(1500 - 10), 0)
    lPoint = [startPoint, endPoint]
    link6 = netiface.createLink(lPoint, 4, "事故路段4")
    link6.setLimitSpeed(120)
    
    # 下游路段
    startPoint = QPointF(m2p(1500 + 10), 0)
    endPoint = QPointF(m2p(3500), 0)
    lPoint = [startPoint, endPoint]
    link7 = netiface.createLink(lPoint, 4, "下游路段")
    link7.setLimitSpeed(120)
   
    conn1 = netiface.createConnector(link1.id(), link2.id(), [1,1,2,3], [1,2,3,4], "", True)
    conn2 = netiface.createConnector(link2.id(), link3.id(), [1,2,3,4], [1,2,3,4], "", True)
    conn3 = netiface.createConnector(link3.id(), link4.id(), [1,2,3,4], [1,2,3,4], "", True)
    conn4 = netiface.createConnector(link4.id(), link5.id(), [1,2,3,4], [1,2,3,4], "", True)
    conn5 = netiface.createConnector(link5.id(), link6.id(), [1,2,3,4], [1,2,3,4], "", True)
    conn6 = netiface.createConnector(link6.id(), link7.id(), [1,2,3,4], [1,2,3,4], "", True)
    
    return None

# 用户插件子类，代表用户自定义与路网相关的实现逻辑，继承自MyCustomerNet
class MyNet(PyCustomerNet):
    def __init__(self):
        super(MyNet, self).__init__()
    
    # 创建路网
    def createNet(self):
        # 代表TESS NG的接口
        iface = tngIFace()
        # 代表TESS NG的路网子接口
        netiface = iface.netInterface()
        
        # Creat(netiface, flow)
        
        
    # 过载的父类方法，当打开网后TESS NG调用此方法
    # 实现的逻辑是：路网加载后获取路段数，如果路网数为0则调用方法createNet构建路网，之后再次获取路段数，如果大于0则启动仿真
    def afterLoadNet(self):
        # 代表TESS NG的接口
        iface = tngIFace()
        # 代表TESS NG的路网子接口
        netiface = iface.netInterface()
        # 获取路段数
        count = netiface.linkCount()
        if(count == 0):
            self.createNet()
        if(netiface.linkCount() > 0):
            #所有路段
            lLink = netiface.links()
            #ID等于1的路段
            link = netiface.findLink(1)
            if link is not None:
                #路段中心线断点集
                lPoint = link.centerBreakPoints()
                lLane = link.lanes()
                if lLane is not None and len(lLane) > 0:
                    #第一条车道中心线断点
                    lPoint = lLane[0].centerBreakPoints()
            #所有连接段
            lConnector = netiface.connectors()
            if lConnector is not None and len(lConnector) > 0:
                #第一条连接段的所有“车道连接”
                lLaneConnector = lConnector[0].laneConnectors()
                #其中第一条“车道连接”
                laneConnector = lLaneConnector[0]
                #"车道连接“断点集
                lPoint = laneConnector.centerBreakPoints()
            
            #启动仿真
            iface.simuInterface().startSimu()
    
    def ref_labelNameAndFont(self, itemType, itemId, ref_outPropName, ref_outFontSize):
        # 代表TESS NG的接口
        iface = tngIFace()
        # 代表TESS NG仿真子接口
        simuiface = iface.simuInterface()
        # 如果仿真正在进行，设置ref_outPropName.value等于GraphicsItemPropName.None_，路段和车道都不绘制标签
        if simuiface.isRunning():
            ref_outPropName.value = GraphicsItemPropName.Name
            return
        # 默认绘制ID
        ref_outPropName.value = GraphicsItemPropName.Id
        # 标签大小为6米
        ref_outFontSize.value = 6
        # 如果是连接段一律绘制名称
        if itemType == NetItemType.GConnectorType:
            ref_outPropName.value = GraphicsItemPropName.Name
        elif itemType == NetItemType.GLinkType:
            if itemId in [1,2,3,4,5,6,7,8,9,10]:
                ref_outPropName.value = GraphicsItemPropName.Name

    # 过载父类方法，是否绘制车道中心线
    def isDrawLaneCenterLine(self, laneId):
        return True

    # 过载父类方法，是否绘制路段中心线
    def isDrawLinkCenterLine(self, linkId):
        if linkId in [1,2,3,4]:
            return False
        else:
            return True




















# -*- coding: utf-8 -*-

import os
from pathlib import Path
import sys

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from Tessng import PyCustomerNet, TessInterface, TessPlugin, NetInterface, tngPlugin, tngIFace, m2p
from Tessng import NetItemType, GraphicsItemPropName

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

        # 第一条路段
        startPoint = QPointF(m2p(-300), 0)
        endPoint = QPointF(m2p(300), 0)
        lPoint = [startPoint, endPoint]
        link1 = netiface.createLink(lPoint, 2, "公路1")
        if link1 is not None:
            # 车道列表
            lanes = link1.lanes()
            # 打印该路段所有车道ID列表
            print("公路1车道ID列表：", [lane.id() for lane in lanes])
            # 在当前路段创建发车点
            dp = netiface.createDispatchPoint(link1)
            if dp != None :
                # 设置发车间隔，含车型组成、时间间隔、发车数
                dp.addDispatchInterval(1, 14, 9)



    # 过载的父类方法，当打开网后TESS NG调用此方法
    #     实现的逻辑是：路网加载后获取路段数，如果路网数为0则调用方法createNet构建路网，之后再次获取路段数，如果大于0则启动仿真
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
                print("一条路段中心线断点：", [(p.x(), p.y()) for p in lPoint])
                lLane = link.lanes()
                if lLane is not None and len(lLane) > 0:
                    #第一条车道中心线断点
                    lPoint = lLane[0].centerBreakPoints()
                    print("一条车道中心线断点：", [(p.x(), p.y()) for p in lPoint])
            #所有连接段
            lConnector = netiface.connectors()
            if lConnector is not None and len(lConnector) > 0:
                #第一条连接段的所有“车道连接”
                lLaneConnector = lConnector[0].laneConnectors()
                #其中第一条“车道连接”
                laneConnector = lLaneConnector[0]
                #"车道连接“断点集
                lPoint = laneConnector.centerBreakPoints()
                print("一条'车道连接'中心线断点：", [(p.x(), p.y()) for p in lPoint])

            #启动仿真
            iface.simuInterface().startSimu()

        # 下面注释掉的代码逻辑是：通过插件获取传入的配置对象config，从中获取属性'__simuafterload'值，如果等于True值启动仿真
        # plugin = tngPlugin()
        # config = plugin.tessngConfig()
        # if config['__simuafterload'] is True:
        #     iface.simuInterface().startSimu()


    ''' 过载的父类方法，在绘制路网元素时被调用，确定用ID或名称，以及字体大小绘制标签，也可确定不绘制标签
    itemType：NetItemType常量，代表不同类型路网元素
    itemId：路网元素的ID
    ref_outPropName：返回值，GraphicsItemPropName枚举类型，影响路段和连接段的标签是否被绘制
        GraphicsItemPropName。None_表示不绘制，GraphicsItemPropName。ID：表示绘制ID，GraphicsItemPropName。NAME:表示绘制名称
    ref_outFontSize，返回值，标签大小，单位：米。假设车道宽度是3.5米，如果ref_outFontSize.value等于7，绘制的标签大小占两个车道宽度
    '''
    def ref_labelNameAndFont(self, itemType, itemId, ref_outPropName, ref_outFontSize):
        # 代表TESS NG的接口
        iface = tngIFace()
        # 代表TESS NG仿真子接口
        simuiface = iface.simuInterface()
        # 如果仿真正在进行，设置ref_outPropName.value等于GraphicsItemPropName.None_，路段和车道都不绘制标签
        if simuiface.isRunning():
            ref_outPropName.value = GraphicsItemPropName.None_
            return
        # 默认绘制ID
        ref_outPropName.value = GraphicsItemPropName.Id
        # 标签大小为6米
        ref_outFontSize.value = 6
        # 如果是连接段一律绘制名称
        if itemType == NetItemType.GConnectorType:
            ref_outPropName.value = GraphicsItemPropName.Name
        elif itemType == NetItemType.GLinkType:
            if itemId == 1 or itemId == 5 or itemId == 6:
                ref_outPropName.value = GraphicsItemPropName.Name

    # 过载父类方法，是否绘制车道中心线
    def isDrawLaneCenterLine(self, laneId):
        return True

    # 过载父类方法，是否绘制路段中心线
    def isDrawLinkCenterLine(self, linkId):
        if linkId == 1:
            return False
        else:
            return True




















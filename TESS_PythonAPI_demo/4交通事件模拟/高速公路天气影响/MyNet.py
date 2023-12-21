# -*- coding: utf-8 -*-

import os
from pathlib import Path
import sys

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from Tessng import TessInterface, TessPlugin, NetInterface, PyCustomerNet
from Tessng import tessngPlugin, tessngIFace, m2p, p2m
from Tessng import NetItemType, GraphicsItemPropName

# 用户插件子类，代表用户自定义与路网相关的实现逻辑，继承自MyCustomerNet
class MyNet(PyCustomerNet):
    def __init__(self):
        super(MyNet, self).__init__()
        self.text = False

    # 创建路网
    def createNet(self):
        # 代表TESS NG的接口
        iface = tessngIFace()
        # 代表TESS NG的路网子接口
        netiface = iface.netInterface()

        # 第一条路段
        startPoint = QPointF(m2p(-1000), 0)
        endPoint = QPointF(m2p(1000), 0)
        lPoint = [startPoint, endPoint]
        link1 = netiface.createLink(lPoint, 3, "双龙大道")
        if link1 is not None:
            # 在当前路段创建发车点
            dp = netiface.createDispatchPoint(link1)
            if dp != None :
                # 设置发车间隔，含车型组成、时间间隔、发车数
                dp.addDispatchInterval(1, 3600, 2000)

        # 设置场景宽度和高度
        netiface.setSceneSize(2000, 600)


    # 过载的父类方法，当打开网后TESS NG调用此方法
    #     实现的逻辑是：路网加载后获取路段数，如果路网数为0则调用方法createNet构建路网，之后再次获取路段数，如果大于0则启动仿真
    def afterLoadNet(self):
        # 代表TESS NG的接口
        iface = tessngIFace()
        # 代表TESS NG的路网子接口
        netiface = iface.netInterface()
        # 获取路段数
        count = netiface.linkCount()
        if(count == 0):
            self.createNet()

    def paint(self, itemType: int, itemId: int, painter):
        iface = tessngIFace()
        netiface = iface.netInterface()

        if not self.text:
            self.text = True

            scene = netiface.graphicsScene()
            failedItem = QGraphicsTextItem("从内侧到外侧，车道限速依次降低。")
            x, y = -300, 20
            failedItem.setPos(QPoint(x, y))
            failedItem.setFont(QFont("黑体", 20))
            failedItem.setDefaultTextColor(QColor(0, 0, 0))
            scene.addItem(failedItem)
        return True





















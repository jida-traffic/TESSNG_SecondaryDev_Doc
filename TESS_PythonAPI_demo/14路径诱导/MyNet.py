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

    # 过载的父类方法，当打开网后TESS NG调用此方法
    #     实现的逻辑是：路网加载后获取路段数，如果路网数为0则调用方法createNet构建路网，之后再次获取路段数，如果大于0则启动仿真
    def afterLoadNet(self):
        pass

    #是否允许用户对路网元素的绘制进行干预，如选择路段标签类型、确定绘制颜色等，本方法目的在于减少不必要的对python方法调用频次
    def isPermitForCustDraw(self):
        # 代表TESS NG的接口
        iface = tessngIFace()
        netface = iface.netInterface()
        netFileName = netface.netFilePath()
        if "Temp" in netFileName:
            return True
        else:
            return False



    ''' 过载的父类方法，在绘制路网元素时被调用，确定用ID或名称，以及字体大小绘制标签，也可确定不绘制标签
    itemType：NetItemType常量，代表不同类型路网元素
    itemId：路网元素的ID
    ref_outPropName：返回值，GraphicsItemPropName枚举类型，影响路段和连接段的标签是否被绘制
        GraphicsItemPropName。None_表示不绘制，GraphicsItemPropName。ID：表示绘制ID，GraphicsItemPropName。NAME:表示绘制名称
    ref_outFontSize，返回值，标签大小，单位：米。假设车道宽度是3.5米，如果ref_outFontSize.value等于7，绘制的标签大小占两个车道宽度
    '''
    def ref_labelNameAndFont(self, itemType, itemId, ref_outPropName, ref_outFontSize):
       pass

    # 过载父类方法，是否绘制车道中心线
    def isDrawLaneCenterLine(self, laneId):
        return True

    # 过载父类方法，是否绘制路段中心线
    def isDrawLinkCenterLine(self, linkId):
        if linkId == 1:
            return False
        else:
            return True




















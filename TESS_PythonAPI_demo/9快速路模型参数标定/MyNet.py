# -*- coding: utf-8 -*-

import os
from pathlib import Path
import sys

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

import Tessng
from Tessng import PyCustomerNet, TessInterface, TessPlugin, NetInterface, tngPlugin, tngIFace, m2p
from Tessng import NetItemType, GraphicsItemPropName

# 用户插件子类，代表用户自定义与路网相关的实现逻辑，继承自MyCustomerNet
class MyNet(PyCustomerNet):
    def __init__(self):
        super(MyNet, self).__init__()

    # 过载的父类方法，当打开网后TESS NG调用此方法
    #     实现的逻辑是：路网加载后获取路段数，如果路网数为0则调用方法createNet构建路网，之后再次获取路段数，如果大于0则启动仿真
    def afterLoadNet(self):
        # 代表TESS NG的接口
        iface = tngIFace()
        # 代表TESS NG的路网子接口
        netiface = iface.netInterface()

    #是否允许用户对路网元素的绘制进行干预，如选择路段标签类型、确定绘制颜色等，本方法目的在于减少不必要的对python方法调用频次
    def isPermitForCustDraw(self):
        # 代表TESS NG的接口
        iface = tngIFace()
        netface = iface.netInterface()
        netFileName = netface.netFilePath()
        if "Temp" in netFileName:
            return True
        else:
            return False






















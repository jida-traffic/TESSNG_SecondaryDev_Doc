# -*- coding: utf-8 -*-

import os
from pathlib import Path
import sys
import time
import json

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

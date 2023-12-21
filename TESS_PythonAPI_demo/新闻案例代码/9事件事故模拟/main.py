# -*- coding: utf-8 -*-
import os
from pathlib import Path
import sys

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from Tessng import *
from MyPlugin import *

if __name__ == '__main__':
    app = QApplication()

    workspace = os.fspath(Path(__file__).resolve().parent)
    config = {'__workspace':workspace,
              # 应急事件1-车辆事故
              '__netfilepath':"./Map/深圳皇岗路干道(局部路径).tess",
              # 应急事件2-应急车道开放
              # '__netfilepath':"./Map/上海内环武宁路汇入段_事故版.tess",
              '__simuafterload': False,
              '__custsimubysteps': False
              }
    plugin = MyPlugin()
    factory = TessngFactory()
    tessng = factory.build(plugin, config)
    if tessng is None:
        sys.exit(0)
    else:
        sys.exit(app.exec_())




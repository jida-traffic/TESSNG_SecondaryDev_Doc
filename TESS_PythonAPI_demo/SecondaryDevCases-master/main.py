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
              # '__netfilepath':"./TESSNGMap/SignalMap/佛山路网-加慢行-加信号灯-1107.tess", # 信控编辑及双环信控方案下发示例
              # '__netfilepath':"./TESSNGMap/FlowMap/路径加载案例-机动车交叉口.tess",
              '__netfilepath':"./TESSNGMap/ActionControlMap/动作控制案例-机动车交叉口.tess",
              # '__netfilepath':"./TESSNGMap/ControlMeasuresMap/上海内环武宁路汇入段.tess",
              # '__netfilepath':"./TESSNGMap/testMap/changan_university_ex1.tess",
              # '__netfilepath':"./TESSNGMap/testMap/szqlg_1205-简化版.tess",
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




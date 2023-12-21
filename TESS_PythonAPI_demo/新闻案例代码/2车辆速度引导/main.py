# -*- coding: utf-8 -*-
import os
from pathlib import Path
import sys
from PySide2.QtWidgets import QApplication

from Tessng import TessngFactory
from MyPlugin import MyPlugin

if __name__ == '__main__':
    app = QApplication()

    workspace = os.fspath(Path(__file__).resolve().parent)
    config = {'__workspace':workspace,
               '__netfilepath':"Data\\车速引导.tess",
              '__simuafterload': True,
              '__custsimubysteps': False
              }
    plugin = MyPlugin()
    factory = TessngFactory()
    tessng = factory.build(plugin, config)
    if tessng is None:
        sys.exit(0)
    else:
        sys.exit(app.exec_())




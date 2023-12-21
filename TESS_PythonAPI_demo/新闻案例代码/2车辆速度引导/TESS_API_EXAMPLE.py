# -*- coding: utf-8 -*-

import os
from pathlib import Path

from Tessng import *
from DockWidget import *


class TESS_API_EXAMPLE(QMainWindow):
    def __init__(self, parent = None):
        super(TESS_API_EXAMPLE, self).__init__(parent)
        self.ui = Ui_TESS_API_EXAMPLEClass()
        self.ui.setupUi(self)
        self.createConnect()

    def createConnect(self):
        self.ui.btnOpenNet.clicked.connect(self.openNet)
        self.ui.btnStartSimu.clicked.connect(self.startSimu)
        self.ui.btnPauseSimu.clicked.connect(self.pauseSimu)
        self.ui.btnStopSimu.clicked.connect(self.stopSimu)

    def openNet(self):
        iface = tngIFace()
        if not iface:
            return
        if iface.simuInterface().isRunning():
            QMessageBox.warning(None, "提示信息", "请先停止仿真，再打开路网")
            return
        custSuffix = "TESSNG Files (*.tess);;TESSNG Files (*.backup)"
        dbDir = os.fspath(Path(__file__).resolve().parent / "Data")
        selectedFilter = "TESSNG Files (*.tess)"
        options = QFileDialog.Options(0)
        netFilePath, filtr = QFileDialog.getOpenFileName(self, "打开文件", dbDir, custSuffix, selectedFilter, options)
        if netFilePath:
            iface.netInterface().openNetFle(netFilePath)

    def startSimu(self):
        iface = tngIFace()
        if not iface:
            return
        if not iface.simuInterface().isRunning() or iface.simuInterface().isPausing():
            iface.simuInterface().startSimu()

    def pauseSimu(self):
        iface = tngIFace()
        if not iface:
            return
        if iface.simuInterface().isRunning():
            iface.simuInterface().pauseSimu()

    def stopSimu(self):
        iface = tngIFace()
        if not iface:
            return
        if iface.simuInterface().isRunning():
            iface.simuInterface().stopSimu()

    def showRunInfo(self, runInfo):
        self.ui.txtMessage.clear()
        self.ui.txtMessage.setText(runInfo)

    def isOk(self):
        QMessageBox.information(None, "提示信息", "is ok!")


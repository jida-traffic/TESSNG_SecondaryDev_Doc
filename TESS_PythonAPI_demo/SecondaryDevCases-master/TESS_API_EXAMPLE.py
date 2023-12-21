# -*- coding: utf-8 -*-

import os
from pathlib import Path
import sys

from DockWidget import *
from Tessng import *

from MyNet import MyNet
from SecondaryDevelopmentCases import SecondaryDevCases


class TESS_API_EXAMPLE(QMainWindow):
    def __init__(self, parent=None):
        super(TESS_API_EXAMPLE, self).__init__(parent)
        self.ui = Ui_TESS_API_EXAMPLEClass()
        self.ui.setupUi(self)
        self.createConnect()
        # 初始化二次开发对象
        self.secondary_dev = SecondaryDevCases(3)
        self.planNumber = 0

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
        # 测试双环信控方案下发
        self.secondary_dev.double_ring_signal_control_test(self.planNumber)
        self.planNumber += 1
        # QMessageBox.information(None, "提示信息", "is ok!")

    def editPhaseExample(self):
        self.secondary_dev.control_Measures(3)

    def updateLinkLimitSpeed(self):
        self.secondary_dev.control_Measures(5)

    def start_simulation(self):
        self.secondary_dev.process_control(1)

    def pause_simulation(self):
        self.secondary_dev.process_control(2)

    def stop_simulation(self):
        self.secondary_dev.process_control(3)

    def restore_simulation(self):
        self.secondary_dev.process_control(4)

    def generate_snapshot(self):
        self.secondary_dev.process_control(5)

    def find_vehiInLinkOrLane_information(self):
        self.secondary_dev.process_control(8.2)

    def find_vehicle_infomation(self):
        self.secondary_dev.process_control(8.3)
    def set_simulation_accuracy(self):
        self.secondary_dev.process_control(10)
    def set_simulation_interval(self):
        self.secondary_dev.process_control(11)
    def set_simulation_AcceMutiples(self):
        self.secondary_dev.process_control(12)

    # 动作控制
    def CalcDynaDispatchParametersExample(self):
        self.secondary_dev.action_control(1)
    def moveVehiExample(self):
        self.secondary_dev.action_control(2)
    def setVehiSpeedExample(self):
        self.secondary_dev.action_control(3)
    def setVehiRoutingExample(self):
        self.secondary_dev.action_control(4)
    def forceVehiDontChangeLaneExample(self):
        self.secondary_dev.action_control(5)
    def forceVehiChangeLaneExample(self):
        self.secondary_dev.action_control(6)
    def runRedLightExample(self):
        self.secondary_dev.action_control(7)
    def stopVehiExample(self):
        self.secondary_dev.action_control(8)
    def setVehiAngleExample(self):
        self.secondary_dev.action_control(9)
    def SetVehiParkExample(self):
        self.secondary_dev.action_control(10)
    def cancelSetVehiExample(self):
        self.secondary_dev.action_control(0)
# -*- coding: utf-8 -*-

from PySide2.QtGui import *
from PySide2.QtWidgets import *

from Tessng import TessPlugin
from MyNet import *
from MySimulator import *
from TESS_API_EXAMPLE import *
from SecondaryDevelopmentCases import SecondaryDevCases

# 用户插件，继承自TessPlugin
class MyPlugin(TessPlugin):
    def __init__(self):
        super(MyPlugin, self).__init__()
        self.mNetInf = None
        self.mSimuInf = None

    def initGui(self):
        # 在TESS NG主界面上增加 QDockWidget对象
        self.examleWindow = TESS_API_EXAMPLE()

        iface = tessngIFace()
        win = iface.guiInterface().mainWindow()

        dockWidget = QDockWidget("自定义与TESS NG交互界面", win)
        dockWidget.setObjectName("mainDockWidget")
        dockWidget.setFeatures(QDockWidget.NoDockWidgetFeatures)
        dockWidget.setAllowedAreas(Qt.LeftDockWidgetArea)
        dockWidget.setWidget(self.examleWindow.centralWidget())
        iface.guiInterface().addDockWidgetToMainWindow(Qt.DockWidgetArea(1), dockWidget)

        # 增加菜单及菜单项
        menuBar = iface.guiInterface().menuBar()
        menu = QMenu(menuBar)
        menu.setObjectName("menuExample")
        menuBar.addAction(menu.menuAction())
        menu.setTitle("双环信控方案下发测试")
        actionOk = menu.addAction("更改为下一方案")
        actionOk.setCheckable(False)
        actionOk.triggered.connect(self.examleWindow.isOk)

        # 动作控制菜单及菜单项
        menu_actionContorl = QMenu(menuBar)
        menu_actionContorl.setObjectName("menuActionContorlExample")
        menuBar.addAction(menu_actionContorl.menuAction())
        menu_actionContorl.setTitle("动作控制")

        actionCalcDynaDispatchParameters = menu_actionContorl.addAction("动态修改发车流量测试(L5路段发车点)")
        actionCalcDynaDispatchParameters.setCheckable(False)
        actionCalcDynaDispatchParameters.triggered.connect(self.examleWindow.CalcDynaDispatchParametersExample)

        actionMoveVehi = menu_actionContorl.addAction("车辆移动测试(L5路段)")
        actionMoveVehi.setCheckable(False)
        actionMoveVehi.triggered.connect(self.examleWindow.moveVehiExample)

        actionSetVehiSpeed = menu_actionContorl.addAction("车辆速度设置测试(L5路段)")
        actionSetVehiSpeed.setCheckable(False)
        actionSetVehiSpeed.triggered.connect(self.examleWindow.setVehiSpeedExample)

        actionSetVehiRouting = menu_actionContorl.addAction("修改车辆路径测试(L1路段)")
        actionSetVehiRouting.setCheckable(False)
        actionSetVehiRouting.triggered.connect(self.examleWindow.setVehiRoutingExample)

        actionForceVehiDontChangeLane = menu_actionContorl.addAction("强制车辆不变道(禁止车辆变道到最右侧车道)")
        actionForceVehiDontChangeLane.setCheckable(False)
        actionForceVehiDontChangeLane.triggered.connect(self.examleWindow.forceVehiDontChangeLaneExample)

        actionForceVehiChangeLane = menu_actionContorl.addAction("强制车辆变道(最右侧车辆左变道)")
        actionForceVehiChangeLane.setCheckable(False)
        actionForceVehiChangeLane.triggered.connect(self.examleWindow.forceVehiChangeLaneExample)

        actionRunRedLight = menu_actionContorl.addAction("强制车辆闯红灯(L12路段概率闯红灯)")
        actionRunRedLight.setCheckable(False)
        actionRunRedLight.triggered.connect(self.examleWindow.runRedLightExample)

        actionStopVehi = menu_actionContorl.addAction("清除L12车辆")
        actionStopVehi.setCheckable(False)
        actionStopVehi.triggered.connect(self.examleWindow.stopVehiExample)

        actionSetVehiAngle = menu_actionContorl.addAction("设置L5车辆航向角(45度)")
        actionSetVehiAngle.setCheckable(False)
        actionSetVehiAngle.triggered.connect(self.examleWindow.setVehiAngleExample)

        actionSetVehiPark = menu_actionContorl.addAction("设置车辆停车(L5)")
        actionSetVehiPark.setCheckable(False)
        actionSetVehiPark.triggered.connect(self.examleWindow.SetVehiParkExample)

        actionCancelSetVehi = menu_actionContorl.addAction("取消车辆控制")
        actionCancelSetVehi.setCheckable(False)
        actionCancelSetVehi.triggered.connect(self.examleWindow.cancelSetVehiExample)


        # 二次开发管控手段控制示例菜单
        menu_controlMeasures = QMenu(menuBar)
        menu_controlMeasures.setObjectName(" menuControlMeasuresExample")
        menuBar.addAction(menu_controlMeasures.menuAction())
        menu_controlMeasures.setTitle("管控手段控制")
        actionEditPhase = menu_controlMeasures.addAction("修改相位示例")
        actionEditPhase.setCheckable(False)
        actionEditPhase.triggered.connect(self.examleWindow.editPhaseExample)
        actionEditPhase = menu_controlMeasures.addAction("修改路段最高限速示例")
        actionEditPhase.setCheckable(False)
        actionEditPhase.triggered.connect(self.examleWindow.updateLinkLimitSpeed)

        # 二次开发流程控制示例菜单
        menu_process_control = QMenu(menuBar)
        menu_process_control.setObjectName(" menuControlMeasuresExample")
        menuBar.addAction(menu_process_control.menuAction())
        menu_process_control.setTitle("流程控制")
        action_startSimu = menu_process_control.addAction("启动仿真")
        action_startSimu.setCheckable(False)
        action_startSimu.triggered.connect(self.examleWindow.start_simulation)
        action_pauseSimu = menu_process_control.addAction("暂停仿真")
        action_pauseSimu.setCheckable(False)
        action_pauseSimu.triggered.connect(self.examleWindow.pause_simulation)
        action_stopSimu = menu_process_control.addAction("停止仿真")
        action_stopSimu.setCheckable(False)
        action_stopSimu.triggered.connect(self.examleWindow.stop_simulation)
        action_restoreSimu = menu_process_control.addAction("恢复仿真")
        action_restoreSimu.setCheckable(False)
        action_restoreSimu.triggered.connect(self.examleWindow.restore_simulation)
        action_GenerateSnapshot = menu_process_control.addAction("生成仿真快照")
        action_GenerateSnapshot.setCheckable(False)
        action_GenerateSnapshot.triggered.connect(self.examleWindow.generate_snapshot)
        action_findVehiInLinkOrLaneInfo = menu_process_control.addAction("查询路段或车道车辆示例")
        action_findVehiInLinkOrLaneInfo.setCheckable(False)
        action_findVehiInLinkOrLaneInfo.triggered.connect(self.examleWindow.find_vehiInLinkOrLane_information)
        action_findVehiInfo = menu_process_control.addAction("查询车辆信息示例")
        action_findVehiInfo.setCheckable(False)
        action_findVehiInfo.triggered.connect(self.examleWindow.find_vehicle_infomation)
        action_setSimuAccuracy = menu_process_control.addAction("设置仿真精度示例")
        action_setSimuAccuracy.setCheckable(False)
        action_setSimuAccuracy.triggered.connect(self.examleWindow.set_simulation_accuracy)
        action_setSimuInterval = menu_process_control.addAction("设置仿真时长示例")
        action_setSimuInterval.setCheckable(False)
        action_setSimuInterval.triggered.connect(self.examleWindow.set_simulation_interval)
        action_setSimuAcceMutiples = menu_process_control.addAction("设置仿真加速比示例")
        action_setSimuAcceMutiples.setCheckable(False)
        action_setSimuAcceMutiples.triggered.connect(self.examleWindow.set_simulation_AcceMutiples)

    # 过载父类方法，在 TESS NG工厂类创建TESS NG对象时调用
    def init(self):
        self.secondary_dev = SecondaryDevCases(1)
        self.initGui()
        self.mNetInf = MyNet(self.secondary_dev)
        self.mSimuInf = MySimulator(self.secondary_dev)
        self.mSimuInf.signalRunInfo.connect(self.examleWindow.showRunInfo)
        iface = tngIFace()
        win = iface.guiInterface().mainWindow()
        # 将信号mSimuInf.forReStopSimu关联到主窗体的槽函数doStopSimu，可以借安全地停止仿真运行
        self.mSimuInf.forStopSimu.connect(win.doStopSimu, Qt.QueuedConnection)
        # 将信号mSimuInf.forReStartSimu关联到主窗体的槽函数doStartSimu，可以借此实现自动重复仿真
        self.mSimuInf.forReStartSimu.connect(win.doStartSimu, Qt.QueuedConnection)

    # 过载父类方法，返回插件路网子接口，此方法由TESS NG调用
    def customerNet(self):
        return self.mNetInf

    # 过载父类方法，返回插件仿真子接口，此方法由TESS NG调用
    def customerSimulator(self):
        return self.mSimuInf

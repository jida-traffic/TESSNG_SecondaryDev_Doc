# -*- coding: utf-8 -*-

from PySide2.QtWidgets import QDockWidget
from Tessng import TessPlugin
from MyNet import *
#from MySimulator_cv_platoon import *
from MySimulator_cv_merge import *
from TESS_API_EXAMPLE import *

# 用户插件，继承自TessPlugin
class MyPlugin(TessPlugin):
    def __init__(self):
        super(MyPlugin, self).__init__()
        self.mNetInf = None
        self.mSimuInf = None

    def initGui(self):
        # 在TESS NG主界面上增加 QDockWidget对象
        self.examleWindow = TESS_API_EXAMPLE()

        iface = tngIFace()
        win = iface.guiInterface().mainWindow()

        dockWidget = QDockWidget("自定义与TESS NG交互界面", win)
        dockWidget.setObjectName("mainDockWidget")
        dockWidget.setFeatures(QDockWidget.NoDockWidgetFeatures)
        dockWidget.setAllowedAreas(Qt.LeftDockWidgetArea)
        dockWidget.setWidget(self.examleWindow.centralWidget())
        iface.guiInterface().addDockWidgetToMainWindow(Qt.DockWidgetArea(1), dockWidget)

    # 过载父类方法，在 TESS NG工厂类创建TESS NG对象时调用
    def init(self):
        self.initGui()
        self.mNetInf = MyNet()
        self.mSimuInf = MySimulator()
        self.mSimuInf.signalRunInfo.connect(self.examleWindow.showRunInfo)
        iface = tngIFace()
        win = iface.guiInterface().mainWindow()
        #将信号mSimuInf.forReStartSimu关联到主窗体的槽函数doStartSimu，可以借实现自动重复仿真
        self.mSimuInf.forReStartSimu.connect(win.doStartSimu, Qt.QueuedConnection)

    # 过载父类方法，返回插件路网子接口，此方法由TESS NG调用
    def customerNet(self):
        return self.mNetInf

    #过载父类方法，返回插件仿真子接口，此方法由TESS NG调用
    def customerSimulator(self):
        return self.mSimuInf

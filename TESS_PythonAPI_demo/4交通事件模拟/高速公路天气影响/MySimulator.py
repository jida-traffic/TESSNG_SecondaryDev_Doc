from PySide2.QtCore import *
from Tessng import *


class MySimulator(QObject, PyCustomerSimulator):
    signalRunInfo = Signal(str)
    forStopSimu = Signal()
    forReStartSimu = Signal()

    def __init__(self):
        QObject.__init__(self)
        PyCustomerSimulator.__init__(self)

        # 车辆抛锚所在车道（从右向左，从0开始）
        self.stop_laneNumber = 1
        self.stop_vehicle = None

    # 仿真前执行
    def ref_beforeStart(self, ref_keepOn):
        iface = tessngIFace()
        simuiface = iface.simuInterface()
        # 设置仿真倍速
        simuiface.setAcceMultiples(1)
        # 设置仿真精度
        simuiface.setSimuAccuracy(10)
        ref_keepOn.value = True

    # 重新计算期望速度
    def ref_reCalcdesirSpeed(self, vehi, ref_desirSpeed):
        laneNumber = vehi.vehicleDriving().laneNumber()
        if laneNumber == 0:
            ref_desirSpeed.value = 120 * (1-0.35)
            return True
        elif laneNumber == 1:
            ref_desirSpeed.value = 120 * (1-0.25)
            return True
        elif laneNumber == 2:
            ref_desirSpeed.value = 120 * (1-0.15)
            return True
        return False

    # TESS NG 在每个计算周期结束后调用此方法
    def afterOneStep(self):
        # TESSNG 顶层接口
        iface = tessngIFace()
        # TESSNG 仿真子接口
        simuiface = iface.simuInterface()
        # 当前仿真计算批次
        batchNum = simuiface.batchNumber()
        # 当前已仿真时间，单位：毫秒
        simuTime = simuiface.simuTimeIntervalWithAcceMutiples()

        # 当前正在运行车辆列表
        lAllVehi = simuiface.allVehiStarted()

        #每20个计算批次做一次小计，将结果通过信号发送出云
        if batchNum % 20 == 0:
            strVehiCount = str(len(lAllVehi))
            strSimuTime = str(simuTime)
            runInfo = f"运行车辆数：{strVehiCount}\n仿真时间：{strSimuTime}(毫秒)"
            self.signalRunInfo.emit(runInfo)




















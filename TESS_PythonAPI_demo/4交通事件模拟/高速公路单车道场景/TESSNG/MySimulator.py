from PySide2.QtCore import *
from DLLs.Tessng import *


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
        simuiface.setAcceMultiples(10)
        # 设置仿真精度
        simuiface.setSimuAccuracy(10)
        ref_keepOn.value = True

    # 重新计算期望速度
    def ref_reCalcdesirSpeed(self, vehi, ref_desirSpeed):
        iface = tessngIFace()
        simuiface = iface.simuInterface()
        # 当前仿真时间：毫秒
        simuTime = simuiface.simuTimeIntervalWithAcceMutiples()

        # 如果时间大于某个值
        if simuTime > 100 * 1000:
            # 如果车辆在抛锚车道
            if vehi.vehicleDriving().laneNumber() == self.stop_laneNumber:
                vdd = p2m(vehi.vehicleDriving().getVehiDrivDistance())
                # 如果车辆在1000m位置处
                if 1000-10 < vdd < 1000+10:
                    # 期望速度设为0
                    ref_desirSpeed.value = 0
                    self.stop_vehicle = vehi
                    vehi.setColor("#FF0000")
                    return True
        return False

    # 计算车辆当前限制车道序号列表
    def calcLimitedLaneNumber(self, vehi):
        # 如果有车抛锚，本车在抛锚车道
        if self.stop_vehicle and vehi.vehicleDriving().laneNumber() == 1 and vehi.id() != self.stop_vehicle.id():
            vdd = p2m(vehi.vehicleDriving().getVehiDrivDistance())
            vdd_stop_vehicle = p2m(self.stop_vehicle.vehicleDriving().getVehiDrivDistance())
            # 如果与抛锚车辆的间距在一定范围内
            if 1 < (vdd_stop_vehicle - vdd) < 500 and vehi.currSpeed() <= 60:
                return [self.stop_laneNumber]
        return []

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
            strSimuTime = str(simuTime/1000)
            runInfo = f"运行车辆数：{strVehiCount}\n仿真时间：{strSimuTime}(秒)"
            self.signalRunInfo.emit(runInfo)




















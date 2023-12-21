from PySide2.QtCore import *
from Tessng import *
import random
from datetime import datetime

# 标记当前是否需要进行动态车道管理
needToApply = True
# 设定ML与GL车道的目标速度差
speedDiffRate = 0.1

# # GL拟合曲线的函数需要的4个参数（采用Van Aerde模型拟合函数）  # Van Aerde模型更适合拟合城市快速路基本图
# Kj_GL = 27.11       # 普通车道的阻塞密度（veh/km）
# Qc_GL = 2047.0      # 普通车道的通行能力
# Vf_GL = 80.19       # 普通车道的自由流速度
# Vm_GL = 59.05       # 普通车道的最大流量对应的速度（最佳车速）
#
# # ML拟合曲线的函数需要的4个参数（采用Van Aerde模型拟合函数）
# Kj_ML = 12.97       # 管控车道的阻塞密度（veh/km）
# Qc_ML = 1991.0      # 管控车道的通行能力
# Vf_ML = 78.73       # 管控车道的自由流速度
# Vm_ML = 57.6        # 管控车道的最大流量对应的速度（最佳车速）

# GL拟合曲线的函数需要的4个参数（采用Van Aerde模型拟合函数）  # Van Aerde模型更适合拟合城市快速路基本图
Kj_GL = 56       # 普通车道的阻塞密度（veh/km）
Qc_GL = 1680      # 普通车道的通行能力
Vf_GL = 71.14       # 普通车道的自由流速度
Vm_GL = 39       # 普通车道的最大流量对应的速度（最佳车速）

# ML拟合曲线的函数需要的4个参数（采用Van Aerde模型拟合函数）
Kj_ML = 50       # 管控车道的阻塞密度（veh/km）
Qc_ML = 1680     # 管控车道的通行能力
Vf_ML = 72       # 管控车道的自由流速度
Vm_ML = 40       # 管控车道的最大流量对应的速度（最佳车速）

def SpeedFlowFunction(x, kj, qc, vf, vm):
    """
    Van Aerde模型拟合函数 X是速度 Y是流量 \n
    表达式： k=1/(C1+C2/(Vf-v)+C3*v)    自变量是速度v 因变量是密度k \n
    将表达式两边乘上v 得到 Q-V的函数：
    表达式： q=v/(C1+C2/(Vf-v)+C3*v)    自变量是速度v 因变量是流量q \n
    :param x: 速度
    :param kj: 阻塞密度Kj
    :param qc: 通行能力Qc
    :param vf: 自由流速度Vf
    :param vm: 最佳车速Vm
    :return: y: 流量
    """
    C1 = vf / (kj * vm * vm) * (2.0 * vm - vf)
    C2 = vf / (kj * vm * vm) * (vf - vm) * (vf - vm)
    C3 = (1.0 / qc) - vf / (kj * vm * vm)
    # y = x / (C1 + C2 / (vf - x) + C3 * x)
    y = x / (C1 + C2 / (abs(vf - x) + 0.1) + C3 * x)
    return y


# 根据拟合出来的表达式 由流量反推出当前速度（反解方程） X为速度 Y为流量
def CalcSpeedbyFlow(Y, isGL=True, getBigX=True):
    Kj = Kj_GL  # 普通车道的阻塞密度
    Qc = Qc_GL  # 普通车道的通行能力
    Vf = Vf_GL  # 普通车道的自由流速度
    Vm = Vm_GL  # 普通车道的最佳速度（最大通行能力对应的速度）

    if not isGL:  # 即为ML，管控车道
        Kj = Kj_ML
        Qc = Qc_ML
        Vf = Vf_ML
        Vm = Vm_ML

    xList = range(55, 75)  # 速度区间，设为45km/h~74km/h
    if getBigX:  # 因为速度——流量曲线是有拐点的，分为上下两半支曲线 存在一个流量对应两个速度的情况
        # 所以用getBigX这个参数来标记是取大的那个速度还是小的那个速度→默认getBigX=True：取大的速度
        for x in reversed(xList):  # v-q曲线上半支：速度从大到小，对应的流量从小到大，一点点看流量能增加到多少；
            y = SpeedFlowFunction(x, Kj, Qc, Vf, Vm)  # 由Van Aerde函数拟合出的流量
            if y >= Y:  # Y：当前流量 y＞=Y时该车道可以增加流量（？）
                return x
    else:  # 如果是取曲线下半支的速度
        for x in xList:  # v-q曲线上半支：速度从小到大，对应的流量也是从小到大，一点点看流量能增加到多少；
            y = SpeedFlowFunction(x * 1.0, Kj, Qc, Vf, Vm)  # 由Van Aerde函数拟合出的流量
            if y >= Y:  # Y：当前流量，y＞=Y时该车道可以增加流量
                return x
    # 如果根据以上过程还是搜索不到合适的x值（速度值），说明这个流量不在这条曲线上（超过这条曲线了，曲线上找不到任何一个比这个流量还高的点）
    # 那就要遍历整条曲线 找到最接近的那个点(其实就是曲线的顶点了，因为只有顶点的通过量是最大的，最接近给定流量)
    topX = 0
    for x in xList:  # 遍历，初始化为topX=0,即速度为0的情况，此时SpeedFlowFunction()输出的流量也为0（?）
        if SpeedFlowFunction(x * 1.0, Kj, Qc, Vf, Vm) >= SpeedFlowFunction(topX * 1.0, Kj, Qc, Vf, Vm):
            topX = x
    # 在 45 - 75 之间找到最佳速度?
    return topX


# 用户插件子类，代表用户自定义与仿真相关的实现逻辑，继承自PyCustomerSimulator
#   多重继承中的父类QObject，在此目的是要能够自定义信号signlRunInfo
class MySimulator(QObject, PyCustomerSimulator):
    def __init__(self):
        QObject.__init__(self)
        PyCustomerSimulator.__init__(self)
        self.Q_GL = 0
        self.V_GL = 0       # 普通车道的速度，是三根车道的平均值

        self.Q_ML = 0
        self.V_ML = 0

        self.Q6 = 0
        self.Q7 = 0
        self.Q8 = 0

        self.V6 = 0
        self.V7 = 0
        self.V8 = 0

        self.MLSpeed = 0
        self.GLSpeed = 0

        self.MLFlow = 0
        self.GLFlow = 0

        self.solutionMLFlow = 0
        self.solutionGLFlow = 0

        self.solutionMLSpeed = 0
        self.solutionGLSpeed = 0

        self.tempSpeedDiffRate = 0
        self.solutionSpeedDiffRate = 0
        self.solutionProductivity = 0
        self.AllowVehsFlow = 0

        self.speedDiffRate = 0

        self.V_GL1 = 0
        self.V_GL2 = 0
        self.V_GL3 = 0
        # 变道开关
        # 普通车道需要变到管控车道
        self.GL2ML = 0
        # 管控车道需要变到普通车道
        self.ML2GL = 0
        # 变道累积
        self.count = 0
        self.managedcars = []
        # 记录需要强制换道的车辆ID
        # 当这些车辆需要换道时，提高车速
        self.Cars = []

    # 过载的父类方法， 初始化车辆，在车辆启动上路时被TESS NG调用一次
    def initVehicle(self, vehi):  # vehi: 车辆ID，不含首位数
        iface = tngIFace()
        simuIFace = iface.simuInterface()
        simuTime = simuIFace.simuTimeIntervalWithAcceMutiples()   # simuTime = 1000→1s
        tmpId = vehi.id() % 100000
        if vehi.vehicleTypeCode() == 13:
            vehi.setColor("Green")

    # 重写调用频次，每分钟修改一次车辆的限制车道
    def setStepsPerCall(self, vehi):
        iface = tessngIFace()
        netface = iface.netInterface()
        #计算限制车道方法被调用频次
        # vehi.setSteps_calcLimitedLaneNumber(steps = 20 * 60)
        # #重新计算是否可以左强制变道方法被调用频次
        # vehi.setSteps_reCalcToLeftLane(steps = 20)
        # #重新计算是否可以右强制变道方法被调用频次
        # vehi.setsteps_reCalcToRightLane(steps = 20)
        # #重新计算是否可以左自由变道方法被调用频次
        # vehi.setsteps reCalcToLeftFreely(steps
        # # 重新计算是否可以右自由变道方法被调用频次
        # vehi.setsteps reCalcToRightFreely(steps
        pass

    def calcLimitedLaneNumber(self, pIVehicle):
        iface = tngIFace()
        simuiface = iface.simuInterface()
        batchNum = simuiface.batchNumber()
        GL_list = [0, 1, 2]  # GL车道编号
        ML_list = [3]  # ML车道编号
        # 行驶距离大于 1049 小于 1433
        dist = p2m(pIVehicle.vehicleDriving().getVehiDrivDistance())  # 车辆已经行驶距离（单位：像素 -> 转为米）
        # ---进入管控区域前---
        # 针对普通车
        if dist<=800 and pIVehicle.vehicleTypeCode() != 13 and pIVehicle.vehicleDriving().laneNumber() == 3:
            pIVehicle.vehicleDriving().toRightLane()
            return ML_list
        # 针对EV车
        if pIVehicle.vehicleTypeCode() == 13 :
            if pIVehicle.vehicleDriving().laneNumber() != 3 :
                pIVehicle.vehicleDriving().toLeftLane()
            return GL_list
        # ---管控区域---
        # 针对非EV车
        else:
            if self.ML2GL:
                # 针对管控车道的车，选择一定数量换道至普通车道
                if pIVehicle.vehicleDriving().laneNumber() == 3:
                    if self.count * 60 < self.AllowVehsFlow:
                        pIVehicle.setColor("Red")
                        self.count += 1
                        print("count:", self.count)
                        return ML_list
                    else:
                        return []
                # 针对普通车道的车，禁止进入管控车道
                else:
                    return ML_list
            elif self.GL2ML:
                if self.count * 60 <= self.AllowVehsFlow and pIVehicle.vehicleDriving().laneNumber() == 2 and dist<=1227:
                    pIVehicle.setColor("Red")
                    self.Cars.append(pIVehicle.id())
                    pIVehicle.vehicleDriving().toLeftLane()
                    self.managedcars.append(pIVehicle.id())
                    self.count += 1
                    print("count:", self.count)
                    return GL_list
                elif pIVehicle.id() in self.managedcars:
                    return GL_list
                else:
                    return ML_list
            else:
                return ML_list


            # if (pIVehicle.roadId() == 3 or pIVehicle.roadId() == 7) and 1227 >= dist:   # 管控段为[1046,1427]
            # # ev车如果不在管控车道，就去管控车道，ML饱和流量？
            # # if pIVehicle.vehicleTypeCode() == 13:
            # #     if pIVehicle.vehicleDriving().laneNumber() != 3:
            # #         self.Cars.append(pIVehicle.id())
            # #     return GL_list
            # # else:
            #     # 变道信号多久刷新？
            #     # 算出一小时需要变出多少车，这里还需要精准控制，X时间内变出求得值的车辆数
            #     #if batchNum % (20 * 60) == 0:
            #     if self.ML2GL :
            #         # 针对管控车道的车，选择相应数量的车强制换道到普通车道，其它车不管控
            #         if pIVehicle.vehicleDriving().laneNumber() == 3:
            #             if self.count * 60 < self.AllowVehsFlow:
            #                 pIVehicle.setColor("Red")
            #                 self.count += 1
            #                 print("count:", self.count)
            #                 return ML_list
            #             else:
            #                 return []
            #         # 针对普通车道的车，禁止进入管控车道
            #         else:
            #             return ML_list
            #
            #     elif self.GL2ML and self.count * 60 < self.AllowVehsFlow and pIVehicle.vehicleDriving().laneNumber() == 2:
            #         pIVehicle.setColor("Red")
            #         self.Cars.append(pIVehicle.id())
            #         self.count += 1
            #         print("count:", self.count)
            #         return GL_list
            #     else:
            #         return []
            # else:
            #     return []


    # 过载的父类方法，TESS NG 在每个计算周期结束后调用此方法，大量用户逻辑在此实现，注意耗时大的计算要尽可能优化，否则影响运行效率
    def afterOneStep(self):
        iface = tngIFace()
        simuiface = iface.simuInterface()
        batchNum = simuiface.batchNumber()
        # 获取当前仿真时间完成穿越采集器的所有车辆信息
        # lVehiInfo = simuiface.getVehisInfoCollected()
        # 获取最近集计时间段内采集器采集的所有车辆集计信息
        lVehisInfoAggr = simuiface.getVehisInfoAggregated()
        if len(lVehisInfoAggr) > 0:
            for vinfo in lVehisInfoAggr:
                # ML车道起点处采集器编号为13
                if vinfo.collectorId == 17:
                    # 集计时间(180s)内过ML检测器的车流量和平均速度，单位：veh/h
                    self.Q_ML = vinfo.vehiCount * 60
                elif vinfo.collectorId == 18:
                    self.Q6 = vinfo.vehiCount * 60
                    self.V6 = vinfo.avgSpeed
                elif vinfo.collectorId == 19:
                    self.Q7 = vinfo.vehiCount * 60
                    self.V7 = vinfo.avgSpeed
                elif vinfo.collectorId == 20:
                    self.Q8 = vinfo.vehiCount * 60
                    self.V8 = vinfo.avgSpeed
                elif vinfo.collectorId == 25:
                    self.V_ML = vinfo.avgSpeed
                    print("speed_ML:",self.V_ML)

                # 断面2
                elif vinfo.collectorId == 24:
                    self.V_GL1 = vinfo.avgSpeed
                elif vinfo.collectorId == 23:
                    self.V_GL2 = vinfo.avgSpeed
                elif vinfo.collectorId == 22:
                    self.V_GL3 = vinfo.avgSpeed

                elif vinfo.collectorId == 21:
                    self.V_ML_out = vinfo.avgSpeed

            self.Q_GL = (self.Q6 + self.Q7 + self.Q8)/3
            self.V_GL = (self.V6 + self.V7 + self.V8)/3         # 检测器来的
            print("speed_GL:", self.V_GL)

            print("speed_ML_out:", self.V_ML_out)
            print("speed_GL_out:",(self.V_GL1+self.V_GL2+self.V_GL3)/3)
        # 随便打印看看检测器的值
        # if batchNum % 100 == 0:
        #     print("普通车道的速度和流量", self.Q_GL, self.V_GL)
        #     print("管控车道的速度和流量", self.Q_ML, self.V_ML)

        # 流量计算取2分钟时检测到的流量数据，这里是在预热（让车跑满路网）
        if batchNum == (20 * 60 * 2):
            # 目前是瞬时的，是否需要求过去5分钟的一个均值？用于计算变道信号
            # MLFlow是一分钟刷新一次
            self.MLFlow = self.Q_ML
            self.GLFlow = self.Q_GL
            #print("管控车道的流量", self.MLFlow)
            #print("普通车道的流量", self.GLFlow)

        # 这里是在不断刷新self.MLFlow、self.GLFlow，作为计算依据，这里要查看检测器的集记时间设置，目前是60秒刷新一次
        if batchNum % (20 * 60 ) == 0:
            # 目前是瞬时的，是否需要求过去5分钟的一个均值？用于计算变道信号
            # MLFlow是一分钟刷新一次
            self.MLFlow = self.Q_ML
            self.GLFlow = self.Q_GL
            self.count = 0
            print("管控车道的流量", self.MLFlow)
            print("普通车道的流量", self.GLFlow)

        # 此处先进行判断：是否两种车道都处在良好的状态？是的话就完全不需要进行车道管理  这里给定一个标准 GL的速度如果在65km/h以上，就不需要执行操作
        # vissim 代码中needToApply并没有作为判断条件
        # if self.V_GL > 65.0:
        #     needToApply = False
        #     if batchNum % (20 * 10):
        #         print("GL State is good, no need to manage.")
        # else:
        #     needToApply = True

        # vissim 代码中getBig并没有作为判断条件
        # getBig = True  # getBig参数用来标记 GL的情况 速度高还是低
        # if self.V_GL < Vm_GL:  # 根据采集到的GL速度数据，判断GL当前情况是处于通畅还是拥堵（对应于基本图的上半支还是下半支） 速度小于Vm 那就是下半支
        #     getBig = False

        # 变道信号刷新频率是根据 self.MLFlow（1分钟）、self.GLFlow（1分钟）、self.V_ML（10s刷新一次）、self.V_GL（1分钟刷新一次）这四个值的刷新频率来的
        # 这里会根据速度差算出变道信号
        if batchNum % (20 * 60 * 3) == 0:
            # 初始化
            self.ML2GL = 0
            self.GL2ML = 0
            if self.V_GL != 0 and self.MLFlow != 0 and self.GLFlow != 0:
                self.speedDiffRate = (self.V_ML - self.V_GL) / self.V_GL
                # print("当前速度差是{}".format(self.speedDiffRate))
                # 管控车道状态良好，运行其他普通车辆进入
                if (self.V_ML - self.V_GL) / self.V_GL > speedDiffRate:
                    # 然后开始由当前GL上的流量递减 以30veh/h 为步长 GL每减少30veh/h，ML就增加30*3=90veh/h
                    # for i in range(1000):
                    while(self.MLFlow<=3600 and self.GLFlow>=0):
                        self.MLFlow += 90
                        self.GLFlow -= 30
                        # 当前流量对应的速度
                        print(self.MLFlow)
                        self.MLSpeed = CalcSpeedbyFlow(self.MLFlow, isGL=False, getBigX=True)
                        self.GLSpeed = CalcSpeedbyFlow(self.GLFlow, isGL=True, getBigX=True)
                        print("calculating_MLSpeed:",self.MLSpeed,"calculating_GLSpeed:",self.GLSpeed)
                        # 然后检查速度差是否满足标准
                        self.tempSpeedDiffRate = (self.MLSpeed - self.GLSpeed) / self.GLSpeed
                        if self.tempSpeedDiffRate <= speedDiffRate:  # 如果速度差满足了标准 那么就给出结果 并结束循环
                            self.solutionMLFlow = int(self.MLFlow) - 90  # solutionMLFlow：算法算出的ML流量应该为多少
                            self.solutionGLFlow = int(self.GLFlow) + 30  # solutionGLFlow：算法算出的一条GL流量应该为多少
                            self.solutionMLSpeed = CalcSpeedbyFlow(self.solutionMLFlow, isGL=False)
                            self.solutionGLSpeed = CalcSpeedbyFlow(self.solutionGLFlow)
                            self.solutionSpeedDiffRate = (self.solutionMLSpeed - self.solutionGLSpeed) / self.solutionGLSpeed
                            # 以生产力（自定义标准）为优化目标的算法还未实现，self.solutionProductivity暂时无意义
                            self.solutionProductivity = self.solutionMLFlow * self.solutionMLSpeed + self.solutionGLFlow * self.solutionGLSpeed * 3
                            self.AllowVehsFlow = abs(self.solutionMLFlow - int(self.Q_ML))  # 所需结果：多少车从GL到ML
                            # 普通车道变到管控车道信号为True
                            self.GL2ML = 1
                            print("需要有{}辆车从普通车道进入到管控车道".format(self.AllowVehsFlow))
                            break
                        else:
                            self.GL2ML = 0

                    if self.MLFlow<=3600 and self.GLFlow>=0:
                        pass
                    else:
                        print("no result")

                # 速度差比值小于0.1，就是管控车道过载，再把普通车辆移出来
                else:
                    ML_overload = 'yes'
                    # 然后开始由当前ML上的流量递减 以30veh/h 为步长 ML每减少30veh/h，GL就增加30/3=10veh/h
                    # for i in range(1000):
                    while(self.MLFlow>=0 and self.GLFlow<=3600):
                        self.MLFlow -= 30
                        print(self.MLFlow)
                        self.GLFlow += 10
                        self.MLSpeed = CalcSpeedbyFlow(self.MLFlow, isGL=False,getBigX=True)
                        self.GLSpeed = CalcSpeedbyFlow(self.GLFlow,getBigX = True)
                        print("calculating_MLSpeed:",self.MLSpeed,"calculating_GLSpeed:",self.GLSpeed)
                        # 然后检查速度差是否满足标准
                        self.tempSpeedDiffRate = (self.MLSpeed - self.GLSpeed) / self.GLSpeed
                        if self.tempSpeedDiffRate >= speedDiffRate:  # 如果速度差满足了标准 那么就给出结果 并结束循环
                            self.solutionMLFlow = int(self.MLFlow)
                            self.solutionGLFlow = int(self.GLFlow)
                            self.solutionMLSpeed = CalcSpeedbyFlow(self.solutionMLFlow, isGL=False)
                            self.solutionGLSpeed = CalcSpeedbyFlow(self.solutionGLFlow)
                            self.solutionSpeedDiffRate = (self.solutionMLSpeed - self.solutionGLSpeed) / self.solutionGLSpeed
                            self.solutionProductivity = self.solutionMLFlow * self.solutionMLSpeed + self.solutionGLFlow * self.solutionGLSpeed * 3
                            self.AllowVehsFlow = abs(self.solutionMLFlow - int(self.Q_ML)) # 所需结果：多少车从ML到GL *是负值
                            # 管控车道变到普通车道信号为True
                            self.ML2GL = 1
                            print("需要有{}辆车从管控车道进入到普通车道".format(self.AllowVehsFlow))
                            break
                        else:
                            self.ML2GL = 0

                    if self.MLFlow<=3600 and self.GLFlow>=0:
                        pass
                    else:
                        print("no result")




    # 计算是否有权利进行左右自由变道,目的是为了降低变道频率
    def ref_beforeToLeftFreely(self, veh, ref_keepOn):
        # my_process = sys.modules["__main__"].__dict__['myprocess']
        # 降低变道频率,change_lane_frequency 越小，禁止计算是否自由变道的可能性越大
        if random.random() > 0.3:
            ref_keepOn.value = False
        if veh.vehicleDriving().laneNumber() in [2,3] :
            ref_keepOn.value = True
        return None

    def ref_beforeToRightFreely(self, veh, ref_keepOn):
        # my_process = sys.modules["__main__"].__dict__['myprocess']
        # 降低变道频率,change_lane_frequency 越小，禁止计算是否自由变道的可能性越大
        if random.random() > 0.3:
            ref_keepOn.value = False
        return None


    # 车辆强制换道时，提高车速
    # 过载的父类方法，重新计算当前速度
    # vehi:车辆
    # ref_inOutSpeed，速度ref_inOutSpeed.value，是已计算好的车辆速度，此方法可以改变它
    # return结果：False：TESS NG忽略此方法作的修改，True：TESS NG采用此方法所作修改
    def ref_reSetSpeed(self, vehi, ref_inOutSpeed):
        tmpId = vehi.id()
        if tmpId in self.Cars:
            ref_inOutSpeed.value = vehi.vehicleDriving().desirSpeed()
            self.Cars.remove(tmpId)
            return True
        return False

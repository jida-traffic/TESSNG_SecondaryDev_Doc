import random
import numpy as np
from datetime import datetime
import torch

from PySide2.QtCore import *
from shiboken2.shiboken2 import wrapInstance

from Tessng import TessInterface, SimuInterface, PyCustomerSimulator, IVehicle, ILink
from Tessng import m2p, p2m, tngIFace, tngPlugin
from Tessng import *

###############################################################################

# 输入相关数据
data = eval(open(r".\input.txt").read())
flow = data['Flow'] # 流量
lane = data['Lane'] # 事故车道(从1开始)
start = data['Start'] # 事故开始时间
dura = data['Duration'] # 事故持续时间(min)
loca = data['Location'] # 事故位置距离上游龙门架距离
stra = data['Strategy'] # 0不使用管控，1使用可变限速，2使用开放路肩

# 写入输出文件
file = open(r".\output.txt", 'w')
txt = ["本次不执行管控策略\n\n","本次执行可变限速策略\n\n","本次执行开放路肩策略\n\n"][stra]
file.write(txt)
file.close()

# 导入风险评估的CNN模型
# CNN = torch.load(r'.\net.pkl')

# 根据事故位置，确定上游路段、事故路段、下游路段的检测器编号
if loca <= 1000:
    U = [10,11,12] # 上游路段检测器编号
    C = [2,3,4] # 事故路段检测器编号
    D = [6,7,8] # 下游路段检测器编号
else:
    U = [2,3,4] # 上游路段检测器编号
    C = [6,7,8] # 事故路段检测器编号
    D = [14,15,16] # 下游路段检测器编号

###############################################################################

DATA1 = {}
DATA2 = []

# 用户插件子类，代表用户自定义与仿真相关的实现逻辑，继承自PyCustomerSimulator
#     多重继承中的父类QObject，在此目的是要能够自定义信号signlRunInfo
class MySimulator(QObject, PyCustomerSimulator):
    signalRunInfo = Signal(str)
    def __init__(self):
        QObject.__init__(self)
        PyCustomerSimulator.__init__(self)
    
    # 过载的父类方法，初始化车辆，在车辆启动上路时被TESS NG调用一次
    def initVehicle(self, vehi):
        return True
    
    # 过载父类方法 对发车点一增加发车时间段
    # 调整发车流量
    # def calcDynaDispatchParameters(self):
    #     # TESSNG 顶层接口
    #     iface = tngIFace()
    #     # ID等于1路段上车辆
    #     lVehi = iface.simuInterface().vehisInLink(1)
        
    #     # 当前时间秒
    #     now = datetime.now()
    #     currSecs = now.hour * 3600 + now.minute * 60 + now.second
    #     di = TESSNG.DispatchInterval()
    #     di.dispatchId = 1
    #     di.fromTime = currSecs
    #     di.toTime = di.fromTime + 3600 - 1
    #     di.vehiCount = flow
    #     di.mlVehicleConsDetail = [TESSNG.VehicleComposition(1, 75), TESSNG.VehicleComposition(2, 25)]
    #     return [di]
    
    # 计算车辆当前限制车道序号列表
    def calcLimitedLaneNumber(self, vehi):
        link = wrapInstance(vehi.road().__int__(), ILink)
        iface = tngIFace()
        currSimuTime = round(iface.simuInterface().simuTimeIntervalWithAcceMutiples()/60000,1) # 换算成分钟
        
        lanes = [] # 禁行车道
        link1 = [2] # 上游路段ID
        link2 = [3,4,5,6] # 事故路段ID
        link3 = [7] # 下游路段ID
        
        # 设置路肩车道关闭
        if link.id() in (link1+link2+link3):
            lanes += [0]
        
        # 模拟事故路段禁行
        d = p2m(vehi.vehicleDriving().getVehiDrivDistance())
        MAX = loca + 3000
        MIN = loca + 3000 - 150
        if MIN < d < MAX and start < currSimuTime <= start+dura:
            lanes += [lane]
        
        # 如果stra不是2，就不执行后面
        if stra != 2:
            return lanes
        
        # 开放路肩策略
        if flow >= 2500:
            if loca >= 400:
                if start < currSimuTime <= start+dura and link.id() in link2:
                    lanes.remove(0)
            elif loca < 400:
                if lane in [1]:
                    if start < currSimuTime <= start+dura and link.id() in link2:
                        lanes.remove(0)
                elif lane in [2,3]:
                    if start < currSimuTime <= start+40 and link.id() in link2:
                        lanes.remove(0)
                    elif start+40 < currSimuTime <= start+dura and link.id() in link1+link2:
                        lanes.remove(0)
        return lanes


    # 可变限速策略
    def ref_calcSpeedLimitByLane(self, link, laneNumber, ref_outSpeed):
        # 如果stra不是1，就不执行后面
        if stra != 1:
            return False
        
        iface = tngIFace()
        currSimuTime = round(iface.simuInterface().simuTimeIntervalWithAcceMutiples()/60000,1) # 换算成分钟
        
        link1 = [2] # 上游路段ID
        link2 = [3,4,5,6] # 下游路段ID
        
        if lane in [1,3]:
            dura0 = 20
        elif lane in [2]:
            dura0 = 30
        
        if flow > 1500:
            if dura <= dura0:
                if start < currSimuTime <= start+5:
                    if link.id() in link1 and laneNumber in [0,1,2,3]:
                        ref_outSpeed.value = 110
                    elif link.id() in link2 and laneNumber in [0,1,2,3]:
                        ref_outSpeed.value = 100
                else:
                    ref_outSpeed.value = 120
            elif dura > dura0:
                if start < currSimuTime <= start+5:
                    if link.id() in link1 and laneNumber in [0,1,2,3]:
                        ref_outSpeed.value = 110
                    elif link.id() in link2 and laneNumber in [0,1,2,3]:
                        ref_outSpeed.value = 100
                elif start+5 < currSimuTime <= start+dura0:
                    if link.id() in link1 and laneNumber in [0,1,2,3]:
                        ref_outSpeed.value = 100
                    elif link.id() in link2 and laneNumber in [0,1,2,3]:
                        ref_outSpeed.value = 90
                elif start+dura0 < currSimuTime <= start+dura:
                    if link.id() in link1 and laneNumber in [0,1,2,3]:
                        ref_outSpeed.value = 90
                    elif link.id() in link2 and laneNumber in [0,1,2,3]:
                        ref_outSpeed.value = 80
                else:
                    ref_outSpeed.value = 120
        else:
            ref_outSpeed.value = 120
        
        return True
    
    
    
    # 过载的父类方法，TESS NG 在每个计算周期结束后调用此方法，大量用户逻辑在此实现，注意耗时大的计算要尽可能优化，否则影响运行效率
    def afterOneStep(self):
        #= == == == == == =以下是获取一些仿真过程数据的方法 == == == == == ==
        # TESSNG 顶层接口
        iface = tngIFace()
        # TESSNG 仿真子接口
        simuiface = iface.simuInterface()
        # 当前已仿真时间，单位：毫秒
        simuTime = simuiface.simuTimeIntervalWithAcceMutiples()
        
        if simuTime/1000%1 == 0:
            print("仿真时间:{:.2f}".format(simuTime/1000))
        
        # 获取平均行程时间
        lVehiTravAggr = simuiface.getVehisTravelAggregated()
        if len(lVehiTravAggr) > 0:
            temp = [vTravAggr for vTravAggr in lVehiTravAggr][0]
            
            t = temp.timeId
            tt = temp.avgTravelTime
            
            file = open("Data\\output.txt", 'a')
            file.write('现在的时间是第{}min\n'.format(t*5))
            file.write("平均行程时间是{:.2f}s\n\n".format(tt))
            file.close()
        
        # 获取道路事故风险
        lVehisInfoAggr = simuiface.getVehisInfoAggregated()
        if len(lVehisInfoAggr) > 0:
            temp0 = {}
            for vinfo in lVehisInfoAggr:
                t = vinfo.timeId
                ID = vinfo.collectorId
                q = vinfo.vehiCount / 3
                v = vinfo.avgSpeed
                k = vinfo.occupancy
                temp0[ID] = [q,v,k]
            DATA1[t] = temp0
            if t%5 == 0:
                QVK = []
                for i in [t-4,t-3,t-2,t-1,t]:
                    temp = DATA1[i]
                    qvk = []
                    for j in [U,C,D]:
                        a = j[0]
                        b = j[1]
                        c = j[2]
                        q1 = temp[a][0]
                        v1 = temp[a][1]
                        k1 = temp[a][2]
                        q2 = temp[b][0]
                        v2 = temp[b][1]
                        k2 = temp[b][2]
                        q3 = temp[c][0]
                        v3 = temp[c][1]
                        k3 = temp[c][2]
                        q = q1 + q2 +q3
                        if q != 0:
                            v = (v1*q1+v2*q2+v3*q3) / q
                            k = (k1*q1+k2*q2+k3*q3) / q
                        else:
                            v,k = 0,0
                        qvk.append([q,v,k])
                    QVK.append(qvk)
                UQ = [QVK[0][0][0],QVK[1][0][0],QVK[2][0][0],QVK[3][0][0],QVK[4][0][0]]
                UV = [QVK[0][0][1],QVK[1][0][1],QVK[2][0][1],QVK[3][0][1],QVK[4][0][1]]
                UK = [QVK[0][0][2],QVK[1][0][2],QVK[2][0][2],QVK[3][0][2],QVK[4][0][2]]
                CQ = [QVK[0][1][0],QVK[1][1][0],QVK[2][1][0],QVK[3][1][0],QVK[4][1][0]]
                CV = [QVK[0][1][1],QVK[1][1][1],QVK[2][1][1],QVK[3][1][1],QVK[4][1][1]]
                CK = [QVK[0][1][2],QVK[1][1][2],QVK[2][1][2],QVK[3][1][2],QVK[4][1][2]]
                DQ = [QVK[0][2][0],QVK[1][2][0],QVK[2][2][0],QVK[3][2][0],QVK[4][2][0]]
                DV = [QVK[0][2][1],QVK[1][2][1],QVK[2][2][1],QVK[3][2][1],QVK[4][2][1]]
                DK = [QVK[0][2][2],QVK[1][2][2],QVK[2][2][2],QVK[3][2][2],QVK[4][2][2]]
                uqa,uqb = np.mean(UQ), np.std(UQ)
                uva,uvb = np.mean(UV), np.std(UV)
                uka,ukb = np.mean(UK), np.std(UK)
                cqa,cqb = np.mean(CQ), np.std(CQ)
                cva,cvb = np.mean(CV), np.std(CV)
                cka,ckb = np.mean(CK), np.std(CK)
                dqa,dqb = np.mean(DQ), np.std(DQ)
                dva,dvb = np.mean(DV), np.std(DV)
                dka,dkb = np.mean(DK), np.std(DK)
                DATA2.append([[[uqa,cqa,dqa], [uqb,cqb,dqb]],
                              [[uva,cva,dva], [uvb,cvb,dvb]],
                              [[uka,cka,dka], [ukb,ckb,dkb]]])
            if t >= 25 and (t-30)%5 == 0:
                temp = DATA2[-5:]
                g2 = temp[-1]
                g3 = temp[-2]
                g4 = temp[-3]
                g5 = temp[-4]
                g6 = temp[-5]
                crash = []
                for i in [0,1,2]:
                    for j in [0,1]:
                        for k in [0,1,2]:
                            crash.append(g2[i][j][k])
                            crash.append(g3[i][j][k])
                            crash.append(g4[i][j][k])
                            crash.append(g5[i][j][k])
                            crash.append(g6[i][j][k])
                crash = np.array(crash).reshape(6,3,5)
                crash = np.array([crash]*2)
                crash = torch.from_numpy(crash)
                crash = crash.to(torch.float32)
                
                RISK = CNN(crash)[0]
                RISK = float(RISK)
                
                file = open("Data\\output.txt", 'a')
                file.write("风险指数是{:.3f}\n\n".format(RISK))
                file.close()












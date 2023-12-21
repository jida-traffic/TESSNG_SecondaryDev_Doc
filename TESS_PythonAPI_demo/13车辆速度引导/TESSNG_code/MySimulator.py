import pandas as pd
from PySide2.QtCore import *

from my_code.config import *
from my_code.functions import *
from Tessng import *

###############################################################################

# 用户插件子类，代表用户自定义与仿真相关的实现逻辑，继承自PyCustomerSimulator
#     多重继承中的父类QObject，在此目的是要能够自定义信号signlRunInfo
class MySimulator(QObject, PyCustomerSimulator):
    signalRunInfo = Signal(str)
    forStopSimu = Signal()
    forReStartSimu = Signal()

    def __init__(self):
        QObject.__init__(self)
        PyCustomerSimulator.__init__(self)

    # 仿真开始前
    def ref_beforeStart(self, ref_keepOn):
        iface = tessngIFace()
        simuiface = iface.simuInterface()
        simuiface.setAcceMultiples(5)

    def afterOneStep(self):
        # TESSNG 顶层接口
        iface = tessngIFace()
        # TESSNG 仿真子接口
        simuiface = iface.simuInterface()
        # TESSNG 路网子接口
        netiface = iface.netInterface()

        # 当前已仿真时间，单位：毫秒
        simuTime = simuiface.simuTimeIntervalWithAcceMutiples()
        
        # 如果仿真时间大于等于最长时间，通知主窗体停止仿真
        if(simuTime >= SimTime * 1000):
            self.forStopSimu.emit()
        
        # 速度引导--------------------------------------------------------------
        
        # 获取当前仿真时刻
        currentTime = round(simuTime/1000, 1)

        # 当前正在运行车辆列表
        lAllVehi = simuiface.allVehiStarted()
        
        if len(lAllVehi) == 0:
            return
        
        # 获取目标路段排队信息
        QueueLength_list = GetQueueLength(lAllVehi, LinksID)
        
        # 遍历每一辆车
        for vehi in lAllVehi:
            vehID = int(vehi.id())%100000 # 获取车辆编号
            vehType = vehi.vehicleTypeCode() # 获取车辆类型
            vehPos = p2m(vehi.vehicleDriving().currDistanceInRoad()) # 获取车辆位置
            vehSpeed = p2m(vehi.currSpeed())  # 获取车辆速度(m/s)
            temp = vehi.roadIsLink()
            vehLink = int(vehi.roadId())
            if temp == False:
                vehLink += 100
            vehDes_Speed = p2m(vehi.vehicleDriving().desirSpeed())*3.6 # 获取车辆期望速度(km/h)
            
            # if vehID == 1 and currentTime%3==0 and currentTime>5:
            #     print(currentTime,round(vehSpeed*3.6,2),round(vehDes_Speed,2))
            
            #添加数据到data中 仿真结束后统计
            real_vehPos = GetRealVehPos(vehLink, vehPos) #获取车辆在路网的累计行驶位移
            datas.append([currentTime,vehID,vehType,vehSpeed,vehLink,vehPos,vehDes_Speed,real_vehPos])
            
            if vehPos < 5 and vehLink in [1]:
                if vehType in [2]:
                    vehi.setColor("#FFA500")
                else:
                    vehi.setColor("#FFFFFF")
            
            if Is_Guidance == False:
                continue
            # 不引导普通车
            if vehType in [2]:
                continue
            # 检查该车辆是否在目标路段上
            if vehLink not in LinksID :
                continue
            
            signalHeadPos = 0
            guidancePoint = []
            guidancePointCount = 0
            QL = 0 # 当前排队长度
            
            # 获取所在路段的引导配置信息（引导点位置，信号灯ID，信号灯位置，当前排队长度等）
            for j in range(len(LinksID)) :
                if vehLink == LinksID[j] :
                    #signalHeadID = SignalHeadsID[j] # 获取对应的信号灯ID
                    signalHeadPos = SignalHeadsPos[j] # 获取对应的信号灯位置
                    guidancePoint = GuidancePoints[j] # 获取引导点位置列表
                    guidancePointCount = len(guidancePoint) # 获取该路段引导点的数量
                    QL = QueueLength_list[j] # 获取当前排队长度
                    break
            
            # 判断车辆是否已经驶过信号灯
            if vehPos > signalHeadPos:
                #如果是的话 那就把车辆的颜色恢复成白色 并且期望速度恢复成默认速度 然后跳过
                vehi.setColor("#FFFFFF")
                Speed_Guidance[vehID] = defaultDesSpeed/3.6 # (m/s)
                continue
            
            # 判断该车是否在引导点附近2米处 [先暂时设定为+-1m，看看识别效果，主要是怕漏检]
            for j in range(guidancePointCount):
                gp = guidancePoint[j] # 获取引导点位置
                #如果车辆进入引导点
                if abs(vehPos - gp) < 1 : # 在引导点附近2米内 就开始引导 防止有漏引导的
                    #计算还剩几个引导点
                    rest_GP_Count = j + 1 # 这里比较巧妙 如果j=0 说明正好是最后一个引导点 还需要引导1次 j的值+1 就是还需要引导几次
                    #进行速度引导，遍历寻找最佳速度
                    guidanceSpeed = FindOptimalSpeed(vehSpeed, currentTime, rest_GP_Count, vehLink, QL) # (m/s)
                    # print(vehSpeed, currentTime, rest_GP_Count, vehLink, QL, guidanceSpeed)
                    #设置车辆的期望速度
                    Speed_Guidance[vehID] = guidanceSpeed # (m/s)
                    
                    #更改车辆的颜色 绿色表示加速 红色表示减速 (加速还是减速是以车辆的当前速度为标准)
                    #如果期望速度没变 那就保持当前颜色 直接跳过
                    if guidanceSpeed*3.6 == vehDes_Speed:
                        continue
                    
                    if guidanceSpeed >= vehSpeed or guidanceSpeed*3.6 >= 80.0 :
                        # 加速，改成红色
                        vehi.setColor("#D92626")
                    else:
                        # 减速，改成绿色
                        vehi.setColor("#00FF07")
                    break

        #每20个计算批次做一次小计，将结果通过信号发送出云
        if currentTime % 1 == 0:
            strLinkCount = str(netiface.linkCount())
            strVehiCount = str(len(lAllVehi))
            strSimuTime = str(simuTime/1000)
            runInfo = f"运行车辆数：{strVehiCount}\n仿真时间：{strSimuTime}(秒)\n\n{QueueLength_list}"
            self.signalRunInfo.emit(runInfo)

    # 重新计算期望速度
    def ref_reCalcdesirSpeed(self, vehi, ref_desirSpeed):
        vehID = int(vehi.id())%100000
        if vehID in Speed_Guidance.keys():
            ref_desirSpeed.value = m2p(Speed_Guidance[vehID])
            # if vehID in [1]:
            #     print(round(Speed_Guidance[vehID]*3.6,2),"---------------")
            #     print(ref_desirSpeed.value)
            # del Speed_Guidance[vehID]
            return True
        return False

    # 仿真结束后
    def afterStop(self):
        try:
            # 最后保存数据
            name = ['currentTime', 'vehID', 'vehType', 'vehSpeed', 'vehLink', 'vehPos', 'desSpeed', 'realVehPos']
            datas_pd = pd.DataFrame(columns=name, data=datas)
            datas_pd.to_csv('Data\\Data.csv', index=None, encoding='gbk')
            CookDatas()
        except:
            pass

    # 过载父类方法， 计算车辆当前限制车道序号列表
    def calcLimitedLaneNumber(self, vehi):
        laneNumber = vehi.vehicleDriving().laneNumber()
        all_lanes = {0, 1, 2, 3}
        return list(all_lanes - {laneNumber})


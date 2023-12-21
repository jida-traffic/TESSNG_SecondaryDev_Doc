import pandas as pd
import math

from Tessng import p2m
from my_code.config import *

###############################################################################

# 输入：速度(m/s)、位移(m)
# 输出：匀速阶段的油耗
def CalcFU(v,d):
    if v > 0:
        fu = d * (0.0411 * (0.132 * v + 0.000302 * v**3) + 0.4629) / v
    else:
        fu = 0
    return fu


# 输入：初速度(m/s)、末速度(m/s)
# 输出：变速阶段的油耗
def CalcAccFU(v0, vt):
    fu = 0 #累计油耗
    tt = 0
    # 先判断是加速还是减速
    if v0 < vt:
        # 是加速运动
        a = acceleration
        # 计算加速过程的总时间
        t = (vt - v0) / a
        # 将时间分成每0.1s一份，分段求每0.1s的油耗
        while tt < t:
            tt += 0.1
            v = v0 + a * tt  #每一小段末尾的速度
            d = (v + v0) / 2.0 * 0.1 #每一小段内的位移
            fu += CalcFU((v + v0) / 2.0 , d) #每一小段内的油耗
    else:
        # 是减速运动
        a = deceleration
        # 计算减速过程的总时间
        t = (v0 - vt) / a
        # 将时间分成每0.1s一份，分段求每0.1s的油耗
        while tt < t:
            tt += 0.1
            v = v0 - a * tt  #每一小段末尾的速度
            d = (v + v0) / 2.0 * 0.1 #每一小段内的位移
            fu += CalcFU((v + v0) / 2.0 , d) #每一小段内的油耗
    return fu


# 输入：当前速度m/s 最终速度m/s 默认是默认的期望速度 60km/s，即车辆停车后要启动恢复至60km/h 这一过程的油耗
# 输出：停车油耗
def CalcStopFU(finalSpeed = 60/3.6):
    StopFU = CalcAccFU(0, finalSpeed) * stop_weight
    return StopFU


# 输入：速度list，list里的每个元素都是该车辆每0.1s记录下的速度(m/s)
# 输出：一辆车的全程油耗
def CalcWholeFU(speedList):
    #把每一段当成匀速运动来计算油耗
    FU = 0.0
    for i in range(len(speedList)):
        v = speedList[i]
        d = v * 0.1 # 计算0.1s内的位移
        FU += CalcFU(v, d)
    return FU


# 输入：当前速度(m/s)、目标速度(m/s)、前方排队长度(m)
# 输出：每个引导区间内的油耗、最终速度、所需时间
def CalcSegmentFU(currentSpeed, targetSpeed, QL=0.0):
    gl = Guidance_Lengeh - QL # gl是扣除排队长度的路段引导长度
    finalSpeed = targetSpeed # 在引导段的最终速度(m/s)
    
    FU = 999.9 # 整段的油耗
    travelTime = 999.9 # 整段行程的时间
    
    # 先处理减速情形
    if currentSpeed > targetSpeed:
        # 计算变速所需时间
        t = (currentSpeed - targetSpeed) / deceleration
        # 计算变速过程的位移
        s = (currentSpeed + targetSpeed) * t / 2
        if s <= gl: # 说明可以在200m位移内完成变速
            # 在这里先计算一下整个行程时间
            travelTime = t + (gl - s) / finalSpeed
            # 然后分段计算油耗
            # 1.减速阶段的油耗
            fu1 = CalcAccFU(currentSpeed, finalSpeed)
            # 2.匀速阶段的油耗
            fu2 = CalcFU(finalSpeed, gl-s)
            #两段油耗汇总
            FU = fu1 + fu2
        else: # 说明不可以完成减速
            # 那么计算一下200m后的最终速度
            finalSpeed = math.sqrt(currentSpeed**2 - 2*deceleration*gl)
            # 再计算一下整个行程时间
            travelTime = (currentSpeed - finalSpeed) / deceleration
            # 直接计算减速阶段的油耗
            FU = CalcAccFU(currentSpeed, finalSpeed)
    # 再处理加速情形
    elif currentSpeed < targetSpeed:
        # 计算变速所需时间
        t = (targetSpeed - currentSpeed) / acceleration
        # 计算变速过程的位移
        s = (currentSpeed + targetSpeed) * t / 2
        if s <= gl: # 说明可以在200m位移内完成变速
            # 在这里先计算一下整个行程时间
            travelTime = t + (gl - s) / finalSpeed
            # 然后分段计算油耗
            # 1.加速阶段的油耗
            fu1 = CalcAccFU(currentSpeed, finalSpeed)
            # 2.匀速阶段的油耗
            fu2 = CalcFU(finalSpeed, gl-s)
            #两段油耗汇总
            FU = fu1 + fu2
        else: # 说明不可以完成加速
            # 那么计算一下200m后的最终速度 
            finalSpeed = math.sqrt(currentSpeed**2 + 2*acceleration*gl)
            # 再计算一下整个行程时间
            travelTime = (finalSpeed - currentSpeed) / acceleration
            # 直接计算减速阶段的油耗
            FU = CalcAccFU(currentSpeed, finalSpeed)
    # 最后处理匀速的情景
    else:
        # 先计算行程时间
        travelTime = gl / finalSpeed
        # 直接返回匀速段的油耗
        FU = CalcFU(finalSpeed, gl)
    
    return FU, finalSpeed, travelTime


# 输入：
# 输出：是不是红灯
def CheckSignalHeadRed(currentTime, t, linkid):
    # 如果处在54s之后 那就是绿灯
    if (currentTime+t+SignalCycle-SignalHead_offset[linkid])%SignalCycle > SignalRed:
        r = False
    else:
        r = True
    return r


# 输入：车辆所在路段id，车辆位置vehpos
# 输出：车辆在路网中的累计位移，车辆当前在路段的相对位置
def GetRealVehPos(linkid, vehpos):
    if linkid in allLinksID:
        realPos = links_Length_Added[linkid] + vehpos
    else:
        realPos = 0
    return realPos


# 输入：所有车辆信息列表+目标路段列表
# 输出：获取路段排队长度信息
def GetQueueLength(vehs_info, target_linksIDs):
    QL_list = [] #里边存着路段实时排队长度信息
    #针对每个目标路段 筛选统计
    for link in target_linksIDs:
        l = 0
        #遍历所有车
        for vehi in vehs_info:
            vehSpeed = p2m(vehi.currSpeed())*3.6 # 获取车辆速度(km/h)
            temp = vehi.roadIsLink()
            vehLink = int(vehi.roadId())
            if temp == False:
                vehLink += 100
            if vehSpeed < 7.2 and vehLink == link: # 速度小于7.2km/h就认为是停车状态
                l += 1
        QL_list.append(l*(4.5+1.0)/4*2) # 计算排队长度,并添加到列表中,车长4.5米,停车间隙1米,4车道,排队长度放大系数2
    return QL_list #返回数组


# 数据处理程序
# 统计每一辆车的油耗
# ALL表示统计主干道上所有车，CV表示只统计主干道上的CV车
def CalcDatas(datas_pd, target):
    # 定义统计对象，1是CV车，2是普通车
    if target == "CV":
        target_type = [1]
    elif target == "ALL":
        target_type = [1,2]

    datas_output = [] # 输出
    total_fu = 0.0 # 总油耗
    total_fu_with_stop = 0.0 # 考虑停车惩罚的总油耗
    total_travelTime = 0.0 # 总行驶时间
    total_stopTimes = 0 # 总停车次数

    # 先统计一共有多少辆车被记录下来
    vehCount = len(set(datas_pd["vehID"]))
    print("车辆总数",vehCount)
    
    # 然后遍历每一辆车的数据，分别切片
    for i in range(1,vehCount + 1) :
        vehData_pd = datas_pd[(datas_pd["vehID"] == i)]

        #获取车辆型号
        vehType = vehData_pd["vehType"].max()
        if vehType not in target_type : #只处理目标车辆
            continue
        
        # 判断这辆车有没有走完全程，即看看有没有出现路段为4的数据
        veh_clip_pd = vehData_pd[vehData_pd['vehLink'] == 4]
        if len(veh_clip_pd) == 0:
            continue
        
        # #提取在三个信号灯路段的数据
        # vehData_pd = vehData_pd[(vehData_pd['vehLink'] > 10) | (vehData_pd['vehLink'] < 10)]

        #同时也要排除初始路段 15号  因为初始路段是用来配合上游绿波形成的
        vehData_pd = vehData_pd[vehData_pd['vehLink'] < 5]

        # 计算出行时间
        travelTime = vehData_pd["currentTime"].max() - vehData_pd["currentTime"].min()
        total_travelTime += travelTime

        # 计算油耗
        veh_Speed_Data = vehData_pd["vehSpeed"].tolist()
        fu = CalcWholeFU(veh_Speed_Data)  # 根据速度数据计算本车油耗
        total_fu += fu # 累计总油耗

        # 计算停车次数
        # 因为已知是有3个红绿灯 所以在流量没有过饱和的情况下（没有二次停车的情况下）可以直接看看车辆在有信号灯的路段中有没有速度为0的数据
        target_links = [1, 2, 3]
        stop_times = 0
        for target_link in target_links :
            temp_data = vehData_pd[vehData_pd['vehLink'] == target_link]
            min_speed = temp_data['vehSpeed'].min()
            if min_speed < 0.1 : #如果车辆在该路段的最小速度小于0.1m/s 那么就认为这辆车停车了1次
                stop_times += 1
        
        total_stopTimes += stop_times

        #根据停车次数来重新整理油耗  = 原始油耗 + 停车次数 *（停车油耗放大系数-1）* 每次停车的油耗
        fu_with_stop = fu + stop_times * (stop_weight - 1.0) * CalcStopFU()
        total_fu_with_stop += fu_with_stop

        #储存数据
        datas_output.append([i,fu,fu_with_stop,travelTime,stop_times])
        
    return datas_output, total_fu, total_fu_with_stop, total_travelTime, total_stopTimes


# 处理数据部分
def CookDatas():
    datas_pd = pd.read_csv("Data\\Data.csv", index_col=False)
    datas_pd = datas_pd.drop_duplicates(subset=["currentTime","vehID"])
    
    # 最后处理数据：输出主干道出发的每辆车的总油耗
    datas_output_ALL,fu_ALL,fustop_ALL,tt_ALL,st_ALL = CalcDatas(datas_pd,"ALL") # 统计主干道上所有车
    datas_output_CV,fu_CV,fustop_CV,tt_CV,st_CV = CalcDatas(datas_pd,"CV") # 统计主干道上CV车
    
    name = ['vehID','FU','FUwithStop','travelTime','stopTimes']
    # 保存结果到CSV文件
    datas_output_pd_ALL = pd.DataFrame(columns=name, data=datas_output_ALL)
    datas_output_pd_ALL.to_csv('Data\\result_ALL.csv', index=None)
    datas_output_CV_pd = pd.DataFrame(columns=name, data=datas_output_CV)
    datas_output_CV_pd.to_csv('Data\\result_CV.csv', index=None)

    print('统计车辆数： %d' % len(datas_output_ALL))
    print('车均油耗： %.2f' % (fu_ALL / len(datas_output_ALL)),"ml")
    print('车均油耗（含停车惩罚）： %.2f' % (fustop_ALL / len(datas_output_ALL)),"ml")
    print('车均行程时间： %.2f' % (tt_ALL / len(datas_output_ALL)),"s")
    print('车均停车次数： %.2f' % (st_ALL / len(datas_output_ALL)))

    print("")

    print('CV统计车辆数： %d' % len(datas_output_CV))
    print('CV车均油耗： %.2f' % (fu_CV / len(datas_output_CV)),"ml")
    print('CV车均油耗（含停车惩罚）： %.2f' % (fustop_CV / len(datas_output_CV)),"ml")
    print('CV车均行程时间： %.2f' % (tt_CV / len(datas_output_CV)),"s")
    print('CV车均停车次数： %.2f' % (st_CV / len(datas_output_CV)))



# 规划算法的遍历算法，寻找到最优的速度使得全程油耗最小
# 输入：当前车辆速度 单位m/s、当前仿真时刻 秒（用来判断未来是否是红灯，是否需要停车）、剩余引导点的数量（用来区别迭代次数
# 输出：最优速度(m/s)
def FindOptimalSpeed(currentSpeed, currentTime, guidancePointCount, linkid, QL):
    #这里为了加快运行速度 直接对大于3次的引导返回默认期望速度（因为车辆其实距离交叉口太远了，此时引导效果不显著）
    if guidancePointCount > 3:
        return defaultDesSpeed / 3.6 #返回默认速度
    
    ranges = int((toSpeed - fromSpeed) / desGap) + 1 # 遍历次数
    optimalSpeed = defaultDesSpeed / 3.6 #初始默认的速度
    minFU = 9999999.99 #油耗
    
    #区分不同的引导次数
    #1.如果只需要引导最后1次
    if guidancePointCount == 1 : 
        for i in range(ranges) :
            targetSpeed = (fromSpeed + i * desGap) / 3.6
            FU,v,t = CalcSegmentFU(currentSpeed, targetSpeed, QL)
            # print(int(targetSpeed*3.6),round(FU,2),round(v*3.6,2),round(t,1))
            # 判断是否遇到红灯停车
            if CheckSignalHeadRed(currentTime,t,linkid):
                stopFU = CalcStopFU()
                FU += stopFU
            if FU <= minFU:
                minFU = FU
                optimalSpeed = targetSpeed
        #最后输出optimalSpeed
        return optimalSpeed
    
    #如果需要引导2次
    elif guidancePointCount == 2 :
        #计算第一段油耗FU1 最终速度finalSpeed 和行程时间t1
        for i in range(ranges) :
            targetSpeed1 = (fromSpeed + i * desGap) / 3.6 
            FU1,finalSpeed,t1 = CalcSegmentFU(currentSpeed, targetSpeed1)
            #再计算第二段油耗FU2  和行程时间t2
            for j in range(ranges) :
                targetSpeed2 = (fromSpeed + j * desGap) / 3.6
                FU2,_,t2 = CalcSegmentFU(finalSpeed, targetSpeed2)
                FU = FU1 + FU2 #两段的总油耗
                #判断是否遇到红灯停车
                if CheckSignalHeadRed(currentTime,t1 + t2,linkid):
                    stopFU = CalcStopFU()
                    FU += stopFU
                if FU <= minFU :
                    minFU = FU
                    optimalSpeed = targetSpeed1
        #最后输出optimalSpeed
        return optimalSpeed
    
    #如果需要引导3次
    elif guidancePointCount == 3 :
        #计算第一段油耗FU1 最终速度finalSpeed1 和行程时间t1
        for i in range(ranges) :
            targetSpeed1 = (fromSpeed + i * desGap) / 3.6 
            FU1,finalSpeed1,t1 = CalcSegmentFU(currentSpeed, targetSpeed1)
            #再计算第二段油耗FU2 最终速度finalSpeed2 和行程时间t2
            for j in range(ranges) :
                targetSpeed2 = (fromSpeed + j * desGap) / 3.6
                FU2,finalSpeed2,t2 = CalcSegmentFU(finalSpeed1, targetSpeed2)
                #最后计算第三段油耗FU3 和 行程时间t3
                for k in range(ranges) :
                    targetSpeed3 = (fromSpeed + k * desGap) / 3.6  
                    FU3,_,t3 = CalcSegmentFU(finalSpeed2, targetSpeed3)
                    FU = FU1 + FU2 + FU3 #三段的总油耗
                    #判断是否遇到红灯停车
                    if CheckSignalHeadRed(currentTime,t1 + t2 + t3,linkid): #
                        stopFU = CalcStopFU()
                        FU += stopFU
                    if FU <= minFU :
                        minFU = FU
                        optimalSpeed = targetSpeed1
        #最后输出optimalSpeed
        return optimalSpeed
    
    #如果需要引导4次
    elif guidancePointCount == 4 :
        #计算第一段油耗FU1 最终速度finalSpeed1 和行程时间t1
        for i in range(ranges) :
            targetSpeed1 = (fromSpeed + i * desGap) / 3.6 
            FU1,finalSpeed1,t1 = CalcSegmentFU(currentSpeed, targetSpeed1)
            #再计算第二段油耗FU2 最终速度finalSpeed2 和行程时间t2
            for j in range(ranges) :
                targetSpeed2 = (fromSpeed + j * desGap) / 3.6
                FU2,finalSpeed2,t2 = CalcSegmentFU(finalSpeed1, targetSpeed2)
                #计算第三段油耗FU3 最终速度finalSpeed3 和行程时间t3
                for k in range(ranges):
                    targetSpeed3 = (fromSpeed + k * desGap) / 3.6
                    FU3,finalSpeed3,t3 = CalcSegmentFU(finalSpeed2, targetSpeed3)
                    #最后计算第四段油耗FU4 和 行程时间t4
                    for l in range(ranges) :
                        targetSpeed4 = (fromSpeed + l * desGap) / 3.6  
                        FU4,_,t4 = CalcSegmentFU(finalSpeed3, targetSpeed4)
                        FU = FU1 + FU2 + FU3 + FU4 #4段的总油耗
                        #判断是否遇到红灯停车
                        if CheckSignalHeadRed(currentTime,t1 + t2 + t3 + t4,linkid):
                            stopFU = CalcStopFU()
                            FU += stopFU
                        if FU <= minFU :
                            minFU = FU
                            optimalSpeed = targetSpeed1
        #最后输出optimalSpeed
        return optimalSpeed
    
    #如果需要引导5次
    elif guidancePointCount == 5 :
        #计算第一段油耗FU1 最终速度finalSpeed1 和行程时间t1
        for i in range(ranges) :
            targetSpeed1 = (fromSpeed + i * desGap) / 3.6 
            FU1,finalSpeed1,t1 = CalcSegmentFU(currentSpeed, targetSpeed1)
            #再计算第二段油耗FU2 最终速度finalSpeed2 和行程时间t2
            for j in range(ranges) :
                targetSpeed2 = (fromSpeed + j * desGap) / 3.6
                FU2,finalSpeed2,t2 = CalcSegmentFU(finalSpeed1, targetSpeed2)
                #计算第三段油耗FU3 最终速度finalSpeed3 和行程时间t3
                for k in range(ranges):
                    targetSpeed3 = (fromSpeed + k * desGap) / 3.6
                    FU3,finalSpeed3,t3 = CalcSegmentFU(finalSpeed2, targetSpeed3)
                    #计算第4段油耗FU4 最终速度finalSpeed4 和行程时间t4
                    for l in range(ranges):
                        targetSpeed4 = (fromSpeed + l * desGap) / 3.6
                        FU4,finalSpeed4,t4 = CalcSegmentFU(finalSpeed3, targetSpeed4)
                        #最后计算第5段油耗FU5 和 行程时间t5
                        for n in range(ranges) :
                            targetSpeed5 = (fromSpeed + n * desGap) / 3.6  
                            FU5,_,t5 = CalcSegmentFU(finalSpeed4, targetSpeed5)
                            FU = FU1 + FU2 + FU3 + FU4 + FU5 #4段的总油耗
                            #判断是否遇到红灯停车
                            if CheckSignalHeadRed(currentTime,t1 + t2 + t3 + t4 + t5,linkid):
                                stopFU = CalcStopFU()
                                FU += stopFU
                            if FU <= minFU :
                                minFU = FU
                                optimalSpeed = targetSpeed1
        #最后输出optimalSpeed
        return optimalSpeed
    
    #如果需要引导6次
    elif guidancePointCount == 6 :
        #计算第一段油耗FU1 最终速度finalSpeed1 和行程时间t1
        for i in range(ranges) :
            targetSpeed1 = (fromSpeed + i * desGap) / 3.6 
            FU1,finalSpeed1,t1 = CalcSegmentFU(currentSpeed, targetSpeed1)
            #再计算第二段油耗FU2 最终速度finalSpeed2 和行程时间t2
            for j in range(ranges) :
                targetSpeed2 = (fromSpeed + j * desGap) / 3.6                 
                FU2,finalSpeed2,t2 = CalcSegmentFU(finalSpeed1, targetSpeed2)
                #计算第三段油耗FU3 最终速度finalSpeed3 和行程时间t3
                for k in range(ranges):
                    targetSpeed3 = (fromSpeed + k * desGap) / 3.6                 
                    FU3,finalSpeed3,t3 = CalcSegmentFU(finalSpeed2, targetSpeed3)
                    #计算第4段油耗FU4 最终速度finalSpeed4 和行程时间t4
                    for l in range(ranges):
                        targetSpeed4 = (fromSpeed + l * desGap) / 3.6                 
                        FU4,finalSpeed4,t4 = CalcSegmentFU(finalSpeed3, targetSpeed4)
                        #计算第5段油耗FU5 和 行程时间t5
                        for n in range(ranges) :
                            targetSpeed5 = (fromSpeed + n * desGap) / 3.6                 
                            FU5,finalSpeed5,t5 = CalcSegmentFU(finalSpeed4, targetSpeed5)
                            #最后计算第6段油耗FU5 和 行程时间t5
                            for o in range(ranges) :
                                targetSpeed6 = (fromSpeed + o * desGap) / 3.6  
                                FU6,_,t6 = CalcSegmentFU(finalSpeed5, targetSpeed6)
                                FU = FU1 + FU2 + FU3 + FU4 + FU5 + FU6 #4段的总油耗
                                #判断是否遇到红灯停车
                                if CheckSignalHeadRed(currentTime,t1 + t2 + t3 + t4 + t5 + t6,linkid): #
                                    stopFU = CalcStopFU()
                                    FU += stopFU
                                if FU <= minFU :
                                    minFU = FU
                                    optimalSpeed = targetSpeed1
        #最后输出optimalSpeed
        return optimalSpeed
    
    else:
        return defaultDesSpeed / 3.6 #返回默认速度




Is_Guidance = True # 表示是否进行速度引导

SimTime = 3600 # 仿真时长

# 车辆性能相关的参数：加减速度(m/s2)
acceleration = 3.5
deceleration = 3.0

stop_weight = 5 # 惩罚系数，用来惩罚停车

Guidance_Lengeh = 200 # 每个引导段长度

defaultDesSpeed = 60 # 默认的期望速度(km/h)
fromSpeed = 30 # 建议速度遍历从30km/h开始
toSpeed = 80 # 建议速度遍历到80km/h结束
desGap = 5 # 速度建议的精度(km/h)

###############################################################################

LinksID = [1, 2, 3] # 存储目标路段的ID
allLinksID = [1,101,2,102,3,103,4] # 存储全部路段的ID
LinksLength = [921.4, 1912.7, 987.3] # 储存每个目标路段的长度

# SignalHeadsID = [1,5,9] # 储存着目标路段的代表信号灯头ID
SignalHeadsPos = [858.7, 1838.7, 982.7] # 存储着信号灯的位置信息

SignalCycle = 72 # 信号灯周期
SignalRed = 54 # 红灯时长
SignalHead_offset = {1:0, 2:0, 3:0} # 每个目标路段对应的信号灯offset
# SignalHead_offset = {1:70, 2:45, 3:41} # 每个目标路段对应的信号灯offset

# 先构建一个路段长度表
links_Length = [(1,921.4),(101,28.2),(2,1912.7),(102,30.8),(3,987.3),(103,85.4),(4,386.7)]
# 然后由路段长度表生成一个路段累计长度字典
links_Length_Added = {}
length = 0
for item in links_Length:
    linkID = item[0]
    links_Length_Added[linkID] = round(length,2)
    length += round(item[1],2)

GuidancePoints = [[],[],[]] # 储存每个目标路段的引导点位置
#处理一下路段各个路段的引导点位置
for i in range(len(LinksID)):
    signalHeadPos = SignalHeadsPos[i]
    guidancePoint = GuidancePoints[i]
    l = signalHeadPos - Guidance_Lengeh - 2.0 # 预留2米作为停车线
    while l > 0 :
        guidancePoint.append(round(l,2))
        l = l - Guidance_Lengeh

###############################################################################

datas = [] # 储存全部车辆数据
QueueLength_list = {} # 实时路段排队信息
Speed_Guidance = {} # 存储引导速度信息




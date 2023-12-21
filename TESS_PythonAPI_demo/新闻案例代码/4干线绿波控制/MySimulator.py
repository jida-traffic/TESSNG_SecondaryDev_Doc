from PySide2.QtCore import *
from PySide2.QtGui import *
from shiboken2.shiboken2 import wrapInstance

from Tessng import TessInterface, SimuInterface, PyCustomerSimulator, IVehicle, ILink
from Tessng import m2p, p2m, tessngIFace, tessngPlugin
from Tessng import *
import function
import json

# 用户插件子类，代表用户自定义与仿真相关的实现逻辑，继承自PyCustomerSimulator
#     多重继承中的父类QObject，在此目的是要能够自定义信号signlRunInfo
class MySimulator(QObject, PyCustomerSimulator):
    signalRunInfo = Signal(str)
    forStopSimu = Signal()
    forReStartSimu = Signal()
    
    def __init__(self, net):
        QObject.__init__(self)
        PyCustomerSimulator.__init__(self)
        self.mNetInf = net
        # 车辆方阵的车辆数

    # def afterStart(self):


    # 过载的父类方法，TESS NG 在每个计算周期结束后调用此方法，大量用户逻辑在此实现，注意耗时大的计算要尽可能优化，否则影响运行效率
    def afterOneStep(self):
        #= == == == == == =以下是获取一些仿真过程数据的方法 == == == == == ==
        # TESSNG 顶层接口
        iface = tessngIFace()
        # TESSNG 仿真子接口
        simuiface = iface.simuInterface()
        # TESSNG 路网子接口
        netiface = iface.netInterface()
        pynetiface = PyCustomerNet()
        # 当前仿真计算批次
        batchNum = simuiface.batchNumber()
        # 当前已仿真时间，单位：毫秒
        simuTime = simuiface.simuTimeIntervalWithAcceMutiples()
        # print(simuTime)



        if int(simuTime / (180 * 1000)) == 1 and simuTime % (180 * 1000) == 0:
            print('当前仿真时间:{}s'.format(simuTime/1000))
            params = json.load(open('param.json', encoding='utf-8'))
            cor_groups = params['groupIdLst']

            origin_groups = {}
            for group_id in cor_groups:
                group = netiface.findSignalGroup(group_id)
                period_time = group.periodTime()
                phase_interval_dict = {}
                for phase in group.phases():
                    start_time = 0
                    for color_interval in phase.listColor():
                        if color_interval.color == '红':
                            start_time += color_interval.interval
                        elif color_interval.color == '绿':
                            green_interval = color_interval.interval
                        elif color_interval.color == '黄':
                            yellow_interval = color_interval.interval
                            break
                    phase_interval_dict[phase.id()] = {'phase_id': phase.id(), 'start_time': start_time,
                                                       'green_interval': green_interval,
                                                       'yellow_interval': yellow_interval,
                                                       'all_red_interval': 0}
                origin_groups[group_id] = {'period_time': period_time, 'phases': phase_interval_dict}

            # maxband计算干线周期和协调相位差
            print('maxband计算干道绿波方案')
            C, o_lst = function.maxband()
            new_groups = function.cal_groups(origin_groups, C, o_lst)
            for group_id, new_group in new_groups.items():
                group = netiface.findSignalGroup(group_id)
                new_period_time = new_group['period_time']
                group.setPeriodTime(new_period_time)
                for phase_id, new_phase in new_group['phases'].items():
                    phase = netiface.findSignalPhase(phase_id)
                    start_time = new_phase.get('start_time')
                    green_interval = new_phase.get('green_interval')
                    yellow_interval = new_phase.get('yellow_interval')
                    new_color_lst = []
                    if start_time + green_interval > new_period_time:  # 该相位绿灯时间将被截断
                        new_color_lst.append(Online.ColorInterval('红', max(start_time + green_interval - new_period_time - green_interval, 0)))
                        new_color_lst.append(Online.ColorInterval('绿', min(start_time + green_interval - new_period_time, green_interval)))
                        new_color_lst.append(Online.ColorInterval('黄', yellow_interval))
                        new_color_lst.append(Online.ColorInterval('红', start_time - (
                                    start_time + green_interval - new_period_time) - yellow_interval))
                        new_color_lst.append(Online.ColorInterval('绿', new_period_time - start_time))
                    elif start_time + green_interval + yellow_interval > new_period_time:  # 该相位黄灯时间将被截断
                        new_color_lst.append(
                            Online.ColorInterval('黄', start_time + green_interval + yellow_interval - new_period_time))
                        new_color_lst.append(Online.ColorInterval('红', start_time - (start_time + green_interval + yellow_interval - new_period_time)))
                        new_color_lst.append(Online.ColorInterval('绿', green_interval))
                        new_color_lst.append(Online.ColorInterval('黄', yellow_interval - (start_time + green_interval + yellow_interval - new_period_time)))
                    else:
                        new_color_lst.append(Online.ColorInterval('红', start_time))
                        new_color_lst.append(Online.ColorInterval('绿', green_interval))
                        new_color_lst.append(Online.ColorInterval('黄', yellow_interval))
                        new_color_lst.append(Online.ColorInterval('红', max((new_period_time - start_time - green_interval - yellow_interval), 0)))
                    phase.setColorList(new_color_lst)
            print('已修改信控方案')


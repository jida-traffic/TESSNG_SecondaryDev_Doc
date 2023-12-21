from PySide2.QtCore import *
from PySide2.QtGui import *
from shiboken2.shiboken2 import wrapInstance

import config
from Tessng import TessInterface, SimuInterface, PyCustomerSimulator, IVehicle, ILink
from Tessng import m2p, p2m, tessngIFace, tessngPlugin
from Tessng import *
import config
import function

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



        if simuTime / (config.aggregate_time * 1000) > 1 and simuTime % (config.aggregate_time * 1000) == 1 * 1000:
            print('仿真第{}秒'.format(simuTime/1000))
            # 每个流向上一个集计间隔的流量
            collectors = simuiface.getVehisInfoAggregated()
            collector_flow_dict = {}
            for collector in collectors:
                collector_id = collector.collectorId
                veh_count = collector.vehiCount
                aggregate_time = collector.toTime - collector.fromTime
                flow = veh_count / aggregate_time * 3600    # 扩大为小时流量
                collector_flow_dict[collector_id] = flow
            phase_flow_dict = {}
            for phase_id, collector_lst in config.phase2collector_dict.items():
                phase_flow_dict[phase_id] = sum([collector_flow_dict[collector_id] for collector_id in collector_lst]) / len(collector_lst)    # 计算每相位单车道的流量
            # print(phase_flow_dict)

            # 每个相位当前绿灯时间
            group = netiface.signalGroups()[0]
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
                phase_interval_dict[phase.id()] = {'phase_id': phase.id(), 'start_time': start_time, 'green_interval': green_interval, 'yellow_interval': yellow_interval, 'all_red_interval': 0}
            # print(phase_interval_dict)

            # 计算韦伯斯特信号配时
            new_period_time, new_phase_interval_dict = function.webster(period_time, phase_interval_dict, phase_flow_dict)
            # print(new_period_time, new_phase_interval_dict)

            # 修改仿真中的信控方案
            group.setPeriodTime(new_period_time)
            for phase in group.phases():
                new_phase = new_phase_interval_dict[phase.id()]
                new_color_lst = []
                new_color_lst.append(Online.ColorInterval('红', new_phase.get('start_time')))
                new_color_lst.append(Online.ColorInterval('绿', new_phase.get('green_interval')))
                new_color_lst.append(Online.ColorInterval('黄', new_phase.get('yellow_interval')))
                new_color_lst.append(Online.ColorInterval('红', max((new_period_time - new_phase.get('start_time') - new_phase.get('green_interval') - new_phase.get('yellow_interval')), 0)))
                phase.setColorList(new_color_lst)
            print('已更新信控方案')


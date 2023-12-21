import math
import config

def webster(period_time, phase_interval_dict, phase_flow_dict):
    # 相位数
    k = len(phase_interval_dict)

    # 全红时间
    all_red_interval_lst = [content['all_red_interval'] for key, content in phase_interval_dict.items()]

    # 黄灯时间
    yellow_interval_lst = [content['yellow_interval'] for key, content in phase_interval_dict.items()]

    # 计算信号总损失时间L
    L = sum(all_red_interval_lst) + sum(yellow_interval_lst)

    # 各相位车道数和流量
    flow_lst = [phase_flow_dict[phase] for phase in phase_interval_dict.keys()]

    # 计算流量比
    y_lst = [i / config.capacity for i in flow_lst]
    total_y = sum(y_lst)

    # 计算交叉口周期C（向上取整）
    c0 = period_time
    c = math.ceil(L / (1 - total_y))
    c = min(max(c, c0 * 0.5), c0 * 2)    # 周期取值范围
    new_period_time = c

    # 计算总有效绿灯时间G_e（向下取整）
    G_e = c - math.floor(L)

    # 计算有效绿灯时间g_e
    green_interval_lst = [math.floor((y_lst[i] / total_y) * G_e) for i in range(k)]

    # 调整有效绿灯时间g_e，保证其值之和等于总有效绿灯时间G_e
    green_interval_lst[-1] += G_e - sum(green_interval_lst)

    # 新的信号灯组
    new_phase_interval_dict = {}
    for phase, content in phase_interval_dict.items():
        i = list(phase_interval_dict.keys()).index(phase)
        new_phase_interval_dict[phase] = {'phase_id': phase, 'start_time': sum(green_interval_lst[:i]) + sum(yellow_interval_lst[:i]),
                                        'green_interval': green_interval_lst[i], 'yellow_interval': yellow_interval_lst[i], 'all_red_interval': all_red_interval_lst[i]}
    return new_period_time, new_phase_interval_dict


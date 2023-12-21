import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime


def plot_traffic_ratios(times, ratios_list):
    '''
    绘制时间-流量比的柱状图
    :param times: 排队计数器集计时间列表
    :param ratios_list: 集计时间列表对应的交通流量比
    :return:
    '''

    # 设置横坐标刻度和标签
    x_labels = [str(time) for time in times]
    index = np.arange(len(times))
    bar_width = 0.15

    # 绘制柱状图
    fig, ax = plt.subplots()
    for i, ratio in enumerate(np.array(ratios_list).T):
        ax.bar(index + i * bar_width, ratio, bar_width, label=f'{["Right", "Left", "Straight"][i]} Turn')

    # 设置图表标题和标签
    ax.set_title('Traffic Ratios Over Time')
    ax.set_xlabel('Time')
    ax.set_ylabel('Traffic Ratios')

    # 设置横坐标刻度和标签
    ax.set_xticks(index + bar_width)
    ax.set_xticklabels(x_labels)

    # 显示图例
    ax.legend()

    # 获取当前日期时间并格式化为字符串
    current_time = datetime.now().strftime('%Y%m%d_%H%M%S')

    # 构建保存文件名
    save_path = f"./VehiQueueResult/{current_time}_300s_interval_Time2TrafficRatios.png"

    # 保存图表
    plt.savefig(save_path)

    # 显示图表
    plt.show()


def plot_queue_lengths(times, queue_lengths_dict):
    '''
        绘制时间-平均排队长度的柱状图
        :param times: 排队计数器集计时间列表
        :param ratios_list: 集计时间列表对应的各车道平均排队长度
        :return:
    '''
    # 提取左转和直行的平均排队长度
    left_turn_lengths = queue_lengths_dict.get(4501, [])
    straight_lengths_1 = queue_lengths_dict.get(4502, [])
    straight_lengths_2 = queue_lengths_dict.get(4503, [])
    straight_lengths_3 = queue_lengths_dict.get(4504, [])

    # 设置横坐标刻度和标签
    x_labels = [str(time) for time in times]
    index = np.arange(len(times))
    bar_width = 0.15

    # 绘制柱状图
    fig, ax = plt.subplots()
    bar1 = ax.bar(index - bar_width, left_turn_lengths, bar_width, label='Left Turn')
    bar2 = ax.bar(index, straight_lengths_1, bar_width, label='Straight lane 1')
    bar3 = ax.bar(index + bar_width, straight_lengths_2, bar_width, label='Straight lane 2')
    bar4 = ax.bar(index + bar_width * 2, straight_lengths_3, bar_width, label='Straight lane 3')

    # 设置图表标题和标签
    ax.set_title('Average Queue Lengths Over Time')
    ax.set_xlabel('Time')
    ax.set_ylabel('Average Queue Length')

    # 设置横坐标刻度和标签
    ax.set_xticks(index)
    ax.set_xticklabels(x_labels)

    # 显示图例
    ax.legend()

    # 获取当前日期时间并格式化为字符串
    current_time = datetime.now().strftime('%Y%m%d_%H%M%S')

    # 构建保存文件名
    save_path = f"./VehiQueueResult/{current_time}_300s_interval_Time2QueueLength.png"

    # 保存图表
    plt.savefig(save_path)

    # 显示图表
    plt.show()

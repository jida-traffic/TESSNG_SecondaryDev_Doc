import os
import logging
import numpy as np


# 传入某一路段上的车辆数据 lAllVehi，计算此时该路段上的速度均值、速度标准差、流量
def calc_state(lAllVehis):
    vs = [vehi.currSpeed() for lAllVehi in lAllVehis for vehi in lAllVehi] # m/s
    if vs:
        return [np.mean(vs), np.std(vs), len(vs)]
    else:
        return [0, 0, 0]


# 传入某一路段上的车辆数据lAllVehi，计算此时该路段上的速度均值、速度标准差、低速车辆数（速度低于50km/h），输出Reward Value
def calc_reward(lAllVehis):
    vs = [vehi.currSpeed() for lAllVehi in lAllVehis for vehi in lAllVehi]
    num = sum(1 for speed in vs if speed * 3.6 < 50)
    if vs:
        return 0.6*np.mean(vs) - np.std(vs) - 0.6*num
    else:
        return 0

# 记录日志
def setup_logger(log_file='example.log', level=logging.INFO):
    # 创建日志记录器对象
    logger = logging.getLogger(__name__)

    # 清空已存在的处理程序和过滤器，以防止重复添加
    logger.handlers = []
    logger.filters = []

    # 配置日志记录器
    logging.basicConfig(
        filename=log_file,  # 将日志信息写入文件
        level=level,  # 设置日志级别
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # 创建一个处理程序
    handler = logging.StreamHandler() # 输出到控制台
    handler.setLevel(level)  # 设置控制台处理程序的日志级别

    # 创建一个格式化器，定义控制台输出的日志信息格式
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # 将控制台处理程序添加到日志记录器
    logger.addHandler(handler)

    return logger


# # 创建用于保存模型参数的文件夹
# path = 'model_parm'
# if not os.path.isdir(path):
#     os.makedirs(path)


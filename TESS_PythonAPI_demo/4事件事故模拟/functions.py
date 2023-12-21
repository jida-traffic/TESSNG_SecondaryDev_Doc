import math

def car_position_road(lane_startPoint, lane_endPoint, vehicle_point):
    '''
    判断车辆位于直线左侧还是右侧
    :param lane_startPoint:线段向量起点
    :param lane_endPoint:线段向量终点
    :param vehicle_point: 车辆坐标
    :return: 车辆位于哪侧的字符串
    '''
    x1, y1 = lane_startPoint.x(), lane_startPoint.y()
    x2, y2 = lane_endPoint.x(), lane_endPoint.y()
    x, y = vehicle_point.x(), vehicle_point.y()

    # 计算直线上两点的向量
    line_vector = (x2 - x1, y2 - y1)

    # 计算直线的法向量（垂直于直线的向量）
    normal_vector = (-line_vector[1], line_vector[0])

    # 计算直线上一个点到车辆的向量
    car_vector = (x - x1, y - y1)

    # 计算叉积
    cross_product = (car_vector[0] * normal_vector[0]) + (car_vector[1] * normal_vector[1])

    # 判断车辆位置
    if cross_product > 0:
        return "right"
    elif cross_product < 0:
        return "left"
    else:
        return "on"


def calculate_angle(startPoint, endPoint):
    '''
    计算向量与y轴负方向夹角，顺时针旋转
    :param startPoint:起点
    :param endPoint: 终点
    :return:
    '''
    x1, y1 = startPoint.x(), startPoint.y()
    x2, y2 = endPoint.x(), endPoint.y()
    # 计算两点之间的差值
    dx = x2 - x1
    dy = y2 - y1

    # 使用atan2计算夹角（弧度）
    angle_radians = math.atan2(dy, dx)

    # 将弧度转换为角度
    angle_degrees = math.degrees(angle_radians)

    # 修正角度，使其符合软件的定义方式
    angle_degrees = (angle_degrees + 360) % 360  # 将角度转为正值
    angle_degrees = (angle_degrees - 90) % 360  # 修正角度，使向上为0度

    # 修正左右方向
    angle_degrees = (angle_degrees + 180) % 360  # 修正左右方向

    return angle_degrees

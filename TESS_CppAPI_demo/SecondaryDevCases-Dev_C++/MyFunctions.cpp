#include "MyFunctions.h"

long Functions::timeToSeconds(QString& timeStr) {
    // 使用冒号分割小时和分钟部分
    QStringList timeParts = timeStr.split(':');

    // 将小时和分钟部分转换为整数
    int hours = timeParts[0].toInt();
    int minutes = timeParts[1].toInt();

    // 计算总秒数
    int totalSeconds = hours * 3600 + minutes * 60;

    return totalSeconds;
}

// 判断车辆位于直线左侧还是右侧
QString Functions::carPositionRoad(QPointF& laneStartPoint, QPointF& laneEndPoint, QPointF& vehiclePoint) {
    /*
    判断车辆位于直线左侧还是右侧
    :param laneStartPoint: 线段向量起点
    :param laneEndPoint: 线段向量终点
    :param vehiclePoint: 车辆坐标
    :return: 车辆位于哪侧的字符串
    */
    qreal x1 = laneStartPoint.x(), y1 = laneStartPoint.y();
    qreal x2 = laneEndPoint.x(), y2 = laneEndPoint.y();
    qreal x = vehiclePoint.x(), y = vehiclePoint.y();

    // 计算直线上两点的向量
    QPointF lineVector(x2 - x1, y2 - y1);

    // 计算直线的法向量（垂直于直线的向量）
    QPointF normalVector(-lineVector.y(), lineVector.x());

    // 计算直线上一个点到车辆的向量
    QPointF carVector(x - x1, y - y1);

    // 计算叉积
    qreal crossProduct = (carVector.x() * normalVector.x()) + (carVector.y() * normalVector.y());

    // 判断车辆位置
    if (crossProduct > 0) {
        return "right";
    }
    else if (crossProduct < 0) {
        return "left";
    }
    else {
        return "on";
    }
}

// 计算向量与y轴负方向夹角，顺时针旋转
double Functions::calculateAngle(QPointF& startPoint, QPointF& endPoint) {
    /*
    计算向量与y轴负方向夹角，顺时针旋转
    :param startPoint: 起点
    :param endPoint: 终点
    :return: 夹角（角度）
    */
    qreal x1 = startPoint.x(), y1 = startPoint.y();
    qreal x2 = endPoint.x(), y2 = endPoint.y();

    // 计算两点之间的差值
    qreal dx = x2 - x1;
    qreal dy = y2 - y1;

    // 使用atan2计算夹角（弧度）
    qreal angleRadians = qAtan2(dy, dx);

    // 将弧度转换为角度
    qreal angleDegrees = qRadiansToDegrees(angleRadians);

    // 修正角度，使其符合软件的定义方式
    angleDegrees = fmod(angleDegrees + 360, 360);  // 将角度转为正值
    angleDegrees = fmod(angleDegrees - 90, 360);   // 修正角度，使向上为0度

    // 修正左右方向
    angleDegrees = fmod(angleDegrees + 180, 360);  // 修正左右方向

    return angleDegrees;
}


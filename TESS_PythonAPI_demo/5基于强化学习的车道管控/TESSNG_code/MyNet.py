from PySide2.QtCore import *

from DLLs.Tessng import PyCustomerNet, tessngIFace, m2p, p2m, Online


# 用户插件子类，代表用户自定义与路网相关的实现逻辑，继承自MyCustomerNet
class MyNet(PyCustomerNet):
    def __init__(self):
        super(MyNet, self).__init__()

        self.lane_count = 4
        self.flow = 4200

    # 创建路网
    def createNet(self):
        # 代表TESS NG的接口
        iface = tessngIFace()
        # 代表TESS NG的路网子接口
        netiface = iface.netInterface()

        # 设置场景高度和宽度
        netiface.setSceneSize(4000, 400)

        # 路段1
        startPoint = QPointF(m2p(-2000), 0)
        endPoint = QPointF(m2p(-1000-5), 0)
        lPoint = [startPoint, endPoint]
        link1 = netiface.createLink(lPoint, self.lane_count, "frist")
        link1.setLimitSpeed(120)
        dp = netiface.createDispatchPoint(link1)
        if dp != None :
            # 设置发车间隔，含车型组成、时间间隔、发车数
            dp.addDispatchInterval(1, 3600, self.flow)
        
        # 路段2
        startPoint = QPointF(m2p(-1000), 0)
        endPoint = QPointF(m2p(0-5), 0)
        lPoint = [startPoint, endPoint]
        link2 = netiface.createLink(lPoint, self.lane_count, "second")
        link2.setLimitSpeed(120)
        
        # 路段3
        startPoint = QPointF(m2p(-0), 0)
        endPoint = QPointF(m2p(1000-5), 0)
        lPoint = [startPoint, endPoint]
        link3 = netiface.createLink(lPoint, self.lane_count, "third")
        link3.setLimitSpeed(120)

        # 路段4
        startPoint = QPointF(m2p(1000), 0)
        endPoint = QPointF(m2p(2000), 0)
        lPoint = [startPoint, endPoint]
        link4 = netiface.createLink(lPoint, self.lane_count, "fourth")
        link4.setLimitSpeed(120)

        # 连接段
        lFromLaneNumber = [i+1 for i in range(self.lane_count)]
        lToLaneNumber = [i+1 for i in range(self.lane_count)]
        netiface.createConnector(link1.id(), link2.id(), lFromLaneNumber, lToLaneNumber, "连接段1-2", True)
        netiface.createConnector(link2.id(), link3.id(), lFromLaneNumber, lToLaneNumber, "连接段2-3", True)
        netiface.createConnector(link3.id(), link4.id(), lFromLaneNumber, lToLaneNumber, "连接段3-4", True)

        # 施工区
        param = Online.DynaRoadWorkZoneParam()
        param.roadId = 3
        param.location = 700
        param.length = 300
        param.mlFromLaneNumber = [1,2]
        param.limitSpeed = 60
        param.duration = 0
        netiface.createRoadWorkZone(param)

    def afterLoadNet(self):
        # 代表TESS NG的接口
        iface = tessngIFace()
        # 代表TESS NG的路网子接口
        netiface = iface.netInterface()

        # 获取路段数
        count = netiface.linkCount()
        if(count == 0):
            self.createNet()


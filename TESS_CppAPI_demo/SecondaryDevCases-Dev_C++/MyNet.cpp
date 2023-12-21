#include "MyNet.h"

#include <QMessageBox>

#include "IRoadNet.h"
#include "tessinterface.h"
#include "netinterface.h"
#include "simuinterface.h"
#include "Plugin/_netitemtype.h"
#include "IDispatchPoint.h"
#include "ilink.h"
#include "IConnector.h"
#include "ILaneConnector.h"
#include "UnitChange.h"
#include "IGuidArrow.h"
#include "IVehicleTravelDetector.h"
#include "IVehicleQueueCounter.h"
#include "IVehicleDrivInfoCollector.h"
#include "IBusLine.h"
#include "IBusStation.h"
#include "ISignalGroup.h"
#include "ISignalPhase.h"
#include "isignallamp.h"
#include "IDecisionPoint.h"
#include "IRouting.h"
#include "ISection.h"

MyNet::MyNet(SecondaryDevCases* pSecondDevCasesObj) :mpSecondDevCasesObj(pSecondDevCasesObj) {
}

//加载路网前的准备
void MyNet::beforeLoadNet() {
	//QMessageBox::information(nullptr, QString(), QString("加载路网前的准备"));
}

//加载完路网后的行为
void MyNet::afterLoadNet() {
	/* 原createNet方法见 TESSNG V2.0二次开发版本案例 */

	//如果配置文件配置了加载后启动仿真，则TESSNG会启动仿真，本方法不用启动仿真，否则本方法启动仿真
	QJsonObject config = gpTessPlugin->tessngConfig();
	if (config.value("__simuafterload").isBool() && config.value("__simuafterload").toBool())
	{
		return;
	}

	/* Supplementary Methods */
	//3 - 根据路段，车道序号获取检测器(机动车交叉口案例：L5路段为起点，L9路段为终点)
	QList<IVehicleTravelDetector*>  lvehiTravelDetectors = gpTessInterface->netInterface()->vehiTravelDetectors();
	for (IVehicleTravelDetector*& pVehicleTravelDetector : lvehiTravelDetectors) {
		ILink* linkStartDetector = pVehicleTravelDetector->link_startDetector();
		ILink* linkEndDetector = pVehicleTravelDetector->link_endDetector();
		if (linkStartDetector) {
			if (linkStartDetector->id() == 5) {
				qDebug() << "find the startVehicleTravelDetector in L5:" << pVehicleTravelDetector->id() << endl;
			}
		}
		if (linkEndDetector) {
			if (linkEndDetector->id() == 9) {
				qDebug() << "find the endVehicleTravelDetector in L9:" << pVehicleTravelDetector->id() << endl;
			}
		}
	}
}

//创建路网，包含了一些基础API的使用，用户可在afterLoadNet函数中调用createNet使用。
void MyNet::createNet() {
	IRoadNet* pRoadNet = gpTessInterface->netInterface()->setNetAttrs("API创建路网", "OPENDRIVE");
	qDebug() << pRoadNet->netName();

	//第一条路段
	QPointF startPoint = QPointF(m2p(-300), 0);//m2p(数字)后的坐标可以对上原点在中心的坐标，TESSNG中的坐标始终是像素
	QPointF endPoint = QPointF(m2p(300), 0);
	QList<QPointF> lPoint;
	lPoint << startPoint;
	lPoint << endPoint;
	ILink* pLink1 = gpTessInterface->netInterface()->createLink(lPoint, 7, "曹安公路");

	if (pLink1) {
		//创建发车点
		IDispatchPoint* pDp = gpTessInterface->netInterface()->createDispatchPoint(pLink1);
		if (pDp) {
			pDp->addDispatchInterval(1, 2, 28);//2秒28辆车
		}
	}

	//创建第二条路段
	startPoint = QPointF(m2p(-300), m2p(-25));
	endPoint = QPointF(m2p(300), m2p(-25));
	lPoint.clear();
	lPoint << startPoint;
	lPoint << endPoint;
	ILink* pLink2 = gpTessInterface->netInterface()->createLink(lPoint, 3, "次干道");
	if (pLink2) {
		//创建发车点
		IDispatchPoint* pDp = gpTessInterface->netInterface()->createDispatchPoint(pLink2);
		if (pDp) {
			pDp->addDispatchInterval(1, 3600, 3600);
		}
		//修改车道类型
		pLink2->lanes()[0]->setLaneType(QObject::tr("公交专用道"));
	}

	//创建第三条路段
	startPoint = QPointF(m2p(-300), m2p(25));
	endPoint = QPointF(m2p(-150), m2p(25));
	lPoint.clear();
	lPoint << startPoint;
	lPoint << endPoint;
	ILink* pLink3 = gpTessInterface->netInterface()->createLink(lPoint, 3);
	if (pLink3) {
		//创建发车点
		IDispatchPoint* pDp = gpTessInterface->netInterface()->createDispatchPoint(pLink3);
		if (pDp) {
			pDp->addDispatchInterval(1, 3600, 3600);
		}
	}

	//创建第四条路段
	startPoint = QPointF(m2p(-50), m2p(25));
	endPoint = QPointF(m2p(50), m2p(25));
	lPoint.clear();
	lPoint << startPoint;
	lPoint << endPoint;
	ILink* pLink4 = gpTessInterface->netInterface()->createLink(lPoint, 3);

	//创建第五条路段
	startPoint = QPointF(m2p(150), m2p(25));
	endPoint = QPointF(m2p(300), m2p(25));
	lPoint.clear();
	lPoint << startPoint;
	lPoint << endPoint;
	ILink* pLink5 = gpTessInterface->netInterface()->createLink(lPoint, 3, "自定义限速路段");
	if (pLink5) {
		pLink5->setLimitSpeed(30);
	}

	//创建第六条路段
	startPoint = QPointF(m2p(-300), m2p(50));
	endPoint = QPointF(m2p(300), m2p(50));
	lPoint.clear();
	lPoint << startPoint;
	lPoint << endPoint;
	ILink* pLink6 = gpTessInterface->netInterface()->createLink(lPoint, 3, "动态发车路段");
	if (pLink6) {
		pLink6->setLimitSpeed(80);
	}

	//创建第七条路段
	startPoint = QPointF(m2p(-300), m2p(75));
	endPoint = QPointF(m2p(-250), m2p(75));
	lPoint.clear();
	lPoint << startPoint;
	lPoint << endPoint;
	ILink* pLink7 = gpTessInterface->netInterface()->createLink(lPoint, 3);
	if (pLink7) {
		pLink7->setLimitSpeed(80);
	}

	//创建第八条路段
	startPoint = QPointF(m2p(-50), m2p(75));
	endPoint = QPointF(m2p(300), m2p(75));
	lPoint.clear();
	lPoint << startPoint;
	lPoint << endPoint;
	ILink* pLink8 = gpTessInterface->netInterface()->createLink(lPoint, 3);
	if (pLink8) {
		pLink8->setLimitSpeed(80);
	}

	//创建测试路段
	startPoint = QPointF(m2p(-300), m2p(100));
	endPoint = QPointF(m2p(300), m2p(100));
	lPoint.clear();
	lPoint << startPoint;
	lPoint << endPoint;
	ILink* pLink9 = gpTessInterface->netInterface()->createLink(lPoint, 3);
	if (pLink9) {
		//创建发车点
		IDispatchPoint* pDp = gpTessInterface->netInterface()->createDispatchPoint(pLink9);
		if (pDp) {
			pDp->addDispatchInterval(1, 100, 200);
		}
	}

	//创建路段10
	startPoint = QPointF(m2p(-300), m2p(125));
	endPoint = QPointF(m2p(-100), m2p(125));
	lPoint.clear();
	lPoint << startPoint;
	lPoint << endPoint;
	ILink* pLink10 = gpTessInterface->netInterface()->createLink(lPoint, 3);
	if (pLink10) {
		//创建发车点
		IDispatchPoint* pDp = gpTessInterface->netInterface()->createDispatchPoint(pLink10);
		if (pDp) {
			pDp->addDispatchInterval(1, 50, 50);
			pDp->addDispatchInterval(1, 100, 50);
		}
		//修改车道类型
		pLink10->lanes()[0]->setLaneType(QObject::tr("公交专用道"));
	}

	//创建路段11
	startPoint = QPointF(m2p(0), m2p(150));
	endPoint = QPointF(m2p(300), m2p(150));
	lPoint.clear();
	lPoint << startPoint;
	lPoint << endPoint;
	ILink* pLink11 = gpTessInterface->netInterface()->createLink(lPoint, 3);
	//if (pLink11) {
	//	//修改车道类型
	//	pLink11->lanes()[0]->setLaneType(QObject::tr("公交专用道"));
	//}

	//创建路段12
	startPoint = QPointF(m2p(0), m2p(125));
	endPoint = QPointF(m2p(300), m2p(125));
	lPoint.clear();
	lPoint << startPoint;
	lPoint << endPoint;
	ILink* pLink12 = gpTessInterface->netInterface()->createLink(lPoint, 3);

	//创建路段13
	startPoint = QPointF(m2p(-300), m2p(150));
	endPoint = QPointF(m2p(-100), m2p(150));
	lPoint.clear();
	lPoint << startPoint;
	lPoint << endPoint;
	ILink* pLink13 = gpTessInterface->netInterface()->createLink(lPoint, 3);

	//创建第一条连接段
	if (pLink3 && pLink4) {
		QList<int> lFromLaneNumber = QList<int>() << 1 << 2 << 3;
		QList<int> lToLaneNumber = QList<int>() << 1 << 2 << 3;
		IConnector* pConn1 = gpTessInterface->netInterface()->createConnector(pLink3->id(), pLink4->id(), lFromLaneNumber, lToLaneNumber
			, "连接段1");
	}

	//创建第二条连接段
	if (pLink4 && pLink5) {
		IConnector* pConn2 = gpTessInterface->netInterface()->createConnector(pLink4->id(), pLink5->id(), QList<int>() << 1 << 2 << 3, QList<int>() << 1 << 2 << 3, "连接段2");
	}

	//创建第三条连接段
	if (pLink7 && pLink8) {
		IConnector* pConn3 = gpTessInterface->netInterface()->createConnector(pLink7->id(), pLink8->id(), QList<int>() << 1 << 2 << 3, QList<int>() << 1 << 2 << 3, "动态发车连接段");
	}

	//创建路段10和路段11的连接段
	if (pLink10 && pLink11) {
		IConnector* pConn4 = gpTessInterface->netInterface()->createConnector(pLink10->id(), pLink11->id(), QList<int>() << 1 << 1 << 1, QList<int>() << 3 << 2 << 1, "连接段4");
		//创建公交线路
		IBusLine* pBusLine = gpTessInterface->netInterface()->createBusLine(QList<ILink*>() << pLink10 << pLink11);
		if (pBusLine) {
			pBusLine->setDesirSpeed(m2p(60));
			IBusStation* pBusStation1 = gpTessInterface->netInterface()->createBusStation(pLink10->lanes()[0], m2p(30), m2p(50), "公交站1");
			IBusStation* pBusStation2 = gpTessInterface->netInterface()->createBusStation(pLink11->lanes()[0], m2p(15), m2p(50), "公交站2");
			if (pBusStation1 && gpTessInterface->netInterface()->addBusStationToLine(pBusLine, pBusStation1)) {
				pBusStation1->setType(2);
				qDebug() << "公交站1已关联到公交线路" << endl;
			}
			if (pBusStation2 && gpTessInterface->netInterface()->addBusStationToLine(pBusLine, pBusStation2)) {
				qDebug() << "公交站2已关联到公交线路" << endl;
			}
		}
		//动态创建公交车
		IVehicle* pBus = gpTessInterface->simuInterface()->createBus(pBusLine, 10 * 1000);
		QList<IBusStationLine*> lStationLine = pBusLine->stationLines();
		if (!lStationLine.isEmpty())
		{
			IBusStationLine* pStationLine = lStationLine.first();
			pStationLine->setBusParkingTime(20);
		}
	}

	//创建路段10和路段12的连接段
	if (pLink10 && pLink12) {
		IConnector* pConn5 = gpTessInterface->netInterface()->createConnector(pLink10->id(), pLink12->id(), QList<int>() << 1 << 2 << 3, QList<int>() << 1 << 2 << 3, "连接段5");
	}

	//创建路段13和路段12的连接段
	if (pLink12 && pLink13) {
		IConnector* pConn6 = gpTessInterface->netInterface()->createConnector(pLink13->id(), pLink12->id(), QList<int>() << 3 << 3 << 3, QList<int>() << 1 << 2 << 3, "连接段6");
	}

	//创建信号灯组
	ISignalGroup* pSignalGroup = gpTessInterface->netInterface()->createSignalGroup(QObject::tr("信号灯组1"), 60, 1, 3600);
	//创建相位
	Online::ColorInterval red("R", 28), green("G", 29), yellow("Y", 3);
	ISignalPhase* pSignalPhase = gpTessInterface->netInterface()->createSignalPhase(pSignalGroup, QObject::tr("信号灯组1相位1"), QList<Online::ColorInterval>() << red << yellow << green);
	//创建信号灯
	ISignalLamp* pSignalLamp1 = gpTessInterface->netInterface()->createSignalLamp(pSignalPhase, QObject::tr("信号灯1"), 32, 35, m2p(2));
	ISignalLamp* pSignalLamp2 = gpTessInterface->netInterface()->createSignalLamp(pSignalPhase, QObject::tr("信号灯2"), 34, 37, m2p(2));

	//创建决策点
	IDecisionPoint* pDecisionPoint = gpTessInterface->netInterface()->createDecisionPoint(pLink10, m2p(100));
	//新建决策路径
	IRouting* pDecisionRouting1 = gpTessInterface->netInterface()->createDeciRouting(pDecisionPoint, QList<ILink*>() << pLink10 << pLink12);
	IRouting* pDecisionRouting2 = gpTessInterface->netInterface()->createDeciRouting(pDecisionPoint, QList<ILink*>() << pLink10 << pLink11);
	//创建不同时段流量比
	_RoutingFLowRatio flowRatio1, flowRatio2, flowRatio3, flowRatio4;
	flowRatio1.RoutingFLowRatioID = 1;
	flowRatio1.routingID = pDecisionRouting1->id();
	flowRatio1.startDateTime = 0;
	flowRatio1.endDateTime = 100;
	flowRatio1.ratio = 0.0;
	flowRatio2.RoutingFLowRatioID = 2;
	flowRatio2.routingID = pDecisionRouting2->id();
	flowRatio2.startDateTime = 0;
	flowRatio2.endDateTime = 100;
	flowRatio2.ratio = 1.0;
	flowRatio3.RoutingFLowRatioID = 3;
	flowRatio3.routingID = pDecisionRouting1->id();
	flowRatio3.startDateTime = 100;
	flowRatio3.endDateTime = 999999;
	flowRatio3.ratio = 0.5;
	flowRatio4.RoutingFLowRatioID = 4;
	flowRatio4.routingID = pDecisionRouting2->id();
	flowRatio4.startDateTime = 100;
	flowRatio4.endDateTime = 999999;
	flowRatio4.ratio = 0.5;
	_DecisionPoint decisionPoint;
	decisionPoint.deciPointID = pDecisionPoint->id();
	decisionPoint.deciPointName = pDecisionPoint->name();
	QPointF decisionPointPos;
	if (pDecisionPoint->link()->getPointByDist(pDecisionPoint->distance(), decisionPointPos)) {
		decisionPoint.X = decisionPointPos.x();
		decisionPoint.Y = decisionPointPos.y();
		decisionPoint.Z = pDecisionPoint->link()->z();
	}
	//更新决策点及其各路径不同时间段流量比
	pDecisionPoint = gpTessInterface->netInterface()->updateDecipointPoint(decisionPoint, QList<_RoutingFLowRatio>() << flowRatio1 << flowRatio2 << flowRatio3 << flowRatio4);

	//当前“车道连接”穿过其它“车道连接”形成的交叉点列表
	ILaneConnector* pLaneConnector = gpTessInterface->netInterface()->findConnector(6)->laneConnectors()[2];
	QList<Online::CrossPoint> crossPoints = gpTessInterface->netInterface()->crossPoints(pLaneConnector);
	for (Online::CrossPoint crossPoint : crossPoints) {
		qDebug() << "主车道连接，即被交叉的“车道连接”：" << crossPoint.mpLaneConnector->id();
		qDebug() << "交叉点坐标为：(" << crossPoint.mCrossPoint.x() << "," << crossPoint.mCrossPoint.y() << ")" << endl;
	}

	//关闭主窗体或重新打开新的路网，会从内存删除当前路网元素，不必手动删除。

	//在路段4的最右侧车道上添加直行或右转箭头,导向箭头距离路段起终点不能小于9米
	//ILink* link4 = gpTessInterface->netInterface()->findLink(4);
	//if (link4) {
	//	ILane* rightLane4 = link4->lanes().front();
	//	qreal length = m2p(4.0);
	//	qreal distToTerminal = m2p(50);
	//	Online::GuideArrowType arrowType = Online::GuideArrowType::StraightRight;
	//	if (rightLane4) {
	//		IGuidArrow* guideArrow4 = gpTessInterface->netInterface()->createGuidArrow(rightLane4, length, distToTerminal, arrowType);
	//		qDebug() << "导向箭头类型为：" << guideArrow4->arrowType() << endl;
	//	}
	//}

	//在路段9 50-550米处创建行程检测器
	//ILink* link9 = gpTessInterface->netInterface()->findLink(9);
	//if (link9) {
	//	QList<IVehicleTravelDetector*> vehicleTravelDetector9 = gpTessInterface->netInterface()->createVehicleTravelDetector_link2link(link9, link9, m2p(50), m2p(550));
	//	if (!vehicleTravelDetector9.empty()) {
	//		for (IVehicleTravelDetector* detector : vehicleTravelDetector9) {
	//			detector->setFromTime(10);
	//			detector->setToTime(60);
	//		}
	//	}
	//}

	//在路段9最左侧车道100米处创建排队计数器
	//ILink* link9 = gpTessInterface->netInterface()->findLink(9);
	//if (link9) {
	//	ILane* lfetLane9 = link9->lanes().back();
	//	qreal dist = m2p(100);
	//	IVehicleQueueCounter* counter = gpTessInterface->netInterface()->createVehiQueueCounterOnLink(lfetLane9, dist);
	//	qDebug() << "计数器所在点坐标为：" << counter->point().x() << counter->point().y() << endl;
	//}

	//在路段9最左侧车道100米处创建车辆采集器
	//ILink* link9 = gpTessInterface->netInterface()->findLink(9);
	//if (link9) {
	//	ILane* lfetLane9 = link9->lanes().back();
	//	qreal dist = m2p(100);
	//	IVehicleDrivInfoCollector* collector = gpTessInterface->netInterface()->createVehiCollectorOnLink(lfetLane9, dist);
	//	collector->setDistToStart(m2p(400));
	//}

	//根据id获取路段5上游连接段
	//ISection* sectionLink5 = gpTessInterface->netInterface()->findLink(5);
	//ISection* sectionConnector1 = sectionLink5->fromSection(2);
	//if (sectionConnector1) {
	//	if (sectionConnector1->gtype() == NetItemType::GConnectorType) {
	//		qDebug() << "路段5上游为1的section为：" << sectionConnector1->id() << endl;
	//	}
	//}

	//路段5最左侧车道向前延伸140米后所在点及分段序号
	//ILink* link5 = gpTessInterface->netInterface()->findLink(5);
	//ILaneObject* laneObjLeft5 = link5->laneObjects().back();
	//QPointF outPoint;
	//int outIndex;
	//qreal dist = m2p(140);
	//if (laneObjLeft5->getPointAndIndexByDist(dist, outPoint, outIndex)) {
	//	qDebug() << "路段5最左侧车道向前延伸140米后所在点坐标为：" << outPoint.x() << outPoint.y() <<"，分段序号为：" << outIndex << endl;
	//}

	////根据point对lSection列表中每一个Section所有LaneObject求最短距离
	//QList<ISection*> sections = gpTessInterface->netInterface()->sections();
	//QPointF point(0, 0);
	//QList<Online::Location> locations = gpTessInterface->netInterface()->locateOnSections(point, sections);
	//for (Online::Location& location : locations) {
	//	qDebug() << "相关车道或“车道连接”为：" << location.pLaneObject->id();
	//	qDebug() << "pLaneObject上的最近点点为：(" << location.point.x() << "," << location.point.y() << ")";
	//	qDebug() << "到最近点点的最短距离为：" << location.leastDist;
	//	qDebug() << "最近点到起点的里程：" << location.distToStart;
	//	qDebug() << "最近点所在分段序号：" << location.segmIndex << endl;
	//}

	////根据id获取路段5上游id为2的连接段
	//ISection* pSectionLink = gpTessInterface->netInterface()->findLink(5);
	//ISection* pSectionConnector = pSectionLink->fromSection(2);
	//if (pSectionConnector) {
	//	if (pSectionConnector->gtype() == NetItemType::GConnectorType) {
	//		qDebug() << "路段5上游id为2的section为：" << pSectionConnector->id() << endl;
	//	}
	//}
	//
	////路段5最左侧车道向前延伸140米后所在点及分段序号
	//ILink* pLink = gpTessInterface->netInterface()->findLink(5);
	//ILaneObject* pLaneObjLeft = pLink->laneObjects().back();
	//QPointF outPoint;
	//int outIndex;
	//qreal dist = m2p(140);
	//if (pLaneObjLeft->getPointAndIndexByDist(dist, outPoint, outIndex)) {
	//	qDebug() << "路段5最左侧车道向前延伸140米后所在点坐标为：(" << outPoint.x() << "," << outPoint.y() << ")，分段序号为：" << outIndex << endl;
	//}

	//IVehicleDrivInfoCollector* pCollector = gpTessInterface->netInterface()->createVehiCollectorOnLink(pLeftLane, dist);
	//// 将采集器设置到距路段起点400米处
	//pCollector->setDistToStart(m2p(400));
	//
	////在路段9最左侧车道100米处创建排队计数器
	//IVehicleQueueCounter* pCounter = gpTessInterface->netInterface()->createVehiQueueCounterOnLink(pLeftLane, dist);
	//qDebug() << "计数器所在点坐标为：(" << pCounter->point().x() << "," << pCounter->point().y() << ")" << endl;

	//QList<IVehicleTravelDetector*> lVehicleTravelDetector = gpTessInterface->netInterface()->createVehicleTravelDetector_link2link(link, link, m2p(50), m2p(550));
	//if (!lVehicleTravelDetector.empty()) {
	//	for (IVehicleTravelDetector* detector : lVehicleTravelDetector) {
	//		detector->setFromTime(10);
	//		detector->setToTime(60);
	//	}
	//}
	//
	//IGuidArrow* pGuideArrow = gpTessInterface->netInterface()->createGuidArrow(pRightLane, length, distToTerminal, arrowType);
	//qDebug() << "导向箭头类型为：" << pGuideArrow->arrowType() << endl;
	//
	//// 获取事故区所在的道路类型
	//IAccidentZone* pAccidentZone = gpTessInterface->netInterface()->createAccidentZone(accidentZone);
	//qDebug() << pAccidentZone->roadType() << endl;

	////获取路段9上施工区所在路段的ID
	//IRoadWorkZone* pWorkZone = gpTessInterface->netInterface()->createRoadWorkZone(workZone);
	//qDebug() << "施工区所在路段或连接段ID为：" << pWorkZone->sectionId() << endl;

	////在路段4的最右侧车道上添加直行或右转箭头,导向箭头距离路段起终点不能小于9米
	//ILink* pLink = gpTessInterface->netInterface()->findLink(4);
	//if (pLink) {
	//	ILane* pRightLane = pLink->lanes().front();
	//	qreal length = m2p(4.0);
	//	qreal distToTerminal = m2p(50);
	//	Online::GuideArrowType arrowType = Online::GuideArrowType::StraightRight;
	//	if (pRightLane) {
	//		IGuidArrow* pGuideArrow = gpTessInterface->netInterface()->createGuidArrow(pRightLane, length, distToTerminal, arrowType);
	//		qDebug() << "创建箭头成功，箭头所在车道为：" << pGuideArrow->lane()->id() << endl;
	//	}
	//}

	////在路段9最左侧车道100米处创建车辆采集器
	//ILink* pLink = gpTessInterface->netInterface()->findLink(9);
	//if (pLink) {
	//	ILane* pLeftLane = pLink->lanes().back();
	//	qreal dist = m2p(100);
	//	IVehicleDrivInfoCollector* pCollector = gpTessInterface->netInterface()->createVehiCollectorOnLink(pLeftLane, dist);
	//}
	//
	////在路段9最左侧车道100米处创建排队计数器
	//ILink* pLink = gpTessInterface->netInterface()->findLink(9);
	//if (pLink) {
	//	ILane* pLeftLane = pLink->lanes().back();
	//	qreal dist = m2p(100);
	//	IVehicleQueueCounter* pCcounter = gpTessInterface->netInterface()->createVehiQueueCounterOnLink(pLeftLane, dist);
	//}
	//

	////在路段9 50-550米处创建行程检测器
	//ILink* pLink = gpTessInterface->netInterface()->findLink(9);
	//if (pLink) {
	//	QList<IVehicleTravelDetector*> pDetector = gpTessInterface->netInterface()->createVehicleTravelDetector_link2link(pLink, pLink, m2p(50), m2p(550));
	//}


	//Online::DynaRoadWorkZoneParam workZone;
	////道路ID
	//workZone.roadId = 9;
	////施工区名称
	//workZone.name = "施工区，限速60";
	////位置，距路段或连接段起点距离，单位米
	//workZone.location = m2p(200);
	////施工区长度，单位米
	//workZone.length = m2p(200);
	////车辆经过施工区的最大车速，单位千米/小时
	//workZone.limitSpeed = m2p(60);
	////施工区施工时长，单位秒
	//workZone.duration = 50;
	////施工区起始车道
	//workZone.mlFromLaneNumber.append(2);
	////创建施工区
	//IRoadWorkZone* pZone = gpTessInterface->netInterface()->createRoadWorkZone(workZone);
	//

	//Online::DynaAccidentZoneParam accidentZone;
	////道路ID
	//accidentZone.roadId = 9;
	////事故区名称
	//accidentZone.name = "最左侧车道发生事故";
	////位置，距路段或连接段起点距离，单位米
	//accidentZone.location = m2p(200);
	////事故区长度，单位米
	//accidentZone.length = m2p(50);
	////事故区起始车道序号列表
	//accidentZone.mlFromLaneNumber.append(2);
	////事故等级
	//accidentZone.level = 1;
	////创建事故区
	//IAccidentZone* pZone = gpTessInterface->netInterface()->createAccidentZone(accidentZone);
	//
	////20秒时，移动飞机
	//if (simuTime == 20 * 1000) {
	//	//查找飞机和id为1的车道
	//	IVehicle* pPlane = gpTessInterface->simuInterface()->getVehicle(100001);
	//	ILane* pLane = gpTessInterface->netInterface()->findLane(1);
	//	if (pPlane->vehicleDriving()->moveToLane(pLane, m2p(400))) {
	//		qDebug() << "移动飞机成功" << endl;
	//	}
	//}
	//
	////根据point对lSection列表中每一个Section所有LaneObject求最短距离
	//QList<ISection*> lSections = gpTessInterface->netInterface()->sections();
	//QPointF point(0, 0);
	//QList<Online::Location> locations = gpTessInterface->netInterface()->locateOnSections(point, lSections);
	//for (Online::Location& location : locations) {
	//	qDebug() << "相关车道或“车道连接”为：" << location.pLaneObject->id();
	//	qDebug() << "pLaneObject上的最近点为：(" << location.point.x() << "," << location.point.y() << ")";
	//	qDebug() << "到最近点的最短距离为：" << location.leastDist;
	//	qDebug() << "最近点到起点的里程：" << location.distToStart;
	//	qDebug() << "最近点所在分段序号：" << location.segmIndex << endl;
	//}

	
	
}

//在绘制部分路网元素时也会调用CustomerNet实现类相关方法，范例通过实现方法labelNameAndFont让部分路段和连接段用路段名（默认为ID）绘制标签。所以路段初始状态时标签上才会是路段名
//写标签，按照给定的属性名和字体大小（米）
void MyNet::labelNameAndFont(int itemType, long itemId, int& outPropName, qreal& outFontSize) {
	if (itemType == NetItemType::GConnectorType) {
		outPropName = GraphicsItemPropName::Name;
	}
	//itemId为路网元素ID，无论是路段，连接段还是其它什么，只要ID为对应数字就符合
	else if (itemType == NetItemType::GLinkType) {
		outPropName = GraphicsItemPropName::Id;
	}
}

MyNet::~MyNet() {
}
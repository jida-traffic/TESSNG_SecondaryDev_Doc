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

MyNet::MyNet(){
}

//加载路网前的准备
void MyNet::beforeLoadNet() {
	//QMessageBox::information(nullptr, QString(), QString("加载路网前的准备"));
}

//加载完路网后的行为
void MyNet::afterLoadNet() {
	if (gpTessInterface->netInterface()->linkCount() == 0) {
		//软件打开后自动加载临时路网，因为临时路网上没有路段，所以下面创建路段等要素的语句得到执行
		createNet();
	}



	//2022-07-18
	//获取所有路段
	QList<ILink*> lLink =  gpTessInterface->netInterface()->links();
	int minPointCount = 10000;
	foreach(ILink * pLink, lLink)
	{
		//==============创建当前路段SVG=================
		//路段中心线断点集
		QList<QPointF> lPoints = pLink->centerBreakPoints();
		//路段左侧断点集
		QList<QPointF> lLeftPoints = pLink->leftBreakPoints();
		//路段右侧断点集
		QList<QPointF> lRightPoints = pLink->rightBreakPoints();
		//创建路段SVG,略

		//===============创建当前路段所有车道SVG================
		//路段的所有车道
		QList<ILane*> lLane = pLink->lanes();
		foreach(ILane * pLane, lLane)
		{
			if (pLane->centerBreakPoint3Ds().size() < minPointCount)
			{
				minPointCount = pLane->centerBreakPoint3Ds().size();
			}
			//车道中心线断点集
			QList<QPointF> lPoint = pLane->centerBreakPoints();
			//车道左侧断点集
			QList<QPointF> lLeftPoint = pLane->leftBreakPoints();
			//车道右侧断点集
			QList<QPointF> lRightPoint = pLane->rightBreakPoints();
		}
	}
	qDebug() << minPointCount;

	//2022-07-21
	//获取所有连接段
	QList<IConnector*> lConnector = gpTessInterface->netInterface()->connectors();
	foreach(IConnector* pConn, lConnector)
	{
		QList<ILaneConnector*> lLC = pConn->laneConnectors();
		foreach(ILaneConnector * pLC, lLC)
		{
			//"车道连接”左侧断点集
			QList<QPointF> lLeftPoint = pLC->leftBreakPoints();
			//“车道连接”右侧点集
			QList<QPointF> lRightPoint = pLC->rightBreakPoints();
			//=========编制svg===========

		}
	}

	//如果配置文件配置了加载后启动仿真，则TESSNG会启动仿真，本方法不用启动仿真，否则本方法启动仿真
	QJsonObject config =  gpTessPlugin->tessngConfig();
	if (config.value("__simuafterload").isBool() && config.value("__simuafterload").toBool())
	{
		return;
	}

}

//创建路网
void MyNet::createNet() {
	IRoadNet *pRoadNet = gpTessInterface->netInterface()->setNetAttrs("API创建路网", "OPENDRIVE");
	qDebug() << pRoadNet->netName();

	//第一条路段
	QPointF startPoint = QPointF(m2p(-300), 0);
	QPointF endPoint = QPointF(m2p(300), 0);
	QList<QPointF> lPoint;
	lPoint << startPoint;
	lPoint << endPoint;
	ILink *pLink1 = gpTessInterface->netInterface()->createLink(lPoint, 7, "曹安公路");
	if (pLink1) {
		//创建发车点
		IDispatchPoint *pDp = gpTessInterface->netInterface()->createDispatchPoint(pLink1);
		if (pDp) {
			pDp->addDispatchInterval(1, 2, 28);
		}
	}

	//创建第二条路段
	startPoint = QPointF(m2p(-300), m2p(-25));
	endPoint = QPointF(m2p(300), m2p(-25));
	lPoint.clear();
	lPoint << startPoint;
	lPoint << endPoint;
	ILink *pLink2 = gpTessInterface->netInterface()->createLink(lPoint, 3, "次干道");
	if (pLink2) {
		//创建发车点
		IDispatchPoint *pDp = gpTessInterface->netInterface()->createDispatchPoint(pLink2);
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
	ILink *pLink3 = gpTessInterface->netInterface()->createLink(lPoint, 3);
	if (pLink3) {
		//创建发车点
		IDispatchPoint *pDp = gpTessInterface->netInterface()->createDispatchPoint(pLink3);
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
	ILink *pLink4 = gpTessInterface->netInterface()->createLink(lPoint, 3);

	//创建第五条路段
	startPoint = QPointF(m2p(150), m2p(25));
	endPoint = QPointF(m2p(300), m2p(25));
	lPoint.clear();
	lPoint << startPoint;
	lPoint << endPoint;
	ILink *pLink5 = gpTessInterface->netInterface()->createLink(lPoint, 3, "自定义限速路段");
	if (pLink5) {
		pLink5->setLimitSpeed(30);
	}

	//创建第六条路段
	startPoint = QPointF(m2p(-300), m2p(50));
	endPoint = QPointF(m2p(300), m2p(50));
	lPoint.clear();
	lPoint << startPoint;
	lPoint << endPoint;
	ILink *pLink6 = gpTessInterface->netInterface()->createLink(lPoint, 3, "动态发车路段");
	if (pLink6) {
		pLink6->setLimitSpeed(80);
	}

	//创建第七条路段
	startPoint = QPointF(m2p(-300), m2p(75));
	endPoint = QPointF(m2p(-250), m2p(75));
	lPoint.clear();
	lPoint << startPoint;
	lPoint << endPoint;
	ILink *pLink7 = gpTessInterface->netInterface()->createLink(lPoint, 3);
	if (pLink7) {
		pLink7->setLimitSpeed(80);
	}

	//创建第八条路段
	startPoint = QPointF(m2p(-50), m2p(75));
	endPoint = QPointF(m2p(300), m2p(75));
	lPoint.clear();
	lPoint << startPoint;
	lPoint << endPoint;
	ILink *pLink8 = gpTessInterface->netInterface()->createLink(lPoint, 3);
	if (pLink8) {
		pLink8->setLimitSpeed(80);
	}

	//创建第一条连接段
	if (pLink3 && pLink4) {
		QList<int> lFromLaneNumber = QList<int>() << 1 << 2 << 3;
		QList<int> lToLaneNumber = QList<int>() << 1 << 2 << 3;
		IConnector *pConn1 = gpTessInterface->netInterface()->createConnector(pLink3->id(), pLink4->id(), lFromLaneNumber, lToLaneNumber
			, "连接段1");
	}

	//创建第二条连接段
	if (pLink4 && pLink5) {
		IConnector *pConn2 = gpTessInterface->netInterface()->createConnector(pLink4->id(), pLink5->id(), QList<int>() << 1 << 2 << 3, QList<int>() << 1 << 2 << 3, "连接段2");
	}

	//创建第三条连接段
	if (pLink7 && pLink8) {
		IConnector *pConn3 = gpTessInterface->netInterface()->createConnector(pLink7->id(), pLink8->id(), QList<int>() << 1 << 2 << 3, QList<int>() << 1 << 2 << 3, "动态发车连接段");
	}

	//关闭主窗体或重新打开新的路网，会从内存删除当前路网元素，不必手动删除。
}

//写标签，按照给定的属性名和字体大小（米）
void MyNet::labelNameAndFont(int itemType, long itemId, int &outPropName, qreal &outFontSize) {
	outPropName = GraphicsItemPropName::Id;
	outFontSize = 6;
	if (itemType == NetItemType::GConnectorType) {
		outPropName = GraphicsItemPropName::Name;
	}
	else if (itemType == NetItemType::GLinkType) {
		if (itemId == 1 || itemId == 5 || itemId == 6) {
			outPropName = GraphicsItemPropName::Name;
		}
	}
}

MyNet::~MyNet(){
}
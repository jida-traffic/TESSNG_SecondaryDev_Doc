#include "MySimulator.h"

#include <QMessageBox>
#include <QDateTime>
#include <QDebug>

#include "ilink.h"
#include "ILane.h"
#include "IConnector.h"
#include "ILaneConnector.h"
#include "ivehicle.h"
#include "ivehicledriving.h"
#include "isignallamp.h"
#include "tessinterface.h"
#include "netinterface.h"
#include "simuinterface.h"
#include "ivehicle.h"
#include "IBusLine.h"
#include "IBusStation.h"
#include "IBusStationLine.h"
#include "UnitChange.h"
#include "AutoDynaInfo.h"

MySimulator::MySimulator()
	:mrSquareVehiCount(28), mrSpeedOfPlane(-1), mrStartMSecs(0)
{

}

//开始仿真前的做准备
void MySimulator::beforeStart(bool &keepOn) {
	//当前路网名
	QString tmpNetPath = gpTessInterface->netInterface()->netFilePath();
	if (tmpNetPath != mNetPath)
	{
		mNetPath = tmpNetPath;
		mSimuCount = 0;
	}
	gpTessInterface->simuInterface()->setAcceMultiples(1);

	//开始仿真前修改公交线路站点部分参数
	QList<IBusLine*> lBusLine = gpTessInterface->netInterface()->buslines();
	if (!lBusLine.isEmpty())
	{
		IBusLine* pLine = lBusLine.first();
		long id = pLine->id();
		QList<ILink*> lLink = pLine->links();
		QList<IBusStationLine*> lStationLine = pLine->stationLines();
		if (!lStationLine.isEmpty())
		{
			IBusStationLine* pStationLine = lStationLine.first();
			pStationLine->setBusParkingTime(20);

		}
	}

	//如果return true且keepOn为false，则仿真不被执行，可以偿试将keepOn设为false，观察是否执行仿真
	keepOn = true;
	//如果返回false，不判断keepOn的值，开始仿真
}

//仿真起动后的处理
void MySimulator::afterStart() {
	//像素比，米/像素
	//mrScale = gpTessInterface->netInterface()->sceneScale();
}

//仿真结束后的处理
void MySimulator::afterStop() {
	//QDateTime dt = QDateTime::fromMSecsSinceEpoch(mrStartMSecs);
	//QString dtStr = dt.toString("yyyy年MM月dd日 hh时mm分ss秒");
	//QString startDtStr = QString("仿真开始现实时间:").append(dtStr);

	//dtStr = QDateTime::currentDateTime().toString("yyyy年MM月dd日 hh时mm分ss秒");
	//QString endDtStr = QString("仿真结束现实时间:").append(dtStr);

	//QMessageBox::information(nullptr, QString(), QString().append(startDtStr).append("\n").append(endDtStr));

	mSimuCount++;
	QString netfilePath = gpTessInterface->netInterface()->netFilePath();
	if (netfilePath.contains("深圳南海大道创业路交叉口CFI方案") && mSimuCount < 3)
	{
		emit(forReStartSimu());
	}

}

//初始车辆, laneNumber:车道，从0开始；dist，距起点距离，单位像素；speed：车速，像素/秒
//bool MySimulator::initVehicle(IVehicle *pIVehicle, int laneNumber, qreal dist, qreal speed) {
//初始车辆
void MySimulator::initVehicle(IVehicle *pIVehicle) {
	//======设置部分方法被TESSNG调用频次，参数"__custsimubysteps"设为true时下列设置起作用======
	//每20个计算周期调用1次
	pIVehicle->setSteps_reCalcToLeftFreely(20);
	//每20个计算周期调用1次
	pIVehicle->setSteps_reCalcToRightFreely(20);
	//每个计算周期都调用
	pIVehicle->setSteps_reCalcdesirSpeed(1);
	//每个计算周期都调用
	pIVehicle->setSteps_reSetSpeed(1);

	long tmpId = pIVehicle->id() % 100000;
	QString roadName = pIVehicle->roadName();
	long roadId = pIVehicle->roadId();
	if (roadName == QString("曹安公路")) {
		//飞机
		if (tmpId == 1) {
			pIVehicle->setVehiType(12);
			pIVehicle->initLane(3, m2p(105), 0);
		}
		//工程车
		else if (tmpId >= 2 && tmpId <= 8) {
			pIVehicle->setVehiType(8);
			pIVehicle->initLane((tmpId - 2) % 7, m2p(80), 0);
		}
		//消防车
		else if (tmpId >= 9 && tmpId <= 15) {
			pIVehicle->setVehiType(9);
			pIVehicle->initLane((tmpId - 2) % 7, m2p(65), 0);
		}
		//救护车
		else if (tmpId >= 16 && tmpId <= 22) {
			pIVehicle->setVehiType(10);
			pIVehicle->initLane((tmpId - 2) % 7, m2p(50), 0);
		}
		//最后两队列小车
		else if (tmpId == 23) {
			pIVehicle->setVehiType(1);
			pIVehicle->initLane(1, m2p(35), 0);
		}
		else if (tmpId == 24) {
			pIVehicle->setVehiType(1);
			pIVehicle->initLane(5, m2p(35), 0);
		}
		else if (tmpId == 25) {
			pIVehicle->setVehiType(1);
			pIVehicle->initLane(1, m2p(20), 0);
		}
		else if (tmpId == 26) {
			pIVehicle->setVehiType(1);
			pIVehicle->initLane(5, m2p(20), 0);
		}
		else if (tmpId == 27) {
			pIVehicle->setVehiType(1);
			pIVehicle->initLane(1, (5), 0);
		}
		else if (tmpId == 28) {
			pIVehicle->setVehiType(1);
			pIVehicle->initLane(5, (5), 0);
		}
		if (tmpId >= 23 && tmpId <= 28) {
			pIVehicle->setLength(m2p(4.5), true);
		}
	}
}

//计算加速度
bool MySimulator::calcAcce(IVehicle *pIVehicle, qreal &acce)
{
	AutoDynaInfo *pDynaInfo = (AutoDynaInfo*)pIVehicle->dynaInfo();
	//如果是自动驾驶车辆，将计数加1，如果车速大于10m/s，将加速度设为-2m/s^2，如果车速小于1m/s，将加速度设为2m/s
	if (pDynaInfo)
	{
		pDynaInfo->mrCalcCount++;
		if(pIVehicle->vehiDistFront() < m2p(5))
		{
			//前车距小于5米，让TESSNG计算加速度
			return false;
		}
		else if (pIVehicle->currSpeed() > m2p(10))
		{
			acce = m2p(-2);
		}
		else if (pIVehicle->currSpeed() < m2p(1))
		{
			acce = m2p(2);
		}
		return true;
	}
	return false;
}

//重新计算期望速度
bool MySimulator::reCalcdesirSpeed(IVehicle *pIVehicle, qreal &inOutDesirSpeed) {
	long tmpId = pIVehicle->id() % 100000;
	QString roadName = pIVehicle->roadName();
	if (roadName == QString("曹安公路")) {
		if (tmpId <= mrSquareVehiCount) {
			//当前已仿真时间
			long simuTime = gpTessInterface->simuInterface()->simuTimeIntervalWithAcceMutiples();
			if (simuTime < 5 * 1000) {
				inOutDesirSpeed =  0;
			} else if (simuTime < 10 * 1000) {
				inOutDesirSpeed = m2p(20 / 3.6);
			}
			else {
				inOutDesirSpeed = m2p(40 / 3.6);
			}
			return true;
		}
	}
	return false;
}

//重新设置跟驰的安全时距及安全距离， inOutSi：安全时距，inOutSd: 安全距离
bool MySimulator::reSetFollowingParam(IVehicle *pIVehicle, qreal &inOutSi, qreal &inOutSd) {
	QString roadName = pIVehicle->roadName();
	if (roadName == QString("连接段2")) {
		inOutSd = m2p(30);
		return true;
	}
	return false;
}

QList<Online::DispatchInterval> MySimulator::calcDynaDispatchParameters()
{
	QList<Online::DispatchInterval> lDispatchInterval;
	long simuTime = gpTessInterface->simuInterface()->simuTimeIntervalWithAcceMutiples();
	if (simuTime == 30 * 1000)
	{
		QTime t = QTime::currentTime();
		long currSecs = t.hour() * 3600 + t.minute() * 60 + t.second();
		Online::DispatchInterval di = Online::DispatchInterval();
		di.dispatchId = 1;
		di.fromTime = currSecs;
		di.toTime = di.fromTime + 300 - 1;
		di.vehiCount = 300;
		di.mlVehicleConsDetail << Online::VehicleComposition(1, 90) << Online::VehicleComposition(2, 10);
		lDispatchInterval << di;
	}
	return lDispatchInterval;
}

QList<Online::DecipointFlowRatioByInterval> MySimulator::calcDynaFlowRatioParameters()
{
	QList<Online::DecipointFlowRatioByInterval> lDecipointFLowRatioByInterval;
	long batchNumber = gpTessInterface->simuInterface()->batchNumber();
	if (batchNumber == 100)
	{
		Online::DecipointFlowRatioByInterval dfi = Online::DecipointFlowRatioByInterval();
		dfi.deciPointID = 1;
		dfi.startDateTime = 1;
		dfi.endDateTime = 84000;
		Online::RoutingFlowRatio rfr1 = Online::RoutingFlowRatio(1, 10);
		Online::RoutingFlowRatio rfr2 = Online::RoutingFlowRatio(2, 1);
		dfi.mlRoutingFlowRatio << rfr1;
		dfi.mlRoutingFlowRatio << rfr2;
		lDecipointFLowRatioByInterval << dfi;
	}
	return lDecipointFLowRatioByInterval;
}

//如果在路段上，重新设置车辆加速度，注意：重新设置的加速度导致的车速不受道路限速影响
bool MySimulator::reSetAcce(IVehicle *pIVehicle, qreal &inOutAcce) {
	QString roadName = pIVehicle->roadName();
	if (roadName == QString("连接段1")) {
		//如果车速大于20km/h，加速度设为-5m/s/s
		if (pIVehicle->currSpeed() > m2p(20 / 3.6)) {
			inOutAcce = m2p(-5);
			return true;
		}
		//如果车速大于10km/h，加速度设为-1m/s/s
		else if (pIVehicle->currSpeed() > m2p(20 / 3.6)) {
			inOutAcce = m2p(-1);
			return true;
		}
	}
	return false;
}

//重新设置速度
bool MySimulator::reSetSpeed(IVehicle *pIVehicle, qreal &inOutSpeed) {
	long tmpId = pIVehicle->id() % 100000;
	QString roadName = pIVehicle->roadName();
	if (roadName == QString("曹安公路")) {
		if (tmpId == 1) {
			mrSpeedOfPlane = pIVehicle->currSpeed();
		}
		else if (tmpId >= 2 && tmpId <= mrSquareVehiCount && mrSpeedOfPlane >= 0) {
			inOutSpeed = mrSpeedOfPlane;
			return true;
		}
	}
	long linkid = pIVehicle->startLink()->id();
	long startDt = pIVehicle->startSimuTime();
	return false;
}

//计算是否要左自由变道
bool MySimulator::reCalcToLeftFreely(IVehicle *pIVehicle) {
	//车辆到路段或连接终点距离小于20米不变道
	if (pIVehicle->vehicleDriving()->distToEndpoint() - pIVehicle->length() / 2 < m2p(20)) {
		return false;
	}

	long tmpId = pIVehicle->id() % 100000;
	QString roadName = pIVehicle->roadName();
	if (roadName == QString("曹安公路")) {
		if (tmpId >= 23 && tmpId <= 28) {
			int laneNumber = pIVehicle->vehicleDriving()->laneNumber();
			if (laneNumber == 1 || laneNumber == 4) {
				return true;
			}
		}
	}
	return false;
}

//计算是否要右自由变道
bool MySimulator::reCalcToRightFreely(IVehicle *pIVehicle) {
	long tmpId = pIVehicle->id() % 100000;
	//车辆到路段或连接终点距离小于20米不变道
	if (pIVehicle->vehicleDriving()->distToEndpoint() - pIVehicle->length() / 2 < m2p(20)) {
		return false;
	}

	if (tmpId == 27)
	{
		qDebug();
	}

	QString roadName = pIVehicle->roadName();
	if (roadName == QString("曹安公路")) {
		if (tmpId >= 23 && tmpId <= 28) {
			int laneNumber = pIVehicle->vehicleDriving()->laneNumber();
			if (laneNumber == 2 || laneNumber == 5) {
				return true;
			}
		}
	}
	return false;
}

//计算信号灯颜色
bool MySimulator::calcLampColor(ISignalLamp *pSignalLamp) {
	if (pSignalLamp->id() == 5)
	{
		pSignalLamp->setLampColor("R");
		return true;
	}
	long batchNumber = gpTessInterface->simuInterface()->batchNumber();
	//每计算200批次进行一次信号灯色的变化
	//if ((batchNumber / 200) % 2 == 0) {
	//	pSignalLamp->setLampColor(Qt::green);
	//}
	//else {
	//	pSignalLamp->setLampColor(Qt::red);
	//}
	//if (pSignalLamp->id() == 1)
	//{
	//	pSignalLamp->setLampColor(Qt::red);
	//}
	//else if (pSignalLamp->id() == 2) {
	//	pSignalLamp->setLampColor(Qt::green);
	//}
	//else {
	//	pSignalLamp->setLampColor(Qt::gray);
	//}
	return false;
}

//一个批次计算后的处理
void MySimulator::afterOneStep() {
	//============以下是获取一些仿真过程数据的方法============
	//当前仿真计算批次
	long batchNum = gpTessInterface->simuInterface()->batchNumber();
	//当前已仿真时间，单位：毫秒
	long simuTime = gpTessInterface->simuInterface()->simuTimeIntervalWithAcceMutiples();
	if (batchNum == 20 * 20)
	{
		gpTessInterface->simuInterface()->setAcceMultiples(100);
	}
	//开始仿真的现实时间
	qint64 startRealtime = gpTessInterface->simuInterface()->startMSecsSinceEpoch();
	//所有在运行车辆
	QList<IVehicle*> lAllVehi = gpTessInterface->simuInterface()->allVehiStarted();
	//ID为1的路段上所有已启动车辆
	QList<IVehicle*> lVehi = gpTessInterface->simuInterface()->vehisInLink(1);
	//车辆轨迹
	QList<Online::VehicleStatus> lVehiStatus = gpTessInterface->simuInterface()->getVehisStatus();
	
	//车辆数据采集信息
	QList<Online::VehiInfoCollected> lOutVehiInfo = gpTessInterface->simuInterface()->getVehisInfoCollected();
	//采集器集计信息
	QList<Online::VehiInfoAggregated> lOutVehiInfoAggre = gpTessInterface->simuInterface()->getVehisInfoAggregated();
	//车辆排队信息
	QList<Online::VehiQueueCounted> lOutVehiQueue = gpTessInterface->simuInterface()->getVehisQueueCounted();
	//车辆排队集计数据
	QList<Online::VehiQueueAggregated> lOutVehiQueueAggre = gpTessInterface->simuInterface()->getVehisQueueAggregated();
	//行程序时间采集信息
	QList<Online::VehiTravelDetected> lOutVehiTravel = gpTessInterface->simuInterface()->getVehisTravelDetected();
	//行程时间集计数据
	QList<Online::VehiTravelAggregated> lOutVehiTravelAggre = gpTessInterface->simuInterface()->getVehisTravelAggregated();
	//当前延误
	long delay = gpTessInterface->simuInterface()->delayTimeOnBatchNumber(batchNum);

	mRunInfo = QString("路段数：%0\n运行车辆数：%1\n仿真时间：%2(毫秒)").arg(gpTessInterface->netInterface()->linkCount()).arg(lAllVehi.size()).arg(simuTime);

	if (batchNum % 20 == 0) {
		QString info = mRunInfo;
		emit(forRunInfo(info));
	}

	//动态发车，不通过发车点
	if (batchNum % 50 == 1)
	{
		QString color = QString("#%1%2%3").arg(QString::number(qrand() % 256, 16)).arg(QString::number(qrand() % 256, 16)).arg(QString::number(qrand() % 256, 16));

		//路段上发车
		Online::DynaVehiParam dvp;
		dvp.vehiTypeCode = qrand() % 4 + 1;
		dvp.roadId = 6;
		dvp.laneNumber = qrand() % 3;
		dvp.dist = 50;
		dvp.speed = 20;
		dvp.color = color;
		IVehicle *pIVehicle1 = gpTessInterface->simuInterface()->createGVehicle(dvp);
		if (pIVehicle1)
		{
			AutoDynaInfo *pInfo = new AutoDynaInfo();
			pInfo->mName = QString("自动驾驶_%1").arg(pIVehicle1->id());
			pIVehicle1->setDynaInfo(pInfo);
		}

		//连接段上发车
		Online::DynaVehiParam dvp2;
		dvp2.vehiTypeCode = qrand() % 4 + 1;
		dvp2.roadId = 3;
		dvp2.laneNumber = qrand() % 3;
		dvp2.toLaneNumber = dvp2.laneNumber; //默认为-1，如果大于等于0, 在连接段上发车
		dvp2.dist = 50;
		dvp2.speed = 20;
		dvp2.color = color;
		IVehicle *pIVehicle2 = gpTessInterface->simuInterface()->createGVehicle(dvp2);
		if (pIVehicle2)
		{
			AutoDynaInfo *pInfo = new AutoDynaInfo();
			pInfo->mName = QString("自动驾驶_%1").arg(pIVehicle2->id());
			pIVehicle2->setDynaInfo(pInfo);
		}
	}

	if (simuTime >= 300 * 1000) {
		QString netfilePath = gpTessInterface->netInterface()->netFilePath();
		if (netfilePath.contains("深圳南海大道创业路交叉口CFI方案") && mSimuCount < 3)
		{
			emit(forStopSimu());
		}
	}
}

//绘制车辆，绘制前将车辆对象旋转指定角度
bool MySimulator::paintVehicle(IVehicle *pIVehicle, QPainter *painter)
{
	return false;
}

MySimulator::~MySimulator(){
}
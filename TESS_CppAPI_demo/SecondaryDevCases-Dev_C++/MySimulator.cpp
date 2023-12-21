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
#include "ISection.h"
#include <QRandomGenerator>


MySimulator::MySimulator(SecondaryDevCases* pSecondDevCasesObj)
	:mrSquareVehiCount(28), mrSpeedOfPlane(-1), mrStartMSecs(0), mpSecondDevCasesObj(pSecondDevCasesObj)
{

}

//开始仿真前的做准备
void MySimulator::beforeStart(bool& keepOn) {
}

//仿真起动后的处理
void MySimulator::afterStart() {
	//像素比，米/像素
	//mrScale = gpTessInterface->netInterface()->sceneScale();
}

//仿真结束后的处理
void MySimulator::afterStop() {
}


//初始车辆
void MySimulator::initVehicle(IVehicle* pIVehicle) {
}

//计算加速度
bool MySimulator::calcAcce(IVehicle* pIVehicle, qreal& acce)
{
	return false;
}

//重新计算期望速度
bool MySimulator::reCalcdesirSpeed(IVehicle* pIVehicle, qreal& inOutDesirSpeed) {
	// L5最右侧车道50-100m处，限速10，持续30s
	if (mpSecondDevCasesObj->mActionControlMethodNumber == 10) {
		//当前已仿真时间，单位：秒
		long simuTime = gpTessInterface->simuInterface()->simuTimeIntervalWithAcceMutiples() / 1000;
		if (!mpSecondDevCasesObj->reCalcdesirSpeedFlag) {
			//当前已仿真时间，单位：毫秒
			mpSecondDevCasesObj->reCalcdesirSpeedStartTime = gpTessInterface->simuInterface()->simuTimeIntervalWithAcceMutiples() / 1000;
			mpSecondDevCasesObj->reCalcdesirSpeedFlag = true;
			mRunInfo = QStringLiteral("L5路段最右侧车道50-100m处设置限速区，限速10km/h，持续时间30s！");
			emit(forRunInfo(mRunInfo));
		}
		if (pIVehicle->vehicleDriving()->laneNumber() == 0 && pIVehicle->roadId() == 5) {
			if (pIVehicle->vehicleDriving()->distToStartPoint() < m2p(100) && pIVehicle->vehicleDriving()->distToStartPoint() > m2p(50)) {
				inOutDesirSpeed = 10;
			}
		}
		if (simuTime - mpSecondDevCasesObj->reCalcdesirSpeedStartTime >= 30) {
			mRunInfo = QStringLiteral("L5路段最右侧车道50-100m处限速区已关闭，车辆正常行驶！");
			emit(forRunInfo(mRunInfo));
			mpSecondDevCasesObj->mActionControlMethodNumber = 0;
		}
		return true;
	}
	return false;
}

QList<Online::DecipointFlowRatioByInterval> MySimulator::calcDynaFlowRatioParameters()
{
	QList<Online::DecipointFlowRatioByInterval> lDecipointFLowRatioByInterval;
	long batchNumber = gpTessInterface->simuInterface()->batchNumber();
	if (batchNumber == 100*1000)
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

//重新设置跟驰的安全时距及安全距离， inOutSi：安全时距，inOutSd: 安全距离
bool MySimulator::reSetFollowingParam(IVehicle* pIVehicle, qreal& inOutSi, qreal& inOutSd) {
	return false;
}

QList<Online::DispatchInterval> MySimulator::calcDynaDispatchParameters()
{
	QList<Online::DispatchInterval> lDispatchInterval;
	if (mpSecondDevCasesObj->mActionControlMethodNumber == 1)
	{
		QTime t = QTime::currentTime();
		qDebug() << t;
		long currSecs = t.hour() * 3600 + t.minute() * 60 + t.second();
		Online::DispatchInterval di = Online::DispatchInterval();
		di.dispatchId = 11;
		di.fromTime = currSecs;
		di.toTime = di.fromTime + 300 - 1;
		di.vehiCount = 300;
		di.mlVehicleConsDetail << Online::VehiComposition(1, 90) << Online::VehiComposition(2, 10);
		lDispatchInterval << di;
		mpSecondDevCasesObj->mActionControlMethodNumber = 0;
	}
	return lDispatchInterval;
}

//如果在路段上，重新设置车辆加速度，注意：重新设置的加速度导致的车速不受道路限速影响
bool MySimulator::reSetAcce(IVehicle* pIVehicle, qreal& inOutAcce) {
	return false;
}

//重新设置速度
bool MySimulator::reSetSpeed(IVehicle* pIVehicle, qreal& inOutSpeed) {
	// 3. 修改车辆速度，将L5路段车辆修改为0
	if (mpSecondDevCasesObj->mActionControlMethodNumber == 3) {
		if (pIVehicle->roadId() == 5) {
			inOutSpeed = 0;
			return true;
		}
	}
	// 7.强制车辆闯红灯,让L12等待的车辆强制闯红灯
	if (mpSecondDevCasesObj->mActionControlMethodNumber == 7) {
		if (pIVehicle->roadId() == 12) {
			qreal vehiCurrSpeed = pIVehicle->currSpeed();
			qreal vehiCurrentDistToEnd = pIVehicle->vehicleDriving()->distToEndpoint(true);
			if (m2p(vehiCurrSpeed) < 20 && p2m(vehiCurrentDistToEnd) < 3) {
				// 生成一个随机浮点数，范围在 [0.0, 1.0)
				double randomNumber = QRandomGenerator::global()->generateDouble();
				if (randomNumber < 0.8) {
					inOutSpeed = m2p(15);
					return true;
				}
			}
		}
	}
	return false;
}

//计算是否要左自由变道
bool MySimulator::reCalcToLeftFreely(IVehicle* pIVehicle) {
	return false;
}

//计算是否要右自由变道
bool MySimulator::reCalcToRightFreely(IVehicle* pIVehicle) {
	if (pIVehicle->roadId() == 5 && pIVehicle->lane()->number() == 1 && mpSecondDevCasesObj->mActionControlMethodNumber == 6) {
		return true;
	}
	return false;
}

// 计算限制车道序号
QList<int> MySimulator::calcLimitedLaneNumber(IVehicle* pIVehicle) {
	return QList<int>();
}

bool MySimulator::reCalcDismissChangeLane(IVehicle* pIVehicle) {
	//强制车辆不变道，禁止L2路段所有车辆右变道
	if (mpSecondDevCasesObj->mActionControlMethodNumber == 5)
	{
		if (pIVehicle->roadId() == 2) {
			if (mpSecondDevCasesObj->judgeVehicleLaneChangeDirection(pIVehicle) == QStringLiteral("right")) {
				return true;
			}
		}
	}
	//强制L5路段中间车道向右变道
	if (mpSecondDevCasesObj->mActionControlMethodNumber == 6) {
		if (pIVehicle->roadId() == 5 && (pIVehicle->lane()->number() == 0 || pIVehicle->lane()->number() == 1)) {
			if (mpSecondDevCasesObj->judgeVehicleLaneChangeDirection(pIVehicle) == QStringLiteral("left")) {
				return true;
			}
		}
	}
	return false;
}

bool MySimulator::calcLampColor(ISignalLamp* pSignalLamp) {
	if (mpSecondDevCasesObj->mContorlMeasureMethodNumber == 1) {
		// 将所有信号灯变为绿色
		pSignalLamp->setLampColor("绿");
		return true;
	}
	return false;
}

void MySimulator::afterStep(IVehicle* pIVehicle) {
	//9. 修改车辆航向角，以L5路段为例
	if (mpSecondDevCasesObj->mActionControlMethodNumber == 9) {
		if (pIVehicle->roadId() == 5) {
			pIVehicle->vehicleDriving()->setAngle(45);
		}
	}
}

//一个批次计算后的处理
void MySimulator::afterOneStep() {
	//============以下是获取一些仿真过程数据的方法============
	//当前仿真计算批次
	long batchNum = gpTessInterface->simuInterface()->batchNumber();
	//当前已仿真时间，单位：毫秒
	long simuTime = gpTessInterface->simuInterface()->simuTimeIntervalWithAcceMutiples();
	//开始仿真的现实时间
	qint64 startRealtime = gpTessInterface->simuInterface()->startMSecsSinceEpoch();
	//所有在运行车辆
	QList<IVehicle*> lAllVehi = gpTessInterface->simuInterface()->allVehiStarted();
	//ID为1的路段上所有已启动车辆
	QList<IVehicle*> lVehi = gpTessInterface->simuInterface()->vehisInLink(1);
	//车辆轨迹
	QList<Online::VehicleStatus> lVehiStatus = gpTessInterface->simuInterface()->getVehisStatus();

	// 车辆移动测试时，将L5路段车辆移动过路口的各个车道
	if (mpSecondDevCasesObj->mActionControlMethodNumber == 2) {
		for (int i = 0; i < lAllVehi.size(); ++i) {
			if (lAllVehi[i]->roadId() == 5) {
				ILink* nextLink = gpTessInterface->netInterface()->findLink(9);
				QList<ILaneObject*> lNextLinkLaneObj = nextLink->laneObjects();
				if (lAllVehi[i]->vehicleDriving()->move(lNextLinkLaneObj[i % lNextLinkLaneObj.size()], static_cast<double>(i % 100))) {
					mRunInfo = QStringLiteral("L5路段车辆转移成功！");
					emit(forRunInfo(mRunInfo));
				}
			}
		}
		mpSecondDevCasesObj->mActionControlMethodNumber = 0;
	}

	// 修改车辆路径，将L1路段所有车辆修改为右转路径
	if (mpSecondDevCasesObj->mActionControlMethodNumber == 4) {
		for (IVehicle*& vehi : lAllVehi) {
			if (vehi->roadId() == 1) {
				QList<IDecisionPoint*> lDecisionPoint = gpTessInterface->netInterface()->decisionPoints();
				IDecisionPoint* pDecisionPointInLink1 = nullptr;
				for (IDecisionPoint*& pDecisionPoint : lDecisionPoint) {
					if (pDecisionPoint->link()->id() == 1) {
						pDecisionPointInLink1 = pDecisionPoint;
						break;
					}
				}
				QList<IRouting*> lRoutingsOfDecisionPointInLink1;
				if (pDecisionPointInLink1) {
					lRoutingsOfDecisionPointInLink1 = pDecisionPointInLink1->routings();
				}
				if (!lRoutingsOfDecisionPointInLink1.isEmpty()) {
					if (vehi->routing() != lRoutingsOfDecisionPointInLink1.back()) {
						if (vehi->vehicleDriving()->setRouting(lRoutingsOfDecisionPointInLink1.back())) {
							mRunInfo = QStringLiteral("L1路段所有车辆路径修改为右转！");
							emit(forRunInfo(mRunInfo));
						}
					}
				}
			}
		}
	}

	//8. 强制清除车辆,以L5路段为例，清除所有小客车
	if (mpSecondDevCasesObj->mActionControlMethodNumber == 8) {
		for (IVehicle*& pIVehicle : lAllVehi) {
			if (pIVehicle->roadId() == 5 && pIVehicle->vehicleTypeCode() == 1) {
				pIVehicle->vehicleDriving()->stopVehicle();
			}
		}
		mpSecondDevCasesObj->mActionControlMethodNumber = 0;
	}
}

//绘制车辆，绘制前将车辆对象旋转指定角度
bool MySimulator::paintVehicle(IVehicle* pIVehicle, QPainter* painter)
{
	return false;
}

// 自由左变道前处理
void MySimulator::beforeToLeftFreely(IVehicle* pIVehicle, bool& bKeepOn) {
}
//自由右变道前处理
void  MySimulator::beforeToRightFreely(IVehicle* pIVehicle, bool& bKeepOn) {
}

// 修改跟驰模型参数
QList<Online::FollowingModelParam> MySimulator::reSetFollowingParams() {
	if (mpSecondDevCasesObj->mModelModifyMethodNumber == 1) {
		Online::FollowingModelParam followingModelParamMotor, followingModelParamNonmotor;
		// 机动车
		followingModelParamMotor.vtype = Online::MotorOrNonmotor::Motor;
		followingModelParamMotor.alfa = 5;
		followingModelParamMotor.beit = 3;
		followingModelParamMotor.safeDistance = 15;
		followingModelParamMotor.safeInterval = 10;
		
		// 非机动车
		followingModelParamNonmotor.vtype = Online::MotorOrNonmotor::Nonmotor;
		followingModelParamNonmotor.alfa = 3;
		followingModelParamNonmotor.beit = 1;
		followingModelParamNonmotor.safeDistance = 5;
		followingModelParamNonmotor.safeInterval = 6;

		return QList<Online::FollowingModelParam>() << followingModelParamMotor << followingModelParamNonmotor;
	}
	return QList<Online::FollowingModelParam>();
}

/*
重新设置自由变道参数，
参数 safeTime : 安全操作时间，从驾驶员反应到实施变道(完成变道前半段)所需时间，默认4秒，
	ultimateDist:安全变道(完成变道前半段)后距前车距离，小于此距离压迫感增强，触发驾驶员寻求变道，
	targetRParm:目标车道后车影响系数，大于等于0小于等于1，此值越大目标车道后车距影响越大，反之则越小
*/
bool MySimulator::reSetChangeLaneFreelyParam(IVehicle* pIVehicle, int& safeTime, qreal& ultimateDist, qreal& targetRParam) {
	if (mpSecondDevCasesObj->mModelModifyMethodNumber == 2) {
		// 安全操作时间，从驾驶员反应到实施变道(完成变道前半段)所需时间，默认4秒
		safeTime = 100;
		// 安全变道(完成变道前半段)后距前车距离，小于此距离压迫感增强，触发驾驶员寻求变道
		ultimateDist = 50;
		// 目标车道后车影响系数，大于等于0小于等于1，此值越大目标车道后车距影响越大，反之则越小
		targetRParam = 0.1;
		return true;
	}
	return false;
}

MySimulator::~MySimulator() {
}
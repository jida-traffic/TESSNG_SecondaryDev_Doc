#include "SecondaryDevCases.h"

SecondaryDevCases::SecondaryDevCases(long _id) :
	secondDevId(_id), mpDecisionPoint(nullptr),
	mActionControlMethodNumber(0.0), mContorlMeasureMethodNumber(0.0),
	mPreocessControlMethodNumber(0.0), reCalcdesirSpeedFlag(false),
	reCalcdesirSpeedStartTime(99999), mModelModifyMethodNumber(0) {}

//创建示例路段和连接段
QList<ISection*> SecondaryDevCases::createExampleLinkAndConnector(QString LinkName, int Posy) {
	//创建两条路段
	QPointF startPoint1 = QPointF(m2p(-300), m2p(Posy));//m2p(数字)后的坐标可以对上原点在中心的坐标，TESSNG中的坐标始终是像素
	QPointF endPoint1 = QPointF(m2p(-50), m2p(Posy));
	QList<QPointF> lPoint1;
	lPoint1 << startPoint1 << endPoint1;
	ILink* pLink1 = gpTessInterface->netInterface()->createLink(lPoint1, 3, LinkName + QStringLiteral("路段1"));

	QPointF startPoint2 = QPointF(m2p(50), m2p(Posy));//m2p(数字)后的坐标可以对上原点在中心的坐标，TESSNG中的坐标始终是像素
	QPointF endPoint2 = QPointF(m2p(300), m2p(Posy));
	QList<QPointF> lPoint2;
	lPoint2 << startPoint2 << endPoint2;
	ILink* pLink2 = gpTessInterface->netInterface()->createLink(lPoint2, 3, LinkName + QStringLiteral("路段2"));
	IConnector* pConn = nullptr;
	//创建连接段
	if (pLink1 && pLink2) {
		QList<int> lFromLaneNumber = QList<int>() << 1 << 2 << 3;
		QList<int> lToLaneNumber = QList<int>() << 1 << 2 << 3;
		pConn = gpTessInterface->netInterface()->createConnector(pLink1->id(), pLink2->id(), lFromLaneNumber, lToLaneNumber, LinkName + QStringLiteral("连接段"));
		if (pConn) {
			//连接段车道连接列表
			QList<ILaneObject*> lConnLaneObjs;
			lConnLaneObjs = pConn->laneObjects();
			for (ILaneObject*& pLaneObj : lConnLaneObjs) {
				qDebug() << "上游车道ID" << pLaneObj->fromLaneObject()->id() << "下游车道ID" << pLaneObj->toLaneObject()->id() << endl;
			}
		}
	}
	return QList<ISection*>() << pLink1 << pLink2 << pConn;
}

//信控编辑
void SecondaryDevCases::signalControllerEdit() {

	QList<ISection*> lLinksAndConnector = createExampleLinkAndConnector(QStringLiteral("信控编辑"), -50);
	ILink* pLink1 = lLinksAndConnector.front()->castToLink();
	IConnector* pConn = lLinksAndConnector.back()->castToConnector();
	//连接段车道连接列表
	QList<ILaneObject*> lConnLaneObjs;
	lConnLaneObjs = pConn->laneObjects();
	//创建发车点
	if (pLink1) {
		//创建发车点
		IDispatchPoint* pDp = gpTessInterface->netInterface()->createDispatchPoint(pLink1);
		if (pDp) {
			pDp->addDispatchInterval(1, 200, 400);//200秒400辆车
		}
	}
	//创建信号灯组
	ISignalGroup* pSignalGroup = gpTessInterface->netInterface()->createSignalGroup(QObject::tr("信号灯组1"), 60, 1, 3600);
	//创建相位,40秒绿灯，黄灯3秒，全红3秒
	Online::ColorInterval green("绿", 40), yellow("黄", 3), red("红", 3);
	ISignalPhase* pSignalPhase = gpTessInterface->netInterface()->createSignalPhase(pSignalGroup, QObject::tr("信号灯组1相位1"),
		QList<Online::ColorInterval>() << green << yellow << red);
	//创建信号灯
	for (int i = 0, size = lConnLaneObjs.size(); i < size; ++i) {
		ISignalLamp* pSignalLamp = gpTessInterface->netInterface()->createSignalLamp(pSignalPhase, QObject::tr("信号灯%1").arg(i + 1),
			lConnLaneObjs[i]->fromLaneObject()->id(), lConnLaneObjs[i]->toLaneObject()->id(), m2p(2.0));
	}
}

//双环信控方案下发
void SecondaryDevCases::doubleRingSignalControl(long currentSimuTime) {
	// 读取方案数据
	QFile jsonFile("./Data/Signal_Plan_Data_1109.json");
	if (!jsonFile.open(QIODevice::ReadOnly | QIODevice::Text)) {
		qDebug() << "Error: Could not open Signal_Plan_Data_1109.json";
		return;
	}
	QByteArray jsonData = jsonFile.readAll();
	jsonFile.close();
	QJsonDocument doc = QJsonDocument::fromJson(jsonData);
	QJsonObject signalGroupsDict = doc.object();
	for (QJsonObject::iterator it = signalGroupsDict.begin(); it != signalGroupsDict.end(); ++it) {
		QString groupName = it.key();
		QJsonObject group = it.value().toObject();
		ISignalGroup* pCurrentSignalGroup = nullptr;
		// 通过灯组名称查询到灯组
		QList<ISignalGroup*> lAllSignalGroups = gpTessInterface->netInterface()->signalGroups();
		for (ISignalGroup*& pSignalGroup : lAllSignalGroups) {
			if (pSignalGroup->groupName() == groupName) {
				pCurrentSignalGroup = pSignalGroup;
				break;
			}
		}
		if (!pCurrentSignalGroup) {
			qDebug() << "FindError: The signalGroup not in current net.";
			break;
		}
		//获取当前灯组相位
		QList<ISignalPhase*> lCurrentSignalGroupPhases = pCurrentSignalGroup->phases();
		// 获取所有灯组的起始时间
		QStringList lSignalGroupStartTime = group.keys();
		for (QJsonObject::iterator it2 = group.begin(); it2 != group.end(); ++it2) {
			QString startTime = it2.key();
			// 获取下一个元素的迭代器
			QJsonObject::iterator nextIt = std::next(it2);
			QString endTime = (nextIt != group.end()) ? nextIt.key() : "24:00";
			// 起始时间和结束时间的秒数表示
			long startTimeSeconds = Functions::timeToSeconds(startTime);
			long endTimeSeconds = Functions::timeToSeconds(endTime);
			// 若当前仿真时间位于当前时段内，修改当前时段信号灯组的相位
			if (startTimeSeconds <= currentSimuTime && currentSimuTime < endTimeSeconds) {
				QJsonObject currentGroupData = it2.value().toObject();
				int periodTime = currentGroupData[QStringLiteral("cycle_time")].toInt();
				int yellowInteral = currentGroupData[QStringLiteral("yellow_interval")].toInt();
				QJsonArray phases = currentGroupData[QStringLiteral("phases")].toArray();
				// 修改周期
				pCurrentSignalGroup->setPeriodTime(periodTime);
				for (const QJsonValueRef& phase : phases) {
					QJsonObject phaseObj = phase.toObject();
					QString phaseName = phaseObj[QStringLiteral("phase_name")].toString();
					int phaseNumber = phaseObj[QStringLiteral("phase_number")].toInt();
					qDebug() << "phaseName" << phaseName << phaseNumber << endl;
					QList<Online::ColorInterval> lColorInterval;
					lColorInterval.append(Online::ColorInterval(QStringLiteral("红"), phaseObj[QStringLiteral("start_time")].toInt()));
					lColorInterval.append(Online::ColorInterval(QStringLiteral("绿"), phaseObj[QStringLiteral("green_time")].toInt()));
					lColorInterval.append(Online::ColorInterval(QStringLiteral("黄"), yellowInteral));
					int remainingTime = periodTime - phaseObj[QStringLiteral("start_time")].toInt() - phaseObj[QStringLiteral("green_time")].toInt() - yellowInteral;
					if (remainingTime > 0) {
						lColorInterval.append(Online::ColorInterval(QStringLiteral("红"), remainingTime));
					}
					// 当前灯组包含的相位序号
					ISignalPhase* pCurrentPhase = nullptr;
					for (ISignalPhase*& pCurrentSignalGroupPhase : lCurrentSignalGroupPhases) {
						if (phaseNumber == pCurrentSignalGroupPhase->number()) {
							pCurrentPhase = pCurrentSignalGroupPhase;
							break;
						}
					}
					// 若已存在该相位，修改相位灯色顺序，否则添加相位
					if (pCurrentPhase) {
						// 修改相位
						pCurrentPhase->setColorList(lColorInterval);
						qDebug() << pCurrentPhase->id() << "相位设置成功" << endl;
					}
					else {
						ISignalPhase* pSignalPhase = gpTessInterface->netInterface()->createSignalPhase(pCurrentSignalGroup, phaseName, lColorInterval);
						// 设置相位序号
						pSignalPhase->setNumber(phaseNumber);
						qDebug() << pSignalPhase->id() << "相位创建成功" << endl;
					}
					// 设置相位包含的信号灯
					QJsonArray lampList = phaseObj[QStringLiteral("lamp_lst")].toArray();
					for (const QJsonValue& lampId : lampList) {
						ISignalLamp* pLamp = gpTessInterface->netInterface()->findSignalLamp(lampId.toInt());
						if (!pLamp) {
							/*
							 * 目前一个信号灯属于多个相位，相位间不交叉。
							 * 因此如果要实际下发方案时，应按照仿真时间实时管理相位序号。
							 */
							pLamp->setPhaseNumber(phaseNumber);
							qDebug() << pLamp->id() << "序号信号灯相位设置成功" << endl;
						}
						else {
							qDebug() << "FindError:未查找到信号灯:" << lampId.toInt();
						}
					}
				}
				break;
			}

		}
	}
}

//双环信控方案下发测试
void SecondaryDevCases::doubleRingSignalControlTest(int planNumber) {
	// 读取方案数据
	QFile jsonFile("./Data/Signal_Plan_Data_1109.json");
	if (!jsonFile.open(QIODevice::ReadOnly | QIODevice::Text)) {
		qDebug() << "TestError: Could not open Signal_Plan_Data_1109.json";
		return;
	}
	QByteArray jsonData = jsonFile.readAll();
	jsonFile.close();
	QJsonDocument doc = QJsonDocument::fromJson(jsonData);
	QJsonObject signalGroupsDict = doc.object();
	QList<long> lSignalGroupsStartTimeSeconds;
	//只用一个路测试即可
	for (const QJsonValueRef& group : signalGroupsDict) {
		const QJsonObject& groupObject = group.toObject();
		for (QString& startTime : groupObject.keys()) {
			lSignalGroupsStartTimeSeconds.append(Functions::timeToSeconds(startTime));
		}
	}
	// 当前方案序号
	int currentPlanNumber = planNumber % lSignalGroupsStartTimeSeconds.size();
	qDebug() << lSignalGroupsStartTimeSeconds[currentPlanNumber] << ":双环信控方案更改。";
	doubleRingSignalControl(lSignalGroupsStartTimeSeconds[currentPlanNumber]);
}

//流量加载示例路段和连接段创建
void SecondaryDevCases::trafficLoadingPrePare() {
	QList<ISection*> lLinksAndConnector = createExampleLinkAndConnector(QStringLiteral("流量加载"), -50);
	ILink* pLink1 = lLinksAndConnector.front()->castToLink();
	/* 2.动态发车 */
	QList<ISection*> lLinksAndConnectorDynaVehi = createExampleLinkAndConnector(QStringLiteral("动态发车"), -25);
	ILink* pLink3 = lLinksAndConnectorDynaVehi.front()->castToLink();
	lTrafficLoadingSections << pLink1;
	lTrafficLoadingSections << pLink3;
}

//流量加载
void SecondaryDevCases::trafficLoading(float planNumber) {
	static bool bVehiCompositionFlag = false;
	ILink* pLink1 = nullptr;
	ILink* pLink3 = nullptr;
	if (!lTrafficLoadingSections.isEmpty()) {
		pLink1 = lTrafficLoadingSections.front()->castToLink();
		pLink3 = lTrafficLoadingSections.back()->castToLink();
	}
	if (planNumber == 1 && !bVehiCompositionFlag) {
		// 创建车辆组成及指定车辆类型
		QList<Online::VehiComposition> lVehiTypeProportion;
		// 车型组成：小客车0.3，大客车0.2，公交车0.1，货车0.4
		lVehiTypeProportion.push_back(Online::VehiComposition(1, 0.3));
		lVehiTypeProportion.push_back(Online::VehiComposition(2, 0.2));
		lVehiTypeProportion.push_back(Online::VehiComposition(3, 0.1));
		lVehiTypeProportion.push_back(Online::VehiComposition(4, 0.4));
		int vehiCompositionID = gpTessInterface->netInterface()->createVehicleComposition("动态创建车型组成", lVehiTypeProportion);
		if (vehiCompositionID != -1) {
			qDebug() << "车型组成创建成功，id为：" << vehiCompositionID << endl;
			// 新建发车点,车型组成ID为动态创建的，600秒发300辆车
			if (pLink1) {
				IDispatchPoint* dp = gpTessInterface->netInterface()->createDispatchPoint(pLink1);
				if (dp) {
					dp->addDispatchInterval(vehiCompositionID, 600, 300);
					bVehiCompositionFlag = true;
				}
			}
		}
	}
	else if (planNumber == 2) {
		if (pLink3) {
			Online::DynaVehiParam dvpLane0, dvpLane1, dvpLane2;
			// 在指定车道和位置动态加载车辆(示例：在0,1,2车道不同位置动态加载车辆)
			dvpLane0.vehiTypeCode = 1;
			dvpLane1.vehiTypeCode = 2;
			dvpLane2.vehiTypeCode = 3;
			dvpLane0.roadId = pLink3->id();
			dvpLane1.roadId = pLink3->id();
			dvpLane2.roadId = pLink3->id();
			dvpLane0.laneNumber = 0;
			dvpLane1.laneNumber = 1;
			dvpLane2.laneNumber = 2;
			dvpLane0.dist = m2p(50);
			dvpLane1.dist = m2p(100);
			dvpLane2.dist = m2p(50);
			dvpLane0.speed = 20;
			dvpLane1.speed = 30;
			dvpLane2.speed = 40;
			dvpLane0.color = "#FF0000";
			dvpLane1.color = "#008000";
			dvpLane2.color = "#0000FF";
			auto vehi_lane0 = gpTessInterface->simuInterface()->createGVehicle(dvpLane0);
			auto vehi_lane1 = gpTessInterface->simuInterface()->createGVehicle(dvpLane1);
			auto vehi_lane2 = gpTessInterface->simuInterface()->createGVehicle(dvpLane2);
		}
	}
}

//路径加载
void SecondaryDevCases::flowLoading(float planNumber, long currentTime) {
	static bool bPlanNumberFlag1 = false;
	static bool bPlanNumberFlag2 = false;
	//标准四岔路口流量加载，L3-C2-L10为例
	if (planNumber == 1 && !bPlanNumberFlag1) {
		// 根据路段ID获取路段
		ILink* pLink3 = gpTessInterface->netInterface()->findLink(3);
		ILink* pLink10 = gpTessInterface->netInterface()->findLink(10);
		ILink* pLink6 = gpTessInterface->netInterface()->findLink(6);
		ILink* pLink7 = gpTessInterface->netInterface()->findLink(7);
		ILink* pLink8 = gpTessInterface->netInterface()->findLink(8);
		//新建发车点
		if (pLink3) {
			IDispatchPoint* dp = gpTessInterface->netInterface()->createDispatchPoint(pLink3);
			if (dp) {
				dp->addDispatchInterval(1, 600, 300);
			}
		}
		//创建决策点
		mpDecisionPoint = gpTessInterface->netInterface()->createDecisionPoint(pLink3, m2p(30));
		//创建路径(左，直，右)
		IRouting* decisionRoutingLeft = gpTessInterface->netInterface()->createDeciRouting(mpDecisionPoint, QList<ILink*>() << pLink3 << pLink10 << pLink6);
		IRouting* decisionRoutingStraight = gpTessInterface->netInterface()->createDeciRouting(mpDecisionPoint, QList<ILink*>() << pLink3 << pLink10 << pLink8);
		IRouting* decisionRoutingRight = gpTessInterface->netInterface()->createDeciRouting(mpDecisionPoint, QList<ILink*>() << pLink3 << pLink10 << pLink7);
		//分配左直右流量比
		_RoutingFLowRatio _flowRatioLeft, _flowRatioStraight, _flowRatioRight;
		_flowRatioLeft.RoutingFLowRatioID = 1;
		_flowRatioLeft.routingID = decisionRoutingLeft->id();
		_flowRatioLeft.startDateTime = 0;
		_flowRatioLeft.endDateTime = 999999;
		_flowRatioLeft.ratio = 2.0;
		_flowRatioStraight.RoutingFLowRatioID = 2;
		_flowRatioStraight.routingID = decisionRoutingStraight->id();
		_flowRatioStraight.startDateTime = 0;
		_flowRatioStraight.endDateTime = 999999;
		_flowRatioStraight.ratio = 3.0;
		_flowRatioRight.RoutingFLowRatioID = 3;
		_flowRatioRight.routingID = decisionRoutingRight->id();
		_flowRatioRight.startDateTime = 0;
		_flowRatioRight.endDateTime = 999999;
		_flowRatioRight.ratio = 1.0;
		// 决策点数据
		_DecisionPoint _decisionPointData;
		_decisionPointData.deciPointID = mpDecisionPoint->id();
		_decisionPointData.deciPointName = mpDecisionPoint->name();
		QPointF decisionPointPos;
		if (mpDecisionPoint->link()->getPointByDist(mpDecisionPoint->distance(), decisionPointPos)) {
			_decisionPointData.X = decisionPointPos.x();
			_decisionPointData.Y = decisionPointPos.y();
			_decisionPointData.Z = mpDecisionPoint->link()->z();
		}
		//更新决策点及其各路径不同时间段流量比
		mpDecisionPoint = gpTessInterface->netInterface()->updateDecipointPoint(_decisionPointData, QList<_RoutingFLowRatio>() << _flowRatioLeft << _flowRatioStraight << _flowRatioRight);
		bPlanNumberFlag1 = true;
	}
	//移除右转路径
	else if (planNumber == 2 && bPlanNumberFlag1 && !bPlanNumberFlag2) {
		if (gpTessInterface->netInterface()->removeDeciRouting(mpDecisionPoint, mpDecisionPoint->routings().back())) {
			bPlanNumberFlag2 = true;
			qDebug() << "删除右转路径成功" << endl;
		}
	}
	else if (planNumber == 3) {
		flowLoadingSection(currentTime);
	}
}

//路径断面流量加载
void SecondaryDevCases::flowLoadingSection(long currentTime) {
	// 读取方案数据
	QFile jsonFile("./Data/flow_ratio_quarter.json");
	if (!jsonFile.open(QIODevice::ReadOnly | QIODevice::Text)) {
		qDebug() << "Error: Could not open flow_ratio_quarter.json";
		return;
	}
	QByteArray jsonData = jsonFile.readAll();
	jsonFile.close();
	QJsonDocument doc = QJsonDocument::fromJson(jsonData);
	QJsonObject flowRatioQuarterDict = doc.object();
	for (QJsonObject::iterator it = flowRatioQuarterDict.begin(); it != flowRatioQuarterDict.end(); ++it) {
		int linkId = it.key().toInt();
		QJsonObject quarterRatios = it.value().toObject();
		IDecisionPoint* pCurrentDecisionPoint = nullptr;
		//查找决策点
		QList<IDecisionPoint*> lDecisionPoints = gpTessInterface->netInterface()->decisionPoints();
		for (IDecisionPoint*& pDecisionPoint : lDecisionPoints) {
			if (pDecisionPoint->link()->id() == linkId) {
				pCurrentDecisionPoint = pDecisionPoint;
				break;
			}
		}
		if (pCurrentDecisionPoint) {
			for (QJsonObject::iterator it2 = quarterRatios.begin(); it2 != quarterRatios.end(); ++it2) {
				QString quarterStartTime = it2.key();
				long quarterStartTimeSeconds = Functions::timeToSeconds(quarterStartTime);
				QJsonObject::iterator nextIt = std::next(it2);
				QString quarterEndTime = (nextIt != quarterRatios.end()) ? nextIt.key() : "24:00";
				long quarterEndTimeSeconds = Functions::timeToSeconds(quarterEndTime);
				if (currentTime < quarterEndTimeSeconds && currentTime >= quarterStartTimeSeconds) {
					qDebug() << quarterStartTime << quarterEndTimeSeconds << endl;
					QJsonObject quarterRatio = it2.value().toObject();
					QList<IRouting*> lDecisionPointRoutings = pCurrentDecisionPoint->routings();
					if (lDecisionPointRoutings.size() == 3) {
						// 分配左、直、右流量比
						_RoutingFLowRatio _flowRatioLeft, _flowRatioStraight, _flowRatioRight;
						_flowRatioLeft.RoutingFLowRatioID = lDecisionPointRoutings[0]->id();
						_flowRatioLeft.routingID = lDecisionPointRoutings[0]->id();
						_flowRatioLeft.startDateTime = 1;
						_flowRatioLeft.endDateTime = 99999;
						_flowRatioLeft.ratio = static_cast<long>(quarterRatio["left"].toInt());
						_flowRatioStraight.RoutingFLowRatioID = lDecisionPointRoutings[1]->id();
						_flowRatioStraight.routingID = lDecisionPointRoutings[1]->id();
						_flowRatioStraight.startDateTime = 1;
						_flowRatioStraight.endDateTime = 99999;
						_flowRatioStraight.ratio = static_cast<long>(quarterRatio["straight"].toInt());
						_flowRatioRight.RoutingFLowRatioID = lDecisionPointRoutings[2]->id();
						_flowRatioRight.routingID = lDecisionPointRoutings[2]->id();
						_flowRatioRight.startDateTime = 1;
						_flowRatioRight.endDateTime = 99999;
						_flowRatioRight.ratio = static_cast<long>(quarterRatio["right"].toInt());
						// 决策点数据
						_DecisionPoint _decisionPointData;
						_decisionPointData.deciPointID = pCurrentDecisionPoint->id();
						_decisionPointData.deciPointName = pCurrentDecisionPoint->name();
						QPointF decisionPointPos;
						if (pCurrentDecisionPoint->link()->getPointByDist(pCurrentDecisionPoint->distance(), decisionPointPos)) {
							_decisionPointData.X = decisionPointPos.x();
							_decisionPointData.Y = decisionPointPos.y();
							_decisionPointData.Z = pCurrentDecisionPoint->link()->z();
						}
						//更新决策点及其各路径不同时间段流量比
						IDecisionPoint* pUpdatedCurrentDecisionPoint = gpTessInterface->netInterface()->updateDecipointPoint(_decisionPointData, QList<_RoutingFLowRatio>() << _flowRatioLeft << _flowRatioStraight << _flowRatioRight);
						if (pUpdatedCurrentDecisionPoint) {
							qDebug() << quarterStartTime << "流量更新成功" << endl;
						}
					}
					else
					{
						qDebug() << pCurrentDecisionPoint->id() << "决策点需要包含3条路径" << endl;
					}
					break;
				}
			}
		}
	}
}

//动作控制
void SecondaryDevCases::actionControl(float planNumber) {
	/*以动作控制案例-机动车交叉口路网的L5路段为例*/

	/*
	'''1. 修改发车流量信息'''
	修改发车流量信息需在MySimulator中的calcDynaDispatchParameters函数
	*/
	/*
	'''2. 车辆位置移动'''
		# 见MySimulator中的afterOneStep函数
	*/
	/*
	'''3. 修改车辆速度'''
		# 见MySimulator中的reSetSpeed函数
	*/
	/*
	'''4. 修改车辆路径'''
		 # 以L1路段上的路径为例，见MySimulator中的afterOneStep函数
	*/
	/*
	'''5. 强制车辆不变道'''
		 # 以L2路段上的路径为例，见MySimulator中的afterOneStep函数
	*/
	/*
	'''6. 强制车辆变道'''
		 # 以L5路段上的路径为例，见MySimulator中的afterOneStep函数
	*/
	/*
	'''7. 强制车辆闯红灯'''
		# 见MySimulator的reSetSpeed函数
	*/
	/*
	'''8. 强制清除车辆'''
		# 以L5路段上的路径为例，见afterOneStep
	*/
	/*
	'''9. 修改车辆航向角'''
		# 以L5路段上的路径为例，见afterStep
	*/
	/*
	   10. 车道关闭和恢复
		# 可由强制变道和不变道实现。
	*/
	mActionControlMethodNumber = planNumber;
}

// 判断车辆变道意图
QString SecondaryDevCases::judgeVehicleLaneChangeDirection(IVehicle* pIVehicle) {
	ILane* pLane = pIVehicle->lane();
	QPointF vehiCurrPos = pIVehicle->pos();
	qreal vehiCurrDistToStart = pLane->distToStartPoint(vehiCurrPos);
	QList<QPointF> lLaneCenterBreakPoints = pLane->centerBreakPoints();
	int vehiSegmentIndex = -1;
	for (int i = 0, size = lLaneCenterBreakPoints.size(); i < size; ++i) {
		qreal centerBreakPointDistToStart = pLane->distToStartPoint(lLaneCenterBreakPoints[i]);
		if (vehiCurrDistToStart < centerBreakPointDistToStart) {
			vehiSegmentIndex = i;
			break;
		}
	}
	if (vehiSegmentIndex > 0 && vehiSegmentIndex < lLaneCenterBreakPoints.size()) {
		QPointF startBreakPoint = lLaneCenterBreakPoints[vehiSegmentIndex - 1];
		QPointF endBreakPoint = lLaneCenterBreakPoints[vehiSegmentIndex];
		// 以点积判断车辆处于中心线左侧还是右侧
		QString vehiDirection = Functions::carPositionRoad(startBreakPoint, endBreakPoint, vehiCurrPos);
		// 判断车头角度偏度
		double breakLaneAngle = Functions::calculateAngle(startBreakPoint, endBreakPoint);
		// 若车辆处于中心线右侧且车头右偏，则判定为右变道意图
		if (vehiDirection == "right" && pIVehicle->angle() > breakLaneAngle) {
			return QStringLiteral("right");
		}
		// 若车辆处于中心线左侧且车头左偏，则判定为左变道意图
		else if (vehiDirection == "left" && pIVehicle->angle() < breakLaneAngle) {
			return QStringLiteral("left");
		}
		else {
			return QStringLiteral("noChange");
		}
	}
	else {
		qDebug() << "FindError:can't find the segment,relevant info:" << vehiSegmentIndex << vehiCurrDistToStart << vehiCurrPos << endl;
	}
	return QStringLiteral("");
}

//管控手段控制
void SecondaryDevCases::controlMeasures(float planNumber, int limitSpeed) {
	/*
	'''1. 修改信号灯灯色'''
	见MySimulator的calcLampColor函数
	*/
	mContorlMeasureMethodNumber = planNumber;
	/*
	'''2. 修改信号灯灯色'''
	*/
	// 以L12路段相位直行信号灯相位为例（ID为7），由红90绿32黄3红25改为红10绿110黄3红28
	if (planNumber == 2) {
		ISignalPhase* pSignalPhase7OfL12 = gpTessInterface->netInterface()->findSignalPhase(7);
		Online::ColorInterval redIntervalFront("红", 10), greenInterval("绿", 110), yellowInterval("黄", 3), redIntervalBack("红", 28);
		pSignalPhase7OfL12->setColorList(QList<Online::ColorInterval>() << redIntervalFront << greenInterval << yellowInterval << redIntervalBack);
	}
	/*
	'''3. 修改路段限速'''
	*/
	//以L5路段为例
	if (planNumber == 3) {
		ILink* pLink5 = gpTessInterface->netInterface()->findLink(5);
		qreal minSpeedOfLink5 = pLink5->minSpeed();
		if (limitSpeed >= minSpeedOfLink5) {
			pLink5->setLimitSpeed(static_cast<qreal>(limitSpeed));
		}
	}
}

//流程控制
void SecondaryDevCases::processControl(float planNumber) {
	/*
	'''1. 启动、暂停、恢复、停止仿真'''
	*/
	if (planNumber == float(1.1)) {
		gpTessInterface->simuInterface()->startSimu();
	}
	if (planNumber == float(1.2)) {
		gpTessInterface->simuInterface()->pauseSimu();
	}
	if (planNumber == float(1.3)) {
		gpTessInterface->simuInterface()->stopSimu();
	}
	if (planNumber == float(1.4)) {
		gpTessInterface->simuInterface()->pauseSimuOrNot();
	}
	/*
	'''2. 获取运动信息'''
	*/
	//2.1 获取路网在途车辆
	if (planNumber == float(2.1)) {
		//所有在运行车辆
		QList<IVehicle*> lAllVehi = gpTessInterface->simuInterface()->allVehiStarted();
		QString runInfo = QStringLiteral("路网在途车辆共%0辆，ID为:\n").arg(lAllVehi.size());
		for (IVehicle*& vehi : lAllVehi) {
			runInfo += QStringLiteral("车辆%0,当前坐标(%1,%2)\n").arg(vehi->id()).arg(vehi->pos().x()).arg(vehi->pos().y());
		}
		emit(showDynaInfo(runInfo));
	}
	//2.2 根据路段|车道获取车辆list,以L5路段，lane20车道为例。
	if (planNumber == float(2.2)) {
		QList<IVehicle*> lVehiOnLink5 = gpTessInterface->simuInterface()->vehisInLink(5);
		QString runInfoOfLinkAndLane = QStringLiteral("L5路段车辆共%0辆，ID为:\n").arg(lVehiOnLink5.size());
		for (IVehicle*& vehi : lVehiOnLink5) {
			runInfoOfLinkAndLane += QStringLiteral("车辆%0,当前坐标(%1,%2)\n").arg(vehi->id()).arg(vehi->pos().x()).arg(vehi->pos().y());
		}
		QList<IVehicle*> lVehiOnLane20 = gpTessInterface->simuInterface()->vehisInLane(20);
		runInfoOfLinkAndLane += QStringLiteral("Lane20车道车辆共%0辆，ID为:\n").arg(lVehiOnLane20.size());
		for (IVehicle*& vehi : lVehiOnLane20) {
			runInfoOfLinkAndLane += QStringLiteral("车辆%0,当前坐标(%1,%2)\n").arg(vehi->id()).arg(vehi->pos().x()).arg(vehi->pos().y());
		}
		emit(showDynaInfo(runInfoOfLinkAndLane));
	}
	//2.3 根据车辆id获取具体的车辆信息,以id为300001的车辆为例
	if (planNumber == float(2.3)) {
		IVehicle* vehi300001 = gpTessInterface->simuInterface()->getVehicle(300001);
		if (vehi300001) {
			QString runInfoOfVehi = QStringLiteral("%0车辆信息为:\n").arg(vehi300001->id());
			runInfoOfVehi += QStringLiteral("所在路段ID:%0\n").arg(vehi300001->roadId());
			runInfoOfVehi += QStringLiteral("所在车道序号:%0\n").arg(vehi300001->lane()->number() + 1);
			runInfoOfVehi += QStringLiteral("当前车速:%0\n").arg(vehi300001->currSpeed());
			runInfoOfVehi += QStringLiteral("当前加速度:%0\n").arg(vehi300001->acce());
			runInfoOfVehi += QStringLiteral("当前角度:%0\n").arg(vehi300001->angle());
			runInfoOfVehi += QStringLiteral("当前位置:(%1,%2)\n").arg(vehi300001->pos().x()).arg(vehi300001->pos().y());
			runInfoOfVehi += QStringLiteral("其它：......\n");
			emit(showDynaInfo(runInfoOfVehi));
		}
	}
	// 3. 设置仿真精度
	if (planNumber == 3) {
		gpTessInterface->simuInterface()->setSimuAccuracy(10);
	}
	// 4. 设置仿真开始结束时间
	if (planNumber == 4) {
		gpTessInterface->simuInterface()->setSimuIntervalScheming(30);
	}
	// 5. 设置仿真加速比
	if (planNumber == 5) {
		gpTessInterface->simuInterface()->setAcceMultiples(10);
	}
}

//模型修改
void SecondaryDevCases::modelModify(int planNumber) {
	/*1. 修改跟驰模型参数（机动车，非机动车）*/
	// 见MySimulator中的reSetFollowingParams函数

	mModelModifyMethodNumber = planNumber;
}




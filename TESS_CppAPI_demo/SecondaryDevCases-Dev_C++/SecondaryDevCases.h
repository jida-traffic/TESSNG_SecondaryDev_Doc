#ifndef __SecondaryDevCases__
#define __SecondaryDevCases__

#include <QFile>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QMutex>

#include "tessinterface.h"
#include "UnitChange.h"
#include "netinterface.h"
#include "ilink.h"
#include "IDispatchPoint.h"
#include "IConnector.h"
#include "ISignalGroup.h"
#include "ISignalPhase.h"
#include "ISignalLamp.h"
#include "ISection.h"
#include "simuinterface.h"
#include "IRouting.h"
#include "IDecisionPoint.h"
#include "iVehicle.h"
#include "ivehicledriving.h"

#include "MyFunctions.h"

class IDecisionPoint;

class SecondaryDevCases : public QObject {
	Q_OBJECT
public:
	SecondaryDevCases(long _id);
	//创建示例路段和连接段
	QList<ISection*> createExampleLinkAndConnector(QString LinkName, int Posy);
	//信控编辑
	void signalControllerEdit();
	//双环信控方案下发
	void doubleRingSignalControl(long currentSimuTime);
	//双环信控方案下发测试
	void doubleRingSignalControlTest(int planNumber);
	//流量加载
	void trafficLoading(float planNumber);
	//流量加载示例路段和连接段创建
	void trafficLoadingPrePare();
	//路径加载
	void flowLoading(float planNumber ,long currentTime);
	//路径断面流量加载
	void flowLoadingSection(long currentTime);
	//动作控制
	void actionControl(float planNumber);
	//动作控制方案号
	float mActionControlMethodNumber;
	// 判断车辆变道意图
	QString judgeVehicleLaneChangeDirection(IVehicle* pIVehicle);
	//管控手段控制
	void controlMeasures(float planNumber, int limitSpeed);
	//管控手段控制方案号
	float mContorlMeasureMethodNumber;
	//流程控制
	void processControl(float planNumber);
	//流程控制方案号
	float mPreocessControlMethodNumber;
	//期望速度标志位与开始时间
	bool reCalcdesirSpeedFlag;
	long reCalcdesirSpeedStartTime;
	//模型修改
	void modelModify(int planNumber);
	//模型修改方案号
	int mModelModifyMethodNumber;

private:
	long secondDevId;
	QMutex mutex;
	IDecisionPoint* mpDecisionPoint;
	QList<ISection*> lTrafficLoadingSections;
	
signals:
	//展示动态信息
	void showDynaInfo(const QString& info);
};

#endif // !__SecondaryDevCase__

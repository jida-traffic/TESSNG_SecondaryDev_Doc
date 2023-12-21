#ifndef __MySimulator__
#define __MySimulator__

#include <QObject>

#include "Plugin/customersimulator.h"
#include "IRoadWorkZone.h"
#include "IAccidentZone.h"
#include "SecondaryDevCases.h"

class SecondaryDevCases;

class MySimulator : public QObject, public CustomerSimulator
{
	Q_OBJECT

public:
	MySimulator(SecondaryDevCases* pSecondDevCasesObj);
	~MySimulator();

	//仿真前的准备
	void beforeStart(bool& keepOn) override;
	//仿真起动后的处理
	void afterStart() override;
	//仿真结束后的处理
	void afterStop() override;

	//初始车辆
	void initVehicle(IVehicle* pIVehicle) override;
	//计算加速度
	bool calcAcce(IVehicle* pIVehicle, qreal& acce) override;
	//重新计算期望速度
	bool reCalcdesirSpeed(IVehicle* pIVehicle, qreal& inOutDesirSpeed) override;
	//重新设置跟驰的安全时距及安全距离
	bool reSetFollowingParam(IVehicle* pIVehicle, qreal& inOutSi, qreal& inOutSd) override;
	//计算动态发车参数
	QList<Online::DispatchInterval> calcDynaDispatchParameters() override;
	//计算动态修改决策流量比的参数
	QList<Online::DecipointFlowRatioByInterval> calcDynaFlowRatioParameters() override;
	//重新设置车辆加速度
	bool reSetAcce(IVehicle* pIVehicle, qreal& inOutAcce) override;
	//重新设置速度
	bool reSetSpeed(IVehicle* pIVehicle, qreal& inOutSpeed) override;
	//计算是否要左自由变道
	bool reCalcToLeftFreely(IVehicle *pIVehicle) override;
	//计算是否要右自由变道
	bool reCalcToRightFreely(IVehicle *pIVehicle) override;
	//计算信号灯颜色
	bool calcLampColor(ISignalLamp* pSignalLamp) override;
	//一个批次计算后的处理
	void afterOneStep() override;
	//插件绘制车辆
	bool paintVehicle(IVehicle* pIVehicle, QPainter* painter) override;
	//完成车辆 pIVehicle “一个批次计算”后的处理。
	void afterStep(IVehicle* pIVehicle);
	// 修改跟驰模型参数
	QList<Online::FollowingModelParam> reSetFollowingParams();

	// 计算限制车道序号
	QList<int> calcLimitedLaneNumber(IVehicle* pIVehicle) override;
	// 撤销变道
	bool reCalcDismissChangeLane(IVehicle* pIVehicle) override;
	/*
	重新设置自由变道参数，
	参数 safeTime : 安全操作时间，从驾驶员反应到实施变道(完成变道前半段)所需时间，默认4秒，
		 ultimateDist:安全变道(完成变道前半段)后距前车距离，小于此距离压迫感增强，触发驾驶员寻求变道，
		 targetRParm:目标车道后车影响系数，大于等于0小于等于1，此值越大目标车道后车距影响越大，反之则越小
	*/
	 bool reSetChangeLaneFreelyParam(IVehicle* pIVehicle, int& safeTime, qreal& ultimateDist, qreal& targetRParam) override;

	//动态创建施工区
	//IRoadWorkZone* createWorkzone();

	//动态创建事故区
	IAccidentZone* createAccidentZone();

	//自由左变道前处理
	void beforeToLeftFreely(IVehicle* pIVehicle, bool& bKeepOn) override;

	//自由右变道前处理
	void beforeToRightFreely(IVehicle* pIVehicle, bool& bKeepOn) override;

private:
	//像素比
	//qreal mrScale;
	//排成方正车辆数
	int mrSquareVehiCount;
	//仿真开始的现实时间
	qint64 mrStartMSecs;
	//飞机速度
	qreal mrSpeedOfPlane;
	//支行过程产生的信息
	QString mRunInfo;
	//当前正在仿真计算的路网名称
	QString mNetPath;
	//相同路网连续仿真次数
	int mSimuCount;

	//二次开发案例对象
	SecondaryDevCases* mpSecondDevCasesObj;
signals:
	//要求展示信息的消息
	void forRunInfo(const QString& info);

	//要求停止仿真的消息
	void forStopSimu();
	//当仿真结束后，要求重新启动仿真的消息
	void forReStartSimu();
	//要求重新加载指定路网的消息
	void forReLoadNetFileByPath(const QString&);
};

#endif
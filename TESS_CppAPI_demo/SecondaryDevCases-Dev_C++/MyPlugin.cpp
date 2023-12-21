#include "MyPlugin.h"

#include <QDockWidget>
#include <QMessageBox>

#include "tessinterface.h"
#include "guiinterface.h"
#include "MyNet.h"
#include "MySimulator.h"
#include "TESS_API_EXAMPLE.h"
#include "Plugin/StepsPerCall.h"

MyPlugin::MyPlugin()
	:mpExampleWindow(nullptr), mpMyNet(nullptr), mpMySimulator(nullptr), mpSecondDevCasesObj(nullptr)
{
}

void MyPlugin::init()
{
	mpSecondDevCasesObj = new SecondaryDevCases(0);
	initGui();
	mpMyNet = new MyNet(mpSecondDevCasesObj);
	mpMySimulator = new MySimulator(mpSecondDevCasesObj);

	QObject::connect(mpMySimulator, SIGNAL(forRunInfo(const QString)), mpExampleWindow, SLOT(showRunInfo(const QString)));
	QObject::connect(mpSecondDevCasesObj, SIGNAL(showDynaInfo(const QString)), mpExampleWindow, SLOT(showRunInfo(const QString)));

	QMainWindow* pMainWindow = gpTessInterface->guiInterface()->mainWindow();
	QObject::connect(mpMySimulator, SIGNAL(forReStartSimu()), pMainWindow, SLOT(doStartSimu()), Qt::QueuedConnection);
	QObject::connect(mpMySimulator, SIGNAL(forStopSimu()), pMainWindow, SLOT(doStopSimu()), Qt::QueuedConnection);
}

void MyPlugin::initGui() {
	//在TESS NG主界面上增加 QDockWidget对象
	mpExampleWindow = new TESS_API_EXAMPLE(mpSecondDevCasesObj);
	QDockWidget* pDockWidget = new QDockWidget(QString("自定义与TESS NG交互界面"), (QWidget*)gpTessInterface->guiInterface()->mainWindow());
	pDockWidget->setObjectName(QStringLiteral("mainDockWidget"));
	pDockWidget->setFeatures(QDockWidget::NoDockWidgetFeatures);
	pDockWidget->setAllowedAreas(Qt::LeftDockWidgetArea);
	pDockWidget->setWidget(mpExampleWindow->centralWidget());
	gpTessInterface->guiInterface()->addDockWidgetToMainWindow(static_cast<Qt::DockWidgetArea>(1), pDockWidget);

	//增加菜单及菜单项
	QMenuBar* pMenuBar = gpTessInterface->guiInterface()->menuBar();

	//双环信控方案下发菜单及菜单项
	QMenu* pMenuDoubleRingSignal = new QMenu(pMenuBar);
	pMenuDoubleRingSignal->setObjectName(QString::fromUtf8("DoubleRingSignalControl"));
	pMenuBar->addAction(pMenuDoubleRingSignal->menuAction());
	pMenuDoubleRingSignal->setTitle(QString("双环信控方案下发测试"));

	QAction* pActionDoubleRingSignal = new QAction(pMenuBar->parent());
	pActionDoubleRingSignal->setObjectName("actionDoubleRingSignalControl");
	pActionDoubleRingSignal->setText(QString("下发方案"));
	pActionDoubleRingSignal->setCheckable(false);
	pMenuDoubleRingSignal->addAction(pActionDoubleRingSignal);
	QObject::connect(pActionDoubleRingSignal, SIGNAL(triggered()), mpExampleWindow, SLOT(doubleRingSignalControlTestResponse()));

	//流量加载菜单及菜单项
	QMenu* pMenuTrafficLoad = new QMenu(pMenuBar);
	pMenuTrafficLoad->setObjectName(QString::fromUtf8("TrafficLoad"));
	pMenuBar->addAction(pMenuTrafficLoad->menuAction());
	pMenuTrafficLoad->setTitle(QString("流量加载"));

	QAction* pActionCreateVehiComposition = new QAction(pMenuBar->parent());
	pActionCreateVehiComposition->setObjectName("actionCreateVehiComposition");
	pActionCreateVehiComposition->setText(QString("创建车型组成测试"));
	pActionCreateVehiComposition->setCheckable(true);
	pMenuTrafficLoad->addAction(pActionCreateVehiComposition);
	QObject::connect(pActionCreateVehiComposition, &QAction::triggered, [=]() {
		mpSecondDevCasesObj->trafficLoading(1);
	});
	QAction* pActionDynaVehi = new QAction(pMenuBar->parent());
	pActionDynaVehi->setObjectName("actionDynaVehi");
	pActionDynaVehi->setText(QString("动态发车测试"));
	pActionDynaVehi->setCheckable(false);
	pMenuTrafficLoad->addAction(pActionDynaVehi);
	QObject::connect(pActionDynaVehi, &QAction::triggered, [=]() {
		mpSecondDevCasesObj->trafficLoading(2);
	});

	//路径加载菜单及菜单项
	QMenu* pMenuFlowLoad = new QMenu(pMenuBar);
	pMenuFlowLoad->setObjectName(QString::fromUtf8("FlowLoad"));
	pMenuBar->addAction(pMenuFlowLoad->menuAction());
	pMenuFlowLoad->setTitle(QString("路径加载与管理"));

	QAction* pActionCreateDecisionPoint = new QAction(pMenuBar->parent());
	pActionCreateDecisionPoint->setObjectName("actionCreateDecisionPoint");
	pActionCreateDecisionPoint->setText(QString("路径创建测试"));
	pActionCreateDecisionPoint->setCheckable(true);
	pMenuFlowLoad->addAction(pActionCreateDecisionPoint);
	QObject::connect(pActionCreateDecisionPoint, &QAction::triggered, [=]() {
		mpSecondDevCasesObj->flowLoading(1, 0);
	});
	QAction* pActionRemoveDecisionPoint = new QAction(pMenuBar->parent());
	pActionRemoveDecisionPoint->setObjectName("actionRemoveDecisionPoint");
	pActionRemoveDecisionPoint->setText(QString("删除路径测试(右转)"));
	pActionRemoveDecisionPoint->setCheckable(true);
	pMenuFlowLoad->addAction(pActionRemoveDecisionPoint);
	QObject::connect(pActionRemoveDecisionPoint, &QAction::triggered, [=]() {
		mpSecondDevCasesObj->flowLoading(2, 0);
	});
	QAction* pActionFlowLoadingSection = new QAction(pMenuBar->parent());
	pActionFlowLoadingSection->setObjectName("actionFlowLoadingSection");
	pActionFlowLoadingSection->setText(QString("断面流量加载测试(L4路段决策点)"));
	pActionFlowLoadingSection->setCheckable(false);
	pMenuFlowLoad->addAction(pActionFlowLoadingSection);
	QObject::connect(pActionFlowLoadingSection, SIGNAL(triggered()), mpExampleWindow, SLOT(flowLoadingSectionTest()));

	//动作控制菜单及菜单项
	QMenu* pMenuActionControl = new QMenu(pMenuBar);
	pMenuActionControl->setObjectName(QString::fromUtf8("ActionControl"));
	pMenuBar->addAction(pMenuActionControl->menuAction());
	pMenuActionControl->setTitle(QString("动作控制"));

	QAction* pActionCalcDynaDispatchParameters = new QAction(pMenuBar->parent());
	pActionCalcDynaDispatchParameters->setObjectName("actionCalcDynaDispatchParameters");
	pActionCalcDynaDispatchParameters->setText(QString("动态修改发车流量测试(L5路段发车点)"));
	pActionCalcDynaDispatchParameters->setCheckable(false);
	pMenuActionControl->addAction(pActionCalcDynaDispatchParameters);
	QObject::connect(pActionCalcDynaDispatchParameters, &QAction::triggered, [=]() {
		mpSecondDevCasesObj->actionControl(1);
	});
	QAction* pActionMoveVehi = new QAction(pMenuBar->parent());
	pActionMoveVehi->setObjectName("actionMoveVehi");
	pActionMoveVehi->setText(QString("车辆移动测试(L5路段)"));
	pActionMoveVehi->setCheckable(false);
	pMenuActionControl->addAction(pActionMoveVehi);
	QObject::connect(pActionMoveVehi, &QAction::triggered, [=]() {
		mpSecondDevCasesObj->actionControl(2);
	});
	QAction* pActionSetVehiSpeed = new QAction(pMenuBar->parent());
	pActionSetVehiSpeed->setObjectName("actionSetVehiSpeed");
	pActionSetVehiSpeed->setText(QString("车辆速度设置测试(L5路段)"));
	pActionSetVehiSpeed->setCheckable(false);
	pMenuActionControl->addAction(pActionSetVehiSpeed);
	QObject::connect(pActionSetVehiSpeed, &QAction::triggered, [=]() {
		mpSecondDevCasesObj->actionControl(3);
	});
	QAction* pActionSetVehiRouting = new QAction(pMenuBar->parent());
	pActionSetVehiRouting->setObjectName("actionSetVehiRouting");
	pActionSetVehiRouting->setText(QString("修改车辆路径测试(L1路段)"));
	pActionSetVehiRouting->setCheckable(false);
	pMenuActionControl->addAction(pActionSetVehiRouting);
	QObject::connect(pActionSetVehiRouting, &QAction::triggered, [=]() {
		mpSecondDevCasesObj->actionControl(4);
	});
	QAction* pActionForceVehiDontChangeLane = new QAction(pMenuBar->parent());
	pActionForceVehiDontChangeLane->setObjectName("actionForceVehiDontChangeLane");
	pActionForceVehiDontChangeLane->setText(QString("强制车辆不变道(L2路段禁止右变道)"));
	pActionForceVehiDontChangeLane->setCheckable(false);
	pMenuActionControl->addAction(pActionForceVehiDontChangeLane);
	QObject::connect(pActionForceVehiDontChangeLane, &QAction::triggered, [=]() {
		mpSecondDevCasesObj->actionControl(5);
	});
	QAction* pActionForceVehiChangeLane = new QAction(pMenuBar->parent());
	pActionForceVehiChangeLane->setObjectName("actionForceVehiChangeLane");
	pActionForceVehiChangeLane->setText(QString("强制车辆变道(L5路段中间车道右变道)"));
	pActionForceVehiChangeLane->setCheckable(false);
	pMenuActionControl->addAction(pActionForceVehiChangeLane);
	QObject::connect(pActionForceVehiChangeLane, &QAction::triggered, [=]() {
		mpSecondDevCasesObj->actionControl(6);
	});
	QAction* pActionRunRedLight = new QAction(pMenuBar->parent());
	pActionRunRedLight->setObjectName("actionRunRedLight");
	pActionRunRedLight->setText(QString("强制车辆闯红灯(L12路段概率闯红灯)"));
	pActionRunRedLight->setCheckable(false);
	pMenuActionControl->addAction(pActionRunRedLight);
	QObject::connect(pActionRunRedLight, &QAction::triggered, [=]() {
		mpSecondDevCasesObj->actionControl(7);
	});
	QAction* pActionStopVehi = new QAction(pMenuBar->parent());
	pActionStopVehi->setObjectName("actionStopVehi");
	pActionStopVehi->setText(QString("清除L5小客车"));
	pActionStopVehi->setCheckable(false);
	pMenuActionControl->addAction(pActionStopVehi);
	QObject::connect(pActionStopVehi, &QAction::triggered, [=]() {
		mpSecondDevCasesObj->actionControl(8);
	});
	QAction* pActionSetVehiAngle = new QAction(pMenuBar->parent());
	pActionSetVehiAngle->setObjectName("actionSetVehiAngle");
	pActionSetVehiAngle->setText(QString("设置L5车辆航向角(45度)"));
	pActionSetVehiAngle->setCheckable(false);
	pMenuActionControl->addAction(pActionSetVehiAngle);
	QObject::connect(pActionSetVehiAngle, &QAction::triggered, [=]() {
		mpSecondDevCasesObj->actionControl(9);
	});
	QAction* pActionSetLimitedSpeedArea = new QAction(pMenuBar->parent());
	pActionSetLimitedSpeedArea->setObjectName("actionSetLimitedSpeedArea");
	pActionSetLimitedSpeedArea->setText(QString("设置限速区(L5最右侧车道)"));
	pActionSetLimitedSpeedArea->setCheckable(false);
	pMenuActionControl->addAction(pActionSetLimitedSpeedArea);
	QObject::connect(pActionSetLimitedSpeedArea, &QAction::triggered, [=]() {
		mpSecondDevCasesObj->actionControl(10);
	});
	//取消车辆动作控制
	QAction* pActionCancelSetVehi = new QAction(pMenuBar->parent());
	pActionCancelSetVehi->setObjectName("actionCancelSetVehi");
	pActionCancelSetVehi->setText(QString("取消车辆控制"));
	pActionCancelSetVehi->setCheckable(false);
	pMenuActionControl->addAction(pActionCancelSetVehi);
	QObject::connect(pActionCancelSetVehi, &QAction::triggered, [=]() {
		mpSecondDevCasesObj->actionControl(0);
	});

	//管控手段控制菜单及菜单项
	QMenu* pMenuContorlMeasure = new QMenu(pMenuBar);
	pMenuContorlMeasure->setObjectName(QString::fromUtf8("ContorlMeasure"));
	pMenuBar->addAction(pMenuContorlMeasure->menuAction());
	pMenuContorlMeasure->setTitle(QString("管控手段控制"));

	QAction* pActionSetLampColor = new QAction(pMenuBar->parent());
	pActionSetLampColor->setObjectName("actionSetLampColor");
	pActionSetLampColor->setText(QString("修改信号灯色测试(绿色)"));
	pActionSetLampColor->setCheckable(false);
	pMenuContorlMeasure->addAction(pActionSetLampColor);
	QObject::connect(pActionSetLampColor, &QAction::triggered, [=]() {
		mpSecondDevCasesObj->controlMeasures(1, 0);
	});

	QAction* pActionSetPhase = new QAction(pMenuBar->parent());
	pActionSetPhase->setObjectName("actionSetPhase");
	pActionSetPhase->setText(QString("修改信号灯相位测试"));
	pActionSetPhase->setCheckable(false);
	pMenuContorlMeasure->addAction(pActionSetPhase);
	QObject::connect(pActionSetPhase, &QAction::triggered, [=]() {
		mpSecondDevCasesObj->controlMeasures(2, 0);
	});

	QAction* pActionSetLimitSpeed = new QAction(pMenuBar->parent());
	pActionSetLimitSpeed->setObjectName("actionSetLimitSpeed");
	pActionSetLimitSpeed->setText(QString("修改路段限速(L5)"));
	pActionSetLimitSpeed->setCheckable(false);
	pMenuContorlMeasure->addAction(pActionSetLimitSpeed);
	QObject::connect(pActionSetLimitSpeed, SIGNAL(triggered()), mpExampleWindow, SLOT(setLinkLimitedSpeed()));

	//取消管控手段控制
	QAction* pActionCancelContorlMeasures = new QAction(pMenuBar->parent());
	pActionCancelContorlMeasures->setObjectName("actionCancelContorlMeasures");
	pActionCancelContorlMeasures->setText(QString("取消管控手段控制"));
	pActionCancelContorlMeasures->setCheckable(false);
	pMenuContorlMeasure->addAction(pActionCancelContorlMeasures);
	QObject::connect(pActionCancelContorlMeasures, &QAction::triggered, [=]() {
		mpSecondDevCasesObj->controlMeasures(0, 0);
	});

	//流程控制菜单及菜单项
	QMenu* pMenuProcessControl = new QMenu(pMenuBar);
	pMenuProcessControl->setObjectName(QString::fromUtf8("ProcessControl"));
	pMenuBar->addAction(pMenuProcessControl->menuAction());
	pMenuProcessControl->setTitle(QString("流程控制"));

	QAction* pActionStartSimu = new QAction(pMenuBar->parent());
	pActionStartSimu->setObjectName("actionStartSimu");
	pActionStartSimu->setText(QString("启动仿真"));
	pActionStartSimu->setCheckable(false);
	pMenuProcessControl->addAction(pActionStartSimu);
	QObject::connect(pActionStartSimu, &QAction::triggered, [=]() {
		mpSecondDevCasesObj->processControl(1.1);
	});
	QAction* pActionPauseSimu = new QAction(pMenuBar->parent());
	pActionPauseSimu->setObjectName("actionPauseSimu");
	pActionPauseSimu->setText(QString("暂停仿真"));
	pActionPauseSimu->setCheckable(false);
	pMenuProcessControl->addAction(pActionPauseSimu);
	QObject::connect(pActionPauseSimu, &QAction::triggered, [=]() {
		mpSecondDevCasesObj->processControl(1.2);
	});
	QAction* pActionStopSimu = new QAction(pMenuBar->parent());
	pActionStopSimu->setObjectName("actionStopSimu");
	pActionStopSimu->setText(QString("停止仿真"));
	pActionStopSimu->setCheckable(false);
	pMenuProcessControl->addAction(pActionStopSimu);
	QObject::connect(pActionStopSimu, &QAction::triggered, [=]() {
		mpSecondDevCasesObj->processControl(1.3);
	});
	QAction* pActionPauseSimuOrNot = new QAction(pMenuBar->parent());
	pActionPauseSimuOrNot->setObjectName("actionPauseSimuOrNot");
	pActionPauseSimuOrNot->setText(QString("暂停/恢复仿真"));
	pActionPauseSimuOrNot->setCheckable(false);
	pMenuProcessControl->addAction(pActionPauseSimuOrNot);
	QObject::connect(pActionPauseSimuOrNot, &QAction::triggered, [=]() {
		mpSecondDevCasesObj->processControl(1.4);
	});
	QAction* pActionGetAllSimuVehicles = new QAction(pMenuBar->parent());
	pActionGetAllSimuVehicles->setObjectName("actionGetAllSimuVehicles");
	pActionGetAllSimuVehicles->setText(QString("获取路网在途车辆"));
	pActionGetAllSimuVehicles->setCheckable(false);
	pMenuProcessControl->addAction(pActionGetAllSimuVehicles);
	QObject::connect(pActionGetAllSimuVehicles, &QAction::triggered, [=]() {
		mpSecondDevCasesObj->processControl(2.1);
	});
	QAction* pActionGetLinkOrLaneSimuVehicles = new QAction(pMenuBar->parent());
	pActionGetLinkOrLaneSimuVehicles->setObjectName("actionGetLinkOrLaneSimuVehicles");
	pActionGetLinkOrLaneSimuVehicles->setText(QString("获取指定路段或车道上的车辆测试(L5、Lane20)"));
	pActionGetLinkOrLaneSimuVehicles->setCheckable(false);
	pMenuProcessControl->addAction(pActionGetLinkOrLaneSimuVehicles);
	QObject::connect(pActionGetLinkOrLaneSimuVehicles, &QAction::triggered, [=]() {
		mpSecondDevCasesObj->processControl(2.2);
	});
	QAction* pActionGetVehiInfoById = new QAction(pMenuBar->parent());
	pActionGetVehiInfoById->setObjectName("actionGetVehiInfoById");
	pActionGetVehiInfoById->setText(QString("根据ID获取车辆信息测试"));
	pActionGetVehiInfoById->setCheckable(false);
	pMenuProcessControl->addAction(pActionGetVehiInfoById);
	QObject::connect(pActionGetVehiInfoById, &QAction::triggered, [=]() {
		mpSecondDevCasesObj->processControl(2.3);
	});
	QAction* pActionSetSimuAccuracy = new QAction(pMenuBar->parent());
	pActionSetSimuAccuracy->setObjectName("actionSetSimuAccuracy");
	pActionSetSimuAccuracy->setText(QString("设置仿真精度测试"));
	pActionSetSimuAccuracy->setCheckable(false);
	pMenuProcessControl->addAction(pActionSetSimuAccuracy);
	QObject::connect(pActionSetSimuAccuracy, &QAction::triggered, [=]() {
		mpSecondDevCasesObj->processControl(3);
	});
	QAction* pActionSetSimuIntervalScheming = new QAction(pMenuBar->parent());
	pActionSetSimuIntervalScheming->setObjectName("actionSetSimuIntervalScheming");
	pActionSetSimuIntervalScheming->setText(QString("设置仿真开始结束时间测试"));
	pActionSetSimuIntervalScheming->setCheckable(false);
	pMenuProcessControl->addAction(pActionSetSimuIntervalScheming);
	QObject::connect(pActionSetSimuIntervalScheming, &QAction::triggered, [=]() {
		mpSecondDevCasesObj->processControl(4);
	});
	QAction* pActionSetAcceMultiples = new QAction(pMenuBar->parent());
	pActionSetAcceMultiples->setObjectName("actionSetAcceMultiples");
	pActionSetAcceMultiples->setText(QString("设置仿真加速比测试"));
	pActionSetAcceMultiples->setCheckable(false);
	pMenuProcessControl->addAction(pActionSetAcceMultiples);
	QObject::connect(pActionSetAcceMultiples, &QAction::triggered, [=]() {
		mpSecondDevCasesObj->processControl(5);
	});

	//模型修改菜单及菜单项
	QMenu* pMenuModelModify = new QMenu(pMenuBar);
	pMenuModelModify->setObjectName(QString::fromUtf8("ModelModify"));
	pMenuBar->addAction(pMenuModelModify->menuAction());
	pMenuModelModify->setTitle(QString("模型修改"));

	QAction* pActionReSetFollowingParams = new QAction(pMenuBar->parent());
	pActionReSetFollowingParams->setObjectName("actionReSetFollowingParams");
	pActionReSetFollowingParams->setText(QString("修改跟驰模型参数测试"));
	pActionReSetFollowingParams->setCheckable(false);
	pMenuModelModify->addAction(pActionReSetFollowingParams);
	QObject::connect(pActionReSetFollowingParams, &QAction::triggered, [=]() {
		mpSecondDevCasesObj->modelModify(1);
	});
	QAction* pActionReSetChangeLaneFreelyParam = new QAction(pMenuBar->parent());
	pActionReSetChangeLaneFreelyParam->setObjectName("actionReSetChangeLaneFreelyParam");
	pActionReSetChangeLaneFreelyParam->setText(QString("修改自由变道模型参数测试"));
	pActionReSetChangeLaneFreelyParam->setCheckable(false);
	pMenuModelModify->addAction(pActionReSetChangeLaneFreelyParam);
	QObject::connect(pActionReSetChangeLaneFreelyParam, &QAction::triggered, [=]() {
		mpSecondDevCasesObj->modelModify(2);
	});
}

void MyPlugin::unload() {
	delete mpMyNet;
	delete mpMySimulator;
	delete mpExampleWindow;
	delete mpSecondDevCasesObj;
}

CustomerGui* MyPlugin::customerGui()
{
	return nullptr;
}

CustomerNet* MyPlugin::customerNet()
{
	return mpMyNet;
}

CustomerSimulator* MyPlugin::customerSimulator()
{
	return mpMySimulator;
}

MyPlugin::~MyPlugin()
{
}
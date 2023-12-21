#ifndef __TESS_API_EXAMPLE__
#define __TESS_API_EXAMPLE__

#include <QtWidgets/QMainWindow>
#include <QInputDialog>

#include "ui_TESS_API_EXAMPLE.h"
#include "SecondaryDevCases.h"

class SecondaryDevCases;

class TESS_API_EXAMPLE : public QMainWindow
{
	Q_OBJECT

public:
	TESS_API_EXAMPLE(SecondaryDevCases* pSecondDevCasesObj,QWidget *parent = Q_NULLPTR);

public slots:
	void showRunInfo(const QString &);

private slots:
	//打开路网
	void openNet();
	//启动仿真
	void startSimu();
	//暂停仿真
	void pauseSimu();
	//停止仿真
	void stopSimu();

	//双环信控方案下发测试槽函数
	void doubleRingSignalControlTestResponse();

	//断面流量加载测试槽函数
	void flowLoadingSectionTest();

	//设置路段限速
	void setLinkLimitedSpeed();

public:
	Ui::TESS_API_EXAMPLEClass ui;
	//二次开发案例对象
	SecondaryDevCases* mpSecondDevCasesObj;
};



#endif
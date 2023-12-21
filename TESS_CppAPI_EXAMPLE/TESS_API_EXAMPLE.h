#ifndef __TESS_API_EXAMPLE__
#define __TESS_API_EXAMPLE__

#include <QtWidgets/QMainWindow>
#include "ui_TESS_API_EXAMPLE.h"

class TESS_API_EXAMPLE : public QMainWindow
{
	Q_OBJECT

public:
	TESS_API_EXAMPLE(QWidget *parent = Q_NULLPTR);

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

public:
	Ui::TESS_API_EXAMPLEClass ui;
};



#endif
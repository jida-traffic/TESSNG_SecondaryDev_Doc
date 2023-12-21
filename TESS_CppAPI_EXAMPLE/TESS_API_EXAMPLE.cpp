#include "TESS_API_EXAMPLE.h"

#include <QPushButton>
#include <QFileDialog>
#include <QMessageBox>

#include "tessinterface.h"
#include "netinterface.h"
#include "simuinterface.h"
#include "guiinterface.h"

TESS_API_EXAMPLE::TESS_API_EXAMPLE(QWidget *parent): QMainWindow(parent){
	ui.setupUi(this);

	QObject::connect(ui.btnOpenNet, &QPushButton::clicked, [this]() {
		openNet();
	});

	QObject::connect(ui.btnStartSimu, &QPushButton::clicked, [this]() {
		startSimu();
	});

	QObject::connect(ui.btnPauseSimu, &QPushButton::clicked, [this]() {
		pauseSimu();
	});

	QObject::connect(ui.btnStopSimu, &QPushButton::clicked, [this]() {
		stopSimu();
	});

}

void TESS_API_EXAMPLE::showRunInfo(const QString &runInfo) {
	ui.txtMessage->clear();
	ui.txtMessage->setText(runInfo);
}

//打开路网
void TESS_API_EXAMPLE::openNet() {
	//if (gpTessInterface->simuInterface()->isRunning()) {
	//	QMessageBox::warning(nullptr, QString(), QString("请先停止仿真，再打开路网"));
	//	return;
	//}

	QString	custSuffix = QString("TESSNG Files (*.tess);;TESSNG Files (*.backup)");
	QString dbDir = QApplication::applicationDirPath() + "/Data";
	QString selectedFilter = QString("TESSNG Files (*.tess)");

	const QFileDialog::Options options = QFlag(0);

	QString netFilePath = QFileDialog::getOpenFileName(this,
		QString("打开文件"),
		dbDir,
		custSuffix,
		&selectedFilter,
		options);

	if (!netFilePath.isEmpty()){
		gpTessInterface->netInterface()->openNetFle(netFilePath);
	}
}

//启动仿真
void TESS_API_EXAMPLE::startSimu() {
	if (!gpTessInterface->simuInterface()->isRunning() || gpTessInterface->simuInterface()->isPausing()) {
		gpTessInterface->simuInterface()->startSimu();
	}
}

//暂停仿真
void TESS_API_EXAMPLE::pauseSimu() {
	if (gpTessInterface->simuInterface()->isRunning()) {
		gpTessInterface->simuInterface()->pauseSimu();
	}
}

//停止仿真
void TESS_API_EXAMPLE::stopSimu() {
	if (gpTessInterface->simuInterface()->isRunning()) {
		gpTessInterface->simuInterface()->stopSimu();
	}
}
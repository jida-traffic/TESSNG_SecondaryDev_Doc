#include "TESS_API_EXAMPLE.h"

#include <QPushButton>
#include <QFileDialog>
#include <QMessageBox>

#include "tessinterface.h"
#include "netinterface.h"
#include "simuinterface.h"
#include "guiinterface.h"

TESS_API_EXAMPLE::TESS_API_EXAMPLE(SecondaryDevCases* pSecondDevCasesObj, QWidget* parent) :mpSecondDevCasesObj(pSecondDevCasesObj), QMainWindow(parent) {
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

void TESS_API_EXAMPLE::showRunInfo(const QString& runInfo) {
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

	if (!netFilePath.isEmpty()) {
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

//双环信控方案下发测试槽函数
void TESS_API_EXAMPLE::doubleRingSignalControlTestResponse() {
	bool isPress;
	// 显示输入对话框
	int inputValue = QInputDialog::getInt(this, "选择下发方案序号", "请输入方案序号（1-11）:", 1, 1, 11, 1, &isPress);
	if (isPress) {
		mpSecondDevCasesObj->doubleRingSignalControlTest(inputValue - 1);
	}
}

void TESS_API_EXAMPLE::flowLoadingSectionTest() {
	bool isPress;
	// 显示输入对话框
	int inputValue = QInputDialog::getInt(this, "请输入仿真时间", "请输入拟定的当前仿真时间进行测试:", 0, 0, 999999, 1, &isPress);
	if (isPress) {
		mpSecondDevCasesObj->flowLoading(3, inputValue);
	}
}

//设置路段限速
void TESS_API_EXAMPLE::setLinkLimitedSpeed() {
	bool isPress;
	// 显示输入对话框
	int inputValue = QInputDialog::getInt(this, "请输入最大限速", "请输入路段的最大限速进行测试:", 20, 20, 120, 1, &isPress);
	if (isPress) {
		mpSecondDevCasesObj->controlMeasures(3, inputValue);
	}
}
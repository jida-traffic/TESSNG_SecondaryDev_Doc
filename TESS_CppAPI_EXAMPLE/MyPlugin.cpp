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
	:mpExampleWindow(nullptr), mpMyNet(nullptr), mpMySimulator(nullptr)
{
}

void MyPlugin::init()
{
	initGui();

	mpMyNet = new MyNet();
	mpMySimulator = new MySimulator();

	QObject::connect(mpMySimulator, SIGNAL(forRunInfo(const QString)), mpExampleWindow, SLOT(showRunInfo(const QString)));

	QMainWindow *pMainWindow = gpTessInterface->guiInterface()->mainWindow();
	QObject::connect(mpMySimulator, SIGNAL(forReStartSimu()), pMainWindow, SLOT(doStartSimu()), Qt::QueuedConnection);
	QObject::connect(mpMySimulator, SIGNAL(forStopSimu()), pMainWindow, SLOT(doStopSimu()), Qt::QueuedConnection);
}

void MyPlugin::initGui() {
	//在TESS NG主界面上增加 QDockWidget对象
	mpExampleWindow = new TESS_API_EXAMPLE();
	QDockWidget *pDockWidget = new QDockWidget(QString("自定义与TESS NG交互界面"), (QWidget *)gpTessInterface->guiInterface()->mainWindow());
	pDockWidget->setObjectName(QStringLiteral("mainDockWidget"));
	pDockWidget->setFeatures(QDockWidget::NoDockWidgetFeatures);
	pDockWidget->setAllowedAreas(Qt::LeftDockWidgetArea);
	pDockWidget->setWidget(mpExampleWindow->centralWidget());
	gpTessInterface->guiInterface()->addDockWidgetToMainWindow(static_cast<Qt::DockWidgetArea>(1), pDockWidget);

	//增加菜单及菜单项
	QMenuBar *pMenuBar = gpTessInterface->guiInterface()->menuBar();
	QMenu *pMenu = new QMenu(pMenuBar);
	pMenu->setObjectName(QString::fromUtf8("menuExample"));
	pMenuBar->addAction(pMenu->menuAction());
	pMenu->setTitle(QString("范例菜单"));

	QAction *pActionOk = new QAction(pMenuBar->parent());
	pActionOk->setObjectName("actionExample");
	pActionOk->setText(QString("范例菜单项"));
	pActionOk->setCheckable(true);

	pMenu->addAction(pActionOk);

	QObject::connect(pActionOk, &QAction::triggered, []() {
		QMessageBox::information(gpTessInterface->guiInterface()->mainWindow(), QString("提示"), QString("is ok!"));
	});

}

void MyPlugin::unload() {
	delete mpMyNet;
	delete mpMySimulator;
	delete mpExampleWindow;
}

CustomerGui *MyPlugin::customerGui()
{
	return nullptr;
}

CustomerNet *MyPlugin::customerNet()
{
	return mpMyNet;
}

CustomerSimulator *MyPlugin::customerSimulator()
{
	return mpMySimulator;
}

MyPlugin::~MyPlugin()
{
}
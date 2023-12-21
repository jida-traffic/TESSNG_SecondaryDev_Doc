#include "TESS_API_EXAMPLE.h"

#include <QtWidgets/QApplication>
#include <QTextCodec>
#include <QFileInfo>
#include <QDir>
#include <QLibrary>

#include "tessinterface.h"
#include "UnitChange.h"
#include "MyPlugin.h"

int main(int argc, char *argv[])
{
	char *pAppFilePath = argv[0];
	QTextCodec* pLocalCode = QTextCodec::codecForLocale();
	QTextCodec* pUtf8 = QTextCodec::codecForName("UTF-8");
	QString tmpString = pLocalCode->toUnicode(pAppFilePath);
	QString appFilePath = pUtf8->fromUnicode(tmpString);
	appFilePath = QString(pAppFilePath);
	appFilePath.replace('\\', '/');
	QFileInfo appFileInfo = QFileInfo(appFilePath);
	QDir appDir = appFileInfo.dir();
	QString pluginDir = appDir.path() + "/plugins";
	QCoreApplication::addLibraryPath(pluginDir);

	QFont font = QFont();
	font.setFixedPitch(true);
	font.setPixelSize(13);
	QGuiApplication::setFont(font);

	QApplication a(argc, argv);

	bool result = false;
	//打开指定路网
	//QString netFilePath = QString("C:/TESSNG_2.0/Example/杭州武林门区域路网公交优先方案.tess");
	//QMainWindow *pWindow = tessng(netFilePath);
	QMainWindow *pWindow = tessng();
	if (pWindow)
	{
		//创建插件实例
		MyPlugin *p = new MyPlugin();
		p->init();

		//加载插件，如果提示没有权限加载，可能的原因是：试用版或基础版使用日期已超过规定期限。企业版无此限制
		gpTessInterface->loadPluginFromMem(p);

		pWindow->showMaximized();
		result = a.exec();
		pWindow->deleteLater();
	}
	return result;
}


/***************************************************
自动驾驶车辆动态信息
****************************************************/

#ifndef __AutoDynaInfo__
#define __AutoDynaInfo__

#include <QObject>

class AutoDynaInfo
{
public:
	AutoDynaInfo();

public :
	//名称
	QString mName;
	//计算次数
	int mrCalcCount;
};

#endif
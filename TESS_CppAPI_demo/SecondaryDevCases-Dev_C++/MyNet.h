#ifndef __MyNet__
#define __MyNet__

#include "Plugin/customernet.h"
#include "Plugin/_netitem.h"
#include "SecondaryDevCases.h"

class MyNet : public CustomerNet
{
public:
	MyNet(SecondaryDevCases* pSecondDevCasesObj);
	~MyNet() override;

	//==========以下是接口方法重新实现==========
	//加载路网前的准备
	void beforeLoadNet() override;
	//加载完路网后的行为
	void afterLoadNet() override;
	//
	bool isPermitForCustDraw() override { return true; }
	//写标签，按照给定的属性名和字体大小（米）
	void labelNameAndFont(int itemType, long itemId, int& outPropName, qreal& outFontSize) override;
	//------------------------------------------

	//==============以下是自定义方法==============
	//创建路网
	void createNet();

	//--------------------------------------------
	//二次开发案例对象
	SecondaryDevCases* mpSecondDevCasesObj;
};

#endif
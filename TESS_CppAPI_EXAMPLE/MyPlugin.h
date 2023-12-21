#ifndef __MyPlugin__
#define __MyPlugin__

#include "Plugin/tessplugin.h"

class TESS_API_EXAMPLE;
class MyNet;
class MySimulator;

class MyPlugin : public TessPlugin
{
public:
	MyPlugin();
	~MyPlugin();

	void init() override;
	void unload() override;
	CustomerGui *customerGui() override;
	CustomerNet *customerNet() override;
	CustomerSimulator *customerSimulator() override;

	void initGui();

private:
	TESS_API_EXAMPLE *mpExampleWindow;
	MyNet *mpMyNet;
	MySimulator *mpMySimulator;
};

#endif
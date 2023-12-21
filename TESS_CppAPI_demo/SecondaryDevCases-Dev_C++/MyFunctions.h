#ifndef __MyFunctions__
#define __MyFunctions__

#include "qobject.h"
#include "qmath.h"

class Functions {
public:
	static long timeToSeconds(QString& timeStr);
	static QString carPositionRoad(QPointF& laneStartPoint, QPointF& laneEndPoint, QPointF& vehiclePoint);
	static double calculateAngle(QPointF& startPoint, QPointF& endPoint);
};


#endif

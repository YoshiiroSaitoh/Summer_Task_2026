#ifndef TEMPERATURE_PROVIDER_H
#define TEMPERATURE_PROVIDER_H

#include <TemperatureData.h>

class TemperatureProvider
{
public:
    virtual int getTemperatures(
        TemperatureData *data,
        int maxCount) = 0;

    virtual ~TemperatureProvider() = default;
};

#endif

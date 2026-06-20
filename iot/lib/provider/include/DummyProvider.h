#ifndef DUMMY_PROVIDER_H
#define DUMMY_PROVIDER_H

#include <TemperatureProvider.h>

class DummyProvider : public TemperatureProvider
{
public:
    int getTemperatures(
        TemperatureData *data,
        int maxCount) override;
};

#endif

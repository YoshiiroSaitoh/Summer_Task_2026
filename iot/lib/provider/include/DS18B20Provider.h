#ifndef DS18B20_PROVIDER_H
#define DS18B20_PROVIDER_H

#include <TemperatureProvider.h>

#include <cstdint>

class DS18B20Provider : public TemperatureProvider
{
public:
    explicit DS18B20Provider(uint8_t pin);

    int getTemperatures(
        TemperatureData *data,
        int maxCount) override;

private:
    uint8_t pin_;
    String probeId_;
    bool probeIdInitialized_;
};

#endif

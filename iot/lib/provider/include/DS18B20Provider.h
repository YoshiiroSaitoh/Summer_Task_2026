#ifndef DS18B20_PROVIDER_H
#define DS18B20_PROVIDER_H

#include <AppConfig.h>
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
    uint8_t probeRoms_[AppConfig::MAX_TEMPERATURE_COUNT][8];
    String probeIds_[AppConfig::MAX_TEMPERATURE_COUNT];
    int probeCount_;
    bool probesInitialized_;
};

#endif

#include "DummyProvider.h"

#ifdef ARDUINO
#include <Arduino.h>
#include <Logger.h>
#else
#include <Logger.h>
#include <random>
#endif

namespace
{
float randomDelta()
{
#ifdef ARDUINO
    static bool seeded = false;
    if (!seeded)
    {
        randomSeed(micros());
        seeded = true;
    }

    return static_cast<float>(random(-200, 301)) / 100.0f;
#else
    static std::mt19937 engine{std::random_device{}()};
    static std::uniform_real_distribution<float> distribution(-2.0f, 3.0f);
    return distribution(engine);
#endif
}

float withVariation(float baseTemperature)
{
    return baseTemperature + randomDelta();
}

void logTemperature(const TemperatureData &temperatureData)
{
    Logger::debugf(
        "Temperature probe: %s = %.2f C",
        temperatureData.sensorId.c_str(),
        temperatureData.temperature);
}
}

int DummyProvider::getTemperatures(
    TemperatureData *data,
    int maxCount)
{
    if (data == nullptr || maxCount < 3)
    {
        return 0;
    }

    data[0] = {"room", withVariation(25.0f)};
    data[1] = {"outside", withVariation(18.0f)};
    data[2] = {"fridge", withVariation(5.0f)};

    for (int index = 0; index < 3; ++index)
    {
        logTemperature(data[index]);
    }

    return 3;
}

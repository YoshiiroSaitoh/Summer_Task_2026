#include "DummyProvider.h"

#ifdef ARDUINO
#include <Arduino.h>
#else
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

    return 3;
}

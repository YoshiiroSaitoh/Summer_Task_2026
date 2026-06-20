#include "DummyProvider.h"

int DummyProvider::getTemperatures(
    TemperatureData *data,
    int maxCount)
{
    if (data == nullptr || maxCount < 3)
    {
        return 0;
    }

    data[0] = {"room", 25.0f};
    data[1] = {"outside", 18.0f};
    data[2] = {"fridge", 5.0f};

    return 3;
}

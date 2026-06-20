#include "ApiClient.h"

#include <cstdio>

namespace
{
String formatTemperature(float value)
{
    char buffer[16];
#ifdef ARDUINO
    dtostrf(value, 0, 1, buffer);
#else
    std::snprintf(buffer, sizeof(buffer), "%.1f", value);
#endif

    return String(buffer);
}
}

ApiClient::ApiClient(
    HttpTransport &transport,
    const char *apiUrl)
    : transport_(transport),
      apiUrl_(apiUrl)
{
}

bool ApiClient::send(
    TemperatureData *data,
    int count)
{
    if (data == nullptr || count <= 0)
    {
        return false;
    }

    const String payload = buildPayload(data, count);
    String responseStatus;
    return transport_.postJson(apiUrl_, payload, &responseStatus);
}

String ApiClient::buildPayload(
    TemperatureData *data,
    int count) const
{
    String payload = "{\"temperatures\":[";

    for (int index = 0; index < count; ++index)
    {
        if (index > 0)
        {
            payload += ",";
        }

        payload += "{\"sensor_id\":\"";
        payload += data[index].sensorId;
        payload += "\",\"temperature\":";
        payload += formatTemperature(data[index].temperature);
        payload += "}";
    }

    payload += "]}";
    return payload;
}

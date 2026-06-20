#ifndef API_CLIENT_H
#define API_CLIENT_H

#include <AppConfig.h>
#include <HttpTransport.h>
#include <TemperatureData.h>

class ApiClient
{
public:
    ApiClient(
        HttpTransport &transport,
        const char *apiUrl = AppConfig::API_URL);

    bool send(
        TemperatureData *data,
        int count);

private:
    HttpTransport &transport_;
    const char *apiUrl_;

    String buildPayload(
        TemperatureData *data,
        int count) const;
};

#endif

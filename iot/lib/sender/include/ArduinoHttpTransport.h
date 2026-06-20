#ifndef ARDUINO_HTTP_TRANSPORT_H
#define ARDUINO_HTTP_TRANSPORT_H

#include <HttpTransport.h>

class ArduinoHttpTransport : public HttpTransport
{
public:
    bool postJson(
        const char *url,
        const String &payload,
        String *responseStatus = nullptr) override;
};

#endif

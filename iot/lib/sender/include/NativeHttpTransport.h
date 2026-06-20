#ifndef NATIVE_HTTP_TRANSPORT_H
#define NATIVE_HTTP_TRANSPORT_H

#include <HttpTransport.h>

class NativeHttpTransport : public HttpTransport
{
public:
    bool postJson(
        const char *url,
        const String &payload,
        String *responseStatus = nullptr) override;
};

#endif

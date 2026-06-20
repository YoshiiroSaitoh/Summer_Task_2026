#ifndef HTTP_TRANSPORT_H
#define HTTP_TRANSPORT_H

#include <Compat.h>

class HttpTransport
{
public:
    virtual bool postJson(
        const char *url,
        const String &payload,
        String *responseStatus = nullptr) = 0;

    virtual ~HttpTransport() = default;
};

#endif

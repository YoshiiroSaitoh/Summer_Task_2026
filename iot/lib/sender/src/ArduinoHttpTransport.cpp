#include "ArduinoHttpTransport.h"

#ifdef ARDUINO

#include <WiFiS3.h>

namespace
{
struct ParsedUrl
{
    bool useTls;
    String host;
    uint16_t port;
    String path;
};

bool parseUrl(const String &url, ParsedUrl &parsedUrl)
{
    const int schemeSeparator = url.indexOf("://");
    if (schemeSeparator <= 0)
    {
        return false;
    }

    const String scheme = url.substring(0, schemeSeparator);
    parsedUrl.useTls = scheme.equalsIgnoreCase("https");
    if (!parsedUrl.useTls && !scheme.equalsIgnoreCase("http"))
    {
        return false;
    }

    const int authorityStart = schemeSeparator + 3;
    const int pathStart = url.indexOf('/', authorityStart);
    const String authority = pathStart >= 0
        ? url.substring(authorityStart, pathStart)
        : url.substring(authorityStart);

    if (authority.length() == 0)
    {
        return false;
    }

    const int portSeparator = authority.indexOf(':');
    parsedUrl.host = portSeparator >= 0
        ? authority.substring(0, portSeparator)
        : authority;

    if (parsedUrl.host.length() == 0)
    {
        return false;
    }

    if (portSeparator >= 0)
    {
        parsedUrl.port = static_cast<uint16_t>(authority.substring(portSeparator + 1).toInt());
    }
    else
    {
        parsedUrl.port = parsedUrl.useTls ? 443 : 80;
    }

    if (parsedUrl.port == 0)
    {
        return false;
    }

    parsedUrl.path = pathStart >= 0
        ? url.substring(pathStart)
        : "/";

    return true;
}

bool sendRequest(
    Client &client,
    const ParsedUrl &parsedUrl,
    const String &payload,
    String *responseStatus)
{
    if (!client.connect(parsedUrl.host.c_str(), parsedUrl.port))
    {
        Serial.println("HTTP connection failed");
        return false;
    }

    client.print("POST ");
    client.print(parsedUrl.path);
    client.println(" HTTP/1.1");
    client.print("Host: ");
    client.println(parsedUrl.host);
    client.println("Content-Type: application/json");
    client.print("Content-Length: ");
    client.println(payload.length());
    client.println("Connection: close");
    client.println();
    client.print(payload);

    unsigned long startedAt = millis();
    while (client.connected() && !client.available() && millis() - startedAt < 5000)
    {
        delay(10);
    }

    String statusLine = client.readStringUntil('\n');
    statusLine.trim();
    Serial.print("HTTP status: ");
    Serial.println(statusLine);

    if (responseStatus != nullptr)
    {
        *responseStatus = statusLine;
    }

    client.stop();

    return statusLine.startsWith("HTTP/1.1 2") || statusLine.startsWith("HTTP/1.0 2");
}
}

bool ArduinoHttpTransport::postJson(
    const char *url,
    const String &payload,
    String *responseStatus)
{
    if (WiFi.status() != WL_CONNECTED)
    {
        Serial.println("WiFi is not connected");
        return false;
    }

    ParsedUrl parsedUrl;
    if (!parseUrl(String(url), parsedUrl))
    {
        Serial.println("Invalid API URL");
        return false;
    }

    Serial.print("Sending payload: ");
    Serial.println(payload);

    if (parsedUrl.useTls)
    {
        WiFiSSLClient sslClient;
        return sendRequest(sslClient, parsedUrl, payload, responseStatus);
    }

    WiFiClient client;
    return sendRequest(client, parsedUrl, payload, responseStatus);
}

#endif

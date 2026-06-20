#include "ArduinoHttpTransport.h"

#ifdef ARDUINO

#include <WiFiS3.h>
#include <Logger.h>

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
    Logger::debugf("=> trying connect %s:%u", parsedUrl.host.c_str(), parsedUrl.port);
    if (!client.connect(parsedUrl.host.c_str(), parsedUrl.port))
    {
        Logger::error("HTTP connection failed");
        Logger::debugf("=> connect failed %s:%u", parsedUrl.host.c_str(), parsedUrl.port);
        return false;
    }

    Logger::debugf("=> POST %s HTTP/1.1", parsedUrl.path.c_str());
    Logger::debugf("=> Host: %s", parsedUrl.host.c_str());
    Logger::debug("=> Content-Type: application/json");
    Logger::debugf("=> Content-Length: %u", static_cast<unsigned int>(payload.length()));
    Logger::debug("=> Connection: close");
    Logger::debugf("=> payload: %s", payload.c_str());

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

    if (!client.available())
    {
        Logger::debug("<= no response received");
    }

    String statusLine = client.readStringUntil('\n');
    statusLine.trim();
    Logger::debugf("<= %s", statusLine.c_str());

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
        Logger::error("WiFi is not connected");
        return false;
    }

    ParsedUrl parsedUrl;
    if (!parseUrl(String(url), parsedUrl))
    {
        Logger::error("Invalid API URL");
        return false;
    }

    Logger::debugf("API URL: %s", url);
    Logger::debugf("API host: %s", parsedUrl.host.c_str());
    Logger::debugf("API port: %u", parsedUrl.port);
    Logger::debugf("API path: %s", parsedUrl.path.c_str());
    Logger::debugf("API scheme: %s", parsedUrl.useTls ? "https" : "http");

    if (parsedUrl.useTls)
    {
        WiFiSSLClient sslClient;
        return sendRequest(sslClient, parsedUrl, payload, responseStatus);
    }

    WiFiClient client;
    return sendRequest(client, parsedUrl, payload, responseStatus);
}

#endif

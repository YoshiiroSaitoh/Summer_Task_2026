#include "NativeHttpTransport.h"

#ifndef ARDUINO

#include <cstring>
#include <sstream>

#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "ws2_32.lib")
#endif

namespace
{
struct ParsedUrl
{
    String host;
    int port;
    String path;
};

bool parseUrl(const char *url, ParsedUrl &parsedUrl)
{
    const String fullUrl(url);
    const int schemeSeparator = fullUrl.indexOf("://");
    if (schemeSeparator <= 0)
    {
        return false;
    }

    const String scheme = fullUrl.substring(0, schemeSeparator);
    if (!scheme.equalsIgnoreCase("http"))
    {
        return false;
    }

    const int authorityStart = schemeSeparator + 3;
    const int pathStart = fullUrl.indexOf('/', authorityStart);
    const String authority = pathStart >= 0
        ? fullUrl.substring(authorityStart, pathStart)
        : fullUrl.substring(authorityStart);

    if (authority.length() == 0)
    {
        return false;
    }

    const int portSeparator = authority.indexOf(':');
    parsedUrl.host = portSeparator >= 0
        ? authority.substring(0, portSeparator)
        : authority;
    parsedUrl.port = portSeparator >= 0
        ? static_cast<int>(authority.substring(portSeparator + 1).toInt())
        : 80;
    parsedUrl.path = pathStart >= 0 ? fullUrl.substring(pathStart) : "/";

    return parsedUrl.host.length() > 0 && parsedUrl.port > 0;
}
}

bool NativeHttpTransport::postJson(
    const char *url,
    const String &payload,
    String *responseStatus)
{
#ifndef _WIN32
    (void)url;
    (void)payload;
    (void)responseStatus;
    return false;
#else
    ParsedUrl parsedUrl;
    if (!parseUrl(url, parsedUrl))
    {
        return false;
    }

    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0)
    {
        return false;
    }

    addrinfo hints{};
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_protocol = IPPROTO_TCP;

    addrinfo *addressInfo = nullptr;
    const std::string portText = std::to_string(parsedUrl.port);
    if (getaddrinfo(parsedUrl.host.c_str(), portText.c_str(), &hints, &addressInfo) != 0)
    {
        WSACleanup();
        return false;
    }

    SOCKET socketHandle = INVALID_SOCKET;
    for (addrinfo *candidate = addressInfo; candidate != nullptr; candidate = candidate->ai_next)
    {
        socketHandle = socket(candidate->ai_family, candidate->ai_socktype, candidate->ai_protocol);
        if (socketHandle == INVALID_SOCKET)
        {
            continue;
        }

        if (connect(socketHandle, candidate->ai_addr, static_cast<int>(candidate->ai_addrlen)) == 0)
        {
            break;
        }

        closesocket(socketHandle);
        socketHandle = INVALID_SOCKET;
    }

    freeaddrinfo(addressInfo);

    if (socketHandle == INVALID_SOCKET)
    {
        WSACleanup();
        return false;
    }

    std::ostringstream request;
    request << "POST " << parsedUrl.path.c_str() << " HTTP/1.1\r\n";
    request << "Host: " << parsedUrl.host.c_str() << "\r\n";
    request << "Content-Type: application/json\r\n";
    request << "Content-Length: " << payload.length() << "\r\n";
    request << "Connection: close\r\n\r\n";
    request << payload.c_str();

    const std::string requestText = request.str();
    int bytesSent = 0;
    while (bytesSent < static_cast<int>(requestText.size()))
    {
        const int sentNow = send(
            socketHandle,
            requestText.c_str() + bytesSent,
            static_cast<int>(requestText.size()) - bytesSent,
            0);

        if (sentNow == SOCKET_ERROR)
        {
            closesocket(socketHandle);
            WSACleanup();
            return false;
        }

        bytesSent += sentNow;
    }

    std::string response;
    char buffer[512];
    int received = 0;
    while ((received = recv(socketHandle, buffer, sizeof(buffer), 0)) > 0)
    {
        response.append(buffer, received);
    }

    closesocket(socketHandle);
    WSACleanup();

    const std::size_t lineEnd = response.find("\r\n");
    const std::string statusLine = lineEnd == std::string::npos
        ? response
        : response.substr(0, lineEnd);

    if (responseStatus != nullptr)
    {
        *responseStatus = statusLine.c_str();
    }

    return statusLine.rfind("HTTP/1.1 2", 0) == 0 || statusLine.rfind("HTTP/1.0 2", 0) == 0;
#endif
}

#endif

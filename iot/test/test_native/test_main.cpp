#include <ApiClient.h>
#include <DummyProvider.h>
#include <NativeHttpTransport.h>

#include <chrono>
#include <cstring>
#include <string>
#include <thread>
#include <unity.h>

#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "ws2_32.lib")
#endif

namespace
{
class LocalHttpServer
{
public:
    explicit LocalHttpServer(int port)
        : port_(port)
    {
    }

    bool start()
    {
#ifndef _WIN32
        return false;
#else
        if (WSAStartup(MAKEWORD(2, 2), &wsaData_) != 0)
        {
            return false;
        }

        serverSocket_ = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
        if (serverSocket_ == INVALID_SOCKET)
        {
            WSACleanup();
            return false;
        }

        sockaddr_in address{};
        address.sin_family = AF_INET;
        address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
        address.sin_port = htons(static_cast<u_short>(port_));

        if (bind(serverSocket_, reinterpret_cast<sockaddr *>(&address), sizeof(address)) != 0)
        {
            closesocket(serverSocket_);
            WSACleanup();
            return false;
        }

        if (listen(serverSocket_, 1) != 0)
        {
            closesocket(serverSocket_);
            WSACleanup();
            return false;
        }

        worker_ = std::thread([this]() { serveOnce(); });
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        return true;
#endif
    }

    void stop()
    {
#ifdef _WIN32
        if (worker_.joinable())
        {
            worker_.join();
        }

        if (serverSocket_ != INVALID_SOCKET)
        {
            closesocket(serverSocket_);
            serverSocket_ = INVALID_SOCKET;
        }

        WSACleanup();
#endif
    }

    ~LocalHttpServer()
    {
        stop();
    }

    std::string request() const
    {
        return request_;
    }

private:
    void serveOnce()
    {
#ifdef _WIN32
        SOCKET clientSocket = accept(serverSocket_, nullptr, nullptr);
        if (clientSocket == INVALID_SOCKET)
        {
            return;
        }

        char buffer[2048];
        int received = 0;
        while ((received = recv(clientSocket, buffer, sizeof(buffer), 0)) > 0)
        {
            request_.append(buffer, received);
            if (request_.find("\r\n\r\n") != std::string::npos)
            {
                const std::size_t contentLengthPosition = request_.find("Content-Length: ");
                if (contentLengthPosition != std::string::npos)
                {
                    const std::size_t valueStart = contentLengthPosition + std::strlen("Content-Length: ");
                    const std::size_t valueEnd = request_.find("\r\n", valueStart);
                    const int contentLength = std::stoi(request_.substr(valueStart, valueEnd - valueStart));
                    const std::size_t bodyStart = request_.find("\r\n\r\n") + 4;
                    if (request_.size() >= bodyStart + static_cast<std::size_t>(contentLength))
                    {
                        break;
                    }
                }
            }
        }

        const char response[] =
            "HTTP/1.1 200 OK\r\n"
            "Content-Length: 2\r\n"
            "Connection: close\r\n"
            "\r\n"
            "OK";
        send(clientSocket, response, static_cast<int>(std::strlen(response)), 0);
        closesocket(clientSocket);
#endif
    }

    int port_;
    std::string request_;
    std::thread worker_;

#ifdef _WIN32
    WSADATA wsaData_{};
    SOCKET serverSocket_ = INVALID_SOCKET;
#endif
};

std::string extractBody(const std::string &request)
{
    const std::size_t bodyStart = request.find("\r\n\r\n");
    return bodyStart == std::string::npos ? "" : request.substr(bodyStart + 4);
}
}

extern "C" void setUp(void)
{
}

extern "C" void tearDown(void)
{
}

void test_dummy_provider_returns_expected_values()
{
    DummyProvider provider;
    TemperatureData temperatures[3];
    const int count = provider.getTemperatures(temperatures, 3);
    TEST_ASSERT_EQUAL_INT(3, count);
    TEST_ASSERT_EQUAL_STRING("room", temperatures[0].sensorId.c_str());
    TEST_ASSERT_FLOAT_WITHIN(0.001f, 25.0f, temperatures[0].temperature);
    TEST_ASSERT_EQUAL_STRING("outside", temperatures[1].sensorId.c_str());
    TEST_ASSERT_FLOAT_WITHIN(0.001f, 18.0f, temperatures[1].temperature);
    TEST_ASSERT_EQUAL_STRING("fridge", temperatures[2].sensorId.c_str());
    TEST_ASSERT_FLOAT_WITHIN(0.001f, 5.0f, temperatures[2].temperature);
}

void test_api_client_posts_expected_json()
{
#ifdef _WIN32
    constexpr int serverPort = 18080;

    LocalHttpServer server(serverPort);
    TEST_ASSERT_TRUE(server.start());

    DummyProvider provider;
    TemperatureData temperatures[3];
    const int count = provider.getTemperatures(temperatures, 3);

    NativeHttpTransport transport;
    ApiClient apiClient(transport, "http://127.0.0.1:18080/temperatures");
    TEST_ASSERT_TRUE(apiClient.send(temperatures, count));

    server.stop();

    const std::string request = server.request();
    TEST_ASSERT_TRUE(request.find("POST /temperatures HTTP/1.1") != std::string::npos);
    TEST_ASSERT_TRUE(request.find("Content-Type: application/json") != std::string::npos);
    TEST_ASSERT_EQUAL_STRING(
        "{\"temperatures\":[{\"sensor_id\":\"room\",\"temperature\":25.0},{\"sensor_id\":\"outside\",\"temperature\":18.0},{\"sensor_id\":\"fridge\",\"temperature\":5.0}]}",
        extractBody(request).c_str());
#else
    TEST_IGNORE_MESSAGE("Native HTTP test is only available on Windows.");
#endif
}

int main(int argc, char **argv)
{
    (void)argc;
    (void)argv;

    UNITY_BEGIN();
    RUN_TEST(test_dummy_provider_returns_expected_values);
    RUN_TEST(test_api_client_posts_expected_json);
    return UNITY_END();
}

#include <Arduino.h>
#include <WiFiS3.h>

#include <ApiClient.h>
#include <AppConfig.h>
#include <ArduinoHttpTransport.h>
#include <DS18B20Provider.h>
#include <DummyProvider.h>
#include <Logger.h>
#include <TemperatureProvider.h>

namespace
{
DummyProvider dummyProvider;
DS18B20Provider ds18b20Provider(AppConfig::DS18B20_PIN);
TemperatureProvider *temperatureProvider = nullptr;
ArduinoHttpTransport httpTransport;
ApiClient apiClient(httpTransport);

const char *wifiStatusToString(int status)
{
    switch (status)
    {
    case WL_NO_SHIELD:
        return "WL_NO_SHIELD";
    case WL_IDLE_STATUS:
        return "WL_IDLE_STATUS";
    case WL_NO_SSID_AVAIL:
        return "WL_NO_SSID_AVAIL";
    case WL_SCAN_COMPLETED:
        return "WL_SCAN_COMPLETED";
    case WL_CONNECTED:
        return "WL_CONNECTED";
    case WL_CONNECT_FAILED:
        return "WL_CONNECT_FAILED";
    case WL_CONNECTION_LOST:
        return "WL_CONNECTION_LOST";
    case WL_DISCONNECTED:
        return "WL_DISCONNECTED";
    default:
        return "WL_UNKNOWN";
    }
}

void logNetworkInfo(Logger::Level level)
{
    const String localIp = WiFi.localIP().toString();
    const String gatewayIp = WiFi.gatewayIP().toString();
    const String subnetMask = WiFi.subnetMask().toString();
    const String dns1 = WiFi.dnsIP(0).toString();
    const String dns2 = WiFi.dnsIP(1).toString();

    if (level == Logger::Level::Debug)
    {
        Logger::debugf("WiFi status: %s", wifiStatusToString(WiFi.status()));
        Logger::debugf("IP address: %s", localIp.c_str());
        Logger::debugf("Gateway: %s", gatewayIp.c_str());
        Logger::debugf("Subnet: %s", subnetMask.c_str());
        Logger::debugf("DNS1: %s", dns1.c_str());
        Logger::debugf("DNS2: %s", dns2.c_str());
        return;
    }

    Logger::infof("WiFi status: %s", wifiStatusToString(WiFi.status()));
    Logger::infof("IP address: %s", localIp.c_str());
    Logger::infof("Gateway: %s", gatewayIp.c_str());
    Logger::infof("Subnet: %s", subnetMask.c_str());
    Logger::infof("DNS1: %s", dns1.c_str());
    Logger::infof("DNS2: %s", dns2.c_str());
}

void connectToWiFi()
{
    Logger::infof("Connecting to WiFi: %s", AppConfig::WIFI_SSID);
    Logger::info("WiFi connect start");

    int attemptCount = 0;
    while (WiFi.status() != WL_CONNECTED && attemptCount < AppConfig::WIFI_MAX_RETRIES)
    {
        Logger::infof("Attempt %d", attemptCount + 1);
        WiFi.begin(AppConfig::WIFI_SSID, AppConfig::WIFI_PASSWORD);
        delay(AppConfig::WIFI_RETRY_DELAY_MS);
        ++attemptCount;
        Logger::infof("status=%s", wifiStatusToString(WiFi.status()));
    }

    if (WiFi.status() == WL_CONNECTED)
    {
        Logger::info("WiFi connected");
        logNetworkInfo(Logger::Level::Info);
        return;
    }

    Logger::error("WiFi connection failed");
    logNetworkInfo(Logger::Level::Debug);
}
}

void executeMeasurementCycle()
{
    if (temperatureProvider == nullptr)
    {
        Logger::error("Temperature provider is not initialized");
        logNetworkInfo(Logger::Level::Debug);
        return;
    }

    TemperatureData temperatures[AppConfig::MAX_TEMPERATURE_COUNT];
    const int count = temperatureProvider->getTemperatures(
        temperatures,
        AppConfig::MAX_TEMPERATURE_COUNT);

    if (count <= 0)
    {
        Logger::warn("No temperatures collected");
        logNetworkInfo(Logger::Level::Debug);
        return;
    }

    if (!apiClient.send(temperatures, count))
    {
        Logger::error("Temperature send failed");
        logNetworkInfo(Logger::Level::Debug);
        return;
    }

    Logger::info("Temperature send succeeded");
}

void setup()
{
    Logger::begin(115200);
    delay(1000);

    connectToWiFi();

    if (AppConfig::WIFI_ONLY_TEST_MODE)
    {
        Logger::info("WiFi-only test mode enabled");
        return;
    }

    switch (AppConfig::TEMPERATURE_PROVIDER_KIND)
    {
    case AppConfig::TemperatureProviderKind::Dummy:
        temperatureProvider = &dummyProvider;
        Logger::info("Temperature provider initialized: Dummy");
        break;
    case AppConfig::TemperatureProviderKind::Ds18b20:
        temperatureProvider = &ds18b20Provider;
        Logger::info("Temperature provider initialized: DS18B20");
        break;
    default:
        temperatureProvider = &dummyProvider;
        Logger::warn("Unknown temperature provider, falling back to Dummy");
        break;
    }
}

void loop()
{
    if (AppConfig::WIFI_ONLY_TEST_MODE)
    {
        delay(AppConfig::LOOP_DELAY_MS);
        return;
    }

    executeMeasurementCycle();

    delay(AppConfig::LOOP_DELAY_MS);
}

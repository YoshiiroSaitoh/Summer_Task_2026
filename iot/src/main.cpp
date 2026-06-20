#include <Arduino.h>
#include <WiFiS3.h>

#include <ApiClient.h>
#include <AppConfig.h>
#include <ArduinoHttpTransport.h>
#include <DummyProvider.h>
#include <TemperatureProvider.h>

namespace
{
DummyProvider dummyProvider;
TemperatureProvider *temperatureProvider = nullptr;
ArduinoHttpTransport httpTransport;
ApiClient apiClient(httpTransport);

void connectToWiFi()
{
    Serial.print("Connecting to WiFi: ");
    Serial.println(AppConfig::WIFI_SSID);

    int attemptCount = 0;
    while (WiFi.status() != WL_CONNECTED && attemptCount < AppConfig::WIFI_MAX_RETRIES)
    {
        WiFi.begin(AppConfig::WIFI_SSID, AppConfig::WIFI_PASSWORD);
        delay(AppConfig::WIFI_RETRY_DELAY_MS);
        ++attemptCount;
        Serial.print(".");
    }

    Serial.println();

    if (WiFi.status() == WL_CONNECTED)
    {
        Serial.println("WiFi connected");
        Serial.print("IP address: ");
        Serial.println(WiFi.localIP());
        return;
    }

    Serial.println("WiFi connection failed");
}
}

void executeMeasurementCycle()
{
    if (temperatureProvider == nullptr)
    {
        Serial.println("Temperature provider is not initialized");
        return;
    }

    TemperatureData temperatures[AppConfig::MAX_TEMPERATURE_COUNT];
    const int count = temperatureProvider->getTemperatures(
        temperatures,
        AppConfig::MAX_TEMPERATURE_COUNT);

    if (count <= 0)
    {
        Serial.println("No temperatures collected");
        return;
    }

    if (!apiClient.send(temperatures, count))
    {
        Serial.println("Temperature send failed");
        return;
    }

    Serial.println("Temperature send succeeded");
}

void setup()
{
    Serial.begin(115200);
    delay(1000);

    connectToWiFi();

    if (AppConfig::WIFI_ONLY_TEST_MODE)
    {
        Serial.println("WiFi-only test mode enabled");
        return;
    }

    temperatureProvider = &dummyProvider;
    Serial.println("Temperature provider initialized");
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

#ifndef APP_CONFIG_H
#define APP_CONFIG_H

#include <Compat.h>

namespace AppConfig
{
constexpr char WIFI_SSID[] = "YOUR_WIFI_SSID";
constexpr char WIFI_PASSWORD[] = "YOUR_WIFI_PASSWORD";
constexpr char API_URL[] = "http://192.168.0.10:8000/temperatures";
constexpr bool WIFI_ONLY_TEST_MODE = false;
constexpr unsigned long WIFI_RETRY_DELAY_MS = 1000;
constexpr int WIFI_MAX_RETRIES = 30;
constexpr int MAX_TEMPERATURE_COUNT = 3;
constexpr unsigned long LOOP_DELAY_MS = 60000;
}

#endif

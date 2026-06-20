#ifndef APP_CONFIG_H
#define APP_CONFIG_H

#include <Compat.h>

namespace AppConfig
{
constexpr char WIFI_SSID[] = "aterm-8d64b1-a";
constexpr char WIFI_PASSWORD[] = "055eacb844343";
constexpr char API_URL[] = "http://api.sv:8080/temperatures/bulk";
constexpr bool WIFI_ONLY_TEST_MODE = false;
constexpr unsigned long WIFI_RETRY_DELAY_MS = 1000;
constexpr int WIFI_MAX_RETRIES = 30;
constexpr int MAX_TEMPERATURE_COUNT = 3;
constexpr unsigned long LOOP_DELAY_MS = 60000;
}

#endif

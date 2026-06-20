# UNO R4 WiFi Temperature Sender

## 讎りｦ・

Arduino UNO R4 WiFi 荳翫〒蜍穂ｽ懊☆繧区ｸｩ蠎ｦ騾∽ｿ｡繧ｯ繝ｩ繧､繧｢繝ｳ繝医〒縺吶・ 
迴ｾ蝨ｨ縺ｯ `DummyProvider` 縺悟崋螳壹・ 3 莉ｶ繧定ｿ斐＠縲～ApiClient` 縺・JSON 繧堤函謌舌＠縺ｦ Web API 縺ｸ POST 縺励∪縺吶・

莉雁屓縺ｮ螳溯｣・〒縺ｯ貂ｩ蠎ｦ蜿門ｾ励・繝繝溘・螳溯｣・→縺励仝iFi 謗･邯壹→ HTTP 騾∽ｿ｡繧堤｢ｺ隱榊ｯｾ雎｡縺ｫ縺励※縺・∪縺吶・

## 繧ｯ繝ｩ繧ｹ讒区・

萓晏ｭ俶婿蜷代・莉･荳九〒縺吶・

```text
main
 竊・
TemperatureProvider
 竊・
ApiClient
```

- `main.cpp`
  - 貂ｬ螳壹し繧､繧ｯ繝ｫ縺ｮ蛻ｶ蠕｡縺ｮ縺ｿ繧呈球蠖薙＠縺ｾ縺吶・
  - `executeMeasurementCycle()` 縺ｧ貂ｩ蠎ｦ蜿門ｾ励→騾∽ｿ｡繧貞他縺ｳ蜃ｺ縺励∪縺吶・
- `TemperatureProvider`
  - 貂ｩ蠎ｦ蜿門ｾ励・謚ｽ雎｡繧､繝ｳ繧ｿ繝ｼ繝輔ぉ繝ｼ繧ｹ縺ｧ縺吶・
  - 蟆・擂 `Ds18b20Provider` 縺ｸ蟾ｮ縺玲崛縺医※繧・`main.cpp` 縺ｯ螟画峩荳崎ｦ√〒縺吶・
- `DummyProvider`
  - 迴ｾ蝨ｨ縺ｮ莉ｮ螳溯｣・〒縺吶・
  - `room` `outside` `fridge` 縺ｮ 3 莉ｶ繧定ｿ斐＠縺ｾ縺吶・
- `ApiClient`
  - `TemperatureData` 驟榊・縺九ｉ JSON 繧堤函謌舌＠縲？TTP POST 繧貞ｮ溯｡後＠縺ｾ縺吶・
- `HttpTransport`
  - `ApiClient` 縺悟茜逕ｨ縺吶ｋ騾壻ｿ｡謚ｽ雎｡縺ｧ縺吶・
  - 螳滓ｩ溘〒縺ｯ `ArduinoHttpTransport`縲仝indows 繝ｭ繝ｼ繧ｫ繝ｫ繝・せ繝医〒縺ｯ `NativeHttpTransport` 繧剃ｽｿ縺・∪縺吶・
- `AppConfig`
  - WiFi SSID縲√ヱ繧ｹ繝ｯ繝ｼ繝峨、PI URL 縺ｪ縺ｩ縺ｮ險ｭ螳壼､繧剃ｿ晄戟縺励∪縺吶・

## 蜃ｦ逅・ヵ繝ｭ繝ｼ

- `setup()`
  - `Serial` 繧貞・譛溷喧縺励∪縺吶・
  - WiFi 縺ｸ謗･邯壹＠縺ｾ縺吶・
  - `TemperatureProvider` 縺ｮ螳滉ｽ薙→縺励※ `DummyProvider` 繧定ｨｭ螳壹＠縺ｾ縺吶・
- `loop()`
  - `executeMeasurementCycle()` 繧貞ｮ溯｡後＠縺ｾ縺吶・
  - 60 遘貞ｾ・ｩ溘＠縺ｾ縺吶・
- `executeMeasurementCycle()`
  - `TemperatureProvider` 縺九ｉ貂ｩ蠎ｦ荳隕ｧ繧貞叙蠕励＠縺ｾ縺吶・
  - `ApiClient` 縺ｸ貂｡縺励※ JSON 蛹悶＠縲、PI 縺ｸ POST 縺励∪縺吶・

## 繝・ぅ繝ｬ繧ｯ繝医Μ讒区・

```text
lib/
笏懌楳sender
笏・ 笏懌楳include
笏・ 笏・ 笏懌楳ApiClient.h
笏・ 笏・ 笏懌楳ArduinoHttpTransport.h
笏・ 笏・ 笏懌楳HttpTransport.h
笏・ 笏・ 笏披楳NativeHttpTransport.h
笏・ 笏披楳src
笏・    笏懌楳ApiClient.cpp
笏・    笏懌楳ArduinoHttpTransport.cpp
笏・    笏披楳NativeHttpTransport.cpp
笏懌楳provider
笏・ 笏懌楳include
笏・ 笏・ 笏懌楳TemperatureProvider.h
笏・ 笏・ 笏披楳DummyProvider.h
笏・ 笏披楳src
笏・    笏披楳DummyProvider.cpp
笏懌楳model
笏・ 笏披楳include
笏・    笏披楳TemperatureData.h
笏披楳config
   笏披楳include
      笏披楳AppConfig.h

src/
笏披楳main.cpp
```

## 險ｭ螳・

`E:\dev\workspace\summertask2026\iot\lib\config\include\AppConfig.h` 繧貞ｮ溽腸蠅・・蛟､縺ｸ譖ｴ譁ｰ縺励※縺上□縺輔＞縲・

- `WIFI_SSID`
- `WIFI_PASSWORD`
- `API_URL`

險ｭ螳壻ｾ・

```cpp
constexpr char WIFI_SSID[] = "your-ssid";
constexpr char WIFI_PASSWORD[] = "your-password";
constexpr char API_URL[] = "http://192.168.1.20:8000/temperatures/bulk";
```

`API_URL` 縺ｫ `localhost` 繧・`127.0.0.1` 繧呈欠螳壹＠縺ｦ繧医＞縺ｮ縺ｯ Windows 繝ｭ繝ｼ繧ｫ繝ｫ繝・せ繝医□縺代〒縺吶・ 
UNO R4 螳滓ｩ溘°繧・PC 荳翫・ API 繧貞娼縺丞ｴ蜷医・縲￣C 縺ｮ LAN IP 繧呈欠螳壹＠縺ｦ縺上□縺輔＞縲・

## 螳滓ｩ溷ｮ溯｡梧焔鬆・

1. `AppConfig.h` 縺ｫ WiFi 縺ｨ API 縺ｮ險ｭ螳壼､繧貞・繧後∪縺吶・
2. 蜿嶺ｿ｡蜈・API 繧定ｵｷ蜍輔＠縺ｾ縺吶・
3. PlatformIO 縺ｧ `uno_r4_wifi` 迺ｰ蠅・ｒ繝薙Ν繝峨・譖ｸ縺崎ｾｼ縺ｿ縺励∪縺吶・
4. 繧ｷ繝ｪ繧｢繝ｫ繝｢繝九ち縺ｧ莉･荳九ｒ遒ｺ隱阪＠縺ｾ縺吶・
   - WiFi 謗･邯壽・蜉・
   - IP 繧｢繝峨Ξ繧ｹ蜿門ｾ・
   - HTTP 繧ｹ繝・・繧ｿ繧ｹ
   - `Temperature send succeeded`

送信する JSON は次の形式です。

```json
[
  {
    "probe_id": "room",
    "temperature": 25.0
  },
  {
    "probe_id": "outside",
    "temperature": 18.0
  },
  {
    "probe_id": "fridge",
    "temperature": 5.0
  }
]
```

## 繝ｭ繝ｼ繧ｫ繝ｫ謗･邯壹ユ繧ｹ繝・

### 繝・せ繝亥燕謠・

Windows 荳翫〒繝ｭ繝ｼ繧ｫ繝ｫ謗･邯壹ユ繧ｹ繝医ｒ螳溯｡後☆繧九↓縺ｯ縲∽ｻ･荳九・迺ｰ蠅・′蠢・ｦ√〒縺吶・

- PlatformIO 縺悟茜逕ｨ縺ｧ縺阪ｋ縺薙→
  - 萓・ VS Code 縺ｮ PlatformIO 諡｡蠑ｵ縲√∪縺溘・ `platformio` CLI
- Windows 縺九ｉ蛻ｩ逕ｨ蜿ｯ閭ｽ縺ｪ C/C++ 繧ｳ繝ｳ繝代う繝ｩ縺悟・縺｣縺ｦ縺・ｋ縺薙→
  - `native` 迺ｰ蠅・〒縺ｯ `gcc` / `g++` 縺悟ｿ・ｦ√〒縺・
  - 萓・ MSYS2 + MinGW-w64
- `gcc` 縺ｨ `g++` 縺ｫ PATH 縺碁壹▲縺ｦ縺・ｋ縺薙→
  - 遒ｺ隱堺ｾ・ `gcc --version`
  - 遒ｺ隱堺ｾ・ `g++ --version`
- VSCode 縺ｮ繧ｿ繝ｼ繝溘リ繝ｫ險ｭ螳壹ｒ菴ｿ縺・ｴ蜷医・ `.vscode/settings.json.sample` 繧・`settings.json` 縺ｫ繧ｳ繝斐・縺励※菴ｿ縺・∪縺・

`winget` 繧剃ｽｿ縺・ｴ蜷医・荳萓・

```powershell
winget search msys2
winget install --id MSYS2.MSYS2 -e
```

MSYS2 蟆主・蠕後・縲｀SYS2 繧ｷ繧ｧ繝ｫ荳翫〒 `mingw-w64-ucrt-x86_64-gcc` 繧貞ｰ主・縺励～g++` 縺・Windows 蛛ｴ縺九ｉ隕九∴繧九ｈ縺・↓ PATH 繧定ｨｭ螳壹＠縺ｦ縺上□縺輔＞縲・

蟆主・謇矩・

```powershell
pacman -Sy
pacman -S --needed mingw-w64-ucrt-x86_64-gcc
```

譖ｴ譁ｰ隕∵ｱゅ′蜃ｺ縺溷ｴ蜷医・縲∽ｻ･荳九ｒ蜈医↓螳溯｡後＠縺ｾ縺吶・

```powershell
pacman -Syu
```

縺昴・蝣ｴ蜷医・縺・▲縺溘ｓ MSYS2 繧ｷ繧ｧ繝ｫ繧帝哩縺倥※蜀榊ｺｦ髢九″縲∝ｿ・ｦ√↑繧峨ｂ縺・ｸ蠎ｦ `pacman -Syu` 繧貞ｮ溯｡後＠縺ｦ縺九ｉ縲∵ｬ｡繧貞ｮ溯｡後＠縺ｦ縺上□縺輔＞縲・

```powershell
pacman -S --needed mingw-w64-ucrt-x86_64-gcc
```

蟆主・蠕後・縲仝indows 縺ｮ PATH 縺ｫ騾壼ｸｸ莉･荳九ｒ霑ｽ蜉縺励∪縺吶・

```text
C:\msys64\ucrt64\bin
```

遒ｺ隱阪さ繝槭Φ繝・

```powershell
gcc --version
g++ --version
```

- `E:\dev\workspace\summertask2026\iot\test\test_native\test_main.cpp:1` 縺ｯ Windows 荳翫〒繝ｭ繝ｼ繧ｫ繝ｫ HTTP 繧ｵ繝ｼ繝舌ｒ襍ｷ蜍輔＠縲～DummyProvider` 縺ｨ `NativeHttpTransport` 繧剃ｽｿ縺｣縺ｦ POST 繧呈､懆ｨｼ縺励∪縺吶・
- 螳溯｡梧Φ螳壹・ `platformio test -e native` 縺ｧ縺吶・
- 縺薙・繝・せ繝医〒縺ｯ莉･荳九ｒ遒ｺ隱阪＠縺ｾ縺吶・
  - `DummyProvider` 縺・3 莉ｶ霑斐☆縺薙→
  - `ApiClient` 縺梧悄蠕・←縺翫ｊ縺ｮ JSON 繧堤函謌舌☆繧九％縺ｨ
  - 繝ｭ繝ｼ繧ｫ繝ｫ HTTP 繧ｵ繝ｼ繝舌∈ POST 縺ｧ縺阪ｋ縺薙→

## 繝ｭ繝ｼ繧ｫ繝ｫ繝・せ繝医・髯千阜

Windows 繝ｭ繝ｼ繧ｫ繝ｫ繝・せ繝医〒遒ｺ隱阪〒縺阪ｋ縺ｮ縺ｯ縲∽ｸｻ縺ｫ騾∽ｿ｡莉墓ｧ倥〒縺吶・

- 遒ｺ隱阪〒縺阪ｋ繧ゅ・
  - JSON 縺ｮ蠖｢蠑・
  - HTTP 繝｡繧ｽ繝・ラ縲√・繝・ム縲√・繝・ぅ
  - API 縺後Μ繧ｯ繧ｨ繧ｹ繝医ｒ蜿礼炊縺ｧ縺阪ｋ縺・
- 遒ｺ隱阪〒縺阪↑縺・ｂ縺ｮ
  - `WiFiS3` 縺ｮ謗･邯壽嫌蜍・
  - UNO R4 螳滓ｩ溘〒縺ｮ繝阪ャ繝医Ρ繝ｼ繧ｯ螳牙ｮ壽ｧ
  - 螳滓ｩ溷崋譛峨・繝｡繝｢繝ｪ繝ｻ繧ｿ繧､繝溘Φ繧ｰ蝠城｡・

縺昴・縺溘ａ縲仝indows 繝ｭ繝ｼ繧ｫ繝ｫ繝・せ繝医・莠句燕讀懆ｨｼ縲ゞNO R4 螳滓ｩ溘ユ繧ｹ繝医・譛邨ら｢ｺ隱阪→縺・≧菴咲ｽｮ縺･縺代〒縺吶・

陬懆ｶｳ:
- 繝・せ繝医さ繝ｼ繝牙・縺ｧ邁｡譏・HTTP 繧ｵ繝ｼ繝舌ｒ襍ｷ蜍輔＠縲、piClient 縺ｮ騾∽ｿ｡蜈医→縺励※蜿励￠縺ｾ縺・
- 螟夜Κ API 繧貞挨繝励Ο繧ｻ繧ｹ縺ｧ襍ｷ蜍輔＠縺ｪ縺上※繧ゅ・∽ｿ｡蜀・ｮｹ繧偵Ο繝ｼ繧ｫ繝ｫ縺ｧ讀懆ｨｼ縺ｧ縺阪∪縺・

## 蟆・擂諡｡蠑ｵ

蟆・擂 `DummyProvider` 繧・`Ds18b20Provider` 縺ｸ蟾ｮ縺玲崛縺医ｋ諠ｳ螳壹〒縺吶・

- `main.cpp` 縺ｮ蜃ｦ逅・ヵ繝ｭ繝ｼ縺ｯ螟画峩縺励∪縺帙ｓ縲・
- `ApiClient` 縺ｮ菫ｮ豁｣縺ｯ荳崎ｦ√〒縺吶・
- 貂ｩ蠎ｦ蜿門ｾ励・蜈ｷ菴灘ｮ溯｣・□縺代ｒ `TemperatureProvider` 豢ｾ逕溘け繝ｩ繧ｹ縺ｨ縺励※霑ｽ蜉縺励∪縺吶・

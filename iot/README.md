# UNO R4 WiFi Temperature Sender

## 概要

Arduino UNO R4 WiFi 上で動作する温度送信クライアントです。  
現在は `DummyProvider` が固定の 3 件を返し、`ApiClient` が JSON を生成して Web API へ POST します。

今回の実装では温度取得はダミー実装とし、WiFi 接続と HTTP 送信を確認対象にしています。

## クラス構成

依存方向は以下です。

```text
main
 ↓
TemperatureProvider
 ↓
ApiClient
```

- `main.cpp`
  - 測定サイクルの制御のみを担当します。
  - `executeMeasurementCycle()` で温度取得と送信を呼び出します。
- `TemperatureProvider`
  - 温度取得の抽象インターフェースです。
  - 将来 `Ds18b20Provider` へ差し替えても `main.cpp` は変更不要です。
- `DummyProvider`
  - 現在の仮実装です。
  - `room` `outside` `fridge` の 3 件を返します。
- `ApiClient`
  - `TemperatureData` 配列から JSON を生成し、HTTP POST を実行します。
- `HttpTransport`
  - `ApiClient` が利用する通信抽象です。
  - 実機では `ArduinoHttpTransport`、Windows ローカルテストでは `NativeHttpTransport` を使います。
- `AppConfig`
  - WiFi SSID、パスワード、API URL などの設定値を保持します。

## 処理フロー

- `setup()`
  - `Serial` を初期化します。
  - WiFi へ接続します。
  - `TemperatureProvider` の実体として `DummyProvider` を設定します。
- `loop()`
  - `executeMeasurementCycle()` を実行します。
  - 60 秒待機します。
- `executeMeasurementCycle()`
  - `TemperatureProvider` から温度一覧を取得します。
  - `ApiClient` へ渡して JSON 化し、API へ POST します。

## ディレクトリ構成

```text
lib/
├─sender
│  ├─include
│  │  ├─ApiClient.h
│  │  ├─ArduinoHttpTransport.h
│  │  ├─HttpTransport.h
│  │  └─NativeHttpTransport.h
│  └─src
│     ├─ApiClient.cpp
│     ├─ArduinoHttpTransport.cpp
│     └─NativeHttpTransport.cpp
├─provider
│  ├─include
│  │  ├─TemperatureProvider.h
│  │  └─DummyProvider.h
│  └─src
│     └─DummyProvider.cpp
├─model
│  └─include
│     └─TemperatureData.h
└─config
   └─include
      └─AppConfig.h

src/
└─main.cpp
```

## 設定

`E:\dev\workspace\summertask2026\iot\lib\config\include\AppConfig.h` を実環境の値へ更新してください。

- `WIFI_SSID`
- `WIFI_PASSWORD`
- `API_URL`

設定例:

```cpp
constexpr char WIFI_SSID[] = "your-ssid";
constexpr char WIFI_PASSWORD[] = "your-password";
constexpr char API_URL[] = "http://192.168.1.20:8000/temperatures";
```

`API_URL` に `localhost` や `127.0.0.1` を指定してよいのは Windows ローカルテストだけです。  
UNO R4 実機から PC 上の API を叩く場合は、PC の LAN IP を指定してください。

## 実機実行手順

1. `AppConfig.h` に WiFi と API の設定値を入れます。
2. 受信先 API を起動します。
3. PlatformIO で `uno_r4_wifi` 環境をビルド・書き込みします。
4. シリアルモニタで以下を確認します。
   - WiFi 接続成功
   - IP アドレス取得
   - HTTP ステータス
   - `Temperature send succeeded`

送信される JSON は以下です。

```json
{
  "temperatures": [
    {
      "sensor_id": "room",
      "temperature": 25.0
    },
    {
      "sensor_id": "outside",
      "temperature": 18.0
    },
    {
      "sensor_id": "fridge",
      "temperature": 5.0
    }
  ]
}
```

## ローカル接続テスト

### テスト前提

Windows 上でローカル接続テストを実行するには、以下の環境が必要です。

- PlatformIO が利用できること
  - 例: VS Code の PlatformIO 拡張、または `platformio` CLI
- Windows から利用可能な C/C++ コンパイラが入っていること
  - `native` 環境では `gcc` / `g++` が必要です
  - 例: MSYS2 + MinGW-w64
- `gcc` と `g++` に PATH が通っていること
  - 確認例: `gcc --version`
  - 確認例: `g++ --version`
- VSCode のターミナル設定を使う場合は `.vscode/settings.json.sample` を `settings.json` にコピーして使います

`winget` を使う場合の一例:

```powershell
winget search msys2
winget install --id MSYS2.MSYS2 -e
```

MSYS2 導入後は、MSYS2 シェル上で `mingw-w64-ucrt-x86_64-gcc` を導入し、`g++` が Windows 側から見えるように PATH を設定してください。

導入手順:

```powershell
pacman -Sy
pacman -S --needed mingw-w64-ucrt-x86_64-gcc
```

更新要求が出た場合は、以下を先に実行します。

```powershell
pacman -Syu
```

その場合はいったん MSYS2 シェルを閉じて再度開き、必要ならもう一度 `pacman -Syu` を実行してから、次を実行してください。

```powershell
pacman -S --needed mingw-w64-ucrt-x86_64-gcc
```

導入後は、Windows の PATH に通常以下を追加します。

```text
C:\msys64\ucrt64\bin
```

確認コマンド:

```powershell
gcc --version
g++ --version
```

- `E:\dev\workspace\summertask2026\iot\test\test_native\test_main.cpp:1` は Windows 上でローカル HTTP サーバを起動し、`DummyProvider` と `NativeHttpTransport` を使って POST を検証します。
- 実行想定は `platformio test -e native` です。
- このテストでは以下を確認します。
  - `DummyProvider` が 3 件返すこと
  - `ApiClient` が期待どおりの JSON を生成すること
  - ローカル HTTP サーバへ POST できること

## ローカルテストの限界

Windows ローカルテストで確認できるのは、主に送信仕様です。

- 確認できるもの
  - JSON の形式
  - HTTP メソッド、ヘッダ、ボディ
  - API がリクエストを受理できるか
- 確認できないもの
  - `WiFiS3` の接続挙動
  - UNO R4 実機でのネットワーク安定性
  - 実機固有のメモリ・タイミング問題

そのため、Windows ローカルテストは事前検証、UNO R4 実機テストは最終確認という位置づけです。

補足:
- テストコード内で簡易 HTTP サーバを起動し、ApiClient の送信先として受けます
- 外部 API を別プロセスで起動しなくても、送信内容をローカルで検証できます

## 将来拡張

将来 `DummyProvider` を `Ds18b20Provider` へ差し替える想定です。

- `main.cpp` の処理フローは変更しません。
- `ApiClient` の修正は不要です。
- 温度取得の具体実装だけを `TemperatureProvider` 派生クラスとして追加します。

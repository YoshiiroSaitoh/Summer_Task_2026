# System State Handoff

## Project Overview

- Python 3.12 の温度ログ API プロジェクト。
- PostgreSQL に `temperature_logs` を保存し、API で登録・最新取得・期間取得を行う。
- `api` 配下がアプリ本体、`db` 配下が初期化 SQL、`tests` 配下が pytest。

## Current Changes

### README updates

- `api/README.md` は `.http` 前提をやめ、`api/tests/tools/seed_requests.py` を使う案内に変更済み。
- `python -m tests.tools.seed_requests --base-url http://localhost:8080 --verify` でデモ投入できる。
- `POST /temperatures` は `recorded_at` 省略可で、サーバー側の現在時刻を使う。

### Seed tool

- `api/tests/tools/seed_requests.py` を追加済み。
- 標準ライブラリだけで POST / GET を実行する。
- `probeA` / `probeB` のデモデータを投入し、`--verify` で最新値を確認する。

### Grafana

- `docker-compose.yaml` に Grafana サービスを追加済み。
- `grafana/provisioning/datasources/postgresql.yaml` で PostgreSQL datasource を固定済み。
- `grafana/provisioning/dashboards/dashboards.yaml` で dashboard provisioning を設定済み。
- `grafana/dashboards/temperature-logs.json` で `Temperature Logs` dashboard を追加済み。
- Dashboard は `temperature_logs` テーブルの時系列温度推移と、probe ごとの最新温度を表示する。

### OpenAPI / generated

- `api/openapi/swagger.yaml` を source of truth として更新済み。
- `api/src/api/generated/*` は OpenAPI Generator で再生成済み。
- `TemperatureCreateRequest.recorded_at` は optional になっている。

## How to Run

### API

```powershell
cd api
python -m pip install -e .[dev]
uvicorn main:app --reload
```

### Seed demo data

```powershell
cd api
python -m tests.tools.seed_requests --base-url http://localhost:8080 --verify
```

### Full stack

```powershell
podman compose up
```

- API: `http://localhost:8080`
- Grafana: `http://localhost:3000`
- Grafana login: `admin` / `admin`

## Known Issues

- `podman compose up grafana` が「止まっている」ように見えるのは、Grafana が常駐プロセスでフォアグラウンド実行されるため。
- `depends_on: condition: service_healthy` と `podman-compose` の組み合わせで待ちが長く見えることがある。
- リポジトリが `/mnt/e` 上にあるため、bind mount と Grafana のクエリで DISK IO が上がりやすい。
- Grafana dashboard は `refresh: 10s` なので、開いているだけで Postgres に定期クエリが飛ぶ。

## Next Options

- `refresh` を長くしてクエリ頻度を下げる。
- bind mount を減らして Grafana の IO を下げる。
- WSL 側の Linux filesystem に repo を移して IO を改善する。

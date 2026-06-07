# summer task 2026

`1stOrder.md` をもとに作成した Python 3.12 の雛形プロジェクトです。

## 構成

- `openapi/swagger.yaml`: OpenAPI 3.1 の仕様書
- `src/api/generated`: Swagger から生成するコード置き場
- `src/api/impl`: 生成コードに対する実装置き場
- `src/control`: 制御層
- `src/dao`: DAO 層
- `tests`: pytest 用テスト
- `db`: 動作前提DBの作成スクリプトなどを定義

## セットアップ

Python 3.12 の仮想環境を有効化したうえで、依存関係を入れます。

```powershell
python -m pip install -e .[dev]
```

## 環境設定

ローカル実行では、次のファイルと環境変数を使います。

- `.env.example`: `DATABASE_URL` の雛形
- `db/setup.sql`: `summer` DB、`apluser` ロール、スキーマ権限の初期化
- `db/setup_tables.sql`: `temperature_logs` テーブルの作成

`DATABASE_URL` は `src/api/impl/default_api_impl.py` で参照されます。

```text
postgresql+psycopg://postgres:postgres@localhost:5432/postgres
```

## SQLファイルの実行手順

PostgreSQL に対して、次の順で実行します。

1. `db/setup.sql`
   - `summer` DB を作成します
   - `apluser` ロールを作成します
   - `apluser` の `search_path` を設定します
2. `db/setup_tables.sql`
   - `temperature_logs` テーブルを作成します

実行例:

```powershell
psql -U postgres -d postgres -f db/setup.sql
psql -U apluser -d summer -f db/setup_tables.sql
```

## API経由のデモ投入

`api/tests/tools/seed_requests.py` にデモ用の送信処理を置いています。

`api` ディレクトリで次を実行すると、`probeA` / `probeB` のデモデータをまとめて投入できます。

```powershell
python -m tests.tools.seed_requests --base-url http://localhost:8080 --verify
```

`--verify` を付けると、投入後に `GET /temperatures/latest/{probe_id}` を確認します。

## テスト

```powershell
python -m pytest
```

## 起動

```powershell
uvicorn main:app --reload
```

起動後は次を確認できます。

- `GET /health`

## 補足

- `pyproject.toml` で依存関係とビルド設定を管理します
- `requirements.txt` はこの構成では不要です
- 生成コードは `src/api/generated` に置き、直接編集しません

# summer task 2026

`1stOrder.md` をもとに作成した Python 3.12 の雛形プロジェクトです。

## 構成

- `openapi/swagger.yaml`: OpenAPI 3.1 の仕様書
- `src/api`: API 層
- `src/control`: 制御層
- `src/dao`: DAO 層
- `tests`: pytest 用テスト

## セットアップ

Python 3.12 を用意したうえで、依存関係をインストールします。

```powershell
pip install -e .[dev]
```

## テスト

```powershell
pytest
```

## 起動

開発用サーバーは `uvicorn` で起動します。

```powershell
uvicorn src.main:app --reload
```

起動後、以下で疎通確認できます。

- `GET /health`

## 補足

- `pyproject.toml` はプロジェクトの構成管理に必要です
- 依存関係、ビルド設定、pytest 設定をここで管理します
- Git 管理下に置いて、リポジトリに含める前提です

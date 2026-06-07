# summer task 2026

`1stOrder.md` をもとに作成した Python 3.12 の雛形プロジェクトです。

## 構成

- `openapi/swagger.yaml`: OpenAPI 3.1 の仕様書
- `src/api/generated`: Swagger から生成するコード置き場
- `src/api/impl`: 生成コードに対する実装置き場
- `src/control`: 制御層
- `src/dao`: DAO 層
- `tests`: pytest 用テスト

## セットアップ

Python 3.12 の仮想環境を有効化したうえで、依存関係を入れます。

```powershell
python -m pip install -e .[dev]
```

## テスト

```powershell
python -m pytest
```

## 起動

```powershell
uvicorn src.main:app --reload
```

起動後は次を確認できます。

- `GET /health`

## 補足

- `pyproject.toml` で依存関係とビルド設定を管理します
- `requirements.txt` はこの構成では不要です
- 生成コードは `src/api/generated` に置き、直接編集しません

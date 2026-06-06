# Pythonで温度記録システムを実装してください

## 設計方針

本システムは学習用途ではなく、保守性・拡張性・再生成容易性を重視した業務システムとして実装してください。

以下の方針を厳守してください。

- OpenAPI First
- Repository Pattern
- DAO Pattern
- SQLAlchemy Core
- PostgreSQL
- レイヤ分離
- 自動生成コードと手書きコードの分離
- Git管理
- 再生成可能な構成

生成コードは何度でも再生成可能であることを前提としてください。

---

# 開発手順

以下の順序で実装してください。

## Phase 1

OpenAPI Specification を作成してください。

生成先：

```text
openapi/swagger.yaml
```

OpenAPI 3.1 を利用してください。

---

## Phase 2

OpenAPI Generator を実行してください。

生成対象：

```text
src/api/generated
```

生成コードのみ作成してください。

---

## Phase 3

OpenAPI Generator の成果物を確認してください。

生成コードは編集しないでください。

Git が利用可能な環境であれば
ここでコミットしてください。

コミットメッセージ：

```text
feat: generate api sources from openapi specification
```

---

## Phase 4

手書き実装を開始してください。

対象：

```text
src/api/impl
src/control
src/dao
tests
```

generated 配下は編集禁止とします。

---

# Git管理

プロジェクトルートを Git リポジトリとして管理してください。

以下を作成してください。

```text
.gitignore
README.md
```

生成コードも Git 管理対象とします。

以下はコミット対象です。

```text
openapi/swagger.yaml

src/api/generated
src/api/impl

src/control

src/dao

tests
```

.gitignore には最低限以下を含めてください。

```text
__pycache__/
*.pyc
.pytest_cache/
.venv/
.coverage
htmlcov/
dist/
build/
```

---

# 技術要件

- Python 3.12
- FastAPI
- 初期実装DBは PostgreSQL
- SQLAlchemy
- pytest

SQLAlchemy ORM全面依存は禁止します。

SQLAlchemy Core を利用してください。

利用可能：

- text()
- select()

---

# アーキテクチャ

以下のレイヤ構成を採用してください。

```text
OpenAPI Specification
          ↓
OpenAPI Generator
          ↓
api/generated
          ↓
api/impl
          ↓
control
          ↓
dao/repository
          ↓
PostgreSQL
```

---

# OpenAPI First

OpenAPI を唯一の真実（Single Source of Truth）としてください。

以下を生成してください。

```text
openapi/swagger.yaml
```

OpenAPI Generator により生成可能なコードは可能な限り生成してください。

生成コードは以下に配置してください。

```text
src/api/generated
```

生成コードは編集禁止とします。

業務実装は以下に配置してください。

```text
src/api/impl
```

再生成時に impl が上書きされない構成としてください。

---

## API仕様

以下を定義してください。

### POST /temperatures

温度登録

Request:

- probe_id
- recorded_at
- temperature

Response:

- id
- probe_id
- recorded_at
- temperature

---

### GET /temperatures/latest/{probe_id}

最新温度取得

Response:

- id
- probe_id
- recorded_at
- temperature

---

### GET /temperatures

期間検索

Query Parameters:

- probe_id
- start_at
- end_at

Response:

- TemperatureLog の配列

---

## Components

以下を定義してください。

- TemperatureLog
- TemperatureCreateRequest
- ErrorResponse

OpenAPI Generator により生成可能なコードは生成してください。

---

# ディレクトリ構成

modern Python の src layout を採用してください。

```text
project/
├── openapi/
│   └── swagger.yaml
│
├── src/
│   ├── api/
│   │   ├── generated/
│   │   └── impl/
│   │
│   ├── control/
│   │
│   ├── dao/
│   │   ├── manager/
│   │   ├── model/
│   │   ├── repository/
│   │   └── exception/
│   │
│   └── common/
│
├── tests/
│   ├── resources/
│   └── test_temperature_log_repository.py
│
├── pyproject.toml
├── README.md
└── .gitignore
```

必要な `__init__.py` を適切に配置してください。

---

# コメント / docstring 方針

以下を満たしてください。

- public class に Google Style docstring を記述すること
- public method に Google Style docstring を記述すること
- 型ヒントを前提として docstring は簡潔にすること
- Args / Returns / Raises を必要に応じて記述すること
- 「何をしているか」ではなく「なぜ必要か」をコメントすること
- obvious なコメントは禁止
- JavaDoc 的な冗長コメントは禁止

例：

```python
def find_latest_by_probe_id(
    self,
    probe_id: str
) -> TemperatureLog | None:
    """
    Retrieve latest temperature log by probe id.

    Args:
        probe_id:
            Probe identifier.

    Returns:
        Latest temperature log if exists.
    """
```

---

# API共通処理

以下を作成してください。

```text
src/api/impl/base_api_impl.py
```

BaseApiImpl を定義してください。

責務：

- 共通ログ出力
- リクエスト開始ログ
- リクエスト終了ログ
- 実行時間計測
- trace_id 出力

各 API Impl は BaseApiImpl を継承してください。

---

# 例外方針

HTTPException は API層以外で利用禁止とします。

レイヤ毎に例外を分離してください。

```text
dao
 └── DBException

control
 ├── BusinessException
 └── TemperatureNotFoundException

api
 └── FastAPI Exception Handler
```

FastAPI Exception Handler を利用してください。

変換ルール：

- BusinessException → 400
- TemperatureNotFoundException → 404
- DBException → 500
- Exception → 500

api/impl では HTTPException を直接生成しないでください。

---
# データベース方針

初期実装は PostgreSQL とする。

ただし設計上は DBConnectionManager を利用し、
将来的に別DB実装へ差し替え可能な構造とすること。

実装対象：

- PostgreSQLManagerImpl

将来的な実装例：

- PostgreSQLManagerImpl
- MySQLManagerImpl
- SQLiteManagerImpl

Repository 層は特定DBへ直接依存しないこと。

SQLAlchemy Core による抽象化を利用すること。

DB固有機能への依存は最小限とすること。

# DB管理

DBConnectionManager 抽象クラスを作成してください。

PostgreSQLManagerImpl を実装してください。

要件：

- create_engine() は Singleton 運用
- SessionLocal(sessionmaker) を保持
- get_session() を提供
- Engine は長寿命
- Session は transaction/request 単位で生成

---

# テーブル

temperature_logs テーブルを利用してください。

存在しない場合は自動作成してください。

| Column | Type |
|----------|----------|
| id | bigint primary key |
| probe_id | varchar(64) |
| recorded_at | timestamp with timezone |
| temperature | numeric(5,2) |

metadata.create_all() を利用してください。

---

# Domain Model

TemperatureLog dataclass を作成してください。

配置：

```text
src/dao/model/temperature_log.py
```

フィールド：

- id
- probe_id
- recorded_at
- temperature

recorded_at は timezone aware datetime とすること。

DB定義は SQLAlchemy の

```python
DateTime(timezone=True)
```

を利用すること
---

# Repository

TemperatureLogRepository を作成してください。

配置：

```text
src/dao/repository/temperature_log_repository.py
```

責務：

- insert
- find_latest_by_probe_id
- find_by_probe_id_and_range

Repository 内では commit しないでください。

---

# Mapping

DB Row → dataclass 変換を行ってください。

```python
TemperatureLog(**row)
```

形式を利用してください。

```python
result.mappings()
```

を利用してください。

---

# Exception

以下を作成してください。

```text
src/dao/exception/db_exception.py
```

DBException を定義してください。

SQLAlchemy例外は必ずラップしてください。

```python
raise DBException(
    "failed to insert temperature log"
) from e
```

---

# Transaction

control 層で以下を管理してください。

- commit
- rollback
- session close

---

# Control

TemperatureControl を作成してください。

責務：

- 温度登録
- 最新温度取得
- 期間検索
- transaction 管理
- validation

DAO 呼び出しは Control から行うこと。

---

# テスト

pytest を利用してください。

テストケース：

- insert が成功すること
- latest が取得できること
- range検索できること
- DBException が発生すること

---

# テストデータ

以下を作成してください。

```text
tests/resources/schema.sql
tests/resources/test_data.sql
```

テスト実行時に投入できるようにしてください。

---

# README

以下を作成してください。

```text
tests/README.md
```

記載内容：

- PostgreSQL 起動方法
- OpenAPI Generator 実行方法
- Git 初期化方法
- 必要な環境変数
- テストデータ投入方法
- pytest 実行方法
- ディレクトリ構成説明

---

# 出力対象

```text
openapi/swagger.yaml

src/api/generated/*
src/api/impl/base_api_impl.py
src/api/impl/*

src/control/*

src/dao/manager/db_connection_manager.py
src/dao/manager/postgresql_manager_impl.py

src/dao/model/temperature_log.py

src/dao/repository/temperature_log_repository.py

src/dao/exception/db_exception.py

tests/test_temperature_log_repository.py

tests/resources/schema.sql
tests/resources/test_data.sql

tests/README.md

pyproject.toml
README.md
.gitignore
```
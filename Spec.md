# 温度計測システム 設計メモ

## 目的

- 実験を一覧から管理できるようにする
- 実験ごとに複数回の採取を扱えるようにする
- 各採取回ごとに probe の役割を固定できるようにする
- probe_id は IoT 送信データから自動登録する
- 不要な実験・probe は論理削除で扱う

## 用語

- **Experiment**: 実験全体
- **Run**: 実験内の1回の採取単位
- **Probe**: 計測器の master
- **Assignment**: run ごとの probe 役割定義
- **Temperature Log**: 受信した温度ログ

## 状態遷移

### Experiment

- `planned`: 作成直後、未開始
- `running`: 実験進行中
- `completed`: 実験完了
- `archived`: 論理削除済み
- `reopen`: `completed` から `running` に戻せる

### Run

- `planned`: 作成直後
- `running`: 採取中
- `ended`: 採取終了

### Probe

- `active`: 有効
- `deleted`: 論理削除済み

## テーブル案

### `experiments`

- `id`
- `name`
- `description`
- `status`
- `started_at`
- `completed_at`
- `archived_at`
- `created_at`
- `updated_at`

### `experiment_runs`

- `id`
- `experiment_id`
- `title`
- `status`
- `started_at`
- `ended_at`
- `created_at`
- `updated_at`

### `experiment_run_probes`

- `id`
- `experiment_run_id`
- `probe_id`
- `role`
- `created_at`
- `updated_at`

### `probes`

- `id`
- `probe_id`
- `deleted_at`
- `created_at`
- `updated_at`

### `temperature_logs`

- `id`
- `experiment_id`
- `experiment_run_id`
- `probe_id`
- `recorded_at`
- `elapsed_seconds`
- `temperature`

## 画面構成

### 実験一覧

- 実験の一覧表示
- 実験の追加
- 実験詳細への遷移
- 実験の論理削除
- 実験の再開

### 実験詳細

- 実験情報表示
- 実験開始 / 完了 / 再開
- 測定回一覧
- 測定回追加
- 測定回ごとの probe 役割編集
- 測定回の開始 / 終了

### Probe 管理

- probe 一覧表示
- 単一選択
- 削除ボタン活性化
- 論理削除

## API 一覧

- `GET /experiments`
- `POST /experiments`
- `GET /experiments/{experiment_id}`
- `PATCH /experiments/{experiment_id}`
- `DELETE /experiments/{experiment_id}`
- `POST /experiments/{experiment_id}/start`
- `POST /experiments/{experiment_id}/complete`
- `POST /experiments/{experiment_id}/reopen`
- `GET /experiments/{experiment_id}/runs`
- `POST /experiments/{experiment_id}/runs`
- `GET /experiments/{experiment_id}/runs/current`
- `POST /experiments/{experiment_id}/runs/{run_id}/start`
- `POST /experiments/{experiment_id}/runs/{run_id}/end`
- `GET /experiments/{experiment_id}/probe-assignments`
- `POST /experiments/{experiment_id}/probe-assignments`
- `PATCH /experiments/{experiment_id}/probe-assignments/{assignment_id}`
- `GET /probes`
- `DELETE /probes/{probe_id}`
- `POST /temperatures`
- `POST /temperatures/bulk`
- `GET /temperatures`
- `GET /temperatures/latest/{probe_id}`

## 実装方針

- API の正本は `api/openapi/swagger.yaml`
- 生成コードは直接編集しない
- 実装は `api/src/api/impl` に閉じる
- probe_id は受信時に自動登録する
- 画面は実験管理と probe 管理を分離する

## Grafana 向けの考え方

- 横軸は `elapsed_seconds`
- 縦軸は `temperature`
- フィルタ軸は `experiment_id` と `experiment_run_id`
- `probe_id` は系列分けに使う
- `role` は系列の意味付けに使う

## 補足

- 物理削除は極力しない
- `current experiment` のグローバル前提は置かない
- 実験ごとの内部管理に寄せる

# Drive Route

自分で作ったドライブルートを登録し、「走って楽しい度合い」を数値で採点・比較する Web API と地図の画面です。

- 地図の画面：https://drive-spot-api.onrender.com/map
- API の仕様書(Swagger UI)：https://drive-spot-api.onrender.com/docs

※ 無料プランで動かしているため、しばらくアクセスがないと、最初の表示に1分ほどかかることがあります。

## 作った理由

一般的なルート案内は、最短距離・最短時間を優先します。
しかし、ドライブそのものが目的のときは、遠回りでもワインディングロードのような走って楽しい道を通りたいと感じていました。
現在は地図を見ながら手作業で楽しそうな道を探し、経由地点を置いてその道を通るルートを作っています。

そこで、自分で作ったドライブルートを登録し、「どれくらい走って楽しいか」を数値で比較できるアプリを作りました。
出発地・目的地・経由地点を指定したルートを Google の Routes API で取得し、迂回率（道のり ÷ 直線距離）やカーブの多さ(1kmあたりに曲がった角度)で採点します。
登録したルートは、一覧で並べ替えて比べたり、地図の上に道の形を書いて確かめたりできます。

## 開発の経緯

最初は、バックエンドの基本(API設計・DB連携・テーブル構造の管理)を身につけるため、ドライブスポットを記録するAPI(ドライブスポット帳API)として作り始めました。
その土台の上に、ルートの登録・採点・地図の画面を足しています。リポジトリ名の drive-spot-api はその名残で、スポットの機能も残しています。

## 使用技術
- Python 3.14 / FastAPI
- SQLAlchemy（ORM）/ Pydantic（入力チェック）
- PostgreSQL 16（Docker で起動）
- Alembic（テーブル構造の変更管理）

## 機能

###  ルート(このアプリの中心)

- 出発地・目的地・経由地点を指定して、ルートを登録する
- 登録の時に Google の Routes API で道を取得し、次の3つを計算して保存する
  - 道のり(km)
  - 迂回率(道のり ÷ 出発地から目的地までの直線距離)
  - カーブの多さ(1kmあたりに曲がった角度の合計。交差点の右左折は除く)
- 地点を変えて編集すると、Google から道を取り直して採点し直す
- 一覧を、道のり・迂回率・カーブの多さで並べ替えて比べる
- 地図の画面(/map)で、一覧から選んだルートの道の形を地図に描く

### スポット

- 行きたい・行ったスポットの登録・一覧・1件取得・編集・削除
- おすすめ度（rating）は 1〜5 の整数のみ受け付ける

### 書き込みの保護

- 登録・編集・削除(POST・PUT・DELETE)は、`X-API-Key` ヘッダーに合言葉がないと 401 を返す
- 見るだけ(GET)は、誰でも使える

## API

| メソッド | パス | 内容 | 合言葉 |
| --- | --- | --- | --- |
| GET | /routes | ルートの一覧（並べ替えできる） | 不要 |
| GET | /routes/{id} | ルートの1件取得（道の形を含む） | 不要 |
| POST | /routes | ルートの登録と採点 | 必要 |
| PUT | /routes/{id} | ルートの編集（地点が変わったら採点し直す） | 必要 |
| DELETE | /routes/{id} | ルートの削除（経由地点も一緒に消える） | 必要 |
| GET | /spots | スポットの一覧 | 不要 |
| GET | /spots/{id} | スポットの1件取得 | 不要 |
| POST | /spots | スポットの登録 | 必要 |
| PUT | /spots/{id} | スポットの編集 | 必要 |
| DELETE | /spots/{id} | スポットの削除 | 必要 |
| GET | /map | 地図の画面（HTML） | 不要 |

一覧の並べ替えは、クエリパラメータで指定します。

- `sort`:`id`(登録順)／`length_km`(道のり)／`detour_ratio`(迂回率)／`curve_deg_per_km`(カーブの多さ)
- `order`:`asc`(小さい順)／`desc`(大きい順)

例:`GET /routes?sort=curve_deg_per_km&order=desc`(カーブの多い順)

## ディレクトリ構成

```text
drive-spot-api/
├── app/
│   ├── main.py          # アプリ本体。ルーターを登録する
│   ├── database.py      # DB接続の設定と、セッションを渡す get_db
│   ├── models.py        # テーブル定義（SQLAlchemy）
│   ├── schemas/
│   │   └── spot.py      # 入力・出力のデータの形（Pydantic）
│   └── routers/
│       └── spots.py     # /spots の各API処理
├── alembic/             # テーブル構造の変更履歴（マイグレーション）
├── tests/
│   ├── conftest.py      # テスト用DBの準備
│   └── test_spots.py    # APIのテスト
├── alembic.ini          # Alembic の設定
├── pytest.ini           # pytest の設定（app を import できるようにする）
├── requirements.txt     # 必要なライブラリの一覧
└── .env.example         # 環境変数のひな形
```

## 起動方法

### 必要なもの
- Python 3.14
- Docker

### 手順

```bash
# 1. リポジトリを取得
git clone https://github.com/riri-86/drive-spot-api.git
cd drive-spot-api

# 2. 仮想環境を作り、ライブラリを入れる
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. 環境変数ファイルを用意
cp .env.example .env

 # .env を開き、 DATABASE_URL と TEST_DATABASE_URL の両方で「ユーザー名」と「パスワード」を postgres に書き換えてください
 # 手順4の POSTGRES_PASSWORD と同じ値にしてください


# 4. PostgreSQL を起動
docker run --name drive-spot-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=drive_spot -v drive-spot-data:/var/lib/postgresql/data -p 5432:5432 -d postgres:16

# 5. テーブルを作成
alembic upgrade head

# 6. サーバーを起動
uvicorn app.main:app --reload
```

起動後、http://127.0.0.1:8000/docs を開くと Swagger UI から API を試せます。

## テスト

pytest でテストを実行します。テストでは開発用とは別のテスト用DB（`drive_spot_test`）を使い、テストごとにテーブルを作成・削除するため、開発用のデータには影響しません。

### 準備（初回のみ）

起動方法の手順4でコンテナを起動したあとに、テスト用DBを作成します。

```bash
docker exec -it drive-spot-db psql -U postgres -c "CREATE DATABASE drive_spot_test;"
```

### 実行

```bash
pytest
```

## 工夫した点
<!-- 各ステップの終わりに追加 -->
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
出発地・目的地・経由地点を指定したルートを Google の Routes API で取得し、迂回率（道のり ÷ 直線距離）やカーブの多さ（1kmあたりに曲がった角度）で採点します。
登録したルートは、一覧で並べ替えて比べたり、地図の上に道の形を書いて確かめたりできます。

## 開発の経緯

最初は、バックエンドの基本（API設計・DB連携・テーブル構造の管理）を身につけるため、ドライブスポットを記録するAPI（ドライブスポット帳API）として作り始めました。
その土台の上に、ルートの登録・採点・地図の画面を足しています。リポジトリ名の drive-spot-api はその名残で、スポットの機能も残しています。

設計と実装はAI（Claude）に相談しながら進めました。提案をそのまま使うのではなく、作りたい機能に合うかを自分で考えて選び、コードは読み解いて説明できるように努めました。

## 使用技術
- 言語・フレームワーク：Python 3.14 / FastAPI
- DB：PostgreSQL 16 / SQLAlchemy（ORM）/ Alembic（テーブル構造の変更管理）
- 入力チェック：Pydantic
- 外部API：Google Routes API（ルートの取得） / Maps JavaScript API（地図の表示）
- 外部APIの呼び出し：httpx / polyline（道の形の文字列を座標に戻す）
- 画面：Jinja2（HTMLテンプレート） / JavaScript
- テスト：pytest（Google の呼び出しはモックに差し替え）
- 実行環境：Docker / Render（公開）

## 機能

###  ルート(このアプリの中心)

- 出発地・目的地・経由地点を指定して、ルートを登録する
- 登録の時に Google の Routes API で道を取得し、次の3つを計算して保存する
  - 道のり（km）
  - 迂回率（道のり ÷ 出発地から目的地までの直線距離）
  - カーブの多さ（1kmあたりに曲がった角度の合計。交差点の右左折は除く）
- 地点を変えて編集すると、Google から道を取り直して採点し直す
- 一覧を、道のり・迂回率・カーブの多さで並べ替えて比べる
- 地図の画面（/map）で、一覧から選んだルートの道の形を地図に描く

### スポット

- 行きたい・行ったスポットの登録・一覧・1件取得・編集・削除
- おすすめ度（rating）は 1〜5 の整数のみ受け付ける

### 書き込みの保護

- 登録・編集・削除（POST・PUT・DELETE）は、`X-API-Key` ヘッダーに合言葉がないと 401 を返す
- 見るだけ（GET）は、誰でも使える

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

- `sort`：`id`（登録順）／`length_km`（道のり）／`detour_ratio`（迂回率）／`curve_deg_per_km`（カーブの多さ）
- `order`：`asc`（小さい順）／`desc`（大きい順）

例：`GET /routes?sort=curve_deg_per_km&order=desc`（カーブの多い順）

## ディレクトリ構成

```text
drive-spot-api/
├── app/
│   ├── main.py            # アプリ本体。ルーターを登録する
│   ├── database.py        # DB 接続の設定と、セッションを渡す get_db
│   ├── models.py          # テーブル定義（spots・routes・route_vias）
│   ├── auth.py            # 書き込みの API で合言葉（X-API-Key）を確かめる
│   ├── schemas/
│   │   ├── spot.py        # 入力・出力のデータの形（Pydantic）
│   │   └── route.py
│   ├── routers/
│   │   ├── spots.py       # /spots の API
│   │   ├── routes.py      # /routes の API（登録・編集のときに採点する）
│   │   └── pages.py       # /map の画面
│   ├── services/
│   │   ├── routes_api.py  # Google Routes API を呼び、道の点を集める
│   │   └── scoring.py     # 道のり・迂回率・カーブの多さの計算
│   └── templates/
│       └── map.html       # 地図の画面（一覧の表示と、道の形を描く JavaScript）
├── alembic/               # テーブル構造の変更履歴（マイグレーション）
├── scripts/               # Routes API の返し方を試したときのスクリプト
├── tests/
│   ├── conftest.py        # テスト用 DB と合言葉の準備
│   ├── test_spots.py      # /spots の API のテスト
│   ├── test_routes.py     # /routes の API のテスト
│   ├── test_routes_api.py # Google を呼ぶ部分のテスト（モック）
│   ├── test_scoring.py    # 採点の計算のテスト
│   └── test_pages.py      # /map の画面のテスト
├── Dockerfile
├── start.sh               # 起動時に alembic upgrade head をしてから uvicorn を動かす
├── alembic.ini            # Alembic の設定
├── pytest.ini             # pytest の設定（app を import できるようにする）
├── requirements.txt       # 必要なライブラリの一覧
└── .env.example           # 環境変数のひな形
```

## 起動方法

### 必要なもの
- Python 3.14
- Docker
- Google Cloud のAPIキー（Routes API 用と Maps JavaScript API 用の2つ）

### 手順

```bash
# 1. リポジトリを取得
git clone https://github.com/riri-86/drive-spot-api.git
cd drive-spot-api

# 2. 仮想環境を作り、ライブラリを入れる
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. 環境変数ファイルを用意（中身は下の「環境変数」を参照）
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

### 環境変数（.env）

| 名前 | 内容 |
| --- | --- |
| `DATABASE_URL` | 開発用 DB。「ユーザー名」と「パスワード」を `postgres` に書き換える（手順4の `POSTGRES_PASSWORD` と同じ値） |
| `TEST_DATABASE_URL` | テスト用 DB。書き換え方は `DATABASE_URL` と同じ |
| `GOOGLE_MAPS_API_KEY` | Routes API のキー。ルートの登録・編集のときに使う |
| `GOOGLE_MAPS_JS_API_KEY` | Maps JavaScript API のキー。地図の画面（/map）で使う |
| `ADMIN_API_KEY` | 書き込みの API の合言葉。自分で決めた長い文字列を入れる |

- Google のキーは、Google Cloud のコンソールで作ります。2つに分け、それぞれ使うAPIだけに制限してください
- 地図用のキーはブラウザから見えるため、ウェブサイトの制限（`http://127.0.0.1:8000/*` など）もかけてください
- 合言葉は、次のコマンドで作れます

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 起動したあと

- http://127.0.0.1:8000/docs ：Swagger UI で API を試せます。登録・編集・削除は、右上の **Authorize** に `ADMIN_API_KEY` の値を入れてから実行します
- http://127.0.0.1:8000/map ：地図の画面です

## テスト

pytest でテストを実行します。テストでは開発用とは別のテスト用DB（`drive_spot_test`）を使い、テストごとにテーブルを作成・削除するため、開発用のデータには影響しません。

Google を呼ぶ部分はモックに差し替えているため、テストではGoogleのAPIキーを使わず、料金もかかりません。

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

### 実現できる形への方針転換

- 課題：最初は、遠回りでも走って楽しい道をアプリが自動で選ぶ機能を考えていた。しかし、Google の Routes API には、カーブの多い道を優先して探す設定が無かった
- 工夫：道を探すのは自分で行い、アプリは「登録したルートを採点して比べる」役に変えた。登録して一覧で比べる形は、先に作っていたスポット帳と同じなので、CRUD・テーブル構造の管理・テストの仕組みをそのまま活かせた
- 結果：既存の機能を活かしながら、「走って楽しい道を選びたい」という本来の目的に、数値で比べるという形である程度近づけた

### ヘアピンカーブを残したまま、交差点の右左折を採点から除く

- 課題：交差点の右左折は走って楽しいカーブではないため、採点から除くことにした。しかし、角度の大きさで交差点を見分けると、峠道のヘアピンカーブのような一番楽しいカーブまで除いてしまう。また、Google が返す点の打ち方によって結果が変わってしまう
- 工夫：「ヘアピンカーブは採点に残す」という条件を決めたうえで、角度で見分ける方法と、Google の道案内の区切り（step）を使う方法を比べた。ヘアピンは1本の道が曲がっているだけなので道案内の区切りにならない。そのため、区切りで起きた曲がりだけを除く方法を選んだ
- 結果：交差点の右左折を除きつつ、ヘアピンカーブは採点に残せるようにした。角度の数字を決め打ちしないので、点の打ち方にも左右されにくい

## 今後の展望

- 楽しいルートを自動で探す：最初に考えていた機能です。今の採点の仕組みを土台にして、経由地点の候補を変えた複数のルートをGoogleから取得して採点し、一番点数の高いルートを選ぶ形を考えています。
- 出発地・目的地・経由地点を地図上で選ぶ：今は座標を入力して各地点を登録していますが、地図をクリックして地点を選択できるようにしたいです。
- 地図で2本以上のルートを並べて比べる：今は1本ずつしか地図に描けないため、選んだ数本を重ねて表示し、点数と道の形を見比べられるようにしたいです。
- 地図に出発地・目的地のピンを表示する：道の向き（どちらから走り始めるか）がわかるようにします。
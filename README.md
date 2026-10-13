# ドライブスポット帳API

行きたい・行ったドライブスポットを記録するAPI

## 作った理由・今後の展望

一般的なルート案内は、最短距離・最短時間を優先します。
しかし、ドライブそのものが目的のときは、遠回りでもワインディングロードよのうな走って楽しい道を通りたいと感じていました。
現在は地図を見ながら手作業で楽しそうな道を探し、経由地点を置いてその道を通るルートを作っています。

そこで、自分で作ったドライブルートを登録し、「どれくらい走って楽しいか」を数値で比較できるアプリ（Drive Route）を目指しています。
出発地・目的地・経由地点を指定したルートを Google Maps で取得し、迂回率（道のり ÷ 直線距離）やカーブの多さで採点して、登録したルートどうしを比べられるようにする予定です。

現在はその第一段階として、バックエンドの基本（API設計・DB連携・テーブル構造の管理）を身につけるため、ドライブスポットを記録する機能に絞って作成しました。

## 使用技術
- Python 3.14 / FastAPI
- SQLAlchemy（ORM）/ Pydantic（入力チェック）
- PostgreSQL 16（Docker で起動）
- Alembic（テーブル構造の変更管理）

## 機能
- スポットの登録・一覧・1件取得・編集・削除
- おすすめ度（rating）は 1〜5 の整数のみ受け付ける

## API
- GET /spots : 一覧取得
- GET /spots/{id} : 1件取得
- POST /spots : 登録
- PUT /spots/{id} : 編集
- DELETE /spots/{id} : 削除

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
# .env を開き、「ユーザー名」と「パスワード」をどちらも postgres に書き換える
# （手順4の POSTGRES_PASSWORD と同じ値にする）

# 4. PostgreSQL を起動
docker run --name drive-spot-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=drive_spot -v drive-spot-data:/var/lib/postgresql/data -p 5432:5432 -d postgres:16

# 5. テーブルを作成
alembic upgrade head

# 6. サーバーを起動
uvicorn app.main:app --reload
```

起動後、http://127.0.0.1:8000/docs を開くと Swagger UI から API を試せます。

## テスト
<!-- テストを書いたら追加 -->

## 工夫した点
<!-- 各ステップの終わりに追加 -->
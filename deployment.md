# デプロイ運用手順書

本書は TRPG Evaluator のステージング／本番環境を Cloud Run 上で運用するために、人間（GCP 管理者）が実行すべき作業をまとめたものです。リポジトリ側では Cloud Build パイプラインと Docker イメージが用意済みなので、ここで記載する GCP 側の設定とコマンドを順に実施してください。

---

## 1. 前提条件

### GCP プロジェクト
- プロジェクト ID: `trpg-evaluator`（仮。実プロジェクト ID を読み替えてください）
- オーナー権限、または以下の API / サービスに対する管理権限を持つアカウントで作業すること。

### 有効化すべき API
```bash
gcloud services enable \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  run.googleapis.com
```

### コマンドライン環境
- `gcloud` CLI (>= 447.0.0)
- Google Cloud SDK でプロジェクトを指定  
  ```bash
  gcloud config set project <PROJECT_ID>
  gcloud config set compute/region asia-northeast1
  ```

### リポジトリからの参照
- `infra/gcp/cloudbuild.yaml` : Cloud Build パイプライン定義
- `infra/docker/*.Dockerfile` : Docker イメージ
- `.env` / Firebase 認証用シークレット: `secrets/` 以下に配置済み（Git 管理外）

---

## 2. Artifact Registry の作成

1. リポジトリ作成  
   ```bash
   gcloud artifacts repositories create trpg-evaluator \
     --repository-format=docker \
     --location=asia-northeast1 \
     --description="Docker images for TRPG Evaluator"
   ```
2. 認証設定（ローカル CLI から push する場合）  
   ```bash
   gcloud auth configure-docker asia-northeast1-docker.pkg.dev
   ```

---

## 3. Cloud Run サービスの作成（初回のみ）

ステージングと本番でサービス名を分けておくと運用しやすい。

```bash
# API
gcloud run deploy trpg-api-stg \
  --region=asia-northeast1 \
  --image=gcr.io/cloudrun/hello \
  --allow-unauthenticated

gcloud run deploy trpg-api \
  --region=asia-northeast1 \
  --image=gcr.io/cloudrun/hello \
  --allow-unauthenticated

# Web
gcloud run deploy trpg-web-stg \
  --region=asia-northeast1 \
  --image=gcr.io/cloudrun/hello \
  --allow-unauthenticated

gcloud run deploy trpg-web \
  --region=asia-northeast1 \
  --image=gcr.io/cloudrun/hello \
  --allow-unauthenticated
```

※ 初回デプロイ後は Cloud Build でイメージが差し替えられるので、ここではダミーイメージで構いません。

---

## 4. Cloud Build サービスアカウントの権限設定

Cloud Build から Artifact Registry / Cloud Run を操作できるように、サービスアカウントにロールを付与する。

```bash
CB_SA="$(gcloud projects describe $(gcloud config get-value project) \
  --format 'value(projectNumber)')@cloudbuild.gserviceaccount.com"

gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
  --member="serviceAccount:${CB_SA}" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
  --member="serviceAccount:${CB_SA}" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
  --member="serviceAccount:${CB_SA}" \
  --role="roles/iam.serviceAccountUser"
```

---

## 5. Firebase 認証情報の配置

- サービスアカウント JSON を Secret Manager へ登録することを推奨。
  ```bash
  gcloud secrets create firebase-credentials --replication-policy=automatic
  gcloud secrets versions add firebase-credentials --data-file=secrets/trpg-evaluator-firebase.json
  ```
- Cloud Run サービスの環境変数に以下を設定:
  - `FIREBASE_AUTH_DISABLED=0`
  - `FIREBASE_PROJECT_ID=<Firebase プロジェクトID>`
  - `FIREBASE_CREDENTIALS_PATH=/secrets/firebase/credentials.json`
- 併せて Secret をマウントするよう、Cloud Build デプロイ時の引数を調整する（必要であれば `cloudbuild.yaml` の `gcloud run deploy` へ `--set-secrets` を追加）。
- Web アプリでは Firebase Web SDK を通じてトークンを取得するため、以下の公開環境変数を設定する（Cloud Run の Web サービス側に `--set-env-vars` で渡す）。
  - `NEXT_PUBLIC_FIREBASE_API_KEY`
  - `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`
  - `NEXT_PUBLIC_FIREBASE_PROJECT_ID`
  - `NEXT_PUBLIC_FIREBASE_APP_ID`

※ Secret 連携が不要な場合でも、少なくとも本番では `FIREBASE_AUTH_DISABLED=0` を指定し、Application Default Credentials もしくはサービスアカウントを割り当ててください。

---

## 6. Cloud Build トリガーの登録

### ステージング用トリガー（例）

1. Cloud Console → Cloud Build → トリガー →「トリガーを作成」
2. ソース: GitHub 連携 or Cloud Source Repositories
3. ブランチフィルター: `^main$`
4. Substitutions:
   - `_ENV=staging`
   - `_API_SERVICE=trpg-api-stg`
   - `_WEB_SERVICE=trpg-web-stg`
   - `_ARTIFACT_REPO=trpg-evaluator`
   - `_FIREBASE_API_KEY=<firebase apiKey>`
   - `_FIREBASE_AUTH_DOMAIN=<firebase authDomain>`
   - `_FIREBASE_PROJECT_ID=<firebase projectId>`
   - `_FIREBASE_APP_ID=<firebase appId>`
5. 承認: 自動で構わない（`main` へのマージで即 staging へデプロイ）

### 本番用トリガー（例）

1. トリガーを複製して `_ENV=prod`, `_API_SERVICE=trpg-api`, `_WEB_SERVICE=trpg-web`
2. 承認ステップを有効化しておくと安全（デプロイ前に人手で確認できる）。

---

## 7. 手動でパイプラインを実行する場合

スプリントのリリースやホットフィックスなど、手動で昇格したい場合は以下のコマンドをローカルから実行。

```bash
# ステージング
gcloud builds submit --config infra/gcp/cloudbuild.yaml \
  --substitutions _ENV=staging,_API_SERVICE=trpg-api-stg,_WEB_SERVICE=trpg-web-stg,_ARTIFACT_REPO=trpg-evaluator,_FIREBASE_API_KEY=<apiKey>,_FIREBASE_AUTH_DOMAIN=<authDomain>,_FIREBASE_PROJECT_ID=<projectId>,_FIREBASE_APP_ID=<appId>

# 本番（署名付き URL など事前に確認した上で実行）
gcloud builds submit --config infra/gcp/cloudbuild.yaml \
  --substitutions _ENV=prod,_API_SERVICE=trpg-api,_WEB_SERVICE=trpg-web,_ARTIFACT_REPO=trpg-evaluator,_FIREBASE_API_KEY=<apiKey>,_FIREBASE_AUTH_DOMAIN=<authDomain>,_FIREBASE_PROJECT_ID=<projectId>,_FIREBASE_APP_ID=<appId>
```

Cloud Build の実行結果から、Cloud Run サービス URL を確認してください。

---

## 8. デプロイ後の確認

1. Cloud Run のログで 200 応答が返っているか、エラーはないか。
2. Web アプリからログイン → API にアクセスし、Firebase Auth が機能しているか。
3. ステージング URL 経由で手動 QA → 問題なければ本番へ昇格。
4. 本番デプロイ後はキャッシュが残っている場合があるので、必要に応じて CDN やブラウザのキャッシュクリアを案内。
5. Firebase Console の Authentication →「ログイン方法」で Google プロバイダを「有効」に設定し、Cloud Run のドメインを承認済みドメインへ追加する。次に「プロジェクトの設定」→「アプリを追加」で Web アプリを登録し、取得した `firebaseConfig` を `.env` / Cloud Run の環境変数へ反映する。
6. Cloud Run 側で `auth.token.verified` ログが出ているか確認し、Bearer トークンが正しく伝播していることを確認。

---

## 9. 障害対応のヒント

- Cloud Build 失敗時: `gcloud builds log --stream <BUILD_ID>` で詳細を確認。権限・リポジトリ名・環境変数の不足が多い。
- Cloud Run 起動失敗: Cloud Run のログ / エラーメッセージを確認し、環境変数や Secret のマウント設定を見直す。
- Firebase 認証エラー: サービスアカウントに `firebaseauth.configs.get` など必要なロールが付与されているかチェック。
- RAG やセッションで問題があれば GCS / Firestore エミュレータ用の環境変数が本番で外れていないか確認する。

---

## 10. 今後のタスク

- 監視: Cloud Monitoring（uptime check、エラーレートアラート）を設定。
- IaC: Terraform などで Artifact Registry, Cloud Run, Cloud Build トリガーをコード化。
- CI/CD: GitHub Actions から Cloud Build を呼び出すワークフローを整備する（必要に応じて）。

以上でデプロイ手順は完了です。ここに記載された順序で作業していただければ、リポジトリの Cloud Build パイプラインを用いてステージング／本番環境へのデプロイが可能になります。今後の改修時は、README および SPEC の変更履歴に沿って手順書をアップデートしてください。

# 🇯🇵 日本株 高配当トラッカー

リベ大（両学長）の高配当株投資方針に基づく、保有銘柄の管理・分析ダッシュボード。

**GitHub Pages で無料ホスティング** / **平日3回 自動更新（GitHub Actions）**

---

## 🌐 公開URL
https://abundant-pnueli.github.io/Japan-High-Dividend-Tracker/

---

## 📊 機能一覧

| # | 機能 | 説明 |
|---|------|------|
| 1 | 銘柄カード | 利回り・PER・PBR・乖離率バッジ付きカード一覧 |
| 2 | 財務スコアランキング | 4指標の合計スコアでソート可能なテーブル |
| 3 | レーダーチャート | 各銘柄の財務スコアをレーダーで可視化（Chart.js） |
| 4 | 乖離率ビジュアライザー | 25日移動平均からの乖離を棒グラフで表示 |
| 5 | 市場パネル | 日経225・VIX・日経VIをヘッダーに常時表示 |
| 6 | ポートフォリオ管理 | 保有数・取得単価を入力→損益率・配当予測を自動計算（localStorage保存） |
| 7 | 最終更新日時 | データ取得日時を右上に表示 |

---

## 🚀 GitHub Pages デプロイ手順

### 1. リポジトリ作成

GitHubで `Japan-High-Dividend-Tracker` という名前で **Public** リポジトリを作成してください。

### 2. ファイルをプッシュ

```bash
cd "C:\Users\ausbr\Desktop\Claude\Japan-High-Dividend-Tracker"
git init
git add .
git commit -m "feat: 日本株高配当トラッカー 初期リリース"
git branch -M main
git remote add origin https://github.com/abundant-pnueli/Japan-High-Dividend-Tracker.git
git push -u origin main
```

### 3. GitHub Pages を有効化

1. GitHubリポジトリ → **Settings** タブ
2. 左サイドバー → **Pages**
3. **Source**: `Deploy from a branch`
4. **Branch**: `main` / `/ (root)` → **Save**
5. 数分後に `https://abundant-pnueli.github.io/Japan-High-Dividend-Tracker/` で公開されます

### 4. 初回データ取得

1. GitHubリポジトリ → **Actions** タブ
2. `株価データ 自動更新` ワークフロー → **Run workflow** → **Run workflow**
3. 緑チェック ✅ が付いたらデータ取得完了
4. ページをリロードすると実際のデータが表示されます

---

## 📁 ファイル構成

```
Japan-High-Dividend-Tracker/
├── index.html                    # フロントエンド（Vanilla JS・ダークテーマ）
├── data/
│   ├── stocks_list.csv           # 保有銘柄リスト（カスタマイズ可）
│   └── stocks.json               # GitHub Actionsが自動生成するデータ
├── scripts/
│   ├── fetch_stocks.py           # yfinanceでデータ取得
│   └── translate_names.py        # 銘柄名マッピング
└── .github/
    └── workflows/
        └── update.yml            # 平日3回自動更新
```

---

## ⏰ 自動更新スケジュール

| 時刻（JST） | 想定タイミング |
|------------|--------------|
| 11:35 | 前場終了後 |
| 15:35 | 後場終了後 |
| 18:00 | 引け後集計 |

---

## 📈 財務スコア計算方法

各項目 **0〜10点**、合計 **40点満点**：

| 指標 | 満点条件 |
|------|---------|
| 配当利回り | 4%以上で10点 |
| PBR | 0.5以下で10点（低いほど高得点） |
| PER | 10倍以下で10点（低いほど高得点） |
| 乖離率 | −10%以下で10点（割安ほど高得点） |

---

## 🛠 銘柄追加・変更方法

`data/stocks_list.csv` を編集してプッシュするだけです：

```csv
code,name
1234,新しい銘柄名
```

---

## 技術スタック

- **フロントエンド**: Vanilla JS / HTML / CSS（フレームワークなし）
- **チャート**: Chart.js 4.x（CDN）
- **データ取得**: Python 3.11 + yfinance
- **ホスティング**: GitHub Pages（無料）
- **CI/CD**: GitHub Actions

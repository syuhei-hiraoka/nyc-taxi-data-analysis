# NYC Taxi Data Analysis

## 概要
NYC Taxi Dataを使用して、地域ごとの需要・ピーク時間帯・時間帯による需要変化を分析し、車両配置戦略を検討するプロジェクト。

## 目的
地域・時間帯ごとの需要変化を分析し、ピーク時の車両配置戦略を検討する。


## 学習目的
BigQueryからSQLでデータを抽出し、SQL言語の習得とともに、Pythonによるデータ可視化・データの分析の実践経験を積む。

## 使用データ
Dataset:
bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022


## 分析内容
analysis_01.py
→ 年間のトリップ数が10万回以上ある曜日ごと・時間ごとの需要の集中データを抽出し、最もタクシーの利用が多い曜日と時間を分析。

analysis_02.py
→ 金曜日・19時の最もタクシーの利用が多かった地域を抽出し、散布図から関係性を分析。

analysis_03.py
→ analysis_01.pyとanalysis_02.pyの結果から上位の5地域を抽出し、ピーク時の時間帯の車両の配置を分析。


## 分析結果
- タクシーの利用回数と乗客の需要の相関係数は約0.993であり、非常に強い正の相関関係が見られた。
- トリップ数と1回あたりの平均乗客数の需要の相関係数は約-0.126であり、明確な線形関係は確認できなかった。
- 15時～19時に需要が集中し、19時にピークを迎えた。特に19時から20時にかけて需要が大きく減少する傾向が確認された。この結果から、車両配置は19時のピークに合わせて増車するだけでなく、20時以降の需要減少を考慮して減車する必要があると考えた。
- 需要の多い曜日は、水曜日・金曜日・土曜日で、最大は金曜日だと確認できた。


## 分析対象地域の選定
金曜日19時のピーク需要が高く、年間のトリップ数も多い地域を対象とした。

さらに、17時→18時の需要増加率を組み合わせ、
「現在の需要規模」と「ピーク前の需要の伸び」の2つの観点から
車両配置の優先度を評価した。

その結果、以下の5地域を分析対象とした。

170、186、68、107、141

![需要の時間帯](images/peak_demand_time.png)
![需要の曜日](images/peak_demand_dayofweek.png)
![分析対象地域選定](images/demand_concentration.png)

### ピーク需要の集中度
- 分析対象地域を絞るため、以下の2つの指標を使用した。
  - full_trip_count：年間の総需要
  - peak_concentration：年間の総需要でピークの需要がどのくらいの割合を占めているか

- 年間のピーク需要の集中度スコア =
年間のタクシー需要 × 0.8
+ ピーク集中度 × 0.2

- 80:20で算出したのは、70：30では年間のタクシー需要度が下がり、ピーク集中度の主張が強くなり順位に影響したため、年間のタクシー需要度の割合を増やした。

### 需要優先度スコア
- 地域ごとの需要特性を比較するため、以下の3つの指標を使用した。
  - trip_count：タクシーの利用回数
  - passenger_demand：乗車した乗客の総数
  - avg_passenger_count：1回の利用あたりの平均乗客数

- trip_count と passenger_demand には強い正の相関（r=0.966）が確認された。一方、 avg_passenger_count はこれらとは異なる傾向を示した。

- そのため、利用回数や総乗客数だけではなく、1回あたりの利用人数という異なる需要特性も考慮するため、avg_passenger_count を評価指標に加えた。

- 各指標を正規化したうえで重み付けし、需要優先度スコアを算出した。

- 需要優先度スコア =
トリップ数 × 0.5
+ 乗客需要 × 0.3
+ 平均乗客数 × 0.2

50:30:20
40:40:20
60:20:20

を比較し、
重みを変更しても今回の5地域の順位に変化がなかったため、最終的にtrip_countを最も重視する50:30:20を採用した。

![需要数鮮度と需要増加率](images/priority_scatter.png)

## 車両配置戦略
|地域ID | 17時 | 18時 | 19時 | 20時 | 21時 |
|---|---|---|---|---|---|
| 170 | 配置強化 | 配置強化 | ピーク | 減車 | 減車 |
| 186 | 配置強化 | 配置強化 | ピーク | 減車 | 減車 |
| 107 | 配置強化 | 配置強化 | ピーク | 減車 | 減車 |
| 68 | 配置強化 | 配置強化 | ピーク | 減車 | 減車 |
| 141 | 配置強化 | 配置強化 | 減車 | 減車 | 減車 |

![車両配置戦略](images/vehicle_deployment_heatmap.png)

## 分析から得られた知見
- 170・186：
  需要が高いため、ピークに向けた車両確保を優先

- 107：
  ピーク前から需要が増加するため、早めに配置強化

- 68：
  需要増加を考慮し、状況に応じて配置

- 141：
  19時から需要が減少するため、19時から減車を検討

- その他：
  20時以降の需要減少を考慮して減車を検討

### 分析のまとめ

本分析では、地域ごとの需要規模だけでなく、
ピーク前の需要増加率とピーク後の需要減少タイミングを組み合わせることで、
地域ごとに異なる車両配置戦略を検討した。

その結果、単純に需要の多い地域へ車両を集中させるのではなく、
「需要規模」「需要の増加」「需要の減少」の3つの観点から
配置強化・ピーク・減車のタイミングを検討できることを確認した。

## 使用技術
### Language
- Python
- SQL

### Libraries
- pandas
- Numpy
- Matplotlib

### Data Warehouse
- Google BigQuery


## プロジェクト構成
```text
NYC Taxi Data Analysis/
├── .gitignore
├── README.md
├── requirements.txt
|
├── python/
|    ├── analysis_01.py          # 需要の多い曜日・時間を分析
|    ├── analysis_02.py          # ピーク時の地域別需要を分析
|    ├── analysis_03.py          # 上位地域の車両配置戦略を分析
|    │
|    ├── analysis_utils.py       # 分析・統計計算用の関数
|    ├── data_utils.py           # データ取得・前処理用の関数
|    ├── output_utils.py         # 分析結果の出力用の関数
|    ├── plot_utils.py           # グラフ描画用の関数
|    └── strategy_utils.py       # 車両配置戦略の計算用の関数
|
└── sql/
    ├── 01_basic_analysis.sql       # 需要の多い曜日・時間を抽出
    ├── 02_peak_demand_analysis.sql # ピーク時の需要の多い地域を抽出
    └── 03_time_series_analysis.sql # 地域・曜日・時間別のデータを抽出
```


```mermaid
flowchart TD
    A[BigQuery] ---> B[SQLでデータ抽出]
    B ---> C[データをグラフで表示]
    C ---> D[乗客需要]
    C ---> E[タクシー需要]
    D ---> F[正規化・スコア計算]
    E ---> F
    F ---> G[優先度]
    G ---> H[配置戦略]
```

## 実行方法


### 1. リポジトリをクローン
```powershell
git clone https://github.com/syuhei-hiraoka/nyc-taxi-data-analysis.git
cd nyc-taxi-data-analysis
```
### 2. 仮想環境を作成
```powershell
python -m venv python/.venv
python/.venv/Scripts/Activate.ps1
```

### 3. 必要なライブラリをインストール
```powershell
pip install -r requirements.txt
```

### 4. Google Cloudの認証

Application Default Credentialsを設定します。

```powershell
gcloud auth application-default login
```

### 5. Pythonファイルを実行
プロジェクトのルートディレクトリから以下のコマンドを実行します。

```powershell
python python/analysis_01.py
python python/analysis_02.py
python python/analysis_03.py
```

## 今後の改善
- 地域の実際の地理を含めた分析
- より高度な予測モデルの導入
import pandas as pd
import matplotlib.pyplot as plt
from google.cloud import bigquery
from data_utils import get_df_from_sql

from analysis_utils import (
    normalize_and_score,
    time_series_analysis,
)
from strategy_utils import (
    strategy_arrangement,
    increase_start_analysis,
    calculate_duration,
    deployment_period_analysis,
    strategy_result,
    deployment_start_analysis,
    decrease_hour_analysis,
    convert_strategy_to_numeric,
)
from plot_utils import (
    plot_scatter,
    plot_heatmap,
    plot_line,
)
from output_utils import print_selected_columns

LOCATIONS = ["170", "186", "68", "107", "141"]
HOURS = [17, 18, 19, 20, 21]
COLUMNS = ["地域ID","17時","18時","19時","20時","21時"]
MAPPING = {
    "通常": 0,
    "減車": 1,
    "配置強化": 2,
    "ピーク": 3,
}
TIME_COLUMNS = [
    "17時",
    "18時",
    "19時",
    "20時",
    "21時",
]

normalize_items = [
    ("full_trip_count", "full_trip_norm"),
    ("peak_concentration", "peak_conc_norm"),
    ("trip_count", "trip_count_norm"),
    ("passenger_demand", "passenger_demand_norm"),
    ("avg_passenger_count", "avg_passenger_count_norm")
]

client = bigquery.Client(
    project="nyc-taxi-data-analysis-506307"
)
plt.rcParams["font.family"] = "Meiryo"

df = normalize_and_score(
    client, "sql/02_peak_demand_analysis.sql", normalize_items
)

df_01 = get_df_from_sql(client, "sql/03_time_series_analysis.sql")
print(df[["pickup_location_id", "hour", "trip_count"]])
print(df["pickup_location_id"].unique())
result_df = time_series_analysis(df_01, LOCATIONS, HOURS, "pickup_location_id")
plot_line(
    df_01, 
    LOCATIONS, 
    "pickup_location_id", 
    "hour", 
    "trip_count", 
    "Hour", 
    "Trip Count", 
    "Hour Transition Analysis"
)
plt.legend()
plt.show()

print(result_df)

df_merged = pd.merge(
    df, result_df, left_on='pickup_location_id', right_on='location', how='inner'
)

priority_plot_offsets = {
    170 : (-15, 15),
    186 : (15, -15),
    68 : (-15, 15),
    107 : (-15, -15),
    141 : (15, 15),
}

x_threshold = df_merged["demand_priority_score"].median()
y_threshold = df_merged["change_ratio_17_18"].median()

plot_scatter(
    df_merged, 
    "demand_priority_score", 
    "change_ratio_17_18", 
    "Demand Priority Score", 
    "Change ratio 17-18", 
    "Demand change ratio 17-18", 
    x_threshold=x_threshold, 
    y_threshold=y_threshold,
)

strategy = strategy_arrangement(
    df_merged, 
    "demand_priority_score", 
    "change_ratio_17_18", 
    x_threshold, 
    y_threshold,
    )

priority_columns = [
    "pickup_location_id",
    "change_ratio_17_18",
    "strategy",
]
print_selected_columns(df_merged, "demand_priority_score", priority_columns)

df_merged["deployment_start"] = deployment_start_analysis(df_merged, "increase_start", "strategy")

df_merged["decrease_hour"] = decrease_hour_analysis(df_merged, "decrease_start")

df_merged["deployment_hour"] = increase_start_analysis(df_merged, "increase_start", "strategy")

df_merged["deployment_duration"] = calculate_duration(df_merged, "decrease_hour", "deployment_hour")

df_merged["deployment_period"] = deployment_period_analysis(df_merged, "deployment_hour", "decrease_hour")

plot_scatter(
    df_merged, 
    "demand_priority_score", 
    "change_ratio_17_18", 
    "Demand Priority Score", 
    "Increase Rate Between 17 And 18", 
    "Priority Between 17 And 18", 
    label_column="pickup_location_id", 
    offsets=priority_plot_offsets,
)

plt.legend()
plt.show()
strategy_df = df_merged[
    [
        "pickup_location_id",
        "trip_count",
        "passenger_demand",
        "demand_priority_score",
        "strategy",
        "change_ratio_17_18",
        "change_ratio_18_19",
        "change_ratio_19_20",
        "change_ratio_20_21",
        "deployment_hour",
        "hour",
        "decrease_hour",
        "deployment_duration",
        "deployment_period",
    ]
]

print(strategy_df)
results_df = df_merged[
    [
        "pickup_location_id",
        "demand_priority_score",
        "strategy",
        "deployment_period",
        "decrease_hour",
    ]
]

print(results_df)

results = strategy_result(
    strategy_df, 
    "pickup_location_id",
    HOURS, 
    "deployment_hour", 
    "hour", 
    "decrease_hour",
)

deployment_df = pd.DataFrame(
    results,
    columns=COLUMNS
)
print(deployment_df)

deployment_numeric = convert_strategy_to_numeric(deployment_df, TIME_COLUMNS, MAPPING)

plot_heatmap(
    deployment_numeric,
    TIME_COLUMNS,
    strategy_df["pickup_location_id"],
    "Hour",
    "Pickup Location ID",
    "Vehicle Deployment Strategy",
    deployment_df[TIME_COLUMNS],
)

plt.show()
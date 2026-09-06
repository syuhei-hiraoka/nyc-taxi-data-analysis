import matplotlib.pyplot as plt
from google.cloud import bigquery
from data_utils import get_df_from_sql
from analysis_utils import (
    regression_process,
    correlation_calculation,
    column_counts,
)
from plot_utils import (
    plot_scatter,
    plot_bar,
    plot_heatmap,
)

client = bigquery.Client(
    project="nyc-taxi-data-analysis-506307"
)
df = get_df_from_sql(client, "sql/01_basic_analysis.sql")
correlation_items = [
    ("full_trip_count", "passenger_demand"),
    ("trip_count", "passenger_demand"),
    ("trip_count", "avg_passenger_count"),
]
scatter_items = [
    ("full_trip_count", "passenger_demand", "Annual number of passenger", "peak demand", "annual full_trip_count of peak_passenger_demand"),
    ("trip_count", "passenger_demand", "trip_count", "passenger_demand", "trip_count and passenger_demand"),
    ("trip_count", "avg_passenger_count", "trip_count", "avg_passenger_count", "trip_count and avg_passenger_count"),
]
y_pred = regression_process(df, "full_trip_count", "passenger_demand")

for x_column, y_column in correlation_items:
    print(correlation_calculation(df, x_column, y_column))

for x_column, y_column, xlabel, ylabel, title in scatter_items:
    plot_scatter(
        df, x_column, y_column, xlabel, ylabel, title,
    )
    if x_column == "full_trip_count":
        plt.plot(df[x_column], y_pred)
    plt.show()

hour_counts = column_counts(df, "hour")
week_counts = column_counts(df, "day_of_week")
bar_items = [
    (
        hour_counts.index, 
        hour_counts.values, 
        "Hour", 
        "Number of peak regions", 
        "Peak Hour Distribution by Region"
    ),
    (
        week_counts.index, 
        week_counts.values, 
        "Day of Week", 
        "Number of peak regions", 
        "Peak Week Distribution by Region"
    ),
]

for x_data, y_data, xlabel, ylabel, title in bar_items:
    plot_bar(
        x_data, y_data, xlabel, ylabel, title
    )
    plt.show()

pivot = df.pivot_table(
    index="day_of_week",
    columns="hour",
    aggfunc="size",
    fill_value=0
)
plot_heatmap(
    pivot,
    pivot.columns,
    pivot.index,
    "Hour",
    "Day of Week",
    "Peak Region Distribution by Day and Hour",
)
plt.show()
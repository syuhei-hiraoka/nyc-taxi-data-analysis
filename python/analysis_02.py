import matplotlib.pyplot as plt
from google.cloud import bigquery
from analysis_utils import normalize_and_score
from plot_utils import plot_scatter
from output_utils import print_selected_columns
client = bigquery.Client(
    project="nyc-taxi-data-analysis-506307"
)

normalize_items = [
    ("full_trip_count", "full_trip_norm"),
    ("peak_concentration", "peak_conc_norm"),
    ("trip_count", "trip_count_norm"),
    ("passenger_demand", "passenger_demand_norm"),
    ("avg_passenger_count", "avg_passenger_count_norm")
]
df = normalize_and_score(
    client, "sql/02_peak_demand_analysis.sql", normalize_items
)

columns = [
    "pickup_location_id", 
    "trip_count_norm", 
    "passenger_demand_norm", 
    "avg_passenger_count_norm",
]
print_selected_columns(
    df, "demand_priority_score", columns,
)

peak_demand_plot_offsets = {
        170: (-15, 15),
        186: (-15, 15),
        107: (-15, -15),
        68: (15, 15),
        141: (15, -15),
        164: (15, 15),
        90:(15,15),
        137: (15, 15),
    }
plot_scatter(
    df,
    "trip_count", 
    "passenger_demand", 
    "Trip_count", 
    "Passenger_demand", 
    "Peak demand analysis",
    label_column="pickup_location_id",
    size=df["avg_passenger_count"] * 500,
    offsets=peak_demand_plot_offsets,
)
plt.show()

plot_scatter(
    df,
    "annual_peak_priority_score", 
    "trip_count", 
    "Annual Peak Priority Score", 
    "Trip Count", 
    "Normal Time And Peak Time Relation",
    label_column="pickup_location_id", 
    offsets=peak_demand_plot_offsets,
)
plt.show()
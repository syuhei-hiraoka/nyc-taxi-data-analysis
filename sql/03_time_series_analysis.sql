SELECT
    pickup_location_id,
    EXTRACT(HOUR FROM pickup_datetime) AS hour,
    COUNT(*) AS trip_count,
    SUM(passenger_count) AS passenger_demand,
    SUM(passenger_count) / COUNT(*) AS avg_passenger_count
FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022`
WHERE
    passenger_count >= 1
    AND EXTRACT(DAYOFWEEK FROM pickup_datetime) = 6
    AND EXTRACT(HOUR FROM pickup_datetime) BETWEEN 17 AND 21
    AND pickup_location_id IN ('170', '186', '68', '107', '141')
GROUP BY
    pickup_location_id, hour
ORDER BY
    pickup_location_id, hour;
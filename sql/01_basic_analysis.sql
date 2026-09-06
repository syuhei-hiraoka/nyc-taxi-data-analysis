SELECT
    peak.pickup_location_id,
    peak.hour,
    peak.day_of_week,
    peak.trip_count,
    peak.passenger_demand,
    peak.avg_passenger_count,
    annual.full_trip_count
FROM (
    SELECT
        pickup_location_id,
        hour,
        day_of_week,
        trip_count,
        passenger_demand,
        avg_passenger_count,
        rank
    FROM (
        SELECT
            pickup_location_id,
            hour,
            day_of_week,
            trip_count,
            passenger_demand,
            passenger_demand / trip_count AS avg_passenger_count,
            RANK() OVER(
                PARTITION BY pickup_location_id
                ORDER BY passenger_demand DESC
            ) AS rank
        FROM (
            SELECT
                pickup_location_id,
                EXTRACT(HOUR FROM pickup_datetime) AS hour,
                EXTRACT(DAYOFWEEK FROM pickup_datetime) AS day_of_week,
                COUNT(*) AS trip_count,
                SUM(passenger_count) AS passenger_demand,
            FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022`
            WHERE
                passenger_count >= 1
                AND pickup_location_id IN (
                    SELECT
                        pickup_location_id,
                    FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022`
                    WHERE
                        passenger_count >= 1
                    GROUP BY
                        pickup_location_id
                    HAVING
                    COUNT(*) >= 100000
                )
            GROUP BY
                pickup_location_id, hour, day_of_week
        )
    )
    WHERE
        rank = 1
    ) AS peak
JOIN (
    SELECT
        pickup_location_id,
        COUNT(*) AS full_trip_count
    FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022` 
    WHERE
        passenger_count >= 1
    GROUP BY
        pickup_location_id
    HAVING COUNT(*) >= 100000
) AS annual
ON
    peak.pickup_location_id = annual.pickup_location_id;

import pandas as pd
import numpy as np
import google.cloud.bigquery
from data_utils import (
    get_df_from_sql,
    normalize_series,
)

def normalize_and_score(client: google.cloud.bigquery.Client, sql_file: str, normalize_items: list) -> pd.DataFrame:
    """
    SQLファイルを読み込み、BigQueryクライアントを使用してデータフレームを取得し、正規化とスコア計算を行う関数。
    
    Parameters
    ----------
    client : google.cloud.bigquery.Client
        BigQueryクライアントオブジェクト。
    sql_file : str
        SQLファイルのパス。
    normalize_items : list of tuples
        正規化する列名と新しい列名のタプルのリスト。
    
    Returns
    -------
    pandas.DataFrame
        正規化とスコア計算を行ったデータフレーム。
    """
    df = get_df_from_sql(client, sql_file)

    df["peak_concentration"] = df["trip_count"] / df["full_trip_count"]

    for norm_column, norm_name in normalize_items:
        df[norm_name] = normalize_series(df[norm_column])

    df["annual_peak_priority_score"] = (
        df["full_trip_norm"] * 0.8
        +
        df["peak_conc_norm"] * 0.2
    )

    df["demand_priority_score"] = (
        df["trip_count_norm"] * 0.5
        + df["passenger_demand_norm"] * 0.3
        + df["avg_passenger_count_norm"] * 0.2
    )
    return df

def change_ratio_between_time_periods(before: float, after: float) -> float:
    """
    2つの値の間の変化率を計算する関数。
    
    Parameters
    ----------
    before : float
        変化前の値。
    after : float
        変化後の値。
    
    Returns
    -------
    float
        変化率。
    """
    return (after - before) / before

def regression_process(df: pd.DataFrame, x_column: str, y_column: str) -> pd.Series:
    """
    線形回帰を使用して、指定された列の回帰直線を計算する関数。
    
    Parameters
    ----------
    df : pandas.DataFrame
        データフレーム。
    x_column : str
        回帰の独立変数となる列名。
    y_column : str
        回帰の従属変数となる列名。
    
    Returns
    -------
    pandas.Series
        回帰直線の予測値。
    """
    slope, intercept = np.polyfit(
        df[x_column],
        df[y_column],
        1
    )
    return slope * df[x_column] + intercept

def correlation_calculation(df: pd.DataFrame, x_column: str, y_column: str) -> float:
    """
    2つの列間の相関係数を計算する関数。
    
    Parameters
    ----------
    df : pandas.DataFrame
        データフレーム。
    x_column : str
        相関を計算する列名。
    y_column : str
        相関を計算する列名。
    
    Returns
    -------
    float
        相関係数。
    """
    return df[x_column].corr(df[y_column])

def column_counts(df: pd.DataFrame, column: str) -> pd.Series:
    """
    指定された列の値の出現回数を計算する関数。
    
    Parameters
    ----------
    df : pandas.DataFrame
        データフレーム。
    column : str
        値の出現回数を計算する列名。
    
    Returns
    -------
    pandas.Series
        値とその出現回数のペア。
    """
    return df[column].value_counts().sort_index()

def get_hourly_trip_counts(location_data: pd.DataFrame, hours: list) -> list:
    """
    指定された時間帯のトリップ数を取得する関数。
    
    Parameters
    ----------
    location_data : pandas.DataFrame
        地域ごとのデータ。
    hours : list
        取得する時間帯のリスト。
    
    Returns
    -------
    list
        各時間帯のトリップ数。
    """
    hours_data = []
    for i in hours:
        hour_data = location_data["trip_count"].loc[location_data["hour"] == i]
        if not hour_data.empty:
            hour_data = hour_data.iloc[0]
            hours_data.append(hour_data)
        else:
            hours_data.append(0)
    return hours_data

def calculate_change_ratios(hours_data: list) -> list:
    """
    指定された時間帯のトリップ数の変化率を計算する関数。
    
    Parameters
    ----------
    hours_data : list
        各時間帯のトリップ数。
    
    Returns
    -------
    list
        各時間帯のトリップ数の変化率。
    """
    change_ratios = []
    for i in range(len(hours_data) - 1):
        change_ratio = change_ratio_between_time_periods(hours_data[i], hours_data[i+1])
        change_ratios.append(change_ratio)
    return change_ratios

def find_first_period(change_ratios: list[float], hours: list[int], condition: callable) -> str:
    """
    指定された条件を満たす最初の時間帯を見つける関数。
    
    Parameters
    ----------
    change_ratios : list[float]
        各時間帯のトリップ数の変化率。
    hours : list[int]
        時間帯のリスト。
    condition : function
        条件を判定する関数。
    
    Returns
    -------
    str
        最初の時間帯の文字列。
    """
    for i, change_ratio in enumerate(change_ratios):
        if condition(change_ratio):
            return f"{hours[i]} → {hours[i+1]}"
        
def time_series_analysis(
    df: pd.DataFrame, 
    locations: list[str], 
    hours: list[int],
    pickup_location_id: str,
    increase_threshold: float = 0.15,
    decrease_threshold: float = 0.0
) -> pd.DataFrame:
    """
    指定された地域ごとの時間帯のトリップ数の変化率を分析する関数。
    
    Parameters
    ----------
    df : pandas.DataFrame
        データフレーム。
    locations : list[str]
        分析する地域のリスト。
    hours : list[int]
        分析する時間帯のリスト。
    pickup_location_id : str
        地域IDの列名。
    increase_threshold : float, optional
        増加開始の閾値。デフォルトは0.15。
    decrease_threshold : float, optional 
         減少開始の閾値。デフォルトは0.0。
    
    Returns
    -------
    pandas.DataFrame
        各地域ごとの時間帯のトリップ数の変化率と増加・減少開始時間を含むデータフレーム。
    """
    results = []
    for location in locations:
        location_data = df[df[pickup_location_id] == location]
        hours_data = get_hourly_trip_counts(location_data, hours)
        change_ratios = calculate_change_ratios(hours_data)
        
        increase_start = find_first_period(
            change_ratios, 
            hours, 
            lambda change_ratio: change_ratio >= increase_threshold
        )

        decrease_start = find_first_period(
            change_ratios, 
            hours, 
            lambda change_ratio: change_ratio < decrease_threshold
        )
            
        results.append(
            [location] + change_ratios + [increase_start] + [decrease_start]
        ) 
    return pd.DataFrame(
        results,
        columns=[
            "location",
            "change_ratio_17_18",
            "change_ratio_18_19",
            "change_ratio_19_20",
            "change_ratio_20_21",
            "increase_start",
            "decrease_start",
        ]
    )


import pandas as pd
import google.cloud.bigquery

def get_df_from_sql(client: google.cloud.bigquery.Client, sql_file: str) -> pd.DataFrame:
    """
    SQLファイルを読み込み、BigQueryクライアントを使用してデータフレームを取得する関数。
    
    Parameters
    ----------
    client : google.cloud.bigquery.Client
        BigQueryクライアントオブジェクト。
    sql_file : str
        SQLファイルのパス。
        
    Returns
    -------
    pandas.DataFrame
        SQLクエリの結果を含むデータフレーム。
    """
    with open(sql_file) as file:
        sql = file.read()
    query_job = client.query(sql)
    df = query_job.to_dataframe()
    return df
    
def normalize_series(series: pd.Series) -> pd.Series:
    """
    需要に関する情報を正規化する関数。
    
    Parameters
    ----------
    series : pandas.Series
        正規化するシリーズ。
    
    Returns
    -------
    pandas.Series
        正規化されたシリーズ。
    """
    return (series - series.min()) / (series.max() - series.min())


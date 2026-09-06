import pandas

def print_demand_priority(
    df: pandas.DataFrame, 
    target_column: str, 
    columns: list[str]
) -> None:
    """
    需要の比率から優先度を表示する処理。
    
    Parameters
    ----------
    df : pandas.DataFrame
        データフレーム。
    target_column : str
        指定した優先度列を基準にDataFrameを並べ替えて表示する。
    columns : list[str]
        表示する列名のリスト。
    
    Returns
    -------
    None
    """
    print(
    df[columns + [target_column]].sort_values(
        target_column,
        ascending=False
    )
)
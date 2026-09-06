import pandas

def print_selected_columns(
    df: pandas.DataFrame, 
    target_column: str, 
    columns: list[str]
) -> None:
    """
    選択した列を表示する処理。
    
    Parameters
    ----------
    df : pandas.DataFrame
        データフレーム。
    target_column : str
        指定した列を基準にDataFrameを並べ替えて表示する。
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
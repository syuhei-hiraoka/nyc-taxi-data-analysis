import pandas as pd

def strategy_arrangement(
    df_merged: pd.DataFrame, 
    peak_column: str, 
    change_ratio_column: str, 
    priority_threshold: float, 
    change_ratio_threshold: float
) -> pd.Series:
    """
    需要優先度と変化率に基づいて戦略を決定する関数。
    
    Parameters
    ----------
    df_merged : pandas.DataFrame
        データフレーム。
    peak_column : str
        需要優先度の列名。
    change_ratio_column : str
        変化率の列名。
    priority_threshold : float
        需要優先度の閾値。
    change_ratio_threshold : float
        変化率の閾値。  
    
    Returns
    -------
    pandas.Series
        戦略を示す列。
    """

    strategy = []
    for _, row in df_merged.iterrows():
        
        if row[peak_column] >= priority_threshold and row[change_ratio_column] >= change_ratio_threshold:
            strategy.append("ピーク前から最優先")
        elif row[peak_column] >= priority_threshold and row[change_ratio_column] < change_ratio_threshold:
            strategy.append("ピーク時の車両確保を優先")
        elif row[peak_column] < priority_threshold and row[change_ratio_column] >= change_ratio_threshold:
            strategy.append("状況に応じて配置")
        else:
            strategy.append("通常配置・優先度低")
            
    df_merged["strategy"] = strategy
    return df_merged["strategy"]

def increase_start_analysis(df: pd.DataFrame, increase_start: str, strategy: str) -> list[int]:
    """
    配置強化の開始時間を分析する関数。

    Parameters
    ----------
    df : pandas.DataFrame
        データフレーム。
    increase_start : str
        配置強化の開始時間の列名。
    strategy : str
        戦略の列名。
        
    Returns
    -------
    list[int]
        配置強化の開始時間のリスト。
    """
    deployment_hour = []
    for _, row in df.iterrows():
        start = None
        if pd.notna(row[increase_start]):
            start = int(row[increase_start].split("→")[0].strip())
        elif row[strategy] == "ピーク時の車両確保を優先":
            start = 17
        else:
            start = None
        deployment_hour.append(start)
    return deployment_hour

def calculate_duration(df: pd.DataFrame, decrease_hour: str, deployment_hour: str) -> list[int]:
    """
    配置強化の継続時間を計算する関数。

    Parameters
    ----------
    df : pandas.DataFrame
        データフレーム。
    decrease_hour : str
        減車時間の列名。
    deployment_hour : str
        配置強化の開始時間の列名。

    Returns
    -------
    list[int]
        配置強化の継続時間のリスト。
    """
    deployment_duration = []
    for idx, row in df.iterrows():
        info = None
        if pd.notna(row[decrease_hour]) and pd.notna(row[deployment_hour]):
            info = int(row[decrease_hour]) - row[deployment_hour]
        deployment_duration.append(info)
    return deployment_duration

def deployment_period_analysis(df: pd.DataFrame, deployment_hour: str, decrease_hour: str) -> list[str]:
    """
    配置強化の期間を分析する関数。

    Parameters
    ----------
    df : pandas.DataFrame
        データフレーム。
    deployment_hour : str
        配置強化の開始時間の列名。
    decrease_hour : str
        減車時間の列名。

    Returns
    -------
    list[str]
        配置強化の期間のリスト。
    """
    deployment_period = []
    for _, row in df.iterrows():
        period = ''
        if pd.notna(row[deployment_hour]) and pd.notna(row[decrease_hour]):
            period = f'{row[deployment_hour]}時~{row[decrease_hour]}時'
        deployment_period.append(period)
    return deployment_period

def strategy_result(
    df: pd.DataFrame, 
    location: str, 
    hours: list[int], 
    deployment_hour: str, 
    hour: str, 
    decrease_hour: str
) -> list[str]:
    """
    戦略の結果を分析する関数。

    Parameters
    ----------
    df : pandas.DataFrame
        データフレーム。
    location : str
        場所の列名。
    hours : list[int]
        時間のリスト。
    deployment_hour : str
        配置強化の開始時間の列名。
    hour : str
        時間の列名。
    decrease_hour : str
        減車時間の列名。

    Returns
    -------
    list[str]
        戦略の結果のリスト。
    """
    results = []
    for _, row in df.iterrows():
        result = [row[location]]
        state = ""
        for h in hours:
            if h < row[deployment_hour]:
                state = "通常"
            elif row[deployment_hour] <= h < row[hour]:
                state = "配置強化"
            elif h >= int(row[decrease_hour]):
                state = "減車"
            elif h == row[hour]:
                state = "ピーク"
            else:
                state = "通常"
            result.append(state)
        results.append(result)
    return results

def deployment_start_analysis(df: pd.DataFrame, increase_start: str, strategy: str) -> list[str]:
    """
    配置強化の開始時間を分析する関数。

    Parameters
    ----------
    df : pandas.DataFrame
        データフレーム。
    increase_start : str
        配置強化の開始時間の列名。
    strategy : str
        戦略の列名。

    Returns
    -------
    list[str]
        配置強化の開始時間のリスト。
    """
    deployment_start = []
    for _, row in df.iterrows():
        start = ''
        if pd.notna(row[increase_start]):
            start = f'{row[increase_start].split("→")[0].strip()}から配置を強化する準備を開始'
            
        elif row[strategy] == "ピーク時の車両確保を優先":
            start = '17時からピークに向けた車両確保を開始'
        else:
            start = '17時から増車する根拠が弱いので、別途判断'
        deployment_start.append(start)
    return deployment_start

def decrease_hour_analysis(df: pd.DataFrame, decrease_start: str) -> list[str]:
    """
    減車時間を分析する関数。
    
    Parameters
    ----------
    df : pandas.DataFrame
        データフレーム。
    decrease_start : str
        減車開始時間の列名。
        
    Returns
    -------
    list[str]
        減車時間のリスト。
    """
    decrease_hour = []
    for _, row in df.iterrows():
        start = None
        if pd.notna(row[decrease_start]):
            start = row[decrease_start].split("→")[1].strip()
        else:
            start = None
        decrease_hour.append(start)
    return decrease_hour

def convert_strategy_to_numeric(df: pd.DataFrame, time_columns: list[str], mapping: dict) -> pd.DataFrame:
    """
    戦略を数値に変換する関数。

    Parameters
    ----------
    df : pandas.DataFrame
        データフレーム。
    time_columns : list[str]
        時間の列名のリスト。
    mapping : dict
        変換マッピング。

    Returns
    -------
    pandas.DataFrame
        数値に変換されたデータフレーム。
    """
    numeric_df = df[time_columns].copy()
    
    for column in time_columns:
        numeric_df[column] = numeric_df[column].map(mapping)
    return numeric_df


import matplotlib.pyplot as plt
import pandas as pd

def plot_scatter(
    df: pd.DataFrame, 
    x_column: str, 
    y_column: str, 
    xlabel: str, 
    ylabel: str, 
    title: str, 
    label_column: str = None, 
    size: int = None, 
    offsets: dict = None, 
    x_threshold: float = None, 
    y_threshold: float = None   
) -> None:
    """
    散布図をプロットする処理。
    
    Parameters
    ----------
    df : pandas.DataFrame
        データフレーム。
    x_column : str
        x軸の列名。
    y_column : str
        y軸の列名。 
    xlabel : str
        x軸のラベル。
    ylabel : str
        y軸のラベル。
    title : str
        グラフのタイトル。
    label_column : str, optional
        ラベルの列名。デフォルトはNone。
    size : int, optional
        散布図の点のサイズ。デフォルトはNone。
    offsets : dict, optional
        ラベルのオフセット位置を指定する辞書。デフォルトはNone
    x_threshold : float, optional
        x軸の閾値。デフォルトはNone。
    y_threshold : float, optional
        y軸の閾値。デフォルトはNone。
        
    Returns
    -------
    None
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    
    ax.scatter(
        df[x_column], df[y_column],
        s=size,
        alpha=0.5,
        c="blue",
        edgecolor="black"
    )
    if label_column is not None and offsets is not None:
        for _, row in df.iterrows():
            ax.annotate(
                row[label_column],
                (row[x_column], row[y_column]),
                textcoords = "offset points",
                xytext = offsets[int(row[label_column])],
                ha = 'center'
            )
    if x_threshold is not None:
        ax.axvline(x=x_threshold, color='black', linestyle='--', linewidth=1.5)
    if y_threshold is not None:
        ax.axhline(y=y_threshold, color='black', linestyle='--', linewidth=1.5)
        
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)

def plot_bar(x_data: list[str], y_data: list[float], xlabel: str, ylabel: str, title: str) -> None:
    """
    棒グラフをプロットする処理。
    
    Parameters
    ----------
    x_data : list[str]
        x軸のデータ。
    y_data : list[float]
        y軸のデータ。
    xlabel : str
        x軸のラベル。
    ylabel : str
        y軸のラベル。
    title : str
        グラフのタイトル。

    Returns
    -------
    None
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.bar(x_data, y_data)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)

def plot_heatmap(
    pivot: pd.DataFrame, 
    x_labels: list[str], 
    y_labels: list[str], 
    xlabel: str, 
    ylabel: str, 
    title: str, 
    text_data: pd.DataFrame = None
)-> None:
    """
    ヒートマップをプロットする処理。

    Parameters
    ----------
    pivot : pandas.DataFrame
        ヒートマップのデータ。
    x_labels : list[str]
        x軸のラベル。
    y_labels : list[str]
        y軸のラベル。
    xlabel : str
        x軸のラベル。
    ylabel : str
        y軸のラベル。
    title : str
        グラフのタイトル。
    text_data : pandas.DataFrame, optional
        テキストデータ。デフォルトはNone。

    Returns
    -------
    None
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(pivot)
    ax.set_xticks(range(len(x_labels)), x_labels)
    ax.set_yticks(range(len(y_labels)), y_labels)
    if text_data is not None:
        for i in range(len(y_labels)):
            for j in range(len(x_labels)):
                ax.text(
                    j,
                    i,
                    text_data.iloc[i, j],
                    ha="center",
                    va="center"
                )
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)

def plot_line(
    df: pd.DataFrame, 
    locations: list[str], 
    pickup_location_id: str, 
    x_column: str, 
    y_column: str, 
    xlabel: str, 
    ylabel: str, 
    title: str
) -> None:
    """
    折れ線グラフをプロットする処理。

    Parameters
    ----------
    df : pandas.DataFrame
        グラフのデータ。
    locations : list[str]
        ロケーションのリスト。
    pickup_location_id : str
        取り出しロケーションのID。
    x_column : str
        x軸の列名。
    y_column : str
        y軸の列名。
    xlabel : str
        x軸のラベル。
    ylabel : str
        y軸のラベル。
    title : str
        グラフのタイトル。

    Returns
    -------
    None
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    for location in locations:
        location_data = df[df[pickup_location_id] == location]
        ax.plot(location_data[x_column], location_data[y_column], label=location)    
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)

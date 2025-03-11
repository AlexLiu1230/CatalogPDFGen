import pandas as pd

def read_csv(file_path: str):
    """
    讀取 CSV 檔案並返回 pandas DataFrame。
    :param file_path: CSV 檔案的路徑。
    :return: 包含 CSV 數據的 pandas DataFrame。
    """
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None
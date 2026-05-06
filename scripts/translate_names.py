# translate_names.py
# stocks_list.csv から銘柄コード→日本語名のマッピングを提供

import csv
import os

def get_name_map():
    """銘柄コード(str) → 日本語名(str) の辞書を返す"""
    name_map = {}
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'stocks_list.csv')
    with open(csv_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name_map[row['code'].strip()] = row['name'].strip()
    return name_map

if __name__ == '__main__':
    m = get_name_map()
    for code, name in m.items():
        print(f"{code}: {name}")

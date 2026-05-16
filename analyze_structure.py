import requests
from bs4 import BeautifulSoup
import re


def analyze_page_structure():
    url = "https://data.earthquake.cn/datashare/report.shtml?PAGEID=earthquake_subao"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 查找表格数据
    tables = soup.find_all('table')
    print(f"找到 {len(tables)} 个表格")

    # 特别查找数据表格
    data_tables = soup.find_all('table', class_='cls-data-table')
    print(f"找到 {len(data_tables)} 个数据表格")

    # 查看表格结构
    for i, table in enumerate(data_tables[:2]):  # 只看前两个
        print(f"\n=== 表格 {i + 1} ===")
        rows = table.find_all('tr')
        for j, row in enumerate(rows[:5]):  # 只看前5行
            cells = row.find_all(['td', 'th'])
            cell_data = [cell.get_text(strip=True) for cell in cells]
            print(f"行 {j}: {cell_data}")


if __name__ == "__main__":
    analyze_page_structure()
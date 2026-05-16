import requests
from bs4 import BeautifulSoup
import json


def find_data_api():
    # 目标网址
    url = "https://data.earthquake.cn/datashare/report.shtml?PAGEID=earthquake_subao"

    try:
        # 发送请求获取网页内容
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'

        if response.status_code == 200:
            print("成功获取网页内容！")

            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找可能的API接口
            print("\n=== 查找隐藏的API接口 ===")

            # 查找script标签
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    if 'ajax' in script.string or 'fetch' in script.string or 'XMLHttpRequest' in script.string:
                        print("找到可能的AJAX请求:")
                        print(script.string[:500])  # 只打印前500字符

            # 查找隐藏的输入字段
            hidden_inputs = soup.find_all('input', {'type': 'hidden'})
            print(f"\n找到 {len(hidden_inputs)} 个隐藏输入字段")

            # 查找包含数据的span
            data_spans = soup.find_all('span', {'style': 'display:none'})
            for span in data_spans:
                if 'value' in span.attrs:
                    print(f"隐藏数据: {span.attrs}")

        else:
            print(f"请求失败，状态码: {response.status_code}")

    except Exception as e:
        print(f"发生错误: {e}")


if __name__ == "__main__":
    find_data_api()
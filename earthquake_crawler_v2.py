import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re


class EarthquakeDataCrawler:
    def __init__(self):
        self.base_url = "https://data.earthquake.cn/datashare/report.shtml"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'Origin': 'https://data.earthquake.cn',
            'Referer': 'https://data.earthquake.cn/datashare/report.shtml?PAGEID=earthquake_subao',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
        }
        self.session = requests.Session()

    def get_earthquake_data(self, start_date, end_date, min_magnitude=3.0):
        """获取地震数据 - 使用POST请求"""
        # 首先获取第一页数据，同时提取必要的隐藏参数
        print("正在获取第一页数据并解析分页信息...")

        # 基础表单数据
        base_form_data = {
            'DISPLAY_TYPE': '1',
            'PAGEID': 'earthquake_subao',
            'begtime': start_date,
            'endtime': end_date,
            'minM': str(min_magnitude),
            'maxM': '10',
            'minLon': '-180.0',
            'maxLon': '180.0',
            'minLat': '-90.0',
            'maxLat': '90.0',
            'minDepths': '0',
            'maxDepths': '1000',
            'locationselect': 'world',
            'location': '',
            'catalog_PAGENO': '1',  # 第一页
            'WX_ISAJAXLOAD': 'true',
            'refreshComponentGuid': 'earthquake_subao_guid_catalog'
        }

        all_earthquakes = []

        try:
            # 获取第一页数据
            first_page_data, total_pages = self.get_first_page(base_form_data)
            if first_page_data:
                all_earthquakes.extend(first_page_data)
                print(f"第一页获取到 {len(first_page_data)} 条记录")
                print(f"总页数: {total_pages}")

            # 更新表单数据，添加从第一页获取的参数
            base_form_data.update({
                'catalog_ALLDATASETS_RECORDCOUNT': f'catalog__default_default_default_key__default_default_default_key={total_pages * 20};',
                'catalog_RECORDCOUNT': str(total_pages * 20),
                'catalog_PAGECOUNT': str(total_pages)
            })

            # 获取后续页面
            for page in range(2, total_pages + 1):
                print(f"正在获取第{page}页数据...")
                page_data = self.get_page_data(base_form_data, page)
                if page_data:
                    all_earthquakes.extend(page_data)
                    print(f"第{page}页获取到 {len(page_data)} 条记录")
                else:
                    print(f"第{page}页获取失败")
                time.sleep(1)  # 避免请求过快

            print(f"总共获取到 {len(all_earthquakes)} 条地震记录")

            # 去重处理
            unique_earthquakes = self.remove_duplicates(all_earthquakes)
            print(f"去重后剩余 {len(unique_earthquakes)} 条唯一记录")

            return unique_earthquakes

        except Exception as e:
            print(f"获取数据时发生错误: {e}")
            return None

    def get_first_page(self, form_data):
        """获取第一页数据并解析总页数"""
        try:
            randnum = random.random()

            response = self.session.post(
                f"{self.base_url}?randnum={randnum}",
                data=form_data,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                # 解析数据
                earthquakes = self.parse_html_data(response.text)

                # 解析总页数
                total_pages = self.parse_total_pages(response.text)

                return earthquakes, total_pages
            else:
                print(f"获取第一页失败，状态码: {response.status_code}")
                return None, 1

        except Exception as e:
            print(f"获取第一页数据时发生错误: {e}")
            return None, 1

    def get_page_data(self, form_data, page_number):
        """获取指定页面的数据"""
        try:
            randnum = random.random()

            # 更新页码
            form_data['catalog_PAGENO'] = str(page_number)

            response = self.session.post(
                f"{self.base_url}?randnum={randnum}",
                data=form_data,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                return self.parse_html_data(response.text)
            else:
                print(f"获取第{page_number}页失败，状态码: {response.status_code}")
                return None

        except Exception as e:
            print(f"获取第{page_number}页数据时发生错误: {e}")
            return None

    def parse_total_pages(self, html_content):
        """从HTML中解析总页数"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # 方法1: 从分页信息中解析
        navigate_info = soup.find('span', class_='cls-navigate-info')
        if navigate_info:
            text = navigate_info.get_text()
            match = re.search(r'共\s*(\d+)\s*页', text)
            if match:
                return int(match.group(1))

        # 方法2: 从分页链接中解析
        page_links = soup.find_all('a', href=re.compile(r'catalog_PAGENO=\d+'))
        if page_links:
            page_nums = []
            for link in page_links:
                onclick = link.get('onclick', '')
                match = re.search(r"catalog_PAGENO=(\d+)", onclick)
                if match:
                    page_nums.append(int(match.group(1)))
            if page_nums:
                return max(page_nums)

        # 方法3: 如果以上都失败，使用默认值53（根据你提供的信息）
        print("无法解析总页数，使用默认值53")
        return 53

    def parse_html_data(self, html_content):
        """解析HTML页面中的地震数据"""
        soup = BeautifulSoup(html_content, 'html.parser')
        earthquakes = []

        data_table = soup.find('table', {'id': 'earthquake_subao_guid_catalog_data'})
        if not data_table:
            print("未找到数据表格")
            return []

        rows = data_table.find_all('tr')[1:]  # 跳过表头行

        if not rows:
            print("表格中没有数据行")
            return []

        for i, row in enumerate(rows):
            cells = row.find_all('td')
            if len(cells) >= 9:
                try:
                    earthquake = {
                        '序号': cells[1].get_text(strip=True),
                        '发震时间': cells[2].get_text(strip=True),
                        '经度': float(cells[3].get_text(strip=True)),
                        '纬度': float(cells[4].get_text(strip=True)),
                        '深度': float(cells[5].get_text(strip=True)),
                        '震级': float(cells[6].get_text(strip=True)),
                        '位置': cells[7].get_text(strip=True),
                        '类型': cells[8].get_text(strip=True)
                    }
                    earthquakes.append(earthquake)
                except (ValueError, IndexError) as e:
                    print(f"解析第 {i + 1} 行数据时出错: {e}")
                    continue
            else:
                print(f"第 {i + 1} 行列数不足: {len(cells)}")

        return earthquakes

    def remove_duplicates(self, earthquakes):
        """去除重复的地震记录"""
        seen = set()
        unique_earthquakes = []

        for eq in earthquakes:
            # 使用时间、经度、纬度、震级作为唯一标识
            key = (eq['发震时间'], eq['经度'], eq['纬度'], eq['震级'])
            if key not in seen:
                seen.add(key)
                unique_earthquakes.append(eq)

        return unique_earthquakes

    def save_to_csv(self, data, filename):
        """保存数据到CSV文件"""
        if data:
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"数据已保存到 {filename}")
            return df
        else:
            print("没有数据可保存")
            return None


def main():
    # 创建爬虫实例
    crawler = EarthquakeDataCrawler()

    # 设置正确的日期范围
    start_date = "2024-11-25"
    end_date = "2025-11-25"

    print(f"获取从 {start_date} 到 {end_date} 的地震数据")

    # 获取数据
    earthquake_data = crawler.get_earthquake_data(start_date, end_date, min_magnitude=3.0)

    if earthquake_data:
        # 保存数据
        df = crawler.save_to_csv(earthquake_data, 'earthquake_data.csv')

        # 显示数据统计
        if df is not None:
            print("\n=== 数据统计 ===")
            print(f"总记录数: {len(df)}")

            # 转换时间格式并统计
            df['发震时间'] = pd.to_datetime(df['发震时间'])
            print(f"时间范围: {df['发震时间'].min()} 到 {df['发震时间'].max()}")

            # 计算数据覆盖的月份数
            df['年月'] = df['发震时间'].dt.to_period('M')
            unique_months = df['年月'].nunique()
            print(f"数据覆盖月份数: {unique_months}")

            print(f"震级范围: {df['震级'].min()} - {df['震级'].max()}")
            print(f"深度范围: {df['深度'].min()} - {df['深度'].max()} km")
            print(f"位置数量: {df['位置'].nunique()}")

            # 显示前几条数据
            print("\n前5条数据预览:")
            for i, row in df.head().iterrows():
                print(f"{i + 1}. {row['发震时间']} - 震级: {row['震级']} - 位置: {row['位置']}")
    else:
        print("未能获取到数据")


if __name__ == "__main__":
    main()
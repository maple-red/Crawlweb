import pandas as pd
import numpy as np
from datetime import datetime
import re


class EarthquakeDataCleaner:
    def __init__(self, csv_file):
        try:
            self.df = pd.read_csv(csv_file, encoding='utf-8-sig')
            print(f"成功读取数据，原始数据形状: {self.df.shape}")
        except Exception as e:
            print(f"读取文件时出错: {e}")
            self.df = pd.DataFrame()

    def is_domestic_location(self, location):
        """判断是否为国内地震位置"""
        if pd.isna(location):
            return False

        # 国内省份、自治区、直辖市关键词
        domestic_keywords = [
            # 省份
            '河北', '山西', '辽宁', '吉林', '黑龙江', '江苏', '浙江', '安徽', '福建', '江西',
            '山东', '河南', '湖北', '湖南', '广东', '海南', '四川', '贵州', '云南', '陕西',
            '甘肃', '青海', '台湾',
            # 自治区
            '内蒙古', '广西', '西藏', '宁夏', '新疆',
            # 直辖市
            '北京', '天津', '上海', '重庆',
            # 特别行政区
            '香港', '澳门',
            # 常见国内地区描述
            '中国', '东海', '南海', '黄海', '渤海', '台湾海峡'
        ]

        # 检查是否包含国内关键词
        for keyword in domestic_keywords:
            if keyword in str(location):
                return True

        return False

    def extract_province(self, location):
        """从位置信息中提取省份"""
        if pd.isna(location):
            return '未知'

        location_str = str(location)

        # 省份匹配规则
        province_patterns = {
            '河北': r'河北|石家庄|唐山|秦皇岛|邯郸|邢台|保定|张家口|承德|沧州|廊坊|衡水',
            '山西': r'山西|太原|大同|阳泉|长治|晋城|朔州|晋中|运城|忻州|临汾|吕梁',
            '内蒙古': r'内蒙古|呼和浩特|包头|乌海|赤峰|通辽|鄂尔多斯|呼伦贝尔|巴彦淖尔|乌兰察布',
            '辽宁': r'辽宁|沈阳|大连|鞍山|抚顺|本溪|丹东|锦州|营口|阜新|辽阳|盘锦|铁岭|朝阳|葫芦岛',
            '吉林': r'吉林|长春|吉林市|四平|辽源|通化|白山|松原|白城|延边',
            '黑龙江': r'黑龙江|哈尔滨|齐齐哈尔|鸡西|鹤岗|双鸭山|大庆|伊春|佳木斯|七台河|牡丹江|黑河|绥化|大兴安岭',
            '江苏': r'江苏|南京|无锡|徐州|常州|苏州|南通|连云港|淮安|盐城|扬州|镇江|泰州|宿迁',
            '浙江': r'浙江|杭州|宁波|温州|嘉兴|湖州|绍兴|金华|衢州|舟山|台州|丽水',
            '安徽': r'安徽|合肥|芜湖|蚌埠|淮南|马鞍山|淮北|铜陵|安庆|黄山|滁州|阜阳|宿州|六安|亳州|池州|宣城',
            '福建': r'福建|福州|厦门|莆田|三明|泉州|漳州|南平|龙岩|宁德',
            '江西': r'江西|南昌|景德镇|萍乡|九江|新余|鹰潭|赣州|吉安|宜春|抚州|上饶',
            '山东': r'山东|济南|青岛|淄博|枣庄|东营|烟台|潍坊|济宁|泰安|威海|日照|临沂|德州|聊城|滨州|菏泽',
            '河南': r'河南|郑州|开封|洛阳|平顶山|安阳|鹤壁|新乡|焦作|濮阳|许昌|漯河|三门峡|南阳|商丘|信阳|周口|驻马店',
            '湖北': r'湖北|武汉|黄石|十堰|宜昌|襄阳|鄂州|荆门|孝感|荆州|黄冈|咸宁|随州|恩施',
            '湖南': r'湖南|长沙|株洲|湘潭|衡阳|邵阳|岳阳|常德|张家界|益阳|郴州|永州|怀化|娄底|湘西',
            '广东': r'广东|广州|韶关|深圳|珠海|汕头|佛山|江门|湛江|茂名|肇庆|惠州|梅州|汕尾|河源|阳江|清远|东莞|中山|潮州|揭阳|云浮',
            '广西': r'广西|南宁|柳州|桂林|梧州|北海|防城港|钦州|贵港|玉林|百色|贺州|河池|来宾|崇左',
            '海南': r'海南|海口|三亚|三沙|儋州',
            '四川': r'四川|成都|自贡|攀枝花|泸州|德阳|绵阳|广元|遂宁|内江|乐山|南充|眉山|宜宾|广安|达州|雅安|巴中|资阳|阿坝|甘孜|凉山',
            '贵州': r'贵州|贵阳|六盘水|遵义|安顺|毕节|铜仁|黔西南|黔东南|黔南',
            '云南': r'云南|昆明|曲靖|玉溪|保山|昭通|丽江|普洱|临沧|楚雄|红河|文山|西双版纳|大理|德宏|怒江|迪庆',
            '西藏': r'西藏|拉萨|日喀则|昌都|林芝|山南|那曲',
            '陕西': r'陕西|西安|铜川|宝鸡|咸阳|渭南|延安|汉中|榆林|安康|商洛',
            '甘肃': r'甘肃|兰州|嘉峪关|金昌|白银|天水|武威|张掖|平凉|酒泉|庆阳|定西|陇南|临夏|甘南',
            '青海': r'青海|西宁|海东|海北|黄南|海南|果洛|玉树|海西',
            '宁夏': r'宁夏|银川|石嘴山|吴忠|固原|中卫',
            '新疆': r'新疆|乌鲁木齐|克拉玛依|吐鲁番|哈密|昌吉|博尔塔拉|巴音郭楞|阿克苏|克孜勒苏|喀什|和田|伊犁|塔城|阿勒泰',
            '台湾': r'台湾|台北|高雄|基隆|台中|台南|新竹|嘉义',
            '北京': r'北京',
            '天津': r'天津',
            '上海': r'上海',
            '重庆': r'重庆',
            '香港': r'香港',
            '澳门': r'澳门'
        }

        for province, pattern in province_patterns.items():
            if re.search(pattern, location_str):
                return province

        return '其他国内地区'

    def clean_data(self):
        """清洗数据并限制为国内地震"""
        if self.df.empty:
            print("没有数据可清洗")
            return None

        print("开始数据清洗...")

        # 显示原始数据信息
        print("\n原始数据信息:")
        print(f"总记录数: {len(self.df)}")
        print("\n前3行数据:")
        print(self.df.head(3))

        # 移除完全空值的行
        self.df = self.df.dropna(how='all')
        print(f"移除全空行后: {self.df.shape}")

        # 转换日期格式
        try:
            self.df['发震时间'] = pd.to_datetime(self.df['发震时间'], errors='coerce')
            # 移除日期转换失败的行
            self.df = self.df.dropna(subset=['发震时间'])
        except Exception as e:
            print(f"日期转换错误: {e}")

        # 提取年份、月份和日期
        self.df['年份'] = self.df['发震时间'].dt.year
        self.df['月份'] = self.df['发震时间'].dt.month
        self.df['日期'] = self.df['发震时间'].dt.date
        self.df['小时'] = self.df['发震时间'].dt.hour

        # 创建震级级别
        self.df['震级级别'] = pd.cut(self.df['震级'],
                                     bins=[0, 3, 4, 5, 6, 10],
                                     labels=['3-4级', '4-5级', '5-6级', '6-7级', '7级以上'])

        # 过滤有效数据
        initial_count = len(self.df)
        self.df = self.df[
            (self.df['震级'] >= 3) &
            (self.df['震级'] <= 10) &
            (self.df['深度'] >= 0) &
            (self.df['深度'] <= 1000) &
            (self.df['经度'] >= -180) & (self.df['经度'] <= 180) &
            (self.df['纬度'] >= -90) & (self.df['纬度'] <= 90)
            ]
        print(f"数据过滤: {initial_count} -> {len(self.df)} 条记录")

        # 新增：筛选国内地震数据
        print("\n开始筛选国内地震数据...")
        domestic_mask = self.df['位置'].apply(self.is_domestic_location)
        domestic_count = domestic_mask.sum()
        international_count = len(self.df) - domestic_count

        print(f"国内地震记录: {domestic_count} 条")
        print(f"国际地震记录: {international_count} 条")

        # 只保留国内地震数据
        self.df = self.df[domestic_mask]

        # 提取省份信息
        self.df['省份'] = self.df['位置'].apply(self.extract_province)

        print(f"筛选国内数据后: {self.df.shape}")
        print(f"清洗后数据形状: {self.df.shape}")

        return self.df

    def get_summary_stats(self):
        """获取数据统计摘要"""
        if self.df.empty:
            return {}

        # 省份统计
        province_stats = self.df['省份'].value_counts()

        stats = {
            '总记录数': len(self.df),
            '时间范围': f"{self.df['发震时间'].min()} 到 {self.df['发震时间'].max()}",
            '平均震级': round(self.df['震级'].mean(), 2),
            '最大震级': self.df['震级'].max(),
            '最小震级': self.df['震级'].min(),
            '平均深度': round(self.df['深度'].mean(), 2),
            '涉及省份数量': self.df['省份'].nunique(),
            '数据覆盖月份数': self.df['月份'].nunique(),
            '地震最频繁省份': province_stats.index[0] if len(province_stats) > 0 else '无',
            '地震最频繁省份次数': province_stats.iloc[0] if len(province_stats) > 0 else 0
        }
        return stats

    def analyze_by_region(self):
        """按省份分析"""
        if self.df.empty:
            return {}

        province_stats = self.df['省份'].value_counts().head(10)
        return province_stats

    def analyze_by_province(self):
        """详细省份分析"""
        if self.df.empty:
            return {}

        province_analysis = self.df.groupby('省份').agg({
            '震级': ['count', 'mean', 'max'],
            '深度': 'mean'
        }).round(2)

        # 扁平化列名
        province_analysis.columns = ['地震次数', '平均震级', '最大震级', '平均深度']
        return province_analysis.sort_values('地震次数', ascending=False)


def main():
    # 清洗数据
    cleaner = EarthquakeDataCleaner('earthquake_data.csv')
    cleaned_data = cleaner.clean_data()

    if cleaned_data is not None:
        # 获取统计信息
        stats = cleaner.get_summary_stats()
        print("\n=== 国内地震数据统计摘要 ===")
        for key, value in stats.items():
            print(f"{key}: {value}")

        # 省份分析
        province_stats = cleaner.analyze_by_region()
        print("\n=== 地震频发省份TOP10 ===")
        print(province_stats)

        # 详细省份分析
        detailed_province_stats = cleaner.analyze_by_province()
        print("\n=== 各省份详细统计 ===")
        print(detailed_province_stats)

        # 保存清洗后的数据
        cleaned_data.to_csv('cleaned_earthquake_data.csv', index=False, encoding='utf-8-sig')
        print("\n清洗后的国内地震数据已保存为 'cleaned_earthquake_data.csv'")

        # 保存统计信息
        with open('data_statistics.txt', 'w', encoding='utf-8') as f:
            f.write("国内地震数据统计分析\n")
            f.write("====================\n\n")
            for key, value in stats.items():
                f.write(f"{key}: {value}\n")

            f.write(f"\n地震频发省份TOP10:\n{province_stats}\n")

            f.write(f"\n各省份详细统计:\n")
            f.write(detailed_province_stats.to_string())
        print("统计信息已保存为 'data_statistics.txt'")
    else:
        print("数据清洗失败")


if __name__ == "__main__":
    main()
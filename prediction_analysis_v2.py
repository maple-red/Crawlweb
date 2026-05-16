import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False


class EarthquakeRegionPredictor:
    def __init__(self, data_file):
        try:
            self.df = pd.read_csv(data_file, encoding='utf-8-sig')
            self.df['发震时间'] = pd.to_datetime(self.df['发震时间'])
            print(f"成功加载清洗后的数据: {len(self.df)} 条记录")
        except Exception as e:
            print(f"加载数据失败: {e}")
            self.df = pd.DataFrame()

    def analyze_recent_earthquakes(self, months=12):
        """分析近一年地震数据"""
        if self.df.empty:
            return None

        # 计算一年前的日期
        end_date = self.df['发震时间'].max()
        start_date = end_date - timedelta(days=months * 30)

        # 筛选近一年的数据
        recent_data = self.df[self.df['发震时间'] >= start_date].copy()

        print(f"分析时间范围: {start_date.date()} 到 {end_date.date()}")
        print(f"近一年地震记录: {len(recent_data)} 条")

        return recent_data

    def calculate_region_probabilities(self, recent_data):
        """计算各地区未来三个月发生地震的概率"""
        if recent_data.empty:
            return pd.DataFrame()

        # 按省份统计地震次数
        province_stats = recent_data['省份'].value_counts().reset_index()
        province_stats.columns = ['省份', '近一年地震次数']

        # 计算概率（基于频率统计）
        total_earthquakes = province_stats['近一年地震次数'].sum()
        province_stats['发生概率'] = (province_stats['近一年地震次数'] / total_earthquakes * 100).round(2)

        # 添加概率等级
        province_stats['风险等级'] = pd.cut(province_stats['发生概率'],
                                            bins=[0, 5, 10, 20, 100],
                                            labels=['低风险', '中风险', '高风险', '极高风险'])

        # 按概率排序
        province_stats = province_stats.sort_values('发生概率', ascending=False)

        return province_stats

    def get_region_details(self, recent_data, province_stats):
        """获取各地区详细统计信息"""
        details = {}

        for province in province_stats['省份']:
            province_data = recent_data[recent_data['省份'] == province]

            if len(province_data) > 0:
                details[province] = {
                    '近一年地震次数': len(province_data),
                    '平均震级': round(province_data['震级'].mean(), 2),
                    '最大震级': province_data['震级'].max(),
                    '平均深度': round(province_data['深度'].mean(), 1),
                    '最近地震时间': province_data['发震时间'].max().strftime('%Y-%m-%d'),
                    '主要震级范围': self.get_magnitude_range(province_data)
                }

        return details

    def get_magnitude_range(self, data):
        """获取主要震级范围"""
        if len(data) == 0:
            return "无数据"

        # 计算震级分布的众数范围
        magnitude_bins = [3, 4, 5, 6, 10]
        magnitude_labels = ['3-4级', '4-5级', '5-6级', '6级以上']

        mag_counts = pd.cut(data['震级'], bins=magnitude_bins, labels=magnitude_labels).value_counts()

        if len(mag_counts) > 0:
            return mag_counts.index[0]  # 返回最常见的震级范围
        else:
            return "3-4级"

    def create_probability_chart(self, province_stats):
        """创建地区概率排序图"""
        if province_stats.empty:
            print("没有足够数据创建图表")
            return

        # 取前15个地区
        top_provinces = province_stats.head(15)

        plt.figure(figsize=(14, 10))

        # 创建颜色映射基于风险等级
        color_map = {
            '低风险': 'lightgreen',
            '中风险': 'gold',
            '高风险': 'orange',
            '极高风险': 'red'
        }

        colors = [color_map[level] for level in top_provinces['风险等级']]

        # 创建水平条形图
        bars = plt.barh(range(len(top_provinces)),
                        top_provinces['发生概率'],
                        color=colors,
                        alpha=0.7,
                        edgecolor='black')

        # 设置图表属性
        plt.yticks(range(len(top_provinces)), top_provinces['省份'])
        plt.xlabel('未来三个月发生地震概率 (%)', fontsize=12)
        plt.title('未来三个月易发生地震地区概率排序（基于近一年数据）', fontsize=14, fontweight='bold')
        plt.gca().invert_yaxis()  # 反转Y轴使概率最高的在顶部
        plt.grid(True, alpha=0.3, axis='x')

        # 在条形上添加概率值
        for i, bar in enumerate(bars):
            width = bar.get_width()
            plt.text(width + 0.5, bar.get_y() + bar.get_height() / 2,
                     f'{width}%', ha='left', va='center', fontweight='bold')

            # 在左侧添加地震次数
            quake_count = top_provinces.iloc[i]['近一年地震次数']
            plt.text(-2, bar.get_y() + bar.get_height() / 2,
                     f'{quake_count}次', ha='right', va='center', fontsize=9)

        # 添加图例
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=color_map[level], label=level)
                           for level in color_map.keys()]
        plt.legend(handles=legend_elements, loc='lower right')

        # 添加说明文本
        plt.figtext(0.02, 0.02,
                    f"注: 左侧数字为近一年地震次数\n数据更新至: {datetime.now().strftime('%Y-%m-%d')}",
                    fontsize=9, style='italic')

        plt.tight_layout()
        plt.savefig('earthquake_region_probability.png', dpi=300, bbox_inches='tight')
        plt.show()

    def generate_prediction_report(self, province_stats, region_details):
        """生成预测报告"""
        print("\n正在生成地震预测报告...")

        report_content = f"""地震发生地区概率预测报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
预测周期: 未来三个月
数据基础: 近一年国内地震活动统计
分析方法: 基于历史地震频率的概率推断

未来三个月各地区地震发生概率排名:
================================================================================
"""
        # 添加地区排名表格
        for i, (_, row) in enumerate(province_stats.iterrows(), 1):
            province = row['省份']
            probability = row['发生概率']
            quake_count = row['近一年地震次数']
            risk_level = row['风险等级']

            details = region_details.get(province, {})
            avg_magnitude = details.get('平均震级', 'N/A')
            max_magnitude = details.get('最大震级', 'N/A')
            last_quake = details.get('最近地震时间', 'N/A')
            mag_range = details.get('主要震级范围', 'N/A')

            report_content += f"{i:2d}. {province:<8} | 概率: {probability:>5}% | 近一年: {quake_count:>3}次 | 风险: {risk_level}\n"
            report_content += f"     平均震级: {avg_magnitude} | 最大震级: {max_magnitude} | 主要震级: {mag_range} | 最近地震: {last_quake}\n"
            report_content += "     " + "-" * 70 + "\n"

        # 添加分析总结
        report_content += f"""
分析总结:
==========

1. 高风险地区 ({province_stats[province_stats['风险等级'] == '极高风险'].shape[0]}个):
   {', '.join(province_stats[province_stats['风险等级'] == '极高风险']['省份'].head().tolist())}

2. 主要特征:
   - 基于近一年地震活动频率统计
   - 考虑了各地区的地震活动模式
   - 概率计算基于历史发生频率

3. 使用建议:
   - 高风险地区应加强监测和防范
   - 中风险地区保持常规监测
   - 低风险地区进行基础监测

4. 注意事项:
   - 本预测基于历史统计规律，仅供参考
   - 实际地震发生受多种复杂因素影响
   - 建议结合其他监测手段和专家意见

数据统计:
- 分析地区总数: {len(province_stats)} 个
- 近一年总地震数: {province_stats['近一年地震次数'].sum()} 次
- 平均概率: {province_stats['发生概率'].mean():.2f}%
- 最高概率: {province_stats['发生概率'].max():.2f}%
- 最低概率: {province_stats['发生概率'].min():.2f}%

注: 地震预测是世界性难题，本报告基于历史数据进行概率推断，仅供参考。
"""

        # 保存报告
        with open('earthquake_region_prediction.txt', 'w', encoding='utf-8') as f:
            f.write(report_content)

        print("预测报告已生成: earthquake_region_prediction.txt")

    def create_prediction_analysis(self):
        """创建完整的预测分析"""
        if self.df.empty:
            print("没有数据可分析")
            return

        print("开始地震地区概率预测分析...")

        # 分析近一年数据
        recent_data = self.analyze_recent_earthquakes(months=12)

        if recent_data is None or len(recent_data) == 0:
            print("近一年无地震数据，无法进行分析")
            return

        # 计算地区概率
        province_stats = self.calculate_region_probabilities(recent_data)

        if province_stats.empty:
            print("无法计算地区概率")
            return

        # 获取地区详细信息
        region_details = self.get_region_details(recent_data, province_stats)

        # 创建概率图表
        print("生成地区概率排序图...")
        self.create_probability_chart(province_stats)

        # 生成预测报告
        print("生成预测报告...")
        self.generate_prediction_report(province_stats, region_details)

        # 显示简要结果
        print(f"\n=== 预测分析完成 ===")
        print(f"分析地区数量: {len(province_stats)}")
        print(f"最高概率地区: {province_stats.iloc[0]['省份']} ({province_stats.iloc[0]['发生概率']}%)")
        print(f"生成文件:")
        print(f"- earthquake_region_probability.png (地区概率图)")
        print(f"- earthquake_region_prediction.txt (详细预测报告)")


def main():
    # 创建预测分析
    predictor = EarthquakeRegionPredictor('cleaned_earthquake_data.csv')
    predictor.create_prediction_analysis()


if __name__ == "__main__":
    main()
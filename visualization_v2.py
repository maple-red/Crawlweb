import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import warnings

warnings.filterwarnings('ignore')

# 设置中文字体和图形样式
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False


class EarthquakeVisualizer:
    def __init__(self, data_file):
        try:
            self.df = pd.read_csv(data_file, encoding='utf-8-sig')
            self.df['发震时间'] = pd.to_datetime(self.df['发震时间'])
            print(f"成功加载数据: {len(self.df)} 条记录")
        except Exception as e:
            print(f"加载数据失败: {e}")
            self.df = pd.DataFrame()

    def filter_china_earthquakes(self):
        """筛选国内地震数据"""
        # 定义中国相关的关键词
        china_keywords = [
            '中国', '新疆', '四川', '云南', '西藏', '青海', '甘肃', '宁夏',
            '内蒙古', '陕西', '山西', '河北', '北京', '天津', '辽宁', '吉林',
            '黑龙江', '山东', '江苏', '上海', '浙江', '安徽', '福建', '江西',
            '河南', '湖北', '湖南', '广东', '广西', '海南', '重庆', '贵州'
        ]

        # 筛选包含中国关键词的地震记录
        china_mask = self.df['位置'].str.contains('|'.join(china_keywords), na=False)
        china_earthquakes = self.df[china_mask].copy()

        print(f"国内地震记录: {len(china_earthquakes)} 条")
        return china_earthquakes

    def create_monthly_statistics(self, china_df):
        """创建月度地震次数统计图"""
        plt.figure(figsize=(12, 6))

        # 按月份统计地震次数
        monthly_counts = china_df['月份'].value_counts().sort_index()

        # 确保所有月份都有数据（1-12月）
        all_months = pd.Series(index=range(1, 13), dtype=int).fillna(0)
        monthly_counts = all_months.combine(monthly_counts, max, fill_value=0)

        # 绘制柱状图
        bars = plt.bar(monthly_counts.index, monthly_counts.values,
                       color='skyblue', edgecolor='black', alpha=0.7)

        # 设置图表属性
        plt.xlabel('月份', fontsize=12)
        plt.ylabel('地震发生次数', fontsize=12)
        plt.title('国内月度地震次数统计', fontsize=14, fontweight='bold')
        plt.xticks(range(1, 13))
        plt.grid(True, alpha=0.3, axis='y')

        # 在柱子上显示数值
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                plt.text(bar.get_x() + bar.get_width() / 2., height,
                         f'{int(height)}', ha='center', va='bottom')

        plt.tight_layout()
        plt.savefig('monthly_earthquake_statistics.png', dpi=300, bbox_inches='tight')
        plt.show()

        return monthly_counts

    def create_magnitude_statistics(self, china_df):
        """创建震级次数统计图"""
        plt.figure(figsize=(12, 6))

        # 按震级统计次数（四舍五入到1位小数）
        china_df['震级_rounded'] = china_df['震级'].round(1)
        magnitude_counts = china_df['震级_rounded'].value_counts().sort_index()

        # 绘制柱状图
        bars = plt.bar(magnitude_counts.index, magnitude_counts.values,
                       color='lightcoral', edgecolor='black', alpha=0.7)

        # 设置图表属性
        plt.xlabel('震级', fontsize=12)
        plt.ylabel('发生次数', fontsize=12)
        plt.title('国内地震震级分布统计', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3, axis='y')

        # 在柱子上显示数值（只显示次数较多的）
        for bar in bars:
            height = bar.get_height()
            if height >= max(magnitude_counts.values) * 0.1:  # 只显示超过最大值10%的标签
                plt.text(bar.get_x() + bar.get_width() / 2., height,
                         f'{int(height)}', ha='center', va='bottom', fontsize=8)

        plt.tight_layout()
        plt.savefig('magnitude_distribution_statistics.png', dpi=300, bbox_inches='tight')
        plt.show()

        return magnitude_counts

    def create_time_period_pie_chart(self, china_df):
        """创建时间段饼状图"""
        plt.figure(figsize=(10, 8))

        # 定义时间段
        # 白天: 8:00-23:00 (8-22时)
        # 夜间: 23:00-8:00 (23-7时)
        day_mask = (china_df['小时'] >= 8) & (china_df['小时'] <= 22)
        night_mask = ~day_mask

        day_count = day_mask.sum()
        night_count = night_mask.sum()

        # 饼图数据
        sizes = [day_count, night_count]
        labels = [f'白天 (8:00-23:00)\n{day_count}次', f'夜间 (23:00-8:00)\n{night_count}次']
        colors = ['lightgreen', 'lightblue']
        explode = (0.05, 0)  # 突出显示白天部分

        # 绘制饼图
        plt.pie(sizes, explode=explode, labels=labels, colors=colors,
                autopct='%1.1f%%', shadow=True, startangle=90)
        plt.title('国内地震时间段分布', fontsize=14, fontweight='bold')

        plt.tight_layout()
        plt.savefig('time_period_distribution.png', dpi=300, bbox_inches='tight')
        plt.show()

        return day_count, night_count

    def generate_statistics_report(self, china_df, monthly_counts, magnitude_counts, day_count, night_count):
        """生成统计分析报告"""
        print("正在生成统计分析报告...")

        # 基本统计信息
        total_earthquakes = len(china_df)
        time_range = f"{china_df['发震时间'].min().strftime('%Y-%m-%d')} 到 {china_df['发震时间'].max().strftime('%Y-%m-%d')}"
        avg_magnitude = china_df['震级'].mean()
        max_magnitude = china_df['震级'].max()
        min_magnitude = china_df['震级'].min()
        avg_depth = china_df['深度'].mean()

        # 月度统计
        max_month = monthly_counts.idxmax()
        max_month_count = monthly_counts.max()
        min_month = monthly_counts.idxmin()
        min_month_count = monthly_counts.min()

        # 震级统计
        common_magnitude = magnitude_counts.idxmax()
        common_magnitude_count = magnitude_counts.max()

        # 时间段统计
        day_percentage = (day_count / total_earthquakes) * 100
        night_percentage = (night_count / total_earthquakes) * 100

        # 写入报告文件
        with open('earthquake_statistics_report.txt', 'w', encoding='utf-8') as f:
            f.write("地震数据统计分析报告\n")
            f.write("=" * 50 + "\n\n")

            f.write("一、总体统计信息\n")
            f.write("-" * 30 + "\n")
            f.write(f"统计时间范围: {time_range}\n")
            f.write(f"国内地震总次数: {total_earthquakes} 次\n")
            f.write(f"平均震级: {avg_magnitude:.2f}\n")
            f.write(f"最大震级: {max_magnitude}\n")
            f.write(f"最小震级: {min_magnitude}\n")
            f.write(f"平均深度: {avg_depth:.1f} km\n\n")

            f.write("二、月度分布统计\n")
            f.write("-" * 30 + "\n")
            for month in range(1, 13):
                count = monthly_counts[month]
                f.write(f"{month}月: {count} 次\n")
            f.write(f"\n地震最频繁月份: {max_month}月 ({max_month_count}次)\n")
            f.write(f"地震最少月份: {min_month}月 ({min_month_count}次)\n\n")

            f.write("三、震级分布统计\n")
            f.write("-" * 30 + "\n")
            # 显示前10个最常见的震级
            top_magnitudes = magnitude_counts.head(10)
            for mag, count in top_magnitudes.items():
                f.write(f"震级 {mag}: {count} 次\n")
            f.write(f"\n最常见震级: {common_magnitude}级 ({common_magnitude_count}次)\n\n")

            f.write("四、时间段分布统计\n")
            f.write("-" * 30 + "\n")
            f.write(f"白天 (8:00-23:00): {day_count} 次 ({day_percentage:.1f}%)\n")
            f.write(f"夜间 (23:00-8:00): {night_count} 次 ({night_percentage:.1f}%)\n\n")

            f.write("五、数据说明\n")
            f.write("-" * 30 + "\n")
            f.write("1. 数据来源: 中国地震台网中心\n")
            f.write("2. 统计范围: 中国大陆及周边地区\n")
            f.write("3. 时间范围: 最近一年的地震数据\n")
            f.write("4. 震级范围: 3.0级以上地震\n")

        print("统计分析报告已生成: earthquake_statistics_report.txt")

    def create_analysis(self):
        """创建完整的分析"""
        if self.df.empty:
            print("没有数据可分析")
            return

        print("开始创建地震数据分析...")

        # 筛选国内地震数据
        china_df = self.filter_china_earthquakes()

        if len(china_df) == 0:
            print("未找到国内地震数据，无法进行分析")
            return

        # 创建三个统计图表
        print("1. 生成月度地震次数统计图...")
        monthly_counts = self.create_monthly_statistics(china_df)

        print("2. 生成震级分布统计图...")
        magnitude_counts = self.create_magnitude_statistics(china_df)

        print("3. 生成时间段分布饼图...")
        day_count, night_count = self.create_time_period_pie_chart(china_df)

        # 生成统计分析报告
        print("4. 生成统计分析报告...")
        self.generate_statistics_report(china_df, monthly_counts, magnitude_counts, day_count, night_count)

        print("\n所有分析已完成！")
        print("生成的文件:")
        print("- monthly_earthquake_statistics.png (月度统计图)")
        print("- magnitude_distribution_statistics.png (震级分布图)")
        print("- time_period_distribution.png (时间段饼图)")
        print("- earthquake_statistics_report.txt (统计分析报告)")


def main():
    # 创建可视化分析
    visualizer = EarthquakeVisualizer('cleaned_earthquake_data.csv')

    if not visualizer.df.empty:
        visualizer.create_analysis()

        # 显示基本信息
        print("\n=== 数据基本信息 ===")
        print(f"总记录数: {len(visualizer.df)}")
        print(f"时间范围: {visualizer.df['发震时间'].min()} 到 {visualizer.df['发震时间'].max()}")
        print(f"震级范围: {visualizer.df['震级'].min()} - {visualizer.df['震级'].max()}")
    else:
        print("无法创建分析，数据为空")


if __name__ == "__main__":
    main()
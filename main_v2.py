import os
import time
import sys

# 首先检查依赖
try:
    from check_dependencies import check_and_install_dependencies

    if not check_and_install_dependencies():
        print("依赖库安装失败，请手动安装所需库")
        sys.exit(1)
except Exception as e:
    print(f"依赖检查失败: {e}")
    sys.exit(1)


def main():
    print("=== 地震数据可视化分析系统 v2 ===")
    print("基于HTML页面解析的完整解决方案\n")

    # 步骤1: 爬取数据
    print("步骤1: 爬取地震数据...")
    try:
        from earthquake_crawler_v2 import main as crawl_main
        crawl_main()
        print("✓ 数据爬取完成！\n")
    except Exception as e:
        print(f"✗ 数据爬取失败: {e}")
        return

    time.sleep(2)

    # 检查数据文件是否存在
    if not os.path.exists('earthquake_data.csv'):
        print("✗ 未找到数据文件，程序终止")
        return

    # 步骤2: 清洗数据
    print("步骤2: 数据清洗和处理...")
    try:
        from data_cleaner_v2 import main as clean_main
        clean_main()
        print("✓ 数据清洗完成！\n")
    except Exception as e:
        print(f"✗ 数据清洗失败: {e}")
        return

    time.sleep(2)

    # 检查清洗后的数据文件是否存在
    if not os.path.exists('cleaned_earthquake_data.csv'):
        print("✗ 未找到清洗后的数据文件，程序终止")
        return

    # 步骤3: 可视化分析
    print("步骤3: 生成可视化图表...")
    try:
        from visualization_v2 import main as vis_main
        vis_main()
        print("✓ 可视化分析完成！\n")
    except Exception as e:
        print(f"✗ 可视化分析失败: {e}")
        return

    time.sleep(2)

    # 步骤4: 高级预测分析
    print("步骤4: 进行高级趋势预测...")
    try:
        from prediction_analysis_v2 import main as advanced_pred_main
        advanced_pred_main()
        print("✓ 高级预测分析完成！\n")
    except Exception as e:
        print(f"⚠ 高级预测分析跳过: {e}")
        # 尝试使用基础预测作为备选
        try:
            from prediction_analysis_v2 import main as pred_main
            pred_main()
            print("✓ 基础预测分析完成！\n")
        except Exception as e:
            print(f"✗ 所有预测分析失败: {e}")

    print("=== 所有任务已完成 ===")
    print("\n生成的文件清单:")
    print("📊 数据文件:")
    print("   - earthquake_data.csv (原始数据)")
    print("   - cleaned_earthquake_data.csv (清洗后数据)")
    if os.path.exists('data_statistics.txt'):
        print("   - data_statistics.txt (数据统计)")

    print("\n📈 分析图表:")
    chart_files = [
        'earthquake_summary_dashboard.png',
        'earthquake_time_series.png',
        'earthquake_regional_analysis.png',
        'earthquake_depth_analysis.png',
        'earthquake_monthly_heatmap.png'
    ]
    for chart in chart_files:
        if os.path.exists(chart):
            print(f"   - {chart}")

    if os.path.exists('earthquake_prediction_analysis.png'):
        print("   - earthquake_prediction_analysis.png (预测分析)")

    print("\n📋 报告文件:")
    if os.path.exists('prediction_report.txt'):
        print("   - prediction_report.txt (预测报告)")

    print("\n🎯 项目特点:")
    print("   ✓ 直接从HTML页面解析数据")
    print("   ✓ 自动处理分页")
    print("   ✓ 完整的数据清洗流程")
    print("   ✓ 丰富的可视化图表")
    print("   ✓ 趋势预测分析")
    print("   ✓ 详细的统计报告")


if __name__ == "__main__":
    main()
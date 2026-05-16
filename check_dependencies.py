def check_and_install_dependencies():
    """检查并安装必要的依赖"""
    required_libraries = {
        'requests': 'requests',
        'pandas': 'pandas',
        'matplotlib': 'matplotlib',
        'seaborn': 'seaborn',
        'beautifulsoup4': 'beautifulsoup4',
        'scikit-learn': 'sklearn'
    }

    missing_libraries = []

    print("正在检查依赖库...")

    for pip_name, import_name in required_libraries.items():
        try:
            __import__(import_name)
            print(f"✓ {pip_name} 已安装")
        except ImportError:
            print(f"✗ {pip_name} 未安装")
            missing_libraries.append(pip_name)

    if missing_libraries:
        print(f"\n缺少以下库: {', '.join(missing_libraries)}")
        print("正在尝试自动安装...")

        import subprocess
        import sys

        for lib in missing_libraries:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
                print(f"✓ 成功安装 {lib}")
            except subprocess.CalledProcessError:
                print(f"✗ 安装 {lib} 失败，请手动运行: pip install {lib}")
                return False

        print("\n所有依赖库安装完成！")
    else:
        print("\n所有依赖库都已安装！")

    return True


if __name__ == "__main__":
    check_and_install_dependencies()
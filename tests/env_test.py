import importlib
required_packages = {
    'flask': 'Flask Web 框架',
    'pymysql': 'MySQL数据库驱动',
    'jinja2': '模板引擎',
    'werkzeug': 'WSGI工具库',
    'dotenv': '环境变量加载'
}

print("开始检查 Python 环境依赖...\n")

missing = []

for package, description in required_packages.items():
    try:
        importlib.import_module(package)
        print(f"[✔] {package} - {description}")
    except ImportError:
        print(f"[✘] {package} 缺失！({description})")
        missing.append(package)

if not missing:
    print("\n 所有依赖已正确安装，环境配置正常。")
else:
    print("\n 以下依赖未安装，请使用 pip 安装：")
    for pkg in missing:
        print(f"   pip install {pkg}")

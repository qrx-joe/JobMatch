#!/usr/bin/env python3
"""
JobMatch 快速启动脚本

一键启动后端服务和运行演示
"""

import subprocess
import sys
import os
import time


def print_step(step, message):
    """打印步骤"""
    print(f"\n{'='*60}")
    print(f"  步骤{step}: {message}")
    print('='*60)


def check_dependencies():
    """检查依赖"""
    print_step(1, "检查依赖")

    # 检查Python
    try:
        result = subprocess.run(['python', '--version'], capture_output=True, text=True)
        print(f"Python版本: {result.stdout.strip()}")
    except:
        print("ERROR: 未找到Python")
        return False

    # 检查uv
    try:
        result = subprocess.run(['uv', '--version'], capture_output=True, text=True)
        print(f"uv版本: {result.stdout.strip()}")
    except:
        print("ERROR: 未安装uv")
        print("请运行: pip install uv")
        return False

    # 检查依赖安装
    try:
        result = subprocess.run(['uv', 'pip', 'show', 'fastapi'], capture_output=True, text=True)
        if 'Name: fastapi' not in result.stdout:
            print("安装依赖...")
            subprocess.run(['uv', 'sync'], check=True)
    except:
        print("安装依赖...")
        subprocess.run(['uv', 'sync'], check=True)

    print("依赖检查完成")
    return True


def run_demo():
    """运行演示"""
    print_step(2, "运行演示脚本")

    demo_script = os.path.join(os.path.dirname(__file__), 'demo_full_pipeline.py')
    subprocess.run(['uv', 'run', 'python', demo_script, '--profile', '经济学,本科,女,25,山西,中共党员'])


def start_backend():
    """启动后端服务"""
    print_step(3, "启动后端服务")

    print("启动FastAPI服务...")
    print("API文档地址: http://localhost:8000/docs")
    print("按 Ctrl+C 停止服务\n")

    backend_script = os.path.join(os.path.dirname(__file__), 'server', 'app.py')
    subprocess.run(['uv', 'run', 'uvicorn', 'server.app:app', '--host', '0.0.0.0', '--port', '8000', '--reload'])


def main():
    """主函数"""
    print("\n" + "="*60)
    print("  JobMatch 智能选岗平台 - 快速启动")
    print("="*60)

    # 检查依赖
    if not check_dependencies():
        return

    # 运行演示或启动服务
    print("\n请选择操作:")
    print("  1. 运行演示脚本（不启动服务）")
    print("  2. 启动后端服务")
    print("  3. 演示 + 启动服务")

    choice = input("\n请输入选择 (1/2/3): ").strip()

    if choice == '1':
        run_demo()
    elif choice == '2':
        start_backend()
    elif choice == '3':
        run_demo()
        print("\n" + "="*60)
        print("  演示完成，准备启动服务...")
        print("="*60)
        time.sleep(2)
        start_backend()
    else:
        print("无效选择")


if __name__ == "__main__":
    main()
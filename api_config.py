#!/usr/bin/env python3
"""
API配置管理器
处理Claude API的配置和密钥管理
"""

import os
from pathlib import Path


class APIConfig:
    """API配置管理"""

    def __init__(self):
        self.env_file = Path(".env")
        self._load_env()

    def _load_env(self):
        """加载.env文件"""
        if self.env_file.exists():
            with open(self.env_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ.setdefault(key, value)

    @property
    def anthropic_api_key(self) -> str | None:
        """获取Anthropic API Key"""
        return os.getenv("ANTHROPIC_API_KEY")

    @property
    def is_configured(self) -> bool:
        """检查API是否已配置"""
        return bool(self.anthropic_api_key and self.anthropic_api_key.startswith("sk-"))

    def setup_api_key(self, api_key: str) -> bool:
        """
        设置API Key到.env文件

        Args:
            api_key: Anthropic API Key

        Returns:
            bool: 是否设置成功
        """
        try:
            # 验证key格式
            if not api_key.startswith("sk-"):
                print("[错误] API Key格式不正确，应以'sk-'开头")
                return False

            # 读取现有内容
            lines = []
            if self.env_file.exists():
                with open(self.env_file, encoding="utf-8") as f:
                    lines = f.readlines()

            # 更新或添加API key
            key_found = False
            new_lines = []
            for line in lines:
                if line.startswith("ANTHROPIC_API_KEY="):
                    new_lines.append(f"ANTHROPIC_API_KEY={api_key}\n")
                    key_found = True
                else:
                    new_lines.append(line)

            if not key_found:
                new_lines.append(f"ANTHROPIC_API_KEY={api_key}\n")

            # 写回文件
            with open(self.env_file, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

            # 更新环境变量
            os.environ["ANTHROPIC_API_KEY"] = api_key

            print(f"[OK] API Key已保存到 {self.env_file.absolute()}")
            print(f"[OK] Key前缀: {api_key[:12]}...")
            return True

        except Exception as e:
            print(f"[错误] 保存API Key失败: {e}")
            return False

    def get_status(self) -> dict:
        """获取API配置状态"""
        key = self.anthropic_api_key
        return {
            "configured": self.is_configured,
            "key_present": bool(key),
            "key_prefix": key[:12] + "..." if key and len(key) > 12 else None,
            "env_file_exists": self.env_file.exists(),
            "env_file_path": str(self.env_file.absolute()),
        }


def interactive_setup():
    """交互式设置API Key"""
    print("=" * 80)
    print("Claude API配置")
    print("=" * 80)
    print()

    config = APIConfig()
    status = config.get_status()

    if status["configured"]:
        print("[OK] API已配置")
        print(f"   Key: {status['key_prefix']}")
        print()
        response = input("是否重新配置? (y/N): ").strip().lower()
        if response != "y":
            return

    print("请从 https://console.anthropic.com/ 获取API Key")
    print("Key格式: sk-ant-api03-...")
    print()

    api_key = input("请输入API Key: ").strip()

    if not api_key:
        print("[错误] API Key不能为空")
        return

    if config.setup_api_key(api_key):
        print()
        print("[OK] 配置成功！现在可以测试API连接")
    else:
        print()
        print("[错误] 配置失败")


if __name__ == "__main__":
    interactive_setup()

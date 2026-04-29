#!/usr/bin/env python3
"""
字符串处理工具函数
"""

import re
import unicodedata
from typing import List, Optional


def clean_text(text: str) -> str:
    """
    清理文本，去除多余空白字符

    Args:
        text: 原始文本

    Returns:
        str: 清理后的文本
    """
    if not text:
        return ""

    # 替换多种空白字符为空格
    text = re.sub(r"\s+", " ", text)
    # 去除首尾空白
    return text.strip()


def remove_special_chars(text: str, keep_spaces: bool = True) -> str:
    """
    去除特殊字符

    Args:
        text: 原始文本
        keep_spaces: 是否保留空格

    Returns:
        str: 清理后的文本
    """
    if not text:
        return ""

    if keep_spaces:
        pattern = r"[^a-zA-Z0-9一-鿿\s]"
    else:
        pattern = r"[^a-zA-Z0-9一-鿿]"

    return re.sub(pattern, "", text)


def normalize_text(text: str) -> str:
    """
    规范化文本（全角转半角等）

    Args:
        text: 原始文本

    Returns:
        str: 规范化后的文本
    """
    if not text:
        return ""

    # 全角转半角
    result = []
    for char in text:
        inside_range = 0x0021 <= ord(char) <= 0x007E
        if char == "　":  # 全角空格
            result.append(" ")
        elif inside_range:
            result.append(char)
        else:
            result.append(chr(ord(char) - 0xFEE0))
    text = "".join(result)

    return clean_text(text)


def extract_numbers(text: str) -> List[int]:
    """
    从文本中提取所有数字

    Args:
        text: 文本

    Returns:
        List[int]: 数字列表
    """
    if not text:
        return []

    numbers = re.findall(r"\d+", text)
    return [int(n) for n in numbers]


def extract_major_code(text: str) -> Optional[str]:
    """
    从文本中提取专业代码

    Args:
        text: 文本，如 "经济学类（0201）"

    Returns:
        str: 专业代码，如 "0201"，或None
    """
    if not text:
        return None

    # 匹配4位数字代码
    match = re.search(r"[（(](\d{4})[）)]", text)
    if match:
        return match.group(1)

    return None


def split_by_comma(text: str) -> List[str]:
    """
    按逗号分割（处理中文逗号和英文逗号）

    Args:
        text: 文本

    Returns:
        List[str]: 分割后的列表
    """
    if not text:
        return []

    # 先替换中文逗号为英文逗号
    text = text.replace("，", ",")
    # 按逗号分割
    parts = text.split(",")
    # 清理每项
    return [clean_text(p) for p in parts if clean_text(p)]


def truncate(text: str, max_length: int, suffix: str = "...") -> str:
    """
    截断文本

    Args:
        text: 文本
        max_length: 最大长度
        suffix: 省略号

    Returns:
        str: 截断后的文本
    """
    if not text or len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def is_valid_phone(phone: str) -> bool:
    """
    验证手机号

    Args:
        phone: 手机号

    Returns:
        bool: 是否有效
    """
    if not phone:
        return False

    # 去除非数字字符
    phone = re.sub(r"\D", "", phone)

    # 中国手机号：11位，以1开头
    if len(phone) == 11 and phone[0] == "1":
        return True

    return False


def is_valid_id_card(id_card: str) -> bool:
    """
    验证身份证号

    Args:
        id_card: 身份证号

    Returns:
        bool: 是否有效
    """
    if not id_card:
        return False

    # 去除非数字和X字符
    id_card = id_card.upper()
    id_card_clean = re.sub(r"[^0-9X]", "", id_card)

    # 18位身份证
    if len(id_card_clean) == 18:
        return True

    # 15位身份证
    if len(id_card_clean) == 15:
        return True

    return False


def mask_phone(phone: str) -> str:
    """
    脱敏手机号

    Args:
        phone: 手机号

    Returns:
        str: 脱敏后的手机号，如 "138****5678"
    """
    if not phone or len(phone) < 7:
        return phone

    # 去除非数字
    phone = re.sub(r"\D", "", phone)

    if len(phone) == 11:
        return f"{phone[:3]}****{phone[7:]}"

    return phone


def mask_id_card(id_card: str) -> str:
    """
    脱敏身份证号

    Args:
        id_card: 身份证号

    Returns:
        str: 脱敏后的身份证号，如 "110101***********1234"
    """
    if not id_card or len(id_card) < 10:
        return id_card

    id_card = id_card.upper()
    return f"{id_card[:6]}**********{id_card[-4:]}"


# 导出
__all__ = [
    "clean_text",
    "remove_special_chars",
    "normalize_text",
    "extract_numbers",
    "extract_major_code",
    "split_by_comma",
    "truncate",
    "is_valid_phone",
    "is_valid_id_card",
    "mask_phone",
    "mask_id_card",
]
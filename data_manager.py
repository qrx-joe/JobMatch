#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据管理器 - 支持用户自定义专业和关联关系
提供CRUD操作和数据持久化
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class CustomMajor:
    """用户自定义专业"""
    id: str
    name: str
    category: str  # 所属大类
    subcategory: str  # 专业类
    description: str = ""
    related_majors: List[str] = None  # 关联专业ID列表
    created_at: str = ""
    updated_at: str = ""
    source: str = "custom"  # custom | builtin

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
        if self.related_majors is None:
            self.related_majors = []


@dataclass
class CustomRelation:
    """用户自定义关联关系"""
    id: str
    from_major: str
    to_major: str
    relation_type: str  # belongs_to | related | similar
    description: str = ""
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class DataManager:
    """数据管理器 - 管理用户自定义数据"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        self.majors_file = self.data_dir / "custom_majors.json"
        self.relations_file = self.data_dir / "custom_relations.json"
        self.history_file = self.data_dir / "edit_history.json"

        self.majors: Dict[str, CustomMajor] = {}
        self.relations: Dict[str, CustomRelation] = {}
        self.history: List[Dict] = []

        self._load_data()

    def _load_data(self):
        """加载所有数据"""
        # 加载专业
        if self.majors_file.exists():
            try:
                with open(self.majors_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for mid, mdata in data.items():
                        self.majors[mid] = CustomMajor(**mdata)
            except Exception as e:
                print(f"[警告] 加载自定义专业失败: {e}")

        # 加载关系
        if self.relations_file.exists():
            try:
                with open(self.relations_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for rid, rdata in data.items():
                        self.relations[rid] = CustomRelation(**rdata)
            except Exception as e:
                print(f"[警告] 加载自定义关系失败: {e}")

        # 加载历史
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except:
                pass

    def _save_data(self):
        """保存所有数据"""
        # 保存专业
        majors_data = {mid: asdict(m) for mid, m in self.majors.items()}
        with open(self.majors_file, 'w', encoding='utf-8') as f:
            json.dump(majors_data, f, ensure_ascii=False, indent=2)

        # 保存关系
        relations_data = {rid: asdict(r) for rid, r in self.relations.items()}
        with open(self.relations_file, 'w', encoding='utf-8') as f:
            json.dump(relations_data, f, ensure_ascii=False, indent=2)

        # 保存历史
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history[-100:], f, ensure_ascii=False, indent=2)  # 只保留最近100条

    def _add_history(self, action: str, item_type: str, item_id: str, details: dict):
        """添加编辑历史"""
        self.history.append({
            "action": action,
            "type": item_type,
            "id": item_id,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    # ========== 专业管理 ==========

    def add_major(self, name: str, category: str, subcategory: str,
                  description: str = "", related_majors: List[str] = None) -> CustomMajor:
        """
        添加新专业

        Args:
            name: 专业名称
            category: 所属大类（如"经济学"）
            subcategory: 专业类（如"经济学类"）
            description: 专业描述
            related_majors: 关联专业ID列表

        Returns:
            CustomMajor: 新创建的专业对象
        """
        # 生成ID
        mid = f"custom_{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # 检查是否已存在
        for m in self.majors.values():
            if m.name == name:
                raise ValueError(f"专业 '{name}' 已存在")

        major = CustomMajor(
            id=mid,
            name=name,
            category=category,
            subcategory=subcategory,
            description=description,
            related_majors=related_majors or []
        )

        self.majors[mid] = major
        self._add_history("add", "major", mid, {"name": name, "category": category})
        self._save_data()

        return major

    def update_major(self, major_id: str, **kwargs) -> CustomMajor:
        """更新专业信息"""
        if major_id not in self.majors:
            raise ValueError(f"专业 '{major_id}' 不存在")

        major = self.majors[major_id]

        allowed_fields = ['name', 'category', 'subcategory', 'description', 'related_majors']
        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(major, key, value)

        major.updated_at = datetime.now().isoformat()

        self._add_history("update", "major", major_id, kwargs)
        self._save_data()

        return major

    def delete_major(self, major_id: str) -> bool:
        """删除专业"""
        if major_id not in self.majors:
            return False

        major = self.majors.pop(major_id)
        self._add_history("delete", "major", major_id, {"name": major.name})
        self._save_data()

        return True

    def get_major(self, major_id: str) -> Optional[CustomMajor]:
        """获取专业"""
        return self.majors.get(major_id)

    def find_major_by_name(self, name: str) -> Optional[CustomMajor]:
        """通过名称查找专业"""
        for m in self.majors.values():
            if m.name == name:
                return m
        return None

    def list_majors(self, category: str = None) -> List[CustomMajor]:
        """列出所有专业"""
        majors = list(self.majors.values())
        if category:
            majors = [m for m in majors if m.category == category]
        return sorted(majors, key=lambda m: m.created_at, reverse=True)

    # ========== 关系管理 ==========

    def add_relation(self, from_major: str, to_major: str,
                     relation_type: str = "related", description: str = "") -> CustomRelation:
        """
        添加专业关联关系

        Args:
            from_major: 源专业ID
            to_major: 目标专业ID
            relation_type: 关系类型 (belongs_to/related/similar)
            description: 关系描述
        """
        rid = f"rel_{from_major}_{to_major}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        relation = CustomRelation(
            id=rid,
            from_major=from_major,
            to_major=to_major,
            relation_type=relation_type,
            description=description
        )

        self.relations[rid] = relation

        # 同时更新专业的related_majors列表
        if from_major in self.majors and to_major not in self.majors[from_major].related_majors:
            self.majors[from_major].related_majors.append(to_major)

        self._add_history("add", "relation", rid,
                         {"from": from_major, "to": to_major, "type": relation_type})
        self._save_data()

        return relation

    def delete_relation(self, relation_id: str) -> bool:
        """删除关系"""
        if relation_id not in self.relations:
            return False

        relation = self.relations.pop(relation_id)
        self._add_history("delete", "relation", relation_id,
                         {"from": relation.from_major, "to": relation.to_major})
        self._save_data()

        return True

    def list_relations(self, major_id: str = None) -> List[CustomRelation]:
        """列出关系"""
        relations = list(self.relations.values())
        if major_id:
            relations = [r for r in relations
                        if r.from_major == major_id or r.to_major == major_id]
        return relations

    # ========== 数据导入导出 ==========

    def export_to_json(self, filepath: str):
        """导出所有数据到JSON"""
        data = {
            "export_time": datetime.now().isoformat(),
            "majors": {mid: asdict(m) for mid, m in self.majors.items()},
            "relations": {rid: asdict(r) for rid, r in self.relations.items()},
            "history": self.history[-50:]  # 最近50条历史
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return filepath

    def import_from_json(self, filepath: str, merge: bool = True):
        """从JSON导入数据"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not merge:
            self.majors.clear()
            self.relations.clear()

        # 导入专业
        for mid, mdata in data.get("majors", {}).items():
            if mid not in self.majors:
                self.majors[mid] = CustomMajor(**mdata)

        # 导入关系
        for rid, rdata in data.get("relations", {}).items():
            if rid not in self.relations:
                self.relations[rid] = CustomRelation(**rdata)

        self._save_data()
        return len(data.get("majors", {})), len(data.get("relations", {}))

    def get_statistics(self) -> dict:
        """获取数据统计"""
        return {
            "majors": {
                "total": len(self.majors),
                "by_category": self._count_by_category()
            },
            "relations": {
                "total": len(self.relations)
            },
            "history": {
                "total": len(self.history),
                "recent": self.history[-5:] if self.history else []
            }
        }

    def _count_by_category(self) -> Dict[str, int]:
        """按类别统计专业数量"""
        counts = {}
        for m in self.majors.values():
            counts[m.category] = counts.get(m.category, 0) + 1
        return counts

    def get_edit_history(self, limit: int = 20) -> List[Dict]:
        """获取编辑历史"""
        return self.history[-limit:][::-1]  # 倒序返回

    def undo_last_action(self) -> bool:
        """撤销最后一次操作"""
        if not self.history:
            return False

        last_action = self.history.pop()
        action_type = last_action["action"]
        item_type = last_action["type"]
        item_id = last_action["id"]

        try:
            if action_type == "add":
                if item_type == "major":
                    self.majors.pop(item_id, None)
                elif item_type == "relation":
                    self.relations.pop(item_id, None)

            elif action_type == "delete":
                # 恢复删除需要保存完整数据，这里简化处理
                pass

            self._save_data()
            return True

        except Exception as e:
            print(f"[错误] 撤销失败: {e}")
            return False


def interactive_manager():
    """交互式数据管理"""
    manager = DataManager()

    while True:
        print("\n" + "=" * 80)
        print("数据管理系统")
        print("=" * 80)

        stats = manager.get_statistics()
        print(f"\n当前数据: {stats['majors']['total']}个专业, {stats['relations']['total']}个关系")

        print("\n操作选项:")
        print("  1. 添加新专业")
        print("  2. 查看所有专业")
        print("  3. 删除专业")
        print("  4. 添加专业关系")
        print("  5. 导出数据")
        print("  6. 导入数据")
        print("  7. 查看编辑历史")
        print("  8. 撤销操作")
        print("  0. 退出")

        choice = input("\n请选择操作: ").strip()

        if choice == "1":
            print("\n--- 添加新专业 ---")
            name = input("专业名称: ").strip()
            if not name:
                print("[错误] 专业名称不能为空")
                continue

            category = input("所属大类 (如: 经济学): ").strip()
            subcategory = input("专业类 (如: 经济学类): ").strip()
            description = input("专业描述: ").strip()

            try:
                major = manager.add_major(name, category, subcategory, description)
                print(f"[OK] 专业 '{name}' 已添加 (ID: {major.id})")
            except ValueError as e:
                print(f"[错误] {e}")

        elif choice == "2":
            print("\n--- 专业列表 ---")
            majors = manager.list_majors()
            if not majors:
                print("暂无自定义专业")
            else:
                for m in majors:
                    print(f"  • {m.name} ({m.category} - {m.subcategory})")

        elif choice == "3":
            print("\n--- 删除专业 ---")
            name = input("要删除的专业名称: ").strip()
            major = manager.find_major_by_name(name)
            if major:
                confirm = input(f"确认删除 '{name}'? (y/N): ").strip().lower()
                if confirm == 'y':
                    manager.delete_major(major.id)
                    print(f"[OK] 已删除 '{name}'")
            else:
                print(f"[错误] 未找到专业 '{name}'")

        elif choice == "4":
            print("\n--- 添加专业关系 ---")
            from_name = input("源专业名称: ").strip()
            to_name = input("目标专业名称: ").strip()

            from_major = manager.find_major_by_name(from_name)
            to_major = manager.find_major_by_name(to_name)

            if from_major and to_major:
                manager.add_relation(from_major.id, to_major.id)
                print(f"[OK] 已添加关系: {from_name} -> {to_name}")
            else:
                print("[错误] 专业未找到，请先添加专业")

        elif choice == "5":
            filepath = input("导出文件路径 (默认: data/export.json): ").strip() or "data/export.json"
            manager.export_to_json(filepath)
            print(f"[OK] 数据已导出到 {filepath}")

        elif choice == "6":
            filepath = input("导入文件路径: ").strip()
            if os.path.exists(filepath):
                m_count, r_count = manager.import_from_json(filepath)
                print(f"[OK] 已导入 {m_count}个专业, {r_count}个关系")
            else:
                print("[错误] 文件不存在")

        elif choice == "7":
            print("\n--- 编辑历史 ---")
            history = manager.get_edit_history(10)
            for h in history:
                print(f"  [{h['timestamp'][:10]}] {h['action']} {h['type']}: {h['id']}")

        elif choice == "8":
            if manager.undo_last_action():
                print("[OK] 已撤销")
            else:
                print("[错误] 撤销失败")

        elif choice == "0":
            print("[OK] 再见！")
            break

        else:
            print("[错误] 无效选项")


if __name__ == "__main__":
    interactive_manager()

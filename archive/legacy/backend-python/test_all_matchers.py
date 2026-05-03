#!/usr/bin/env python3
"""综合验证测试 - 所有新增筛选条件"""
import sys
import tempfile
sys.stdout.reconfigure(encoding='utf-8')

import yaml
from job_matcher_v2 import Job, MatchLevel, JobMatcherV2

print("=" * 60)
print("综合验证测试 - JobMatcherV2 集成测试")
print("=" * 60)

config = {
    "profile": {
        "专业": "经济学", "学历": "本科", "学位": "学士",
        "性别": "女", "户籍": "吕梁市",
        "是否应届": False, "政治面貌": "群众",
        "相关资格": [], "工作年限": 0,
        "英语等级": "CET4", "计算机等级": "二级",
        "身体状况": "", "是否退伍军人": False,
        "是否西部计划志愿者": False, "是否基层服务项目人员": False,
        "院校层次": "普通本科",
    },
    "preference": {"意向城市": ["吕梁市", "太原市"], "服务类别": []},
    "rules": {
        "专业匹配模式": "智能", "学历匹配": "向下兼容",
        "户籍匹配": {"模式": "loose", "优先显示户籍地": True},
        "性别限制": {"模式": "strict"},
        "相关资格匹配": {"模式": "loose"},
        "应届生匹配": {"模式": "loose"},
        "政治面貌匹配": {"模式": "loose"},
    },
    "filter": {"最大竞争比": 100, "最低招募人数": 1, "排除关键词": []},
    "output": {"排序方式": "匹配度降序", "输出模式": "全量标记"},
}

with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
    yaml.dump(config, f, allow_unicode=True)
    config_path = f.name

matcher = JobMatcherV2(config_path)
print(f"用户配置：{matcher.profile.major} | {matcher.profile.education} | {matcher.profile.gender}")
print(f"英语：{matcher.profile.english_level} | 计算机：{matcher.profile.computer_level} | 院校：{matcher.profile.school_level}")
print(f"退伍军人：{matcher.profile.is_veteran} | 西部计划：{matcher.profile.is_west_plan_participant}")

# 创建测试岗位（使用正确的字段）
test_jobs = [
    ("正常岗位", Job(sheet_name="太原市", major="经济学", education="本科及以上", degree="学士")),
    ("退伍军人专项", Job(sheet_name="太原市", major="经济学", education="本科及以上", degree="学士",
                        is_targeted_recruit=True, targeted_type="限退伍军人")),
    ("985院校要求", Job(sheet_name="太原市", major="经济学", education="本科及以上", degree="学士",
                       school_requirement="985")),
    ("英语六级要求", Job(sheet_name="太原市", major="经济学", education="本科及以上", degree="学士",
                        english_requirement="英语六级")),
    ("计算机三级要求", Job(sheet_name="太原市", major="经济学", education="本科及以上", degree="学士",
                          computer_requirement="计算机三级")),
    ("色盲限制", Job(sheet_name="太原市", major="经济学", education="本科及以上", degree="学士",
                    physical_requirement="无色盲")),
    ("西部计划专项", Job(sheet_name="太原市", major="经济学", education="本科及以上", degree="学士",
                         is_targeted_recruit=True, targeted_type="限西部计划志愿者")),
]

print("\n测试结果：")
print("-" * 60)
for label, job in test_jobs:
    result = matcher.match(job)
    reasons = "; ".join(result.mismatch_reasons) if result.mismatch_reasons else "全部符合"
    marker = "✓" if result.match_level != MatchLevel.MISMATCH else "✗"
    print(f"{marker} {label:12s} → {result.match_level.value:8s} | 分数:{result.match_score:3d} | {reasons}")

print("\n" + "=" * 60)
print("验证完成！")
print("=" * 60)

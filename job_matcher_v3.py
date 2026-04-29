#!/usr/bin/env python3
"""
岗位筛选匹配引擎 V3 - 集成语义匹配
支持学历、户籍、工作年限的语义理解
"""

# 导入语义匹配器
from job_matcher_v2 import Job, JobMatcherV2, MatchLevel
from semantic_matcher import EducationMatcher, ExperienceMatcher, HouseholdMatcher, SemanticMatcher


class JobMatcherV3(JobMatcherV2):
    """
    V3版岗位匹配引擎 - 增强语义匹配
    """

    def __init__(self, config_path: str = "config_full.yaml"):
        super().__init__(config_path)
        # 初始化语义匹配器
        self.semantic_matcher = None
        self._init_semantic_matcher()

    def _init_semantic_matcher(self):
        """初始化语义匹配器"""
        profile = {
            "education": self.profile.education,
            "household": self.profile.household,
            "gender": self.profile.gender,
            "work_years": self.profile.work_years,
            "is_fresh_graduate": self.profile.is_fresh_graduate,
        }
        self.semantic_matcher = SemanticMatcher(profile)

    def _match_education_semantic(self, job_education: str) -> tuple[bool, str]:
        """
        使用语义匹配学历

        Args:
            job_education: 岗位要求，如"本科及以上"

        Returns:
            (是否匹配, 原因)
        """
        matcher = EducationMatcher(self.profile.education)
        result = matcher.match(job_education)
        return result.match, result.reason

    def _match_household_semantic(self, other_field: str) -> tuple[bool, str]:
        """
        使用语义匹配户籍

        Args:
            other_field: 其他要求字段

        Returns:
            (是否匹配, 原因)
        """
        matcher = HouseholdMatcher(self.profile.household, self.profile.gender)

        # 检查户籍要求
        result = matcher.match_household(other_field)
        if not result.match:
            return False, result.reason

        return True, result.reason

    def _match_experience_semantic(self, other_field: str) -> tuple[bool, str]:
        """
        使用语义匹配工作年限

        Args:
            other_field: 其他要求字段

        Returns:
            (是否匹配, 原因)
        """
        matcher = ExperienceMatcher(self.profile.work_years, self.profile.is_fresh_graduate)
        result = matcher.match(other_field)
        return result.match, result.reason

    def match(self, job: Job) -> Job:
        """
        V3版匹配 - 增强语义理解
        """
        # 先调用父类的匹配逻辑
        job = super().match(job)

        # 如果已经确定不符合，直接返回
        if job.match_level == MatchLevel.MISMATCH:
            return job

        # 增强语义匹配 - 检查其他要求字段
        semantic_checks = []

        # 1. 学历语义匹配（如果父类没匹配好）
        if "及以上" in job.education or "以上" in job.education:
            match, reason = self._match_education_semantic(job.education)
            if match:
                if reason not in job.match_reasons:
                    job.match_reasons.append(f"[语义匹配] {reason}")
            else:
                semantic_checks.append(f"学历语义不匹配: {reason}")

        # 2. 户籍语义匹配
        if job.other and ("户籍" in job.other or "户口" in job.other):
            match, reason = self._match_household_semantic(job.other)
            if not match:
                semantic_checks.append(f"户籍语义不匹配: {reason}")
                job.match_level = MatchLevel.MISMATCH
            else:
                if reason not in job.match_reasons:
                    job.match_reasons.append(f"[语义匹配] {reason}")

        # 3. 工作年限语义匹配
        if job.other and ("年" in job.other or "应届" in job.other):
            match, reason = self._match_experience_semantic(job.other)
            if not match:
                semantic_checks.append(f"工作年限语义不匹配: {reason}")
                job.match_level = MatchLevel.MISMATCH
            else:
                if reason not in job.match_reasons:
                    job.match_reasons.append(f"[语义匹配] {reason}")

        # 4. 性别语义匹配
        if job.other and ("限男性" in job.other or "限女性" in job.other):
            matcher = HouseholdMatcher(self.profile.household, self.profile.gender)
            result = matcher.match_gender(job.other)
            if not result.match:
                semantic_checks.append(f"性别不匹配: {result.reason}")
                job.match_level = MatchLevel.MISMATCH

        # 更新不匹配原因
        if semantic_checks:
            job.mismatch_reasons.extend(semantic_checks)

        return job


def test_v3_matcher():
    """测试V3匹配器"""
    print("=" * 80)
    print("Job Matcher V3 - 语义匹配测试")
    print("=" * 80)

    # 创建测试用的配置
    import os
    import tempfile

    config_content = """
profile:
  专业: "金融学"
  学历: "本科"
  学位: "学士"
  性别: "男"
  户籍: "济南市"
  是否应届: false
  政治面貌: "群众"
  相关资格: []
  工作年限: 3

preference:
  意向城市: ["济南市", "青岛市"]

rules:
  性别限制:
    模式: "loose"
  户籍匹配:
    模式: "loose"
  应届生匹配:
    模式: "loose"

filter:
  最大竞争比: 100
"""

    # 写入临时配置文件
    config_path = tempfile.mktemp(suffix=".yaml")
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config_content)

    try:
        matcher = JobMatcherV3(config_path)

        print("\n用户档案:")
        print(f"  专业: {matcher.profile.major}")
        print(f"  学历: {matcher.profile.education}")
        print(f"  性别: {matcher.profile.gender}")
        print(f"  户籍: {matcher.profile.household}")
        print(f"  工作年限: {matcher.profile.work_years}年")

        # 测试岗位
        test_jobs = [
            {
                "sheet_name": "济南市",
                "unit": "济南市财政局",
                "job_type": "支农",
                "major": "经济学类",
                "education": "本科及以上",
                "degree": "学士及以上",
                "other": "限济南市户籍，2年以上工作经验",
                "recruit_count": 5,
                "applicants": 60,
                "approved": 45,
                "paid": 40,
            },
            {
                "sheet_name": "青岛市",
                "unit": "青岛市统计局",
                "job_type": "支农",
                "major": "统计学类",
                "education": "本科及以上",
                "degree": "学士及以上",
                "other": "限山东省户籍",
                "recruit_count": 3,
                "applicants": 30,
                "approved": 25,
                "paid": 20,
            },
            {
                "sheet_name": "烟台市",
                "unit": "烟台市教育局",
                "job_type": "支教",
                "major": "教育学类",
                "education": "硕士研究生及以上",
                "degree": "硕士及以上",
                "other": "限女性，应届毕业生",
                "recruit_count": 10,
                "applicants": 250,
                "approved": 200,
                "paid": 180,
            },
            {
                "sheet_name": "济南市",
                "unit": "济南市科技局",
                "job_type": "支农",
                "major": "经济学类",
                "education": "本科及以上",
                "degree": "学士及以上",
                "other": "限青岛市户籍",
                "recruit_count": 2,
                "applicants": 40,
                "approved": 30,
                "paid": 25,
            },
        ]

        print("\n" + "-" * 80)
        print("岗位匹配测试")
        print("-" * 80)

        for job_data in test_jobs:
            job = Job(**job_data)
            result = matcher.match(job)

            print(f"\n[LOC] {result.sheet_name} - {result.unit}")
            print(f"   专业要求: {result.major}")
            print(f"   其他要求: {result.other}")
            print(f"   匹配等级: {result.match_level.value}")
            print(f"   匹配分数: {result.match_score}")

            if result.match_reasons:
                print("   ✓ 匹配原因:")
                for reason in result.match_reasons[-3:]:  # 只显示最后3条
                    print(f"     • {reason}")

            if result.mismatch_reasons:
                print("   ✗ 不匹配原因:")
                for reason in result.mismatch_reasons:
                    print(f"     • {reason}")

    finally:
        # 清理临时文件
        if os.path.exists(config_path):
            os.remove(config_path)


if __name__ == "__main__":
    test_v3_matcher()

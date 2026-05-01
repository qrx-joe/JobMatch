#!/usr/bin/env python3
"""
Excel文件读取器
"""

import glob

import pandas as pd

from job_matcher import Job


class JobExcelReader:
    """岗位表Excel读取器"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df_by_sheet: dict[str, pd.DataFrame] = {}
        self.headers_by_sheet: dict[str, list[str]] = {}

    def read_all(self) -> list[Job]:
        """读取所有Sheet的岗位数据"""
        jobs = []

        xl = pd.ExcelFile(self.file_path)
        for sheet_name in xl.sheet_names:
            # 跳过省林草局（通常不是地市岗位）
            if sheet_name == "省林草局":
                continue

            sheet_jobs = self._read_sheet(sheet_name)
            jobs.extend(sheet_jobs)

        return jobs

    def _read_sheet(self, sheet_name: str) -> list[Job]:
        """读取单个Sheet"""
        jobs = []

        # 读取原始数据（不指定header）
        df_raw = pd.read_excel(self.file_path, sheet_name=sheet_name, header=None)

        # 找到表头行
        header_row_idx = self._find_header_row(df_raw)
        if header_row_idx is None:
            print(f"警告: {sheet_name} 无法找到表头行，跳过")
            return []

        # 重新读取，使用正确的header
        df = pd.read_excel(self.file_path, sheet_name=sheet_name, header=header_row_idx)

        # 标准化列名
        df.columns = [str(c).strip() for c in df.columns]

        # 提取岗位数据
        for _idx, row in df.iterrows():
            # 跳过空行
            if pd.isna(row.iloc[0]):
                continue

            job = self._parse_row(row, sheet_name)
            if job:
                jobs.append(job)

        print(f"  {sheet_name}: 读取 {len(jobs)} 个岗位")
        return jobs

    def _find_header_row(self, df: pd.DataFrame) -> int | None:
        """找到表头所在行"""

        for idx in range(min(10, len(df))):
            row_text = " ".join([str(v) for v in df.iloc[idx].values if pd.notna(v)])
            if all(kw in row_text for kw in ["序号", "服务单位"]):
                if any(kw in row_text for kw in ["岗位名称", "岗位类型", "学历", "专业"]):
                    return idx

        return None

    def _parse_row(self, row: pd.Series, sheet_name: str) -> Job | None:
        """解析一行数据为Job对象"""
        try:
            job = Job()
            job.sheet_name = sheet_name

            # 基础字段映射
            col_map = {
                "序号": ["序号", "序号 ", "No"],
                "服务单位": ["服务单位", "服务单位 ", "单位"],
                "岗位类型": ["岗位类型", "岗位名称", "岗位"],
                "服务类别": ["服务类别", "服务类型", "类别"],
                "招募人数": ["招募人数", "招聘人数", "招录人数"],
                "学历": ["学历", "学历要求", "服务岗位要求"],
                "学位": ["学位", "学位要求"],
                "专业": ["专业", "专业要求"],
                "相关资格": ["相关资格", "资格要求"],
                "其他": ["其他", "其他要求", "备注"],
                "联系电话": ["联系电话", "电话"],
                "联系人": ["联系人"],
                "岗位描述": ["岗位描述", "描述"],
                "福利待遇": ["福利待遇", "待遇"],
            }

            # 提取字段
            job.index = self._get_value(row, col_map["序号"], 0)
            job.unit = self._get_value(row, col_map["服务单位"], "")
            job.job_type = self._get_value(row, col_map["岗位类型"], "")
            job.service_category = self._get_value(row, col_map["服务类别"], "")
            job.recruit_count = self._parse_int(self._get_value(row, col_map["招募人数"], "1"))
            job.education = self._get_value(row, col_map["学历"], "")
            job.degree = self._get_value(row, col_map["学位"], "")
            job.major = self._get_value(row, col_map["专业"], "")
            job.qualifications = self._get_value(row, col_map["相关资格"], "")
            job.other = self._get_value(row, col_map["其他"], "")
            job.phone = self._get_value(row, col_map["联系电话"], "")
            job.contact = self._get_value(row, col_map["联系人"], "")
            job.description = self._get_value(row, col_map["岗位描述"], "")
            job.benefits = self._get_value(row, col_map["福利待遇"], "")

            # 清理数据
            job.unit = str(job.unit).strip()
            job.major = str(job.major).strip()

            # 过滤无效数据
            if not job.unit or job.unit in ["服务单位", "nan", ""]:
                return None

            return job

        except Exception as e:
            print(f"  解析行出错: {e}")
            return None

    def _get_value(self, row: pd.Series, possible_names: list[str], default="") -> str:
        """根据可能的列名获取值"""
        # 清理列名（移除换行符和多余空格）
        cleaned_index = {
            str(col).replace("\n", "").replace(" ", "").strip(): col for col in row.index
        }

        for name in possible_names:
            # 尝试原始匹配
            if name in row.index:
                val = row[name]
                if pd.notna(val):
                    return str(val).strip()

            # 尝试清理后的匹配
            cleaned_name = name.replace("\n", "").replace(" ", "").strip()
            if cleaned_name in cleaned_index:
                original_col = cleaned_index[cleaned_name]
                val = row[original_col]
                if pd.notna(val):
                    return str(val).strip()

        return default

    def _parse_int(self, val: str, default: int = 0) -> int:
        """解析整数"""
        try:
            return int(float(val))
        except:
            return default


class StatsExcelReader:
    """统计表Excel读取器"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.stats: dict[tuple, dict] = {}

    def read(self) -> dict[tuple, dict]:
        """读取统计数据"""
        df = pd.read_excel(self.file_path, header=1)  # 第二行是表头

        print(f"统计表: 共 {len(df)} 条记录")

        for _, row in df.iterrows():
            try:
                # 提取关键字段
                unit_full = str(row.get("服务单位", "")).strip()
                job_type = str(row.get("岗位类型", "")).strip()
                recruit = int(row.get("招募人数", 0)) if pd.notna(row.get("招募人数")) else 0
                applicants = (
                    int(row.get("填报信息人数", 0)) if pd.notna(row.get("填报信息人数")) else 0
                )
                approved = (
                    int(row.get("初审通过人数", 0)) if pd.notna(row.get("初审通过人数")) else 0
                )
                paid = int(row.get("缴费人数", 0)) if pd.notna(row.get("缴费人数")) else 0

                if not unit_full:
                    continue

                key = (unit_full, job_type)
                self.stats[key] = {
                    "recruit": recruit,
                    "applicants": applicants,
                    "approved": approved,
                    "paid": paid,
                }

            except Exception:
                continue

        print(f"统计表: 成功解析 {len(self.stats)} 条记录")
        return self.stats

    def match_job(self, job: Job) -> dict | None:
        """
        为岗位匹配统计数据
        """
        # 构建可能的单位名
        possible_units = [
            f"{job.sheet_name}-{job.unit}",  # 如 "太原市-太原市杏花岭区..."
            job.unit,  # 直接匹配
        ]

        job_type = job.job_type.strip()

        # 尝试精确匹配
        for unit in possible_units:
            key = (unit, job_type)
            if key in self.stats:
                return self.stats[key]

        # 尝试模糊匹配
        return self._fuzzy_match(job)

    def _fuzzy_match(self, job: Job) -> dict | None:
        """模糊匹配统计数据"""
        best_score = 0
        best_match = None

        job_unit_clean = self._clean_unit_name(job.unit)

        for (stats_unit, stats_type), stats in self.stats.items():
            # 岗位类型必须匹配
            if stats_type != job.job_type:
                continue

            # 计算相似度
            score = self._calc_similarity(job_unit_clean, stats_unit)

            if score > best_score and score >= 0.6:
                best_score = score
                best_match = stats

        return best_match

    def _clean_unit_name(self, name: str) -> str:
        """清理单位名"""
        name = str(name).strip()
        # 移除常见前缀
        prefixes = [
            "太原市",
            "大同市",
            "朔州市",
            "忻州市",
            "吕梁市",
            "晋中市",
            "阳泉市",
            "长治市",
            "晋城市",
            "临汾市",
            "运城市",
        ]
        for prefix in prefixes:
            if name.startswith(prefix):
                name = name[len(prefix) :]
                break
        return name.strip()

    def _calc_similarity(self, job_unit: str, stats_unit: str) -> float:
        """计算单位名相似度"""
        # 清理统计表中的单位名

        # 如果岗位单位名在统计单位名中
        if job_unit in stats_unit:
            return 0.8

        # 如果统计单位名在岗位单位名中
        if stats_unit in job_unit:
            return 0.8

        # 计算字符重叠率
        job_chars = set(job_unit)
        stats_chars = set(stats_unit)

        if not job_chars or not stats_chars:
            return 0.0

        overlap = len(job_chars & stats_chars)
        return overlap / max(len(job_chars), len(stats_chars))


if __name__ == "__main__":
    # 测试读取
    import glob

    # 找岗位表
    job_files = glob.glob("*岗位汇总表*.xlsx")
    if job_files:
        reader = JobExcelReader(job_files[0])
        jobs = reader.read_all()
        print(f"\n总计读取 {len(jobs)} 个岗位")

        # 显示前5个
        print("\n前5个岗位示例:")
        for job in jobs[:5]:
            print(f"  [{job.sheet_name}] {job.unit} - {job.job_type}")
            print(f"    学历: {job.education}, 专业: {job.major}")

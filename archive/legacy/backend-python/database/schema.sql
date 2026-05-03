-- JobMatch 数据库 Schema
-- 创建日期: 2026-04-29

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS jobmatch DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE jobmatch;

-- ==================== 岗位表 ====================
CREATE TABLE IF NOT EXISTS jobs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    platform VARCHAR(50) NOT NULL COMMENT '平台类型（三支一扶/公务员等）',
    city VARCHAR(50) COMMENT '地市',
    unit VARCHAR(200) NOT NULL COMMENT '服务单位',
    job_type VARCHAR(100) COMMENT '岗位类型',
    service_category VARCHAR(50) COMMENT '服务类别',
    recruit_count INT DEFAULT 1 COMMENT '招募人数',

    -- 学历与专业
    education VARCHAR(50) COMMENT '学历要求',
    degree VARCHAR(50) COMMENT '学位要求',
    major VARCHAR(200) COMMENT '专业要求',
    age_limit VARCHAR(50) COMMENT '年龄要求',
    political_requirement VARCHAR(50) COMMENT '政治面貌要求',
    grassroots_experience VARCHAR(100) COMMENT '基层工作经验要求',
    directional_recruit VARCHAR(100) COMMENT '定向招录',
    qualifications VARCHAR(100) COMMENT '资格证书要求',
    other TEXT COMMENT '其他要求',

    -- 联系方式
    phone VARCHAR(50) COMMENT '联系电话',
    contact VARCHAR(50) COMMENT '联系人',

    -- 竞争数据
    applicants INT DEFAULT 0 COMMENT '报名人数',
    approved INT DEFAULT 0 COMMENT '初审通过人数',
    paid INT DEFAULT 0 COMMENT '缴费人数',
    competition_ratio FLOAT DEFAULT 0.0 COMMENT '竞争比',

    -- 原始数据
    raw_data JSON COMMENT '原始JSON数据',

    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- 索引
    INDEX idx_platform (platform),
    INDEX idx_city (city),
    INDEX idx_major (major),
    INDEX idx_competition_ratio (competition_ratio)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='岗位表';

-- ==================== 用户表 ====================
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    openid VARCHAR(100) UNIQUE NOT NULL COMMENT '微信openid',

    -- 基本信息
    major VARCHAR(100) COMMENT '专业',
    education VARCHAR(50) COMMENT '学历',
    degree VARCHAR(50) COMMENT '学位',
    gender VARCHAR(10) COMMENT '性别',
    age INT DEFAULT 0 COMMENT '年龄',
    household VARCHAR(100) COMMENT '户籍',
    party_status VARCHAR(50) COMMENT '政治面貌',

    -- 附加条件
    is_fresh_graduate BOOLEAN DEFAULT FALSE COMMENT '是否应届生',
    grassroots_exp INT DEFAULT 0 COMMENT '基层工作年限',
    qualifications JSON COMMENT '持有资格证书',
    estimated_score FLOAT DEFAULT 0.0 COMMENT '预估考试成绩',

    -- 偏好设置
    target_cities JSON COMMENT '意向城市',
    target_platforms JSON COMMENT '意向平台类型',

    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- 索引
    INDEX idx_openid (openid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- ==================== 收藏表 ====================
CREATE TABLE IF NOT EXISTS favorites (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '用户ID',
    job_id INT NOT NULL COMMENT '岗位ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 索引
    INDEX idx_user_id (user_id),
    INDEX idx_job_id (job_id),
    UNIQUE KEY uk_user_job (user_id, job_id),

    -- 外键
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='收藏表';

-- ==================== 历史统计数据表 ====================
CREATE TABLE IF NOT EXISTS historical_stats (
    id INT PRIMARY KEY AUTO_INCREMENT,
    job_id INT COMMENT '关联岗位ID',
    year INT NOT NULL COMMENT '年份',

    -- 招录数据
    recruitment_count INT DEFAULT 0 COMMENT '招录人数',
    applicants INT DEFAULT 0 COMMENT '报名人数',
    approved INT DEFAULT 0 COMMENT '初审通过人数',
    paid INT DEFAULT 0 COMMENT '缴费人数',
    competition_ratio FLOAT DEFAULT 0.0 COMMENT '竞争比',

    -- 分数数据
    passing_score FLOAT DEFAULT 0.0 COMMENT '进面最低分',
    avg_score FLOAT DEFAULT 0.0 COMMENT '平均分',
    highest_score FLOAT DEFAULT 0.0 COMMENT '最高分',

    -- 附加信息
    notes TEXT COMMENT '备注',
    source VARCHAR(200) COMMENT '数据来源',

    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 索引
    INDEX idx_job_id (job_id),
    INDEX idx_year (year),
    UNIQUE KEY uk_job_year (job_id, year),

    -- 外键
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='历史统计数据表';

-- ==================== 筛选历史表 ====================
CREATE TABLE IF NOT EXISTS filter_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '用户ID',
    filter_conditions JSON NOT NULL COMMENT '筛选条件',
    result_count INT DEFAULT 0 COMMENT '结果数量',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 索引
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),

    -- 外键
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='筛选历史表';
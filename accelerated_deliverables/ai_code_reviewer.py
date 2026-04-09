#!/usr/bin/env python3
"""
AI代码审查助手 v1.0
基于AI的智能代码审查、质量分析、自动修复建议系统
"""

import ast
import json
import os
import re
import subprocess
import sys
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import logging
import hashlib
import difflib

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class CodeReviewIssue:
    """代码审查问题数据结构"""
    file_path: str
    line_number: int
    column: int
    issue_type: str  # 'bug', 'vulnerability', 'code_smell', 'performance', 'security'
    severity: str  # 'critical', 'high', 'medium', 'low'
    confidence: float  # 置信度 (0-1)
    message: str
    rule_id: str
    fix_suggestion: str
    ai_explanation: str
    before_code: str = ""
    after_code: str = ""
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column": self.column,
            "issue_type": self.issue_type,
            "severity": self.severity,
            "confidence": round(self.confidence, 2),
            "message": self.message,
            "rule_id": self.rule_id,
            "fix_suggestion": self.fix_suggestion,
            "ai_explanation": self.ai_explanation,
            "before_code": self.before_code,
            "after_code": self.after_code,
            "hash": self.calculate_hash(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def calculate_hash(self) -> str:
        """计算问题哈希值"""
        content = f"{self.file_path}:{self.line_number}:{self.column}:{self.issue_type}:{self.message}"
        return hashlib.md5(content.encode()).hexdigest()[:8]

@dataclass
class CodeReviewResult:
    """代码审查结果数据结构"""
    total_files: int
    total_lines: int
    issues_found: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    security_score: float  # 安全评分 (0-100)
    quality_score: float  # 质量评分 (0-100)
    performance_score: float  # 性能评分 (0-100)
    maintainability_score: float  # 可维护性评分 (0-100)
    review_duration: float
    issues: List[CodeReviewIssue]
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "total_files": self.total_files,
            "total_lines": self.total_lines,
            "issues_found": self.issues_found,
            "critical_issues": self.critical_issues,
            "high_issues": self.high_issues,
            "medium_issues": self.medium_issues,
            "low_issues": self.low_issues,
            "security_score": round(self.security_score, 2),
            "quality_score": round(self.quality_score, 2),
            "performance_score": round(self.performance_score, 2),
            "maintainability_score": round(self.maintainability_score, 2),
            "overall_score": self.calculate_overall_score(),
            "review_duration": round(self.review_duration, 3),
            "issues": [issue.to_dict() for issue in self.issues],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def calculate_overall_score(self) -> float:
        """计算总体评分"""
        weights = {
            "security": 0.3,
            "quality": 0.25,
            "performance": 0.25,
            "maintainability": 0.2
        }
        
        # 问题扣分
        issue_penalty = (
            self.critical_issues * 10 +
            self.high_issues * 5 +
            self.medium_issues * 2 +
            self.low_issues * 0.5
        )
        
        base_score = 100 - min(issue_penalty, 50)  # 最多扣50分
        
        # 加权平均
        weighted_score = (
            self.security_score * weights["security"] +
            self.quality_score * weights["quality"] +
            self.performance_score * weights["performance"] +
            self.maintainability_score * weights["maintainability"]
        )
        
        final_score = (base_score * 0.4) + (weighted_score * 0.6)
        return round(max(0, min(100, final_score)), 2)

class AICodeReviewer:
    """AI代码审查助手核心类"""
    
    def __init__(self, config_path: str = None):
        """
        初始化AI代码审查助手
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.issues = []
        self.ai_rules = self._load_ai_rules()
        
        logger.info("AI代码审查助手初始化完成")
    
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        default_config = {
            "code_analysis": {
                "enabled": True,
                "languages": ["python", "javascript", "typescript", "java", "go"],
                "max_file_size_mb": 10,
                "ignore_patterns": [".git", "__pycache__", "node_modules", "venv"]
            },
            "ai_analysis": {
                "enabled": True,
                "use_local_ai": True,
                "use_cloud_ai": False,
                "confidence_threshold": 0.7,
                "max_issues_per_file": 50
            },
            "security_analysis": {
                "enabled": True,
                "check_owasp_top_10": True,
                "check_cwe_top_25": True,
                "check_sast": True
            },
            "performance_analysis": {
                "enabled": True,
                "check_time_complexity": True,
                "check_memory_leaks": True,
                "check_database_optimization": True
            },
            "code_quality": {
                "enabled": True,
                "check_design_patterns": True,
                "check_code_smells": True,
                "check_best_practices": True
            },
            "auto_fix": {
                "enabled": True,
                "apply_safe_fixes": True,
                "require_confirmation": True,
                "backup_original": True
            },
            "reporting": {
                "generate_html": True,
                "generate_json": True,
                "generate_markdown": True,
                "send_notifications": False
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    self._merge_dicts(default_config, user_config)
            except Exception as e:
                logger.warning(f"加载配置文件失败: {e}, 使用默认配置")
        
        return default_config
    
    def _merge_dicts(self, base: Dict, update: Dict):
        """递归合并字典"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_dicts(base[key], value)
            else:
                base[key] = value
    
    def _load_ai_rules(self) -> List[Dict]:
        """加载AI分析规则"""
        return [
            # 安全规则
            {
                "id": "AI-SEC-001",
                "name": "SQL注入检测",
                "description": "检测可能的SQL注入漏洞",
                "severity": "critical",
                "pattern": r"execute\(.*['\"].*\+.*['\"]\)|executemany\(.*['\"].*\+.*['\"]\)",
                "ai_prompt": "检查SQL查询构建是否使用字符串拼接，这可能存在SQL注入风险。",
                "fix_suggestion": "使用参数化查询或ORM的安全方法。",
                "confidence": 0.9
            },
            {
                "id": "AI-SEC-002",
                "name": "XSS漏洞检测",
                "description": "检测可能的跨站脚本攻击漏洞",
                "severity": "critical",
                "pattern": r"render_template_string|\.innerHTML\s*=|document\.write\(",
                "ai_prompt": "检查是否直接渲染用户输入，这可能存在XSS风险。",
                "fix_suggestion": "对用户输入进行转义或使用安全的模板引擎。",
                "confidence": 0.85
            },
            {
                "id": "AI-SEC-003",
                "name": "硬编码密钥检测",
                "description": "检测代码中的硬编码密钥和密码",
                "severity": "high",
                "pattern": r"(api_key|secret_key|password|token)\s*=\s*['\"].{8,}['\"]",
                "ai_prompt": "检查是否在代码中硬编码敏感信息。",
                "fix_suggestion": "将敏感信息移到环境变量或配置文件中。",
                "confidence": 0.95
            },
            {
                "id": "AI-SEC-004",
                "name": "弱加密算法检测",
                "description": "检测弱加密算法的使用",
                "severity": "high",
                "pattern": r"md5|sha1|DES|RC4",
                "ai_prompt": "检查是否使用不安全的加密算法。",
                "fix_suggestion": "使用现代加密算法如AES-256、SHA-256等。",
                "confidence": 0.9
            },
            
            # 代码质量规则
            {
                "id": "AI-QUAL-001",
                "name": "过长函数检测",
                "description": "检测过长的函数",
                "severity": "medium",
                "ai_prompt": "检查函数是否过长，影响可读性和可维护性。",
                "fix_suggestion": "将函数拆分为多个小函数，每个函数只做一件事。",
                "confidence": 0.8
            },
            {
                "id": "AI-QUAL-002",
                "name": "复杂条件检测",
                "description": "检测过于复杂的条件判断",
                "severity": "medium",
                "pattern": r"if.*and.*and.*and|if.*or.*or.*or",
                "ai_prompt": "检查条件判断是否过于复杂。",
                "fix_suggestion": "将复杂条件提取为命名函数或使用卫语句。",
                "confidence": 0.75
            },
            {
                "id": "AI-QUAL-003",
                "name": "重复代码检测",
                "description": "检测重复的代码片段",
                "severity": "medium",
                "ai_prompt": "检查是否存在重复的代码逻辑。",
                "fix_suggestion": "将重复代码提取为公共函数或类。",
                "confidence": 0.7
            },
            {
                "id": "AI-QUAL-004",
                "name": "魔法数字检测",
                "description": "检测代码中的魔法数字",
                "severity": "low",
                "pattern": r"\b\d{2,}\b",
                "ai_prompt": "检查是否使用未命名的数字常量。",
                "fix_suggestion": "将魔法数字定义为命名常量。",
                "confidence": 0.6
            },
            
            # 性能规则
            {
                "id": "AI-PERF-001",
                "name": "N+1查询检测",
                "description": "检测可能的N+1查询问题",
                "severity": "high",
                "ai_prompt": "检查循环中是否执行数据库查询，可能导致N+1问题。",
                "fix_suggestion": "使用预加载或批量查询优化。",
                "confidence": 0.8
            },
            {
                "id": "AI-PERF-002",
                "name": "时间复杂度检测",
                "description": "检测可能的高时间复杂度代码",
                "severity": "medium",
                "pattern": r"for.*for|while.*while",
                "ai_prompt": "检查是否存在嵌套循环，可能导致性能问题。",
                "fix_suggestion": "优化算法复杂度或使用缓存。",
                "confidence": 0.7
            },
            {
                "id": "AI-PERF-003",
                "name": "内存泄漏检测",
                "description": "检测可能的内存泄漏",
                "severity": "high",
                "ai_prompt": "检查是否可能造成内存泄漏的代码模式。",
                "fix_suggestion": "确保资源正确释放，使用上下文管理器。",
                "confidence": 0.65
            },
            
            # 设计模式规则
            {
                "id": "AI-DESIGN-001",
                "name": "单例模式建议",
                "description": "建议使用单例模式的场景",
                "severity": "low",
                "ai_prompt": "检查是否适合使用单例模式。",
                "fix_suggestion": "考虑使用单例模式管理全局状态。",
                "confidence": 0.6
            },
            {
                "id": "AI-DESIGN-002",
                "name": "工厂模式建议",
                "description": "建议使用工厂模式的场景",
                "severity": "low",
                "ai_prompt": "检查是否适合使用工厂模式。",
                "fix_suggestion": "考虑使用工厂模式创建对象。",
                "confidence": 0.6
            },
            {
                "id": "AI-DESIGN-003",
                "name": "观察者模式建议",
                "description": "建议使用观察者模式的场景",
                "severity": "low",
                "ai_prompt": "检查是否适合使用观察者模式。",
                "fix_suggestion": "考虑使用观察者模式实现事件驱动。",
                "confidence": 0.6
            }
        ]
    
    def review_codebase(self, directory: str) -> CodeReviewResult:
        """
        审查代码库
        
        Args:
            directory: 代码目录
            
        Returns:
            代码审查结果
        """
        start_time = time.time()
        
        # 重置状态
        self.issues = []
        
        # 收集代码文件
        code_files = self._collect_code_files(directory)
        
        if not code_files:
            logger.warning(f"在目录 {directory} 中未找到代码文件")
            return self._create_empty_result()
        
        # 分析每个文件
        total_lines = 0
        for file_path in code_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    total_lines += len(lines)
                    
                    # 应用AI规则分析
                    self._analyze_with_ai(file_path, content, lines)
                    
            except Exception as e:
                logger.error(f"分析文件失败 {file_path}: {e}")
        
        # 计算评分
        review_duration = time.time() - start_time
        result = self._calculate_scores(code_files, total_lines, review_duration)
        
        # 生成报告
        self._generate_reports(result)
        
        logger.info(f"代码审查完成: 找到 {len(self.issues)} 个问题, 总体评分: {result.overall_score}")
        
        return result
    
    def _collect_code_files(self, directory: str) -> List[str]:
        """收集代码文件"""
        supported_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.cpp': 'cpp',
            '.c': 'c',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby'
        }
        
        code_files = []
        ignore_patterns = self.config["code_analysis"]["ignore_patterns"]
        max_size_mb = self.config["code_analysis"]["max_file_size_mb"]
        
        for root, dirs, files in os.walk(directory):
            # 过滤忽略目录
            dirs[:] = [d for d in dirs if not any(ip in d for ip in ignore_patterns)]
            
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in supported_extensions:
                    file_path = os.path.join(root, file)
                    
                    # 检查文件大小
                    try:
                        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                        if file_size_mb <= max_size_mb:
                            code_files.append(file_path)
                    except OSError:
                        continue
        
        return code_files
    
    def _analyze_with_ai(self, file_path: str, content: str, lines: List[str]):
        """使用AI规则分析代码"""
        for rule in self.ai_rules:
            try:
                # 基于正则表达式的检查
                if "pattern" in rule:
                    self._check_with_pattern(file_path, content, lines, rule)
                
                # 基于AI提示的检查
                elif "ai_prompt" in rule:
                    self._check_with_ai_prompt(file_path, content, lines, rule)
                    
            except Exception as e:
                logger.error(f"应用规则 {rule.get('id', 'unknown')} 失败: {e}")
    
    def _check_with_pattern(self, file_path: str, content: str, lines: List[str], rule: Dict):
        """基于正则表达式检查"""
        pattern = re.compile(rule["pattern"], re.IGNORECASE | re.MULTILINE)
        
        for match in pattern.finditer(content):
            line_number = content[:match.start()].count('\n') + 1
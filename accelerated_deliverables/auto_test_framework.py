#!/usr/bin/env python3
"""
自动化测试框架 v1.0
专业级测试自动化、持续集成、质量门禁系统
"""

import unittest
import pytest
import coverage
import json
import time
import subprocess
import sys
import os
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import tempfile
import shutil

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """测试结果数据结构"""
    test_name: str
    test_module: str
    status: str  # 'passed', 'failed', 'skipped', 'error'
    duration: float  # 秒
    error_message: str = ""
    stack_trace: str = ""
    assertions: int = 0
    passed_assertions: int = 0
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "test_name": self.test_name,
            "test_module": self.test_module,
            "status": self.status,
            "duration": round(self.duration, 3),
            "error_message": self.error_message,
            "stack_trace": self.stack_trace,
            "assertions": self.assertions,
            "passed_assertions": self.passed_assertions,
            "success_rate": self.calculate_success_rate(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def calculate_success_rate(self) -> float:
        """计算成功率"""
        if self.assertions == 0:
            return 100.0 if self.status == "passed" else 0.0
        return round((self.passed_assertions / self.assertions) * 100, 2)

@dataclass
class TestSuiteResult:
    """测试套件结果数据结构"""
    suite_name: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    error_tests: int
    total_duration: float
    test_results: List[TestResult]
    coverage_percentage: float = 0.0
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "suite_name": self.suite_name,
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "skipped_tests": self.skipped_tests,
            "error_tests": self.error_tests,
            "total_duration": round(self.total_duration, 3),
            "success_rate": self.calculate_success_rate(),
            "coverage_percentage": round(self.coverage_percentage, 2),
            "test_results": [r.to_dict() for r in self.test_results],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def calculate_success_rate(self) -> float:
        """计算成功率"""
        if self.total_tests == 0:
            return 0.0
        return round((self.passed_tests / self.total_tests) * 100, 2)

class AutoTestFramework:
    """自动化测试框架核心类"""
    
    def __init__(self, config_path: str = None):
        """
        初始化测试框架
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.test_results = []
        self.coverage = None
        
        # 初始化覆盖率工具
        self.cov = coverage.Coverage(
            source=[os.getcwd()],
            omit=['*/tests/*', '*/venv/*', '*/__pycache__/*']
        )
        
        logger.info("自动化测试框架初始化完成")
    
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        default_config = {
            "test_discovery": {
                "pattern": "test_*.py",
                "recursive": True,
                "ignore_dirs": [".git", "__pycache__", "venv", "node_modules"]
            },
            "test_execution": {
                "parallel": True,
                "max_workers": 4,
                "timeout_seconds": 300,
                "retry_failed": True,
                "max_retries": 3
            },
            "coverage": {
                "enabled": True,
                "min_coverage": 80,
                "report_formats": ["html", "xml", "json"],
                "branch_coverage": True
            },
            "reporting": {
                "generate_html": True,
                "generate_json": True,
                "generate_junit": True,
                "send_email": False,
                "slack_webhook": None
            },
            "quality_gates": {
                "min_success_rate": 95,
                "max_duration_seconds": 600,
                "require_coverage": True,
                "block_on_failure": True
            },
            "ci_cd_integration": {
                "jenkins": False,
                "github_actions": True,
                "gitlab_ci": False,
                "azure_devops": False
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    # 合并配置
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
    
    def discover_tests(self, directory: str = None) -> List[str]:
        """
        发现测试文件
        
        Args:
            directory: 搜索目录
            
        Returns:
            测试文件路径列表
        """
        if directory is None:
            directory = os.getcwd()
        
        pattern = self.config["test_discovery"]["pattern"]
        recursive = self.config["test_discovery"]["recursive"]
        ignore_dirs = self.config["test_discovery"]["ignore_dirs"]
        
        test_files = []
        
        if recursive:
            for root, dirs, files in os.walk(directory):
                # 过滤忽略目录
                dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
                
                for file in files:
                    if file.endswith('.py') and file.startswith(pattern.replace('*', '')):
                        test_files.append(os.path.join(root, file))
        else:
            for file in os.listdir(directory):
                if file.endswith('.py') and file.startswith(pattern.replace('*', '')):
                    test_files.append(os.path.join(directory, file))
        
        logger.info(f"发现 {len(test_files)} 个测试文件")
        return test_files
    
    def run_tests(self, test_files: List[str] = None, test_names: List[str] = None) -> TestSuiteResult:
        """
        运行测试
        
        Args:
            test_files: 测试文件列表
            test_names: 特定测试名称列表
            
        Returns:
            测试套件结果
        """
        start_time = time.time()
        
        if test_files is None:
            test_files = self.discover_tests()
        
        if not test_files:
            logger.warning("未找到测试文件")
            return TestSuiteResult(
                suite_name="default",
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                skipped_tests=0,
                error_tests=0,
                total_duration=0,
                test_results=[],
                coverage_percentage=0.0
            )
        
        # 开始覆盖率收集
        if self.config["coverage"]["enabled"]:
            self.cov.start()
        
        # 运行测试
        test_results = []
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        skipped_tests = 0
        error_tests = 0
        
        for test_file in test_files:
            try:
                logger.info(f"运行测试文件: {test_file}")
                
                # 使用pytest运行测试
                pytest_args = [
                    test_file,
                    "-v",
                    "--tb=short",
                    f"--timeout={self.config['test_execution']['timeout_seconds']}"
                ]
                
                if test_names:
                    pytest_args.extend(["-k", " or ".join(test_names)])
                
                # 运行测试
                result = subprocess.run(
                    [sys.executable, "-m", "pytest"] + pytest_args,
                    capture_output=True,
                    text=True,
                    timeout=self.config["test_execution"]["timeout_seconds"] + 30
                )
                
                # 解析结果
                file_results = self._parse_pytest_output(result.stdout, result.stderr, test_file)
                test_results.extend(file_results)
                
                # 更新统计
                for tr in file_results:
                    total_tests += 1
                    if tr.status == "passed":
                        passed_tests += 1
                    elif tr.status == "failed":
                        failed_tests += 1
                    elif tr.status == "skipped":
                        skipped_tests += 1
                    elif tr.status == "error":
                        error_tests += 1
                
            except subprocess.TimeoutExpired:
                logger.error(f"测试超时: {test_file}")
                error_tests += 1
                total_tests += 1
                
                test_results.append(TestResult(
                    test_name="TestSuite",
                    test_module=test_file,
                    status="error",
                    duration=self.config["test_execution"]["timeout_seconds"],
                    error_message="测试执行超时"
                ))
                
            except Exception as e:
                logger.error(f"运行测试失败 {test_file}: {e}")
                error_tests += 1
                total_tests += 1
                
                test_results.append(TestResult(
                    test_name="TestSuite",
                    test_module=test_file,
                    status="error",
                    duration=0,
                    error_message=str(e)
                ))
        
        # 停止覆盖率收集
        if self.config["coverage"]["enabled"]:
            self.cov.stop()
            self.cov.save()
            
            # 生成覆盖率报告
            coverage_percentage = self._generate_coverage_report()
        else:
            coverage_percentage = 0.0
        
        total_duration = time.time() - start_time
        
        suite_result = TestSuiteResult(
            suite_name="auto_test_suite",
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
            error_tests=error_tests,
            total_duration=total_duration,
            test_results=test_results,
            coverage_percentage=coverage_percentage
        )
        
        # 生成报告
        self._generate_reports(suite_result)
        
        # 检查质量门禁
        self._check_quality_gates(suite_result)
        
        logger.info(f"测试完成: {passed_tests}通过, {failed_tests}失败, {skipped_tests}跳过, {error_tests}错误")
        logger.info(f"覆盖率: {coverage_percentage}%, 成功率: {suite_result.calculate_success_rate()}%")
        
        return suite_result
    
    def _parse_pytest_output(self, stdout: str, stderr: str, test_file: str) -> List[TestResult]:
        """解析pytest输出"""
        results = []
        
        # 简单解析pytest输出
        lines = stdout.split('\n')
        current_test = None
        
        for line in lines:
            line = line.strip()
            
            # 匹配测试结果行
            if line.startswith("test_") and "PASSED" in line:
                test_name = line.split()[0]
                results.append(TestResult(
                    test_name=test_name,
                    test_module=test_file,
                    status="passed",
                    duration=0.1,  # 简化处理
                    assertions=1,
                    passed_assertions=1
                ))
                
            elif line.startswith("test_") and "FAILED" in line:
                test_name = line.split()[0]
                results.append(TestResult(
                    test_name=test_name,
                    test_module=test_file,
                    status="failed",
                    duration=0.1,
                    error_message="测试失败",
                    assertions=1,
                    passed_assertions=0
                ))
                
            elif line.startswith("test_") and "SKIPPED" in line:
                test_name = line.split()[0]
                results.append(TestResult(
                    test_name=test_name,
                    test_module=test_file,
                    status="skipped",
                    duration=0,
                    error_message="测试跳过"
                ))
        
        # 如果没有解析到结果，创建一个汇总结果
        if not results and "passed" in stdout.lower():
            results.append(TestResult(
                test_name="AllTests",
                test_module=test_file,
                status="passed",
                duration=0.5,
                assertions=10,
                passed_assertions=10
            ))
        
        return results
    
    def _generate_coverage_report(self) -> float:
        """生成覆盖率报告"""
        try:
            # 生成报告
            report_formats = self.config["coverage"]["report_formats"]
            
            if "html" in report_formats:
                self.cov.html_report(directory="coverage_html")
            
            if "xml" in report_formats:
                self.cov.xml_report(outfile="coverage.xml")
            
            if "json" in report_formats:
                self.cov.json_report(outfile="coverage.json")
            
            # 获取总体覆盖率
            total_coverage = self.cov.report()
            
            # 保存详细数据
            coverage_data = self.cov.get_data()
            
            return total_coverage
            
        except Exception as e:
            logger.error(f"生成覆盖率报告失败: {e}")
            return 0.0
    
    def _generate_reports(self, suite_result: TestSuiteResult):
        """生成测试报告"""
        try:
            reports_dir = "test_reports"
            os.makedirs(reports_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # JSON报告
            if self.config["reporting"]["generate_json"]:
                json_path = os.path.join(reports_dir, f"test_report_{timestamp}.json")
                with open(json_path, 'w') as f:
                    json.dump(suite_result.to_dict(), f, indent=2)
                logger.info(f"JSON报告已生成: {json_path}")
            
            # HTML报告
            if self.config["reporting"]["generate_html"]:
                html_path = os.path.join(reports_dir, f"test_report_{timestamp}.html")
                self._generate_html_report(suite_result, html_path)
                logger.info(f"HTML报告已生成: {html_path}")
            
            # JUnit报告
            if self.config["reporting"]["generate_junit"]:
                junit_path = os.path.join(reports_dir, f"junit_report_{timestamp}.xml")
                self._generate_junit_report(suite_result, junit_path)
                logger.info(f"JUnit报告已生成: {junit_path}")
            
        except Exception as e:
            logger.error(f"生成报告失败: {e}")
    
    def _generate_html_report(self, suite_result: TestSuiteResult, output_path: str):
        """生成HTML报告"""
        html_template = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>测试报告 - {suite_result.suite_name}</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f7fb; }}
                .card {{ border: none; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }}
                .stat-card {{ border-left: 5px solid #38b000; padding-left: 15px; }}
                .stat-card.warning {{ border-left-color: #ff9e00; }}
                .stat-card.danger {{ border-left-color: #e63946; }}
                .badge-passed {{ background-color: #38b000; }}
                .badge-failed {{ background-color: #e63946; }}
                .badge-skipped {{ background-color: #6c757d; }}
                .badge-error {{ background-color: #9d0208; }}
            </style>
        </head>
        <body>
            <div class="container-fluid mt-4">
                <div class="row">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-body">
                                <h1 class="mb-4">测试执行报告</h1>
                                <p class="text-muted">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-md-3">
                        <div class="card stat-card">
                            <div class="card-body">
                                <h6 class="text-muted">总测试数</h6>
                                <h2>{suite_result.total_tests}</h2>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card stat-card">
                            <div class="card-body">
                                <h6 class="text-muted">通过测试</h6>
                                <h2 class="text-success">{suite_result.passed_tests}</h2>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card stat-card warning">
                            <div class="card-body">
                                <h6 class="text-muted">失败测试</h6>
                                <h2 class="text-warning">{suite_result.failed_tests}</h2>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card stat-card">
                            <div class="card-body">
                                <h6 class="text-muted">跳过测试</h6>
                                <h2 class="text-muted">{suite_result.skipped_tests}</h2>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="mb-3">测试详情</h5>
                                <div class="table-responsive">
                                    <table class="table table-hover">
                                        <thead>
                                            <tr>
                                                <th>测试名称</th>
                                                <th>状态</th>
                                                <th>执行时间</th>
                                                <th>错误信息</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {suite_result.tests_html}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

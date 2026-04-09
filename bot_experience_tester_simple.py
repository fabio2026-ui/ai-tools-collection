#!/usr/bin/env python3
"""
AI项目机器人体验测试系统 - 简化版
使用curl命令测试项目功能
"""

import subprocess
import json
import time
import os
from datetime import datetime

class BotExperienceTesterSimple:
    def __init__(self):
        self.results = []
        self.start_time = datetime.now()
        
    def run_curl_command(self, url, timeout=5):
        """运行curl命令获取页面内容"""
        try:
            cmd = ["curl", "-s", "-m", str(timeout), url]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "content": result.stdout,
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "content": None,
                    "error": result.stderr
                }
        except Exception as e:
            return {
                "success": False,
                "content": None,
                "error": str(e)
            }
    
    def check_http_status(self, url, timeout=3):
        """检查HTTP状态码"""
        try:
            cmd = ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "-m", str(timeout), url]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.isdigit():
                return int(result.stdout)
            return 0
        except:
            return 0
    
    def test_project(self, port, project_name, category):
        """测试单个项目"""
        print(f"\n🔍 测试项目: {project_name} (端口 {port}) - {category}")
        
        result = {
            "project": project_name,
            "port": port,
            "category": category,
            "timestamp": datetime.now().isoformat(),
            "status": "unknown",
            "http_status": 0,
            "response_time": 0,
            "page_size": 0,
            "features_found": [],
            "issues": []
        }
        
        url = f"http://localhost:{port}"
        
        try:
            # 测试1: 检查HTTP状态
            start_time = time.time()
            http_status = self.check_http_status(url, timeout=5)
            response_time = time.time() - start_time
            
            result["http_status"] = http_status
            result["response_time"] = round(response_time * 1000, 2)
            
            if http_status == 200:
                result["status"] = "online"
                print(f"  ✅ HTTP 200 OK ({response_time:.2f}s)")
                
                # 测试2: 获取页面内容
                curl_result = self.run_curl_command(url, timeout=10)
                
                if curl_result["success"] and curl_result["content"]:
                    content = curl_result["content"]
                    result["page_size"] = len(content)
                    
                    # 分析页面内容
                    checks = [
                        ("HTML页面", "<html>" in content and "</html>" in content),
                        ("标题标签", "<title>" in content and "</title>" in content),
                        ("赚钱相关", any(keyword in content.lower() for keyword in ["赚钱", "收入", "profit", "revenue"])),
                        ("AI相关", any(keyword in content.lower() for keyword in ["ai", "人工智能", "智能"])),
                        ("控制面板", "控制面板" in content or "dashboard" in content.lower()),
                        ("交互元素", any(element in content.lower() for element in ["button", "form", "input", "click"])),
                        ("样式CSS", "<style>" in content or ".css" in content or "class=" in content),
                        ("脚本JS", "<script>" in content or "function(" in content or ".js" in content)
                    ]
                    
                    for feature_name, check_result in checks:
                        if check_result:
                            result["features_found"].append(feature_name)
                            print(f"    ✓ {feature_name}")
                        else:
                            print(f"    ⚠ {feature_name} 未找到")
                    
                    # 根据项目类别检查特定关键词
                    category_keywords = {
                        "内容生成": ["内容", "生成", "写作", "article", "content"],
                        "金融交易": ["交易", "金融", "token", "crypto", "投资"],
                        "客服支持": ["客服", "支持", "help", "service", "chat"],
                        "数据分析": ["数据", "分析", "analytics", "report", "统计"],
                        "趋势预测": ["趋势", "预测", "market", "trend", "分析"],
                        "编程开发": ["代码", "编程", "开发", "code", "program"],
                        "电商产品": ["产品", "销售", "电商", "shop", "product"],
                        "咨询服务": ["咨询", "服务", "advice", "consult", "方案"]
                    }
                    
                    if category in category_keywords:
                        found_keywords = []
                        for keyword in category_keywords[category]:
                            if keyword in content.lower():
                                found_keywords.append(keyword)
                        
                        if found_keywords:
                            result["features_found"].append(f"类别关键词: {', '.join(found_keywords[:3])}")
                            print(f"    ✓ 类别关键词: {', '.join(found_keywords[:3])}")
                    
                    # 检查页面复杂度
                    line_count = content.count('\n')
                    if line_count > 50:
                        result["features_found"].append("复杂页面")
                        print(f"    ✓ 复杂页面 ({line_count} 行)")
                    else:
                        result["features_found"].append("简单页面")
                        print(f"    ⚠ 简单页面 ({line_count} 行)")
                        
                else:
                    result["status"] = "content_error"
                    result["issues"].append("无法获取页面内容")
                    print(f"  ⚠ 页面内容获取失败")
                    
            elif http_status > 0:
                result["status"] = f"http_{http_status}"
                result["issues"].append(f"HTTP状态码: {http_status}")
                print(f"  ❌ HTTP {http_status}")
            else:
                result["status"] = "connection_error"
                result["issues"].append("连接失败")
                print(f"  ❌ 连接失败")
                
        except Exception as e:
            result["status"] = "error"
            result["issues"].append(f"测试异常: {str(e)}")
            print(f"  ❌ 测试异常: {e}")
        
        self.results.append(result)
        return result
    
    def run_comprehensive_test(self):
        """运行全面测试"""
        print("🤖 AI项目机器人体验测试开始")
        print("=" * 60)
        
        # 定义要测试的项目
        projects = [
            (5000, "AutoContentFactory", "内容生成"),
            (5001, "AI Token Platform", "金融交易"),
            (5002, "AI Customer Service", "客服支持"),
            (5003, "DataAnalyst AI", "数据分析"),
            (5004, "TrendMaster AI", "趋势预测"),
            (5005, "CodeGenius AI", "编程开发"),
            (5006, "AI Digital Products", "电商产品"),
            (5007, "AI Trading Signal", "金融交易"),
            (5008, "AI Data Consulting", "咨询服务")
        ]
        
        # 测试所有项目
        for port, name, category in projects:
            self.test_project(port, name, category)
            time.sleep(0.3)  # 避免过载
        
        # 生成报告
        self.generate_report()
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("📊 机器人体验测试报告")
        print("=" * 60)
        
        total = len(self.results)
        online = sum(1 for r in self.results if r["status"] == "online")
        errors = total - online
        
        print(f"📈 总体状态: {online}/{total} 个项目在线")
        print(f"⏱ 测试耗时: {(datetime.now() - self.start_time).total_seconds():.1f}秒")
        
        # 详细结果表格
        print("\n🔍 项目详情:")
        print("-" * 80)
        print(f"{'项目':<20} {'状态':<12} {'响应时间':<10} {'页面大小':<10} {'功能数':<8}")
        print("-" * 80)
        
        for result in self.results:
            status_display = "✅ 在线" if result["status"] == "online" else "❌ 异常"
            response_time = f"{result['response_time']}ms"
            page_size = f"{result['page_size']}字节"
            feature_count = len(result["features_found"])
            
            print(f"{result['project']:<20} {status_display:<12} {response_time:<10} {page_size:<10} {feature_count:<8}")
        
        # 功能分析
        print("\n⚡ 功能分析:")
        all_features = []
        for result in self.results:
            all_features.extend(result["features_found"])
        
        from collections import Counter
        feature_counts = Counter(all_features)
        
        print("最常见功能:")
        for feature, count in feature_counts.most_common(10):
            print(f"  {feature}: {count} 个项目")
        
        # 性能分析
        response_times = [r["response_time"] for r in self.results if r["response_time"] > 0]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            print(f"\n📊 性能统计:")
            print(f"  平均响应时间: {avg_time:.2f}ms")
            print(f"  最快响应: {min(response_times):.2f}ms")
            print(f"  最慢响应: {max(response_times):.2f}ms")
        
        # 保存报告
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_projects": total,
            "online_projects": online,
            "error_projects": errors,
            "performance": {
                "avg_response_time": avg_time if response_times else 0,
                "min_response_time": min(response_times) if response_times else 0,
                "max_response_time": max(response_times) if response_times else 0
            },
            "results": self.results
        }
        
        with open("bot_experience_report.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 详细报告已保存: bot_experience_report.json")
        
        # 用户体验评分
        print("\n🎯 用户体验评分:")
        if online == total:
            print("  ✅ 优秀 - 所有项目可访问，功能完整")
            print("  建议: 立即开始营销推广，用户体验良好")
        elif online >= total * 0.8:
            print("  👍 良好 - 大部分项目可访问")
            print("  建议: 修复少数问题项目后开始营销")
        elif online >= total * 0.6:
            print("  ⚠️ 一般 - 部分项目有问题")
            print("  建议: 先修复主要问题再开始营销")
        else:
            print("  ❌ 较差 - 多数项目不可用")
            print("  建议: 全面检查技术问题")
        
        # 营销建议
        print("\n🚀 营销建议:")
        working_projects = [r for r in self.results if r["status"] == "online"]
        if working_projects:
            print(f"  可立即推广的项目 ({len(working_projects)}个):")
            for project in working_projects[:5]:  # 显示前5个
                print(f"    • {project['project']} - {project['category']}")
            
            if len(working_projects) > 5:
                print(f"    • ... 还有 {len(working_projects) - 5} 个项目")

if __name__ == "__main__":
    tester = BotExperienceTesterSimple()
    tester.run_comprehensive_test()
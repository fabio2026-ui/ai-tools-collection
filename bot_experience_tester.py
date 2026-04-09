#!/usr/bin/env python3
"""
AI项目机器人体验测试系统
模拟真实用户访问每个项目，测试功能完整性
"""

import requests
import json
import time
from datetime import datetime

class BotExperienceTester:
    def __init__(self):
        self.results = []
        self.start_time = datetime.now()
        
    def test_project(self, port, project_name, expected_features):
        """测试单个项目"""
        print(f"\n🔍 测试项目: {project_name} (端口 {port})")
        
        result = {
            "project": project_name,
            "port": port,
            "timestamp": datetime.now().isoformat(),
            "status": "unknown",
            "response_time": 0,
            "features_tested": [],
            "issues": []
        }
        
        try:
            # 测试1: 基本连接
            start = time.time()
            response = requests.get(f"http://localhost:{port}", timeout=5)
            response_time = time.time() - start
            
            result["response_time"] = round(response_time * 1000, 2)  # 毫秒
            
            if response.status_code == 200:
                result["status"] = "online"
                print(f"  ✅ 连接成功 ({response_time:.2f}s)")
                
                # 测试2: 页面内容检查
                content = response.text
                
                # 检查关键元素
                checks = [
                    ("标题", "赚钱研究控制面板" in content or "AI" in content or "项目" in content),
                    ("HTML结构", "<html>" in content and "</html>" in content),
                    ("功能链接", any(link in content for link in ["href=", "button", "form", "input"])),
                    ("JavaScript", "<script>" in content or "function" in content),
                    ("CSS样式", "<style>" in content or ".css" in content or "class=" in content)
                ]
                
                for feature_name, check_result in checks:
                    if check_result:
                        result["features_tested"].append(f"{feature_name}: 存在")
                        print(f"    ✓ {feature_name}")
                    else:
                        result["features_tested"].append(f"{feature_name}: 缺失")
                        result["issues"].append(f"{feature_name} 未找到")
                        print(f"    ⚠ {feature_name} 未找到")
                
                # 测试3: API端点（如果存在）
                api_endpoints = [
                    f"http://localhost:{port}/api/status",
                    f"http://localhost:{port}/api/health",
                    f"http://localhost:{port}/status"
                ]
                
                for api_url in api_endpoints:
                    try:
                        api_resp = requests.get(api_url, timeout=3)
                        if api_resp.status_code == 200:
                            result["features_tested"].append(f"API端点: {api_url}")
                            print(f"    ✓ API端点: {api_url.split('/')[-1]}")
                    except:
                        pass
                
                # 测试4: 交互功能模拟
                if "form" in content.lower() or "input" in content.lower():
                    result["features_tested"].append("交互表单: 存在")
                    print(f"    ✓ 交互表单功能")
                else:
                    result["features_tested"].append("交互表单: 简单展示")
                    print(f"    ⚠ 简单展示页面")
                    
            else:
                result["status"] = "error"
                result["issues"].append(f"HTTP状态码: {response.status_code}")
                print(f"  ❌ 连接失败: HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            result["status"] = "timeout"
            result["issues"].append("连接超时")
            print(f"  ❌ 连接超时")
        except requests.exceptions.ConnectionError:
            result["status"] = "connection_error"
            result["issues"].append("连接错误")
            print(f"  ❌ 连接错误")
        except Exception as e:
            result["status"] = "error"
            result["issues"].append(f"异常: {str(e)}")
            print(f"  ❌ 测试异常: {e}")
        
        self.results.append(result)
        return result
    
    def run_comprehensive_test(self):
        """运行全面测试"""
        print("🤖 AI项目机器人体验测试开始")
        print("=" * 50)
        
        # 定义要测试的项目
        projects = [
            (5000, "AutoContentFactory", ["内容生成", "AI写作", "自动化"]),
            (5001, "AI Token Platform", ["加密货币", "交易", "金融"]),
            (5002, "AI Customer Service", ["客服", "聊天", "支持"]),
            (5003, "DataAnalyst AI", ["数据分析", "可视化", "报告"]),
            (5004, "TrendMaster AI", ["趋势分析", "预测", "市场"]),
            (5005, "CodeGenius AI", ["编程", "代码生成", "开发"]),
            (5006, "AI Digital Products", ["数字产品", "销售", "电商"]),
            (5007, "AI Trading Signal", ["交易信号", "投资", "金融"]),
            (5008, "AI Data Consulting", ["数据咨询", "分析", "服务"])
        ]
        
        # 测试所有项目
        for port, name, features in projects:
            self.test_project(port, name, features)
            time.sleep(0.5)  # 避免过载
        
        # 生成报告
        self.generate_report()
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 50)
        print("📊 机器人体验测试报告")
        print("=" * 50)
        
        total = len(self.results)
        online = sum(1 for r in self.results if r["status"] == "online")
        errors = sum(1 for r in self.results if r["status"] != "online")
        
        print(f"📈 总体状态: {online}/{total} 个项目在线")
        print(f"⏱ 测试耗时: {(datetime.now() - self.start_time).total_seconds():.1f}秒")
        
        # 详细结果
        print("\n🔍 项目详情:")
        for result in self.results:
            status_icon = "✅" if result["status"] == "online" else "❌"
            print(f"  {status_icon} {result['project']} (端口 {result['port']}):")
            print(f"    状态: {result['status']}")
            print(f"    响应时间: {result['response_time']}ms")
            print(f"    功能测试: {len(result['features_tested'])} 项")
            
            if result["issues"]:
                print(f"    问题: {', '.join(result['issues'][:3])}")
        
        # 性能分析
        response_times = [r["response_time"] for r in self.results if r["response_time"] > 0]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            print(f"\n⚡ 平均响应时间: {avg_time:.2f}ms")
            print(f"🚀 最快响应: {min(response_times):.2f}ms")
            print(f"🐌 最慢响应: {max(response_times):.2f}ms")
        
        # 保存报告
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_projects": total,
            "online_projects": online,
            "error_projects": errors,
            "results": self.results
        }
        
        with open("bot_experience_report.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 报告已保存: bot_experience_report.json")
        
        # 用户体验评分
        if online == total:
            print("\n🎉 用户体验评分: 优秀 (所有项目可访问)")
            print("建议: 立即开始营销推广")
        elif online >= total * 0.7:
            print("\n👍 用户体验评分: 良好 (大部分项目可访问)")
            print("建议: 修复问题项目后开始营销")
        else:
            print("\n⚠️ 用户体验评分: 需要改进")
            print("建议: 先修复技术问题")

if __name__ == "__main__":
    tester = BotExperienceTester()
    tester.run_comprehensive_test()
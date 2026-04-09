#!/usr/bin/env python3
"""
今日头条视频测试 - 简化版Video Agent
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import re
import tempfile
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ToutiaoVideoTester:
    """今日头条视频测试器"""
    
    def __init__(self):
        self.work_dir = tempfile.mkdtemp(prefix="toutiao_test_")
        logger.info(f"工作目录: {self.work_dir}")
        
    def get_video_info(self, url):
        """获取视频信息"""
        logger.info(f"获取视频信息: {url}")
        
        try:
            # 设置请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # 发送请求
            req = urllib.request.Request(url, headers=headers)
            response = urllib.request.urlopen(req, timeout=10)
            html_content = response.read().decode('utf-8', errors='ignore')
            
            # 提取视频信息
            video_info = {
                'url': url,
                'platform': 'toutiao',
                'title': '今日头条视频',
                'duration': '未知',
                'uploader': '今日头条用户',
                'view_count': '未知',
                'like_count': '未知'
            }
            
            # 尝试提取标题
            title_match = re.search(r'<title>(.*?)</title>', html_content)
            if title_match:
                video_info['title'] = title_match.group(1).strip()
                logger.info(f"找到标题: {video_info['title']}")
            
            # 尝试提取视频URL
            video_url_match = re.search(r'video_url["\']?\s*:\s*["\'](https?://[^"\']+)["\']', html_content)
            if video_url_match:
                video_url = video_url_match.group(1)
                logger.info(f"找到视频URL: {video_url}")
                video_info['video_url'] = video_url
            
            # 尝试提取描述
            desc_match = re.search(r'description["\']?\s*:\s*["\']([^"\']+)["\']', html_content)
            if desc_match:
                video_info['description'] = desc_match.group(1)
                logger.info(f"找到描述: {video_info['description'][:100]}...")
            
            return video_info
            
        except Exception as e:
            logger.error(f"获取视频信息失败: {e}")
            return None
    
    def analyze_content(self, video_info):
        """分析内容（模拟DeepSeek）"""
        logger.info("分析视频内容...")
        
        # 模拟DeepSeek分析
        analysis_result = {
            'analysis_type': 'summary',
            'summary': f"这是一个来自今日头条的视频，标题为'{video_info.get('title', '未知标题')}'。",
            'key_points': [
                "视频来自今日头条平台",
                "移动端优化页面",
                "适合社交媒体传播"
            ],
            'topics': ['今日头条', '短视频', '社交媒体'],
            'recommendations': [
                "检查视频是否适合目标受众",
                "考虑视频的传播潜力",
                "评估内容质量"
            ]
        }
        
        # 如果有描述，添加到分析
        if 'description' in video_info:
            analysis_result['summary'] += f" 描述: {video_info['description'][:200]}..."
        
        return analysis_result
    
    def generate_report(self, video_info, analysis_result):
        """生成报告"""
        logger.info("生成分析报告...")
        
        report_file = os.path.join(self.work_dir, 'toutiao_analysis_report.md')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# 今日头条视频分析报告\n\n")
            f.write(f"## 视频信息\n")
            f.write(f"- **标题**: {video_info.get('title', '未知')}\n")
            f.write(f"- **平台**: {video_info.get('platform', '未知')}\n")
            f.write(f"- **URL**: {video_info.get('url', '未知')}\n")
            
            if 'video_url' in video_info:
                f.write(f"- **视频直链**: {video_info['video_url']}\n")
            
            if 'description' in video_info:
                f.write(f"- **描述**: {video_info['description'][:200]}...\n")
            
            f.write(f"\n## 内容分析\n")
            f.write(f"**分析类型**: {analysis_result.get('analysis_type', 'summary')}\n\n")
            
            f.write(f"### 内容摘要\n")
            f.write(f"{analysis_result.get('summary', '无摘要')}\n\n")
            
            if 'key_points' in analysis_result:
                f.write(f"### 关键要点\n")
                for i, point in enumerate(analysis_result['key_points'], 1):
                    f.write(f"{i}. {point}\n")
                f.write("\n")
            
            if 'topics' in analysis_result:
                f.write(f"### 主题标签\n")
                f.write(f"{', '.join(analysis_result['topics'])}\n\n")
            
            if 'recommendations' in analysis_result:
                f.write(f"### 建议\n")
                for i, rec in enumerate(analysis_result['recommendations'], 1):
                    f.write(f"{i}. {rec}\n")
                f.write("\n")
            
            f.write(f"## 技术信息\n")
            f.write(f"- **分析时间**: {video_info.get('analysis_time', '未知')}\n")
            f.write(f"- **工作目录**: {self.work_dir}\n")
            f.write(f"- **报告文件**: {report_file}\n")
        
        logger.info(f"报告生成: {report_file}")
        return report_file
    
    def generate_json(self, video_info, analysis_result):
        """生成JSON数据"""
        logger.info("生成JSON数据...")
        
        json_file = os.path.join(self.work_dir, 'analysis_data.json')
        
        data = {
            'video_info': video_info,
            'analysis_result': analysis_result,
            'technical_info': {
                'work_dir': self.work_dir,
                'platform': 'toutiao',
                'analysis_method': 'simulated_deepseek'
            }
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"JSON数据生成: {json_file}")
        return json_file
    
    def process_video(self, url):
        """处理视频"""
        logger.info(f"🚀 开始处理今日头条视频: {url}")
        
        try:
            # 1. 获取视频信息
            video_info = self.get_video_info(url)
            if not video_info:
                logger.error("获取视频信息失败")
                return None
            
            # 添加分析时间
            import datetime
            video_info['analysis_time'] = datetime.datetime.now().isoformat()
            
            # 2. 分析内容
            analysis_result = self.analyze_content(video_info)
            
            # 3. 生成报告
            report_file = self.generate_report(video_info, analysis_result)
            
            # 4. 生成JSON
            json_file = self.generate_json(video_info, analysis_result)
            
            # 5. 准备结果
            result = {
                'success': True,
                'video_info': video_info,
                'analysis_result': analysis_result,
                'output_files': {
                    'report': report_file,
                    'json': json_file
                },
                'work_dir': self.work_dir
            }
            
            logger.info("🎉 视频处理完成!")
            return result
            
        except Exception as e:
            logger.error(f"视频处理失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def cleanup(self):
        """清理临时文件"""
        try:
            import shutil
            if os.path.exists(self.work_dir):
                # 保留输出文件，只清理临时文件
                logger.info(f"清理工作目录: {self.work_dir}")
                # 这里可以选择是否删除工作目录
                # shutil.rmtree(self.work_dir)
        except Exception as e:
            logger.warning(f"清理失败: {e}")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python3 test_toutiao_video.py <视频URL>")
        print("示例: python3 test_toutiao_video.py https://m.toutiao.com/is/fipbBbpELUE/")
        return 1
    
    url = sys.argv[1]
    
    print(f"🚀 测试今日头条视频: {url}")
    print("=" * 50)
    
    tester = ToutiaoVideoTester()
    
    try:
        result = tester.process_video(url)
        
        if result:
            print(f"\n✅ 测试成功!")
            print(f"📹 视频标题: {result['video_info'].get('title', '未知')}")
            print(f"🌐 平台: {result['video_info'].get('platform', '未知')}")
            print(f"📊 分析类型: {result['analysis_result'].get('analysis_type', '未知')}")
            
            print(f"\n📂 输出文件:")
            for file_type, file_path in result['output_files'].items():
                file_name = os.path.basename(file_path)
                print(f"  • {file_type}: {file_name}")
            
            print(f"\n📋 内容摘要:")
            summary = result['analysis_result'].get('summary', '无摘要')
            print(summary[:300] + "..." if len(summary) > 300 else summary)
            
            print(f"\n📁 工作目录: {result['work_dir']}")
            print("=" * 50)
            
            # 显示报告内容
            report_path = result['output_files']['report']
            print(f"\n📄 报告预览:")
            try:
                with open(report_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(content[:500] + "..." if len(content) > 500 else content)
            except:
                print("无法读取报告文件")
            
            return 0
        else:
            print("❌ 测试失败")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️  用户中断")
        return 130
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        return 1
    finally:
        # 可以选择是否清理
        # tester.cleanup()
        pass

if __name__ == "__main__":
    sys.exit(main())
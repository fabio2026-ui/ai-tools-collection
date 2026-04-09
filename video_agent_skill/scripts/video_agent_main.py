#!/usr/bin/env python3
"""
Video Agent 主程序 - 视频处理代理
"""

import os
import sys
import json
import argparse
import tempfile
import logging
from pathlib import Path
import shutil

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from video_downloader import VideoDownloader
from subtitle_processor import SubtitleProcessor
from content_analyzer import ContentAnalyzer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VideoAgent:
    """视频代理主类"""
    
    def __init__(self, config=None):
        """初始化视频代理"""
        self.config = config or {}
        self.work_dir = tempfile.mkdtemp(prefix="video_agent_")
        logger.info(f"工作目录: {self.work_dir}")
        
        # 初始化组件
        self.downloader = VideoDownloader(config)
        self.processor = SubtitleProcessor(config)
        self.analyzer = ContentAnalyzer(config)
        
        # 处理结果
        self.results = {
            'video_info': None,
            'video_file': None,
            'subtitle_files': [],
            'analysis_result': None,
            'output_files': []
        }
    
    def process_video(self, url, options=None):
        """处理视频主流程"""
        options = options or {}
        
        logger.info(f"开始处理视频: {url}")
        logger.info(f"选项: {options}")
        
        try:
            # 1. 获取视频信息
            logger.info("步骤1: 获取视频信息")
            video_info = self.downloader.get_video_info(url)
            if not video_info:
                logger.error("获取视频信息失败")
                return None
            
            self.results['video_info'] = video_info
            logger.info(f"视频信息获取成功: {video_info['title']}")
            
            # 2. 下载视频
            logger.info("步骤2: 下载视频")
            output_path = os.path.join(self.work_dir, 'video.%(ext)s')
            video_file = self.downloader.download_video(
                url, 
                output_path,
                quality=options.get('quality', 'best'),
                format=options.get('format', 'mp4')
            )
            
            if not video_file:
                logger.error("视频下载失败")
                return None
            
            self.results['video_file'] = video_file
            logger.info(f"视频下载成功: {video_file}")
            
            # 3. 处理字幕
            logger.info("步骤3: 处理字幕")
            subtitle_files = []
            
            # 尝试下载现有字幕
            if options.get('download_subtitles', True):
                downloaded_subs = self.downloader.download_subtitles(
                    url,
                    languages=options.get('languages', ['zh', 'en']),
                    output_dir=self.work_dir
                )
                subtitle_files.extend(downloaded_subs)
            
            # 如果没找到字幕，尝试生成
            if not subtitle_files and options.get('generate_subtitles', True):
                logger.info("未找到现有字幕，尝试生成字幕...")
                generated = self.processor.generate_subtitles_with_whisper(
                    video_file,
                    language=options.get('language', 'auto'),
                    model=options.get('whisper_model', 'base')
                )
                
                if generated:
                    subtitle_files.append({
                        'language': generated.get('language', 'auto'),
                        'file': generated['file'],
                        'generated': True,
                        'segments': generated.get('segments', 0)
                    })
            
            self.results['subtitle_files'] = subtitle_files
            logger.info(f"字幕处理完成: {len(subtitle_files)} 个字幕文件")
            
            # 4. 内容分析
            logger.info("步骤4: 内容分析")
            
            # 准备分析内容
            analysis_content = ""
            
            # 添加视频信息
            analysis_content += f"视频标题: {video_info['title']}\n"
            analysis_content += f"视频时长: {video_info['duration']} 秒\n"
            analysis_content += f"上传者: {video_info['uploader']}\n"
            analysis_content += f"平台: {video_info['platform']}\n\n"
            
            # 添加字幕内容
            if subtitle_files:
                for sub in subtitle_files:
                    if isinstance(sub, dict) and 'file' in sub:
                        try:
                            with open(sub['file'], 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # 如果是SRT格式，转换为纯文本
                            if sub['file'].endswith('.srt'):
                                # 简单转换：移除序号和时间戳
                                lines = []
                                for line in content.split('\n'):
                                    line = line.strip()
                                    if not line or line.isdigit() or '-->' in line:
                                        continue
                                    lines.append(line)
                                content = '\n'.join(lines)
                            
                            lang = sub.get('language', 'unknown')
                            analysis_content += f"字幕内容 ({lang}):\n{content}\n\n"
                        except Exception as e:
                            logger.warning(f"读取字幕文件失败: {e}")
            
            # 调用分析器
            analysis_result = self.analyzer.analyze_content(
                analysis_content,
                analysis_type=options.get('analysis_type', 'summary'),
                custom_prompt=options.get('custom_prompt')
            )
            
            self.results['analysis_result'] = analysis_result
            logger.info(f"内容分析完成: {analysis_result.get('analysis_type', 'unknown')}")
            
            # 5. 生成输出
            logger.info("步骤5: 生成输出")
            output_files = self._generate_outputs(options)
            self.results['output_files'] = output_files
            
            # 6. 清理（如果配置了）
            if options.get('cleanup', True):
                logger.info("步骤6: 清理临时文件")
                self._cleanup_files(video_file, subtitle_files)
            
            logger.info("🎉 视频处理完成!")
            return self.results
            
        except Exception as e:
            logger.error(f"视频处理失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _generate_outputs(self, options):
        """生成输出文件"""
        output_files = []
        output_dir = options.get('output_dir', self.work_dir)
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. 生成分析报告
        if self.results['analysis_result']:
            report_file = os.path.join(output_dir, 'analysis_report.md')
            
            with open(report_file, 'w', encoding='utf-8') as f:
                # 视频信息
                video_info = self.results['video_info']
                f.write(f"# 视频分析报告\n\n")
                f.write(f"## 视频信息\n")
                f.write(f"- **标题**: {video_info['title']}\n")
                f.write(f"- **时长**: {video_info['duration']} 秒\n")
                f.write(f"- **上传者**: {video_info['uploader']}\n")
                f.write(f"- **平台**: {video_info['platform']}\n")
                f.write(f"- **观看数**: {video_info.get('view_count', 'N/A')}\n")
                f.write(f"- **点赞数**: {video_info.get('like_count', 'N/A')}\n\n")
                
                # 分析结果
                analysis = self.results['analysis_result']
                f.write(f"## 内容分析\n")
                f.write(f"**分析类型**: {analysis.get('analysis_type', 'summary')}\n\n")
                
                if 'summary' in analysis:
                    f.write(f"### 内容摘要\n")
                    f.write(f"{analysis['summary']}\n\n")
                
                if 'key_points' in analysis:
                    f.write(f"### 关键要点\n")
                    for i, point in enumerate(analysis['key_points'], 1):
                        f.write(f"{i}. {point}\n")
                    f.write("\n")
                
                if 'topics' in analysis:
                    f.write(f"### 主题标签\n")
                    f.write(f"{', '.join(analysis['topics'])}\n\n")
                
                if 'recommendations' in analysis:
                    f.write(f"### 建议\n")
                    for i, rec in enumerate(analysis['recommendations'], 1):
                        f.write(f"{i}. {rec}\n")
                    f.write("\n")
                
                # 字幕信息
                if self.results['subtitle_files']:
                    f.write(f"## 字幕信息\n")
                    f.write(f"共 {len(self.results['subtitle_files'])} 个字幕文件:\n")
                    for sub in self.results['subtitle_files']:
                        lang = sub.get('language', 'unknown')
                        generated = " (生成)" if sub.get('generated') else ""
                        f.write(f"- {lang}{generated}\n")
            
            output_files.append({
                'type': 'report',
                'file': report_file,
                'format': 'markdown'
            })
            logger.info(f"分析报告生成: {report_file}")
        
        # 2. 生成纯文本脚本
        if self.results['subtitle_files']:
            for sub in self.results['subtitle_files']:
                if isinstance(sub, dict) and 'file' in sub:
                    input_file = sub['file']
                    lang = sub.get('language', 'unknown')
                    
                    # 转换为TXT格式
                    txt_file = os.path.join(output_dir, f'script_{lang}.txt')
                    
                    try:
                        with open(input_file, 'r', encoding='utf-8') as f_in:
                            content = f_in.read()
                        
                        # 如果是SRT，转换为纯文本
                        if input_file.endswith('.srt'):
                            lines = []
                            for line in content.split('\n'):
                                line = line.strip()
                                if not line or line.isdigit() or '-->' in line:
                                    continue
                                lines.append(line)
                            content = '\n'.join(lines)
                        
                        with open(txt_file, 'w', encoding='utf-8') as f_out:
                            f_out.write(content)
                        
                        output_files.append({
                            'type': 'script',
                            'file': txt_file,
                            'language': lang,
                            'format': 'txt'
                        })
                        logger.info(f"脚本文件生成: {txt_file}")
                        
                    except Exception as e:
                        logger.warning(f"生成脚本文件失败: {e}")
        
        # 3. 生成JSON格式结果
        json_file = os.path.join(output_dir, 'result.json')
        try:
            # 准备JSON数据
            json_data = {
                'video_info': self.results['video_info'],
                'subtitle_count': len(self.results['subtitle_files']),
                'analysis': self.results['analysis_result'],
                'output_files': [
                    {
                        'type': file_info.get('type'),
                        'file': file_info.get('file'),
                        'format': file_info.get('format')
                    }
                    for file_info in output_files
                ]
            }
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            output_files.append({
                'type': 'data',
                'file': json_file,
                'format': 'json'
            })
            logger.info(f"JSON结果生成: {json_file}")
            
        except Exception as e:
            logger.warning(f"生成JSON文件失败: {e}")
        
        return output_files
    
    def _cleanup_files(self, video_file, subtitle_files):
        """清理文件"""
        try:
            # 删除视频文件
            if video_file and os.path.exists(video_file):
                os.remove(video_file)
                logger.info(f"删除视频文件: {video_file}")
            
            # 删除字幕文件
            for sub in subtitle_files:
                if isinstance(sub, dict) and 'file' in sub:
                    file_path = sub['file']
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.info(f"删除字幕文件: {file_path}")
            
            # 删除工作目录（保留输出文件）
            # 注意：输出文件已经在外部目录，所以可以删除工作目录
            if os.path.exists(self.work_dir):
                # 检查是否还有文件
                remaining_files = list(Path(self.work_dir).rglob('*'))
                if not remaining_files:
                    shutil.rmtree(self.work_dir)
                    logger.info(f"删除工作目录: {self.work_dir}")
                else:
                    logger.warning(f"工作目录还有文件，不删除: {self.work_dir}")
                    
        except Exception as e:
            logger.warning(f"清理文件失败: {e}")
    
    def cleanup(self):
        """清理所有临时文件"""
        try:
            if os.path.exists(self.work_dir):
                shutil.rmtree(self.work_dir)
                logger.info(f"清理工作目录: {self.work_dir}")
        except Exception as e:
            logger.warning(f"清理工作目录失败: {e}")
    
    def __del__(self):
        """析构函数"""
        self.cleanup()

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='Video Agent - 视频处理代理')
    
    # 必需参数
    parser.add_argument('url', help='视频URL')
    
    # 输出选项
    parser.add_argument('--output-dir', '-o', default='./output',
                       help='输出目录 (默认: ./output)')
    parser.add_argument('--output-format', default='all',
                       choices=['all', 'report', 'script', 'json'],
                       help='输出格式 (默认: all)')
    
    # 下载选项
    parser.add_argument('--quality', default='best',
                       choices=['best', 'worst', '720p', '1080p'],
                       help='视频质量 (默认: best)')
    parser.add_argument('--format', default='mp4',
                       choices=['mp4', 'webm', 'mkv'],
                       help='视频格式 (默认: mp4)')
    
    # 字幕选项
    parser.add_argument('--languages', nargs='+', default=['zh', 'en'],
                       help='字幕语言 (默认: zh en)')
    parser.add_argument('--download-subtitles', action='store_true', default=True,
                       help='下载字幕 (默认: 开启)')
    parser.add_argument('--generate-subtitles', action='store_true', default=True,
                       help='生成字幕 (默认: 开启)')
    parser.add_argument('--whisper-model', default='base',
                       choices=['tiny', 'base', 'small', 'medium', 'large'],
                       help='Whisper模型 (默认: base)')
    
    # 分析选项
    parser.add_argument('--analysis-type', default='summary',
                       choices=['summary', 'detailed', 'educational', 'meeting'],
                       help='分析类型 (默认: summary)')
    parser.add_argument('--custom-prompt',
                       help='自定义分析提示')
    
    # 清理选项
    parser.add_argument('--cleanup', action='store_true', default=True,
                       help='处理完成后清理临时文件 (默认: 开启)')
    parser.add_argument('--no-cleanup', dest='cleanup', action='store_false',
                       help='不清理临时文件')
    
    # 其他选项
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='详细输出')
    
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_arguments()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info(f"🚀 启动 Video Agent")
    logger.info(f"视频URL: {args.url}")
    
    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 准备选项
    options = {
        'output_dir': args.output_dir,
        'quality': args.quality,
        'format': args.format,
        'languages': args.languages,
        'download_subtitles': args.download_subtitles,
        'generate_subtitles': args.generate_subtitles,
        'whisper_model': args.whisper_model,
        'analysis_type': args.analysis_type,
        'custom_prompt': args.custom_prompt,
        'cleanup': args.cleanup
    }
    
    # 创建并运行Video Agent
    agent = VideoAgent()
    
    try:
        result = agent.process_video(args.url, options)
        
        if result:
            print(f"\n🎉 视频处理完成!")
            print(f"📹 视频标题: {result['video_info']['title']}")
            print(f"⏱️  视频时长: {result['video_info']['duration']} 秒")
            print(f"📝 字幕文件: {len(result['subtitle_files'])} 个")
            print(f"📊 分析类型: {result['analysis_result'].get('analysis_type', 'unknown')}")
            print(f"📁 输出文件: {len(result['output_files'])} 个")
            
            print(f"\n📂 输出目录: {args.output_dir}")
            for output in result['output_files']:
                file_type = output.get('type', 'unknown')
                file_path = output.get('file', '')
                file_name = os.path.basename(file_path)
                print(f"  • {file_type}: {file_name}")
            
            # 显示分析摘要
            if 'summary' in result['analysis_result']:
                print(f"\n📋 内容摘要:")
                print(result['analysis_result']['summary'][:500] + "...")
            
            return 0
        else:
            print("❌ 视频处理失败")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️  用户中断")
        return 130
    except Exception as e:
        print(f"❌ 处理异常: {e}")
        import traceback
        traceback.print_exc()
        return 1
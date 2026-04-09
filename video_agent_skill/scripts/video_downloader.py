#!/usr/bin/env python3
"""
视频下载器 - 支持多平台的视频下载
"""

import os
import sys
import subprocess
import tempfile
import json
import re
from urllib.parse import urlparse
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VideoDownloader:
    """视频下载器类"""
    
    def __init__(self, config=None):
        """初始化下载器"""
        self.config = config or {}
        self.temp_dir = tempfile.mkdtemp(prefix="video_agent_")
        logger.info(f"临时目录: {self.temp_dir}")
        
        # 检查yt-dlp是否安装
        self._check_dependencies()
    
    def _check_dependencies(self):
        """检查依赖"""
        try:
            subprocess.run(["yt-dlp", "--version"], 
                         capture_output=True, check=True)
            logger.info("✅ yt-dlp 已安装")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("❌ yt-dlp 未安装，请先安装: pip install yt-dlp")
            sys.exit(1)
    
    def detect_platform(self, url):
        """检测视频平台"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        platform_map = {
            'youtube.com': 'youtube',
            'youtu.be': 'youtube',
            'bilibili.com': 'bilibili',
            'b23.tv': 'bilibili',
            'tiktok.com': 'tiktok',
            'douyin.com': 'douyin',
            'vimeo.com': 'vimeo',
            'dailymotion.com': 'dailymotion',
            'twitch.tv': 'twitch',
            'facebook.com': 'facebook',
            'instagram.com': 'instagram'
        }
        
        for key, platform in platform_map.items():
            if key in domain:
                return platform
        
        # 检查是否是本地文件或直接视频链接
        if url.startswith('file://') or url.endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
            return 'local'
        
        return 'unknown'
    
    def get_video_info(self, url):
        """获取视频信息"""
        logger.info(f"获取视频信息: {url}")
        
        try:
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-playlist',
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                logger.error(f"获取信息失败: {result.stderr}")
                return None
            
            info = json.loads(result.stdout)
            
            # 提取关键信息
            video_info = {
                'title': info.get('title', '未知标题'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', '未知上传者'),
                'view_count': info.get('view_count', 0),
                'like_count': info.get('like_count', 0),
                'description': info.get('description', '')[:500],  # 限制长度
                'thumbnail': info.get('thumbnail', ''),
                'formats': self._extract_formats(info),
                'subtitles': self._extract_subtitles(info),
                'platform': self.detect_platform(url)
            }
            
            logger.info(f"视频信息获取成功: {video_info['title']} ({video_info['duration']}秒)")
            return video_info
            
        except subprocess.TimeoutExpired:
            logger.error("获取视频信息超时")
            return None
        except json.JSONDecodeError:
            logger.error("解析视频信息失败")
            return None
        except Exception as e:
            logger.error(f"获取视频信息异常: {e}")
            return None
    
    def _extract_formats(self, info):
        """提取可用格式"""
        formats = []
        
        if 'formats' in info:
            for fmt in info['formats']:
                if fmt.get('vcodec') != 'none':  # 只包含视频格式
                    formats.append({
                        'format_id': fmt.get('format_id', ''),
                        'ext': fmt.get('ext', ''),
                        'resolution': fmt.get('resolution', ''),
                        'filesize': fmt.get('filesize', 0),
                        'fps': fmt.get('fps', 0),
                        'vcodec': fmt.get('vcodec', ''),
                        'acodec': fmt.get('acodec', '')
                    })
        
        # 按文件大小排序（从小到大）
        formats.sort(key=lambda x: x.get('filesize', 0))
        return formats[:10]  # 返回前10个格式
    
    def _extract_subtitles(self, info):
        """提取字幕信息"""
        subtitles = []
        
        if 'subtitles' in info:
            for lang, sub_list in info['subtitles'].items():
                for sub in sub_list:
                    if sub.get('ext') in ['vtt', 'srt', 'ass', 'lrc']:
                        subtitles.append({
                            'language': lang,
                            'name': sub.get('name', ''),
                            'ext': sub.get('ext', ''),
                            'url': sub.get('url', '')
                        })
        
        if 'automatic_captions' in info:
            for lang, sub_list in info['automatic_captions'].items():
                for sub in sub_list:
                    if sub.get('ext') in ['vtt', 'srt']:
                        subtitles.append({
                            'language': lang,
                            'name': f"自动生成 - {lang}",
                            'ext': sub.get('ext', ''),
                            'url': sub.get('url', ''),
                            'auto_generated': True
                        })
        
        return subtitles
    
    def download_video(self, url, output_path=None, quality='best', format='mp4'):
        """下载视频"""
        logger.info(f"开始下载视频: {url}")
        
        if output_path is None:
            output_path = os.path.join(self.temp_dir, 'video.%(ext)s')
        
        # 构建yt-dlp命令
        cmd = [
            'yt-dlp',
            '-o', output_path,
            '--no-playlist',
            '--progress',
            '--newline'
        ]
        
        # 添加质量选项
        if quality == 'best':
            cmd.extend(['-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'])
        elif quality == 'worst':
            cmd.extend(['-f', 'worst'])
        elif quality.startswith('res:'):
            resolution = quality.split(':')[1]
            cmd.extend(['-f', f'bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]'])
        else:
            cmd.extend(['-f', quality])
        
        # 添加格式选项
        if format:
            cmd.extend(['--recode-video', format])
        
        # 添加重试选项
        cmd.extend(['--retries', '3'])
        
        # 添加超时选项
        cmd.extend(['--socket-timeout', '30'])
        
        cmd.append(url)
        
        logger.info(f"执行命令: {' '.join(cmd)}")
        
        try:
            # 执行下载
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # 实时输出进度
            for line in process.stdout:
                line = line.strip()
                if line:
                    # 解析进度信息
                    if '[download]' in line:
                        logger.info(line)
                    elif 'ERROR' in line or 'WARNING' in line:
                        logger.warning(line)
            
            process.wait()
            
            if process.returncode != 0:
                logger.error(f"视频下载失败，返回码: {process.returncode}")
                return None
            
            # 查找下载的文件
            downloaded_files = []
            for file in os.listdir(self.temp_dir):
                if file.startswith('video.') and file.endswith(('.mp4', '.webm', '.mkv', '.avi', '.mov')):
                    downloaded_files.append(os.path.join(self.temp_dir, file))
            
            if not downloaded_files:
                logger.error("未找到下载的视频文件")
                return None
            
            # 选择第一个文件（应该是主视频文件）
            video_file = downloaded_files[0]
            logger.info(f"视频下载完成: {video_file}")
            
            return video_file
            
        except Exception as e:
            logger.error(f"视频下载异常: {e}")
            return None
    
    def download_subtitles(self, url, languages=None, output_dir=None):
        """下载字幕"""
        logger.info(f"开始下载字幕: {url}")
        
        if output_dir is None:
            output_dir = self.temp_dir
        
        if languages is None:
            languages = ['zh', 'en', 'ja', 'ko']  # 默认语言
        
        subtitle_files = []
        
        for lang in languages:
            try:
                # 下载指定语言的字幕
                cmd = [
                    'yt-dlp',
                    '--write-subs',
                    '--write-auto-subs',
                    '--sub-lang', lang,
                    '--skip-download',
                    '--no-playlist',
                    '-o', os.path.join(output_dir, f'subtitle_{lang}.%(ext)s'),
                    url
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    # 查找下载的字幕文件
                    for file in os.listdir(output_dir):
                        if file.startswith(f'subtitle_{lang}.') and file.endswith(('.vtt', '.srt', '.ass')):
                            subtitle_files.append({
                                'language': lang,
                                'file': os.path.join(output_dir, file)
                            })
                            logger.info(f"字幕下载成功: {lang} -> {file}")
                
            except Exception as e:
                logger.warning(f"下载字幕失败 ({lang}): {e}")
                continue
        
        return subtitle_files
    
    def cleanup(self):
        """清理临时文件"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.info(f"清理临时目录: {self.temp_dir}")
        except Exception as e:
            logger.warning(f"清理临时文件失败: {e}")
    
    def __del__(self):
        """析构函数，自动清理"""
        self.cleanup()

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python video_downloader.py <视频URL> [输出路径]")
        sys.exit(1)
    
    url = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    downloader = VideoDownloader()
    
    # 获取视频信息
    info = downloader.get_video_info(url)
    if info:
        print("\n📹 视频信息:")
        print(f"标题: {info['title']}")
        print(f"时长: {info['duration']} 秒")
        print(f"上传者: {info['uploader']}")
        print(f"平台: {info['platform']}")
        
        # 显示可用格式
        if info['formats']:
            print("\n📋 可用格式:")
            for fmt in info['formats'][:5]:  # 显示前5个
                size_mb = fmt['filesize'] / (1024 * 1024) if fmt['filesize'] else 0
                print(f"  {fmt['format_id']}: {fmt['resolution']} ({size_mb:.1f}MB)")
        
        # 显示字幕
        if info['subtitles']:
            print("\n📝 可用字幕:")
            for sub in info['subtitles'][:5]:  # 显示前5个
                auto = " (自动生成)" if sub.get('auto_generated') else ""
                print(f"  {sub['language']}: {sub['name']}{auto}")
    
    # 下载视频
    print(f"\n⬇️ 开始下载视频...")
    video_file = downloader.download_video(url, output_path)
    
    if video_file:
        print(f"✅ 视频下载完成: {video_file}")
        
        # 下载字幕
        print(f"\n📝 开始下载字幕...")
        subtitles = downloader.download_subtitles(url)
        
        if subtitles:
            print(f"✅ 字幕下载完成 ({len(subtitles)} 个):")
            for sub in subtitles:
                print(f"  {sub['language']}: {sub['file']}")
        else:
            print("⚠️ 未找到可下载的字幕")
        
        return {
            'video_file': video_file,
            'subtitles': subtitles,
            'info': info
        }
    else:
        print("❌ 视频下载失败")
        return None

if __name__ == "__main__":
    result = main()
    if result:
        print(f"\n🎉 处理完成!")
        print(f"视频文件: {result['video_file']}")
        print(f"字幕文件: {len(result['subtitles'])} 个")
    else:
        print("\n❌ 处理失败")
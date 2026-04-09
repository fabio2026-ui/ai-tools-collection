#!/usr/bin/env python3
"""
字幕处理器 - 提取、生成、转换字幕文件
"""

import os
import sys
import json
import argparse
import tempfile
import logging
from pathlib import Path
import subprocess

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SubtitleProcessor:
    """字幕处理器类"""
    
    def __init__(self, config=None):
        """初始化字幕处理器"""
        self.config = config or {}
        self.temp_dir = tempfile.mkdtemp(prefix="subtitle_processor_")
        logger.info(f"临时目录: {self.temp_dir}")
        
        # 检查依赖
        self._check_dependencies()
    
    def _check_dependencies(self):
        """检查依赖"""
        dependencies = ['ffmpeg', 'ffprobe']
        
        for dep in dependencies:
            try:
                subprocess.run([dep, '-version'], capture_output=True, check=True)
                logger.info(f"✓ {dep} 已安装")
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.warning(f"⚠️  {dep} 未安装，某些功能可能受限")
    
    def extract_subtitles(self, video_file, languages=None):
        """从视频中提取字幕"""
        languages = languages or ['zh', 'en']
        extracted_files = []
        
        logger.info(f"从视频中提取字幕: {video_file}")
        
        # 使用ffmpeg提取字幕
        for lang in languages:
            try:
                # 构建输出文件名
                base_name = os.path.splitext(os.path.basename(video_file))[0]
                output_file = os.path.join(self.temp_dir, f"{base_name}_{lang}.srt")
                
                # 提取字幕的命令
                cmd = [
                    'ffmpeg',
                    '-i', video_file,
                    '-map', f'0:s:m:language:{lang}?',
                    output_file,
                    '-y'  # 覆盖输出文件
                ]
                
                logger.debug(f"执行命令: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0 and os.path.exists(output_file):
                    # 检查文件是否为空
                    file_size = os.path.getsize(output_file)
                    if file_size > 100:  # 大于100字节才认为是有效的
                        extracted_files.append({
                            'language': lang,
                            'file': output_file,
                            'size': file_size,
                            'extracted': True
                        })
                        logger.info(f"✓ 提取 {lang} 字幕成功: {output_file} ({file_size} bytes)")
                    else:
                        os.remove(output_file)
                        logger.warning(f"⚠️  提取的 {lang} 字幕文件为空")
                else:
                    logger.warning(f"⚠️  提取 {lang} 字幕失败: {result.stderr[:200]}")
                    
            except Exception as e:
                logger.error(f"提取 {lang} 字幕时出错: {e}")
        
        return extracted_files
    
    def generate_subtitles_with_whisper(self, video_file, language='auto', model='base'):
        """使用Whisper生成字幕"""
        logger.info(f"使用Whisper生成字幕: {video_file}")
        logger.info(f"语言: {language}, 模型: {model}")
        
        try:
            # 检查Whisper是否安装
            try:
                import whisper
                logger.info("✓ Whisper已安装")
            except ImportError:
                logger.error("❌ Whisper未安装，请运行: pip install openai-whisper")
                return None
            
            # 构建输出文件名
            base_name = os.path.splitext(os.path.basename(video_file))[0]
            output_file = os.path.join(self.temp_dir, f"{base_name}_whisper_{model}.srt")
            
            # 加载Whisper模型
            logger.info(f"加载Whisper模型: {model}")
            whisper_model = whisper.load_model(model)
            
            # 转录视频
            logger.info("开始转录视频...")
            result = whisper_model.transcribe(
                video_file,
                language=language if language != 'auto' else None,
                verbose=True
            )
            
            # 保存为SRT格式
            self._save_as_srt(result['segments'], output_file)
            
            logger.info(f"✓ Whisper转录完成: {output_file}")
            
            return {
                'language': result.get('language', language),
                'file': output_file,
                'segments': len(result['segments']),
                'generated': True,
                'model': model
            }
            
        except Exception as e:
            logger.error(f"Whisper生成字幕失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _save_as_srt(self, segments, output_file):
        """将Whisper结果保存为SRT格式"""
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments, 1):
                # 转换时间戳格式
                start_time = self._format_timestamp(segment['start'])
                end_time = self._format_timestamp(segment['end'])
                
                # 写入SRT格式
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{segment['text'].strip()}\n\n")
    
    def _format_timestamp(self, seconds):
        """格式化时间戳为SRT格式 (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds_remainder = seconds % 60
        milliseconds = int((seconds_remainder - int(seconds_remainder)) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{int(seconds_remainder):02d},{milliseconds:03d}"
    
    def convert_subtitle_format(self, input_file, output_format='txt'):
        """转换字幕格式"""
        logger.info(f"转换字幕格式: {input_file} -> {output_format}")
        
        if not os.path.exists(input_file):
            logger.error(f"输入文件不存在: {input_file}")
            return None
        
        # 确定输入格式
        input_ext = os.path.splitext(input_file)[1].lower()
        
        # 构建输出文件名
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = os.path.join(self.temp_dir, f"{base_name}.{output_format}")
        
        try:
            if input_ext == '.srt' and output_format == 'txt':
                # SRT转TXT
                with open(input_file, 'r', encoding='utf-8') as f_in:
                    content = f_in.read()
                
                # 解析SRT格式
                lines = []
                for line in content.split('\n'):
                    line = line.strip()
                    if not line or line.isdigit() or '-->' in line:
                        continue
                    lines.append(line)
                
                text_content = '\n'.join(lines)
                
                with open(output_file, 'w', encoding='utf-8') as f_out:
                    f_out.write(text_content)
                
                logger.info(f"✓ SRT转TXT完成: {output_file}")
                
            elif input_ext == '.txt' and output_format == 'srt':
                # TXT转SRT（简单转换，没有时间戳）
                with open(input_file, 'r', encoding='utf-8') as f_in:
                    lines = f_in.readlines()
                
                with open(output_file, 'w', encoding='utf-8') as f_out:
                    for i, line in enumerate(lines, 1):
                        if line.strip():
                            f_out.write(f"{i}\n")
                            f_out.write(f"00:00:{i-1:02d},000 --> 00:00:{i:02d},000\n")
                            f_out.write(f"{line.strip()}\n\n")
                
                logger.info(f"✓ TXT转SRT完成: {output_file}")
            
            elif input_ext == '.json' and output_format == 'srt':
                # JSON转SRT
                with open(input_file, 'r', encoding='utf-8') as f_in:
                    data = json.load(f_in)
                
                with open(output_file, 'w', encoding='utf-8') as f_out:
                    if 'segments' in data:
                        for i, segment in enumerate(data['segments'], 1):
                            start_time = self._format_timestamp(segment.get('start', 0))
                            end_time = self._format_timestamp(segment.get('end', 0))
                            text = segment.get('text', '')
                            
                            f_out.write(f"{i}\n")
                            f_out.write(f"{start_time} --> {end_time}\n")
                            f_out.write(f"{text.strip()}\n\n")
                
                logger.info(f"✓ JSON转SRT完成: {output_file}")
            
            else:
                logger.warning(f"不支持从 {input_ext} 转换到 {output_format}")
                return None
            
            return {
                'input': input_file,
                'output': output_file,
                'input_format': input_ext[1:],  # 去掉点
                'output_format': output_format
            }
            
        except Exception as e:
            logger.error(f"转换字幕格式失败: {e}")
            return None
    
    def merge_subtitles(self, files, output_file):
        """合并多个字幕文件"""
        logger.info(f"合并字幕文件: {len(files)} 个文件")
        
        try:
            merged_content = []
            
            for i, file_path in enumerate(files):
                if not os.path.exists(file_path):
                    logger.warning(f"文件不存在: {file_path}")
                    continue
                
                # 读取文件内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 根据文件类型处理
                ext = os.path.splitext(file_path)[1].lower()
                
                if ext == '.srt':
                    # 解析SRT并添加到合并内容
                    lines = []
                    for line in content.split('\n'):
                        line = line.strip()
                        if not line or line.isdigit() or '-->' in line:
                            continue
                        lines.append(line)
                    
                    if lines:
                        merged_content.append(f"=== 文件 {i+1}: {os.path.basename(file_path)} ===")
                        merged_content.extend(lines)
                        merged_content.append("")  # 空行分隔
                
                elif ext == '.txt':
                    # 直接添加TXT内容
                    if content.strip():
                        merged_content.append(f"=== 文件 {i+1}: {os.path.basename(file_path)} ===")
                        merged_content.append(content.strip())
                        merged_content.append("")
                
                else:
                    logger.warning(f"不支持的文件格式: {ext}")
            
            # 写入输出文件
            with open(output_file, 'w', encoding='utf-8') as f_out:
                f_out.write('\n'.join(merged_content))
            
            logger.info(f"✓ 合并完成: {output_file}")
            
            return {
                'output': output_file,
                'merged_files': len(files),
                'successful_files': len([f for f in files if os.path.exists(f)])
            }
            
        except Exception as e:
            logger.error(f"合并字幕文件失败: {e}")
            return None
    
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
        print("用法:")
        print("  python subtitle_processor.py extract <视频文件>")
        print("  python subtitle_processor.py generate <视频文件> [语言] [模型]")
        print("  python subtitle_processor.py convert <输入文件> <输出格式>")
        print("  python subtitle_processor.py merge <文件1> <文件2> ... <输出文件>")
        sys.exit(1)
    
    command = sys.argv[1]
    processor = SubtitleProcessor()
    
    if command == 'extract':
        if len(sys.argv) < 3:
            print("错误: 需要视频文件路径")
            sys.exit(1)
        
        video_file = sys.argv[2]
        languages = sys.argv[3:] if len(sys.argv) > 3 else ['zh', 'en']
        
        result = processor.extract_subtitles(video_file, languages)
        if result:
            print(f"✓ 提取完成: {len(result)} 个字幕文件")
            for sub in result:
                print(f"  - {sub['language']}: {sub['file']}")
        else:
            print("❌ 提取失败")
    
    elif command == 'generate':
        if len(sys.argv) < 3:
            print("错误: 需要视频文件路径")
            sys.exit(1)
        
        video_file = sys.argv[2]
        language = sys.argv[3] if len(sys.argv) > 3 else 'auto'
        model = sys.argv[4] if len(sys.argv) > 4 else 'base'
        
        result = processor.generate_subtitles_with_whisper(video_file, language, model)
        if result:
            print(f"✓ 生成完成:")
            print(f"  语言: {result['language']}")
            print(f"  文件: {result['file']}")
            print(f"  段落: {result['segments']}")
            print(f"  模型: {result['model']}")
        else:
            print("❌ 生成失败")
    
    elif command == 'convert':
        if len(sys.argv) < 4:
            print("错误: 需要输入文件和输出格式")
            sys.exit(1)
        
        input_file = sys.argv[2]
        output_format = sys.argv[3]
        
        result = processor.convert_subtitle_format(input_file, output_format)
        if result:
            print(f"✓ 转换完成:")
            print(f"  输入: {result['input']} ({result['input_format']})")
            print(f"  输出: {result['output']} ({result['output_format']})")
        else:
            print("❌ 转换失败")
    
    elif command == 'merge':
        if len(sys.argv) < 4:
            print("错误: 需要至少2个输入文件和1个输出文件")
            sys.exit(1)
        
        input_files = sys.argv[2:-1]
        output_file = sys.argv[-1]
        
        result = processor.merge_subtitles(input_files, output_file)
        if result:
            print(f"✓ 合并完成:")
            print(f"  输出文件: {result['output']}")
            print(f"  尝试合并: {result['merged_files']} 个文件")
            print(f"  成功合并: {result['successful_files']} 个文件")
        else:
            print("❌ 合并失败")
    
    else:
        print(f"错误: 未知命令 '{command}'")
        sys.exit(1)

if __name__ == '__main__':
    main()
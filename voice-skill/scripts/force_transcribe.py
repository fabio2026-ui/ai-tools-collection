#!/usr/bin/env python3
"""
强制转录脚本 - 尝试多种方法处理OGG格式
"""

import os
import sys
import tempfile
import subprocess
import speech_recognition as sr
from pydub import AudioSegment
import io

def convert_ogg_to_wav_pydub(input_path, output_path):
    """使用pydub转换OGG到WAV"""
    try:
        print(f"尝试使用pydub转换: {input_path}")
        audio = AudioSegment.from_file(input_path, format="ogg")
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(output_path, format="wav")
        print(f"转换成功: {output_path}")
        return True
    except Exception as e:
        print(f"pydub转换失败: {e}")
        return False

def convert_ogg_to_wav_ffmpeg(input_path, output_path):
    """尝试使用系统ffmpeg"""
    try:
        print(f"尝试使用系统ffmpeg转换")
        cmd = ["ffmpeg", "-i", input_path, "-ar", "16000", "-ac", "1", "-y", output_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"ffmpeg转换成功")
            return True
        else:
            print(f"ffmpeg转换失败: {result.stderr}")
            return False
    except FileNotFoundError:
        print("ffmpeg未安装")
        return False
    except Exception as e:
        print(f"ffmpeg转换异常: {e}")
        return False

def transcribe_audio(audio_path, language="zh-CN"):
    """转录音频文件"""
    recognizer = sr.Recognizer()
    
    try:
        with sr.AudioFile(audio_path) as source:
            print(f"读取音频文件: {audio_path}")
            audio_data = recognizer.record(source)
            
            print(f"开始语音识别 (语言: {language})...")
            text = recognizer.recognize_google(audio_data, language=language)
            return text
            
    except sr.UnknownValueError:
        return "无法识别语音内容"
    except sr.RequestError as e:
        return f"语音识别服务错误: {e}"
    except Exception as e:
        return f"处理错误: {e}"

def main():
    if len(sys.argv) < 2:
        print("用法: python force_transcribe.py <音频文件路径> [语言代码]")
        print("示例: python force_transcribe.py audio.ogg zh-CN")
        sys.exit(1)
    
    audio_path = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else "zh-CN"
    
    if not os.path.exists(audio_path):
        print(f"文件不存在: {audio_path}")
        sys.exit(1)
    
    print(f"处理音频文件: {audio_path}")
    print(f"语言设置: {language}")
    
    # 检查文件格式
    file_ext = os.path.splitext(audio_path)[1].lower()
    print(f"文件格式: {file_ext}")
    
    # 如果是WAV格式，直接转录
    if file_ext == '.wav':
        print("检测到WAV格式，直接转录...")
        text = transcribe_audio(audio_path, language)
        print(f"\n转录结果: {text}")
        return
    
    # 如果是OGG格式，尝试转换
    if file_ext == '.ogg':
        print("检测到OGG格式，尝试转换...")
        
        # 创建临时WAV文件
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            temp_wav = tmp.name
        
        try:
            # 方法1: 尝试pydub转换
            if convert_ogg_to_wav_pydub(audio_path, temp_wav):
                text = transcribe_audio(temp_wav, language)
                print(f"\n转录结果: {text}")
                return
            
            # 方法2: 尝试ffmpeg转换
            if convert_ogg_to_wav_ffmpeg(audio_path, temp_wav):
                text = transcribe_audio(temp_wav, language)
                print(f"\n转录结果: {text}")
                return
            
            # 方法3: 尝试直接读取（如果pydub支持）
            print("尝试直接处理OGG...")
            try:
                audio = AudioSegment.from_file(audio_path, format="ogg")
                # 转换为WAV字节流
                wav_bytes = io.BytesIO()
                audio.export(wav_bytes, format="wav")
                wav_bytes.seek(0)
                
                # 使用speech_recognition处理字节流
                recognizer = sr.Recognizer()
                with sr.AudioFile(wav_bytes) as source:
                    audio_data = recognizer.record(source)
                    text = recognizer.recognize_google(audio_data, language=language)
                    print(f"\n转录结果: {text}")
                    return
            except Exception as e:
                print(f"直接处理失败: {e}")
            
            print("所有转换方法都失败了")
            print("请手动转换文件格式或使用在线转换工具")
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_wav):
                os.unlink(temp_wav)
    
    else:
        print(f"不支持的文件格式: {file_ext}")
        print("支持的格式: .wav, .ogg")

if __name__ == "__main__":
    main()
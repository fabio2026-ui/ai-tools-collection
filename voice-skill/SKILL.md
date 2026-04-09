---
name: voice-skill
description: 语音技能 - 语音转文字 + 文字转语音 (无需API，无需ffmpeg版本)
homepage: https://openclaw.ai
metadata:
  {
    "openclaw":
      {
        "emoji": "🎤",
        "requires": { "env": [] },
        "primaryEnv": "",
        "install": ["pip install --break-system-packages SpeechRecognition pydub"]
      },
  }
---

# 🎤 语音技能 (无需API，无需ffmpeg版本)

语音处理技能，支持：
1. **语音转文字** - 使用SpeechRecognition库 (需要网络，无需API密钥)
2. **文字转语音** - 使用系统TTS或生成信息文件
3. **WAV格式支持** - 纯Python处理，无需外部工具

## ⚠️ 当前限制
- **仅支持WAV格式**：其他格式(OGG/MP3)需要先转换为WAV
- **需要网络连接**：使用Google在线语音识别服务
- **无需ffmpeg**：纯Python解决方案，无需系统依赖

## 📋 快速开始

### 1. 安装依赖
```bash
# 安装Python包（需要--break-system-packages）
pip install --break-system-packages SpeechRecognition pydub

# 或者使用用户安装
pip install --user SpeechRecognition pydub
```

### 2. 语音转文字 (仅WAV格式)
```bash
# 使用纯Python转录（需要网络）
python {baseDir}/scripts/pure_python_transcribe.py audio.wav

# 或者使用极简版本
python {baseDir}/scripts/minimal_transcribe.py audio.wav
```

### 3. 文字转语音 (生成信息文件)
```bash
# 生成语音信息文件
python {baseDir}/scripts/text_to_voice_local.py "你好，我是小六" --output message.txt

# 如果系统有TTS工具，可以直接播放
python {baseDir}/scripts/text_to_voice_local.py "需要语音回复的内容"
```

## 🔧 安装要求

### 必需:
```bash
# 安装Python依赖
pip install SpeechRecognition pydub

# Linux系统可能需要安装
sudo apt-get install portaudio19-dev python3-pyaudio espeak ffmpeg
```

### 可选:
- `espeak` - 开源文字转语音引擎
- `gTTS` - Google Text-to-Speech (需要网络)

## 📁 脚本说明

### `scripts/pure_python_transcribe.py`
纯Python语音转文字脚本，无需ffmpeg。

**特点:**
- 仅支持WAV格式
- 需要网络连接（使用Google语音识别）
- 纯Python实现，无外部依赖

**参数:**
- `音频文件路径` - WAV格式音频文件
- `语言代码` - 可选，默认: zh-CN

**示例:**
```bash
python scripts/pure_python_transcribe.py audio.wav
python scripts/pure_python_transcribe.py audio.wav en
```

### `scripts/minimal_transcribe.py`
极简语音转文字脚本。

**特点:**
- 尝试处理多种格式
- 需要pydub（但pydub需要ffmpeg）
- 备用方案：返回错误信息

### `scripts/text_to_voice_local.py`
文字转语音脚本。

**特点:**
- 检查系统TTS工具
- 生成信息文件作为备用
- 支持多种TTS引擎

### `scripts/test_voice_skill.py`
测试脚本，检查所有功能。

## 🎯 使用场景

### 场景1: 处理WAV格式语音消息
当用户发送WAV格式语音消息时：
```bash
# 转录WAV语音消息
python scripts/pure_python_transcribe.py /home/node/.openclaw/media/inbound/voice_message.wav

# 保存转录结果
python scripts/pure_python_transcribe.py voice_message.wav > transcript.txt
```

### 场景2: 处理其他格式语音消息（需要转换）
当用户发送OGG/MP3格式语音消息时：
1. **先转换为WAV格式**（在其他机器上）：
   ```bash
   # 在有ffmpeg的机器上转换
   ffmpeg -i voice_message.ogg -ar 16000 -ac 1 voice_message.wav
   ```
   
2. **然后转录**：
   ```bash
   python scripts/pure_python_transcribe.py voice_message.wav
   ```

### 场景3: 文字转语音回复
当需要语音回复时：
```bash
# 生成语音信息文件
python scripts/text_to_voice_local.py "好的老板，我立即处理！" --output reply_info.txt

# 如果系统有TTS，可以直接播放
python scripts/text_to_voice_local.py "任务已完成"
```

## ⚙️ 配置

### OpenClaw配置
在 `~/.openclaw/openclaw.json` 中添加：

```json
{
  "skills": {
    "voice-skill": {
      "defaultLanguage": "zh-CN",
      "defaultTTS": "espeak",
      "autoTranscribe": true,
      "saveTranscripts": true
    }
  }
}
```

### 环境变量（可选）
```bash
# 设置默认语言
export VOICE_SKILL_LANGUAGE="zh-CN"

# 设置TTS引擎
export VOICE_SKILL_TTS="espeak"

# 设置输出目录
export VOICE_SKILL_OUTPUT_DIR="/home/node/.openclaw/workspace/voice-skill/results"
```

## 🔄 集成到OpenClaw

### 自动语音处理
在OpenClaw配置中启用自动语音转录：

```json
{
  "plugins": {
    "telegram": {
      "autoTranscribeVoice": true,
      "voiceSkillPath": "/home/node/.openclaw/workspace/voice-skill"
    }
  }
}
```

### 快捷命令
添加以下命令到OpenClaw：

```bash
# 语音转文字
/transcribe <音频文件>

# 文字转语音  
/say <文本内容>

# 语音回复
/voice <回复文本>
```

## 🚀 高级功能

### 1. 实时语音识别
```python
# 实时语音流处理
python scripts/realtime_voice.py --device 0 --language zh
```

### 2. 多语言支持
```bash
# 中文语音识别
python scripts/transcribe.py audio.ogg --language zh

# 英文语音识别  
python scripts/transcribe.py audio.ogg --language en

# 自动语言检测
python scripts/transcribe.py audio.ogg --language auto
```

### 3. 语音命令识别
```python
# 识别语音命令
python scripts/voice_commands.py command.ogg --commands "开始,停止,帮助,状态"
```

## 📊 性能优化

### 音频预处理
```bash
# 优化音频质量
ffmpeg -i input.ogg -ar 16000 -ac 1 -b:a 96k output.wav
```

### 批量处理
```bash
# 批量转录
python scripts/batch_transcribe.py audio_folder/ --output transcripts/
```

## 🛠️ 故障排除

### 常见问题

1. **Python包安装失败**
   ```
   错误: externally-managed-environment
   解决: 使用 --break-system-packages 选项:
        pip install --break-system-packages SpeechRecognition pydub
   ```

2. **音频格式不支持**
   ```
   错误: 仅支持WAV格式
   解决: 
     - 将其他格式转换为WAV（需要ffmpeg）
     - 使用在线转换工具
     - 直接录制为WAV格式
   ```

3. **网络连接问题**
   ```
   错误: 语音识别服务错误
   解决: 
     - 检查网络连接
     - Google语音识别需要互联网
     - 尝试其他语音识别服务
   ```

4. **缺少ffmpeg**
   ```
   警告: Couldn't find ffmpeg or avconv
   解决: 
     - 使用纯Python版本（仅WAV）
     - 在其他机器上转换音频格式
     - 使用在线转换服务
   ```

### 调试模式
```bash
# 启用详细日志
python scripts/transcribe.py audio.ogg --debug

# 查看原始API响应
python scripts/transcribe.py audio.ogg --raw
```

## 📈 最佳实践

1. **音频质量**: 使用16kHz, 单声道音频获得最佳识别效果
2. **背景噪音**: 尽量在安静环境中录音
3. **说话清晰**: 清晰、自然的说话方式
4. **文件大小**: 对于长音频，分段处理避免超时
5. **语言提示**: 提供语言提示提高识别准确率

## 🔗 相关资源

- [SpeechRecognition库文档](https://github.com/Uberi/speech_recognition)
- [espeak语音合成](http://espeak.sourceforge.net)
- [FFmpeg音频处理](https://ffmpeg.org)
- [pydub音频处理](https://github.com/jiaaro/pydub)

---
**最后更新**: 2026-04-04
**版本**: 1.0.0
**状态**: ✅ 就绪
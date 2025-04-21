# PolyVocalis - 智能语音分离工具

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

## 🎯 项目概述

PolyVocalis 是基于 FunASR 的智能语音分离系统，提供以下核心功能：

- 🔉 多说话人语音分离与识别
- 🎚️ 音频格式自动转换（支持 15+ 媒体格式）
- ⚡ GPU 加速处理（NVIDIA CUDA 支持）
- 📊 带时间戳的文本转录输出

## 🚀 快速开始

### 环境准备

```bash
# 克隆项目
git clone https://github.com/lb1169656535/PolyVocalis.git
cd PolyVocalis

# 创建环境
conda create -n polyVocalis python=3.12
# 激活环境（根据自己的环境名）
conda activate polyVocalis
# 安装依赖
pip install -r requirements.txt

# 安装系统依赖 (Ubuntu)
sudo apt install ffmpeg
```

### 模型下载

```bash
python download_model.py
```
### 音频格式转换为wav(如果需要)
```bash
python towav.py
```

### 使用示例

```bash
# 单文件处理
python app.py -i input.m4a -o ./output --gpu 0

# 批量处理目录
python app.py -i ./audio_files/*.mp3 -o ./result -t 8
```

## 📂 项目结构

```
PolyVocalis/
├── app.py                 # 主程序
├── download_model.py      # 模型下载工具
├── towav.py               # 音频格式转换工具
├── requirements.txt       # Python 依赖清单
└── README.md
```

## 🔧 核心参数说明

| 参数            | 说明                     | 默认值  |
|----------------|------------------------|-------|
| `-i/--input`   | 输入文件/通配符路径        | 必填   |
| `-o/--output`  | 输出目录                 | 必填   |
| `-w`           | 文本合并词数阈值          | 10    |
| `-t`           | 并行线程数               | 4     |
| `--gpu`        | GPU 设备编号 (-1=CPU)   | 0     |

## 🛠️ 功能特性

### 输入支持格式

| 音频格式          | 视频格式          |
|------------------|------------------|
| MP3, WAV, FLAC   | MP4, AVI, MOV    |
| M4A, AAC, OGG    | MKV, WMV         |

### 输出结构示例

```
output/
└── 2025-4-21/
    └── test_audio/
        ├── spk_0/
        │   ├── segment_0.wav
        │   └── full_spk_0.mp3
        ├── spk_1/
        └── logs/
            └── spk_0_transcript.txt
```

## 📚 文档资源

- [FunASR 官方文档](https://github.com/alibaba-damo-academy/FunASR)
- [模型技术白皮书](docs/technical_whitepaper.md)
- [性能优化指南](docs/optimization_guide.md)

## 🤝 参与贡献

欢迎通过 Issue 或 PR 参与项目开发：

1. Fork 项目仓库
2. 创建特性分支 (`git checkout -b feature/awesome-feature`)
3. 提交修改 (`git commit -am 'Add some feature'`)
4. 推送分支 (`git push origin feature/awesome-feature`)
5. 创建 Pull Request

## 📜 开源协议

本项目采用 [MIT License](LICENSE)

## 📞 联系方式

作者：帅小柏  
B站：[![B站](https://img.shields.io/badge/Bilibili-00A1D6?logo=bilibili)](https://space.bilibili.com/89565664)  
CSDN：[![CSDN](https://img.shields.io/badge/CSDN-FF0000)](https://blog.csdn.net/weixin_46339668)


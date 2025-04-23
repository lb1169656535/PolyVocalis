import os
import sys
import argparse
import logging
from datetime import datetime
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

import ffmpeg
from pydub import AudioSegment
from funasr import AutoModel

# 配置日志系统
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("audio_separator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AudioSeparator")

class AudioSeparator:
    def __init__(self, model_config: Dict, output_dir: str, split_words: int = 10):
        self.model = self._load_model(model_config)
        self.output_dir = output_dir
        self.split_words = split_words
        self.support_formats = {
            'audio': ['.mp3', '.m4a', '.aac', '.ogg', '.wav', '.flac', '.wma', '.aif'],
            'video': ['.mp4', '.avi', '.mov', '.mkv']
        }
        
    def _load_model(self, config: Dict) -> AutoModel:
        """加载语音处理模型"""
        logger.info("正在初始化语音处理模型...")
        try:
            return AutoModel(
                model=config['asr_model'],
                vad_model=config['vad_model'],
                punc_model=config['punc_model'],
                spk_model=config['spk_model'],
                device=config['device'],
                ncpu=config['ncpu'],
                disable_pbar=True,
                disable_log=True
            )
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
            raise

    def process_files(self, file_paths: List[str], workers: int = 4):
        """批量处理文件"""
        logger.info(f"开始处理 {len(file_paths)} 个文件")
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(self.process_single_file, path): path
                for path in file_paths
            }
            
            for future in as_completed(futures):
                path = futures[future]
                try:
                    future.result()
                    logger.info(f"成功处理文件: {path}")
                except Exception as e:
                    logger.error(f"文件处理失败 [{path}]: {str(e)}")

    def process_single_file(self, file_path: str):
        """处理单个文件"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
            
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in self.support_formats['audio'] + self.support_formats['video']:
            raise ValueError(f"不支持的格式: {file_ext}")

        # 预处理音频
        audio_bytes = self._preprocess_audio(file_path)
        
        # 语音分离处理
        result = self.model.generate(
            input=audio_bytes,
            batch_size_s=300,
            is_final=True,
            sentence_timestamp=True
        )
        
        # 分割并保存片段
        segments = self._parse_segments(result[0])
        speaker_audios = self._save_audio_segments(file_path, segments)
        
        # 合并音频
        self._concat_audios(speaker_audios)

    def _preprocess_audio(self, file_path: str) -> bytes:
        """使用FFmpeg预处理音频"""
        logger.debug(f"预处理音频: {file_path}")
        try:
            out, _ = (
                ffmpeg.input(file_path, threads=0, hwaccel='cuda')
                .output("-", format="wav", acodec="pcm_s16le", ac=1, ar=16000)
                .run(cmd=["ffmpeg", "-nostdin"], capture_stdout=True, capture_stderr=True)
            )
            return out
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg预处理失败: {e.stderr.decode()}")
            raise

    def _parse_segments(self, result: Dict) -> List[Dict]:
        """解析模型输出结果"""
        segments = []
        for sentence in result["sentence_info"]:
            if segments and sentence["spk"] == segments[-1]["spk"] and \
               len(segments[-1]["text"]) < self.split_words:
                # 合并短句
                segments[-1]["text"] += sentence["text"]
                segments[-1]["end"] = sentence["end"]
            else:
                # 新段落
                segments.append({
                    "start": sentence["start"],
                    "end": sentence["end"],
                    "text": sentence["text"],
                    "spk": sentence["spk"]
                })
        return segments

    def _save_audio_segments(self, file_path: str, segments: List[Dict]) -> Dict:
        """保存分割后的音频片段"""
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        speaker_audios = {}
        
        for idx, seg in enumerate(segments):
            output_path = self._get_output_path(base_name, seg["spk"], idx, file_path)
            self._cut_audio_segment(file_path, seg["start"], seg["end"], output_path)
            
            if seg["spk"] not in speaker_audios:
                speaker_audios[seg["spk"]] = []
            speaker_audios[seg["spk"]].append(output_path)
            
            self._save_text_log(base_name, seg["spk"], seg)
            
        return speaker_audios

    def _get_output_path(self, base_name: str, spk: str, index: int, orig_path: str) -> str:
        """生成输出路径"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        file_ext = os.path.splitext(orig_path)[1]
        
        output_dir = os.path.join(
            self.output_dir,
            date_str,
            base_name,
            f"spk_{spk}"
        )
        os.makedirs(output_dir, exist_ok=True)
        
        return os.path.join(output_dir, f"segment_{index}{file_ext}")

    def _cut_audio_segment(self, input_path: str, start: int, end: int, output_path: str):
        """切割音频片段"""
        logger.debug(f"切割音频片段: {start}ms - {end}ms")
        try:
            (
                ffmpeg.input(input_path, ss=start/1000, to=end/1000, hwaccel='cuda')
                .output(output_path)
                .run(cmd=["ffmpeg", "-nostdin"], overwrite_output=True, capture_stdout=True)
            )
        except ffmpeg.Error as e:
            logger.error(f"音频切割失败: {e.stderr.decode()}")
            raise

    def _save_text_log(self, base_name: str, spk: str, segment: Dict):
        """保存文本日志"""
        log_dir = os.path.join(self.output_dir, "logs", base_name)
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"spk_{spk}_transcript.txt")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{segment['start']}-{segment['end']}ms]\n{segment['text']}\n\n")

    def _concat_audios(self, speaker_audios: Dict):
        """合并同一说话人的音频片段"""
        logger.info("开始合并音频片段...")
        for spk, files in speaker_audios.items():
            if not files:
                continue
                
            try:
                combined = AudioSegment.from_file(files[0])
                for f in files[1:]:
                    combined += AudioSegment.from_file(f)
                
                output_path = os.path.join(
                    os.path.dirname(files[0]),
                    f"full_spk_{spk}.mp3"
                )
                combined.export(output_path, format="mp3")
                logger.info(f"已合并 {len(files)} 个片段到 {output_path}")
            except Exception as e:
                logger.error(f"音频合并失败: {str(e)}")

def main():
    parser = argparse.ArgumentParser(
        description="语音分离命令行工具",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-i", "--input", required=True, nargs="+",
                      help="输入文件路径（支持通配符）")
    parser.add_argument("-o", "--output", required=True,
                      help="输出目录路径")
    parser.add_argument("-w", "--split-words", type=int, default=10,
                      help="合并文本的单词数阈值")
    parser.add_argument("-t", "--threads", type=int, default=4,
                      help="并行处理线程数")
    parser.add_argument("--gpu", type=int, default=0,
                      help="使用的GPU编号（-1表示使用CPU）")
    args = parser.parse_args()

    # 模型配置
    model_config = {
        "asr_model": "iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
        "vad_model": "iic/speech_fsmn_vad_zh-cn-16k-common-pytorch",
        "punc_model": "iic/punc_ct-transformer_zh-cn-common-vocab272727-pytorch",
        "spk_model": "iic/speech_campplus_sv_zh-cn_16k-common",
        "device": "cuda" if args.gpu >=0 else "cpu",
        "ncpu": max(1, os.cpu_count() // 2)
    }

    try:
        separator = AudioSeparator(model_config, args.output, args.split_words)
        separator.process_files(args.input, args.threads)
        logger.info("处理完成！")
    except Exception as e:
        logger.error(f"运行失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

'''
# 示例用法

python app.py \
  -i /home/liub/project/data/test.wav \
  -o ./output \
  -w 15 \
  -t 4 \
  --gpu 0


python app.py \
  -i /home/liub/project/data/xjia_last/all.wav \
  -o ./output \
  -w 15 \
  -t 4 \
  --gpu 0


'''
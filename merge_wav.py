import os
import ffmpeg
import time
from tqdm import tqdm

def merge_wav_files(input_folder, output_file):
    """
    合并目录中的所有WAV文件（稳定版）
    :param input_folder: 输入文件夹路径
    :param output_file: 输出文件路径
    """
    # 获取排序后的文件列表（按文件名排序）
    file_list = sorted([
        os.path.join(input_folder, f) 
        for f in os.listdir(input_folder)
        if f.lower().endswith('.wav')
    ], key=lambda x: os.path.basename(x))

    if not file_list:
        print(f"在 {input_folder} 中未找到WAV文件")
        return

    print(f"发现 {len(file_list)} 个WAV文件需要合并")

    # 生成临时文件列表
    list_file = os.path.join(input_folder, "concat_list.txt")
    with open(list_file, "w") as f:
        for file_path in file_list:
            f.write(f"file '{os.path.abspath(file_path)}'\n")

    try:
        # 显示进度条
        with tqdm(total=len(file_list), desc="合并进度") as pbar:
            # 执行合并
            (
                ffmpeg
                .input(list_file, format='concat', safe=0)
                .output(output_file, c='copy', loglevel='error')
                .overwrite_output()
                .run(cmd=['ffmpeg', '-nostdin'], 
                     capture_stdout=True,
                     capture_stderr=True)
            )
            pbar.update(len(file_list))

    except ffmpeg.Error as e:
        print(f"\n合并失败: {e.stderr.decode()}")
        return
    finally:
        if os.path.exists(list_file):
            os.remove(list_file)

    # 验证结果
    if os.path.exists(output_file):
        file_size = os.path.getsize(output_file) / (1024 * 1024)
        print(f"\n合并成功！文件大小: {file_size:.2f}MB")
        print(f"输出路径: {output_file}")
    else:
        print("\n合并失败，未生成输出文件")

if __name__ == "__main__":
    # 配置路径
    input_dir = "/home/liub/project/data/xjia_wav"  # 已转换的WAV目录
    output_file = "/home/liub/project/data/merged_output.wav"
    
    # 执行合并
    try:
        merge_wav_files(input_dir, output_file)
    except Exception as e:
        print(f"发生意外错误: {str(e)}")
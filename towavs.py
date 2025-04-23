import os
import ffmpeg

def convert_audio_files(input_folder, output_folder):
    """
    批量转换音频文件为WAV格式
    :param input_folder: 输入文件夹路径
    :param output_folder: 输出文件夹路径
    """
    # 创建输出目录
    os.makedirs(output_folder, exist_ok=True)

    # 获取所有目标文件
    supported_ext = ('.m4a', '.mp3')
    file_list = [
        f for f in os.listdir(input_folder)
        if f.lower().endswith(supported_ext)
    ]

    if not file_list:
        print(f"在 {input_folder} 中未找到可转换文件（支持格式：m4a/mp3）")
        return

    print(f"发现 {len(file_list)} 个待处理文件")

    # 处理计数器
    success_count = 0
    error_files = []

    for filename in file_list:
        input_path = os.path.join(input_folder, filename)
        output_filename = os.path.splitext(filename)[0] + '.wav'
        output_path = os.path.join(output_folder, output_filename)

        try:
            # 显示处理进度
            print(f"正在处理：{filename} => {output_filename}")

            # 执行格式转换
            (
                ffmpeg.input(input_path)
                .output(output_path, 
                        acodec='pcm_s16le',  # 16bit线性PCM
                        ar=16000,            # 16kHz采样率
                        ac=1,                # 单声道
                        loglevel='error'     # 抑制控制台输出
                )
                .run(overwrite_output=True, 
                     capture_stdout=True, 
                     capture_stderr=True)
            )
            success_count += 1
        except Exception as e:
            error_files.append((filename, str(e)))
            continue

    # 输出统计信息
    print("\n转换完成！")
    print(f"成功: {success_count} 个")
    print(f"失败: {len(error_files)} 个")

    if error_files:
        print("\n错误详情：")
        for filename, error in error_files:
            print(f"❌ {filename}: {error}")

if __name__ == "__main__":
    # 配置参数
    input_dir = "/home/liub/project/data/xjia_last"  # 输入文件夹
    output_dir = "/home/liub/project/data/xjia_last"  # 输出文件夹

    # 执行转换
    try:
        convert_audio_files(input_dir, output_dir)
    except Exception as e:
        print(f"发生意外错误: {str(e)}")
        print("请检查：")
        print("1. 输入文件夹路径是否正确")
        print("2. FFmpeg是否已正确安装（命令行执行 ffmpeg -version 验证）")
        print("3. 文件读写权限是否正常")

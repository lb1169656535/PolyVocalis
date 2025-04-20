import ffmpeg

input_file = "/home/liub/project/data/test.m4a"
output_file = input_file.replace(".m4a", ".wav")

try:
    # 执行转换（自动覆盖已有文件）
    (
        ffmpeg.input(input_file)
        .output(output_file, acodec='pcm_s16le', ar=16000, ac=1)
        .run(overwrite_output=True, cmd=['ffmpeg', '-nostdin'])
    )
    print(f"转换成功！输出文件已保存至: {output_file}")
except Exception as e:
    print(f"转换失败: {str(e)}")
    print("请检查：1.文件是否存在 2.FFmpeg是否安装 3.文件权限")

import os
import subprocess
import tkinter as tk
import webbrowser
from tkinter import filedialog, messagebox, StringVar, scrolledtext

from PIL import Image

# 设置字符编码为UTF-8
subprocess.call('chcp 65001', shell=True)

def get_video_path():
    path = filedialog.askopenfilename(title="选择视频文件", filetypes=[("视频文件", "*.mp4")])
    video_path.set(path)

def get_output_path():
    path = filedialog.askdirectory(title="选择输出HTML的文件夹")
    output_path.set(path)

def generate_output_path(input_path):
    dir_name, file_name = os.path.split(input_path)
    name, ext = os.path.splitext(file_name)
    new_name = f"{name}-xg{ext}"
    return os.path.join(dir_name, new_name)

def process_video(input_path, output_folder, segment_duration):
    # 清空输出框内容
    output_text.delete(1.0, tk.END)
    
    # 检查视频文件是否存在
    if not os.path.exists(input_path):
        messagebox.showerror("错误", "视频文件不存在！")
        return

    output_text.insert(tk.END, "开始处理视频...\n")

    # 获取视频文件名（不含扩展名）
    video_name = os.path.splitext(os.path.basename(input_path))[0]
    video_folder = os.path.join(output_folder, video_name)

    # 创建视频文件夹
    if not os.path.exists(video_folder):
        os.mkdir(video_folder)

    output_text.insert(tk.END, f"创建输出文件夹: {video_folder}\n")

    # 使用ffprobe获取视频时长
    duration_output = subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_path], universal_newlines=True)
    duration = int(float(duration_output.strip()))

    # 以每个片段的长度进行循环
    segment_length = duration // 25

    # 生成25个视频片段
    counter = 1
    for i in range(25):
        # 计算截取的起始时间
        start_time = i * segment_length

        output_text.insert(tk.END, f"正在处理片段 {counter}/25...\n")
        output_text.see(tk.END)
        root.update()

        # 使用ffmpeg截取视频片段
        subprocess.call(['ffmpeg', '-ss', str(start_time), '-t', str(segment_duration), '-i', input_path, '-c', 'copy', '-avoid_negative_ts', 'make_zero', os.path.join(video_folder, f'{counter}.mp4')])
        counter += 1

    output_text.insert(tk.END, "视频片段处理完成，开始转换为GIF...\n")
    output_text.see(tk.END)
    root.update()

    # 将视频片段转换为GIF并删除MP4文件
    counter = 1
    for filename in os.listdir(video_folder):
        if filename.endswith(".mp4"):
            output_name = os.path.splitext(filename)[0] + '.gif'
            output_text.insert(tk.END, f"正在将片段 {counter}/25转换为GIF...\n")
            output_text.see(tk.END)
            root.update()

            subprocess.call(['ffmpeg', '-i', os.path.join(video_folder, filename), '-vf', 'fps=10,scale=320:-1:flags=lanczos', '-c:v', 'gif', os.path.join(video_folder, output_name)])
            os.remove(os.path.join(video_folder, filename))
            counter += 1

    output_text.insert(tk.END, "视频片段转换为GIF完成，开始生成HTML文件...\n")
    output_text.see(tk.END)
    root.update()

    # 生成 HTML 文件内容
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{video_name} GIF Gallery</title>
    <style>
        body {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background-color: #f0f0f0;
            margin: 0;
        }}
        .container {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 1px;
            width: 100%;
            max-width: 1450px;
            padding: 20px;
            box-sizing: border-box;
        }}
        .gif {{
            width: 100%;
            height: auto;
        }}
    </style>
    </head>
    <body>
    <h3>{video_name}</h3>
    <div class="container">
        {''.join([f'<img src="{os.path.join(str(i) + ".gif")}" alt="gif{i}" class="gif">' for i in range(1, 26)])}
    </div>
    </body>
    </html>
    """

    # 保存 HTML 文件
    html_file_path = os.path.join(video_folder, f'{video_name}.html')
    with open(html_file_path, 'w', encoding='utf-8') as html_file:
        html_file.write(html_content)

    output_text.insert(tk.END, "HTML 文件已生成！\n")
    output_text.insert(tk.END, f"输出文件夹: {video_folder}\n")
    output_text.see(tk.END)
    root.update()

    # 打开生成的HTML文件
    webbrowser.open(f'file://{html_file_path}')

    output_text.insert(tk.END, "自动打开生成的网页 \n")

def run_app():
    input_path = video_path.get()
    if not input_path:
        messagebox.showerror("错误", "未选择视频文件！")
        return
    
    output_folder = output_path.get()
    if not output_folder:
        messagebox.showerror("错误", "未选择输出文件夹！")
        return

    # 获取用户输入的片段时长
    try:
        segment_duration = int(segment_duration_var.get())
        if segment_duration <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("错误", "请输入有效的片段时长（正整数）！")
        return

    process_video(input_path, output_folder, segment_duration)

# 创建GUI界面
root = tk.Tk()
root.title("截取视频片段生成GIF预览网页（最好是MP4文件）")

# 获取屏幕宽度和高度
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# 设置窗口宽度和高度
window_width = 800
window_height = 600

# 计算窗口居中时左上角的坐标
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2

# 设置窗口居中
root.geometry(f'{window_width}x{window_height}+{x}+{y}')

# 创建并设置StringVar
video_path = StringVar()
output_path = StringVar()
segment_duration_var = StringVar(value="10")

frame = tk.Frame(root)
frame.pack(padx=20, pady=20)

tk.Label(frame, text="视频文件路径:").grid(row=0, column=0, sticky=tk.E)
tk.Entry(frame, textvariable=video_path, width=50).grid(row=0, column=1, padx=5, pady=5)
tk.Button(frame, text="选择", command=get_video_path).grid(row=0, column=2, padx=5, pady=5)

tk.Label(frame, text="输出文件夹路径:").grid(row=1, column=0, sticky=tk.E)
tk.Entry(frame, textvariable=output_path, width=50).grid(row=1, column=1, padx=5, pady=5)
tk.Button(frame, text="选择", command=get_output_path).grid(row=1, column=2, padx=5, pady=5)

tk.Label(frame, text="片段时长（秒）:").grid(row=2, column=0, sticky=tk.E)
tk.Entry(frame, textvariable=segment_duration_var, width=10).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

run_button = tk.Button(frame, text="运行", command=run_app)
run_button.grid(row=3, column=0, columnspan=3, pady=20)

# 添加文本框显示输出信息
output_text = scrolledtext.ScrolledText(root, width=80, height=20, wrap=tk.WORD)
output_text.pack(padx=20, pady=20)

root.mainloop()

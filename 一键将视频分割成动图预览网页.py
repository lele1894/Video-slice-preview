#20:51 2024/11/24
import os
import subprocess
import tkinter as tk
import webbrowser
from tkinter import filedialog, messagebox, StringVar, scrolledtext
from concurrent.futures import ThreadPoolExecutor
import time
import threading
import tkinter.ttk as ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
import re
from ttkthemes import ThemedStyle

def check_dependencies():
    """检查系统是否安装了 ffmpeg 和 ffprobe"""
    try:
        subprocess.check_output(['ffmpeg', '-version'], universal_newlines=True)
        subprocess.check_output(['ffprobe', '-version'], universal_newlines=True)
    except FileNotFoundError:
        messagebox.showerror("错误", "未检测到 ffmpeg 或 ffprobe，请先安装！")
        exit()

def run_ffmpeg_command(command):
    """运行 FFmpeg 命令，捕获异常"""
    try:
        subprocess.check_call(command, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("错误", f"FFmpeg 命令执行失败: {e}")
        return False
    return True

def get_video_path():
    path = filedialog.askopenfilename(title="选择视频文件", filetypes=[("视频文件", "*.mp4")])
    if not path:
        return

    # 检查文件名是否包含特殊字符
    if re.search(r'[<>:"/\\|?*]', os.path.basename(path)):
        messagebox.showerror("错误", "文件名包含特殊字符，请选择其他文件！")
        return

    video_path.set(path)

    # 设置默认输出路径为视频所在文件夹
    default_output_path = os.path.dirname(path)
    output_path.set(default_output_path)

def get_output_path():
    path = filedialog.askdirectory(title="选择输出HTML的文件夹")
    output_path.set(path)

def create_output_folder(folder_path):
    """创建输出文件夹"""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

def process_segment(input_path, output_folder, start_time, segment_duration, index, scale):
    """处理单个视频片段并转换为 GIF"""
    mp4_output = os.path.join(output_folder, f"{index}.mp4")
    gif_output = os.path.join(output_folder, f"{index}.gif")

    # 截取视频片段，开始时间推迟60秒
    if not run_ffmpeg_command([
        'ffmpeg', '-ss', str(start_time), '-t', str(segment_duration), '-i', input_path,
        '-c', 'copy', '-avoid_negative_ts', 'make_zero', mp4_output,
        '-y'
    ]):
        return None

    # 转换为 GIF，使用用户选择的清晰度
    if not run_ffmpeg_command([
        'ffmpeg', '-i', mp4_output, '-vf', f'fps=10,scale={scale}:-1:flags=lanczos', '-c:v', 'gif', gif_output,
        '-y'
    ]):
        return None

    # 删除 MP4 文件
    if os.path.exists(mp4_output):
        os.remove(mp4_output)

    return gif_output

def process_video(input_path, output_folder, segment_duration, root):
    """处理视频：多线程分段处理并生成GIF"""
    # 清空输出容
    output_text.delete(1.0, tk.END)

    # 检查输入文件和输出目录
    if not os.path.exists(input_path):
        messagebox.showerror("错误", "视频文件不存在！")
        return
    create_output_folder(output_folder)

    output_text.insert(tk.END, "开始处理视频...\n")
    start_time_all = time.time()

    # 获取视频总时长
    try:
        duration_output = subprocess.check_output(
            ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
             'stream=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_path],
            universal_newlines=True
        )
        total_duration = int(float(duration_output.strip()))
    except subprocess.CalledProcessError:
        messagebox.showerror("错误", "无法获取视频时长，请检查文件！")
        return

    # 计算每份的起始时间
    segment_length = total_duration // 25
    video_name = os.path.splitext(os.path.basename(input_path))[0]
    video_folder = create_output_folder(os.path.join(output_folder, video_name))

    output_text.insert(tk.END, f"创建输出文件夹: {video_folder}\n")

    # 获取用户选择的清晰度
    scale = resolution_var.get()

    # 使用多线程处理视频片段
    futures = []
    gif_files = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        for i in range(25):
            start_time = i * segment_length
            futures.append(
                executor.submit(process_segment, input_path, video_folder, start_time, segment_duration, i + 1, scale)
            )

        for future in futures:
            try:
                gif_files.append(future.result(timeout=600))  # 超时时间
            except Exception as e:
                output_text.insert(tk.END, f"任务失败: {e}\n")

    # 清除未生成的 None 值
    gif_files = [gif for gif in gif_files if gif]

    # 生成 HTML 文件
    output_text.insert(tk.END, "所有视频片段处理完成，开始生成HTML文件...\n")
    output_text.see(tk.END)
    root.after(100)  # 更新GUI

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
            gap: 10px;
            width: 100%;
            max-width: 1450px;
            padding: 20px;
        }}
        .gif {{
            width: 100%;
            height: auto;
            max-width: 100%;
            object-fit: cover;
        }}
    </style>
    </head>
    <body>
    <h3>{video_name}</h3>
    <div class="container">
        {''.join([f'<img src="{os.path.basename(gif_file)}" class="gif">' for gif_file in gif_files])}
    </div>
    </body>
    </html>
    """
    html_file_path = os.path.join(video_folder, f'{video_name}.html')
    with open(html_file_path, 'w', encoding='utf-8') as html_file:
        html_file.write(html_content)

    output_text.insert(tk.END, "HTML 文件已生成！\n")
    output_text.insert(tk.END, f"输出文件夹: {video_folder}\n")
    output_text.see(tk.END)
    root.after(100)  # 更新GUI

    # 打开生成的HTML文件
    webbrowser.open(f'file://{html_file_path}')
    output_text.insert(tk.END, "自动打开生成的网页\n")

    # 打印耗时
    end_time_all = time.time()
    elapsed_time = end_time_all - start_time_all
    output_text.insert(tk.END, f"总耗时：{elapsed_time:.2f} 秒\n")

def run_app():
    """运行主程序"""
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

    thread = threading.Thread(target=process_video, args=(input_path, output_folder, segment_duration, root))
    thread.start()

def on_drop(event):
    """处理拖拽文件事件"""
    path = event.data
    video_path.set(path)
    default_output_path = os.path.dirname(path)
    output_path.set(default_output_path)

# 检查依赖
check_dependencies()

# 创建GUI界面
root = TkinterDnD.Tk()
root.title("视频GIF预览生成器")

# 创建变量
video_path = StringVar()
output_path = StringVar()
segment_duration_var = StringVar(value="3")  # 设置默认值为3
resolution_var = StringVar()

# 绑定拖拽事件
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', on_drop)

# 应用主题
style = ThemedStyle(root)
style.set_theme("arc")  # 使用arc主题

# 设置窗口大小和最小尺寸
root.geometry("700x500")
root.minsize(600, 400)

# 创建主框架并添加内边距
main_frame = ttk.Frame(root, padding="20")
main_frame.pack(fill=tk.BOTH, expand=True)

# 修改frame的创建方式
frame = ttk.LabelFrame(main_frame, text="配置选项", padding="10")
frame.pack(fill=tk.X, padx=5, pady=5)

# 修改输入控件的布局
ttk.Label(frame, text="视频文件路径:", style='Info.TLabel').grid(row=0, column=0, sticky=tk.E, padx=5)
video_entry = ttk.Entry(frame, textvariable=video_path, width=50)
video_entry.grid(row=0, column=1, padx=5, pady=8, sticky=tk.EW)
ttk.Button(frame, text="选择文件", command=get_video_path).grid(row=0, column=2, padx=5)

ttk.Label(frame, text="输出文件夹路径:").grid(row=1, column=0, sticky=tk.E)
ttk.Entry(frame, textvariable=output_path, width=50).grid(row=1, column=1, padx=5, pady=5)
ttk.Button(frame, text="选择", command=get_output_path).grid(row=1, column=2, padx=5, pady=5)

ttk.Label(frame, text="展示的动图时长(秒):").grid(row=2, column=0, sticky=tk.E)
ttk.Entry(frame, textvariable=segment_duration_var, width=10).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

ttk.Label(frame, text="GIF清晰度:").grid(row=3, column=0, sticky=tk.E)
resolution_options = ttk.Combobox(frame, textvariable=resolution_var, values=["320", "480", "640", "800"])
resolution_options.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
resolution_options.current(0)  # 设置默认选项

# 修改运行按钮样式
run_button = ttk.Button(frame, text="开始处理", command=run_app, style='Action.TButton')
run_button.grid(row=4, column=0, columnspan=3, pady=15)

# 修改输出文本框
output_frame = ttk.LabelFrame(main_frame, text="处理日志", padding="10")
output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

output_text = scrolledtext.ScrolledText(
    output_frame, 
    width=80, 
    height=10, 
    wrap=tk.WORD,
    font=('Consolas', 9)
)
output_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

root.mainloop()
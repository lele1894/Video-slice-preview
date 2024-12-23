# 视频切片转GIF用网页预览

将视频自动分割成多个GIF动图，并生成预览网页。可用于视频内容快速预览、视频教程章节预览等场景。

![界面预览](01.png)

网页预览效果：

![网页预览](02.gif)

## 功能特点
- 自动将视频切割成等长GIF动图
- 生成包含所有GIF预览的网页
- 支持自定义切片时长和间隔
- 支持调整GIF尺寸和质量
- 简单易用的图形界面
- 支持拖拽导入视频

## 使用方法

### 可执行文件版本
从 [Releases](../../releases) 页面下载最新的 `video-to-gif-preview.exe`。

使用前准备：
1. 下载并安装 [FFmpeg](https://github.com/BtbN/FFmpeg-Builds/releases)
2. 将 FFmpeg 添加到系统环境变量
   - 或者直接将 ffmpeg.exe 和 ffprobe.exe 放在程序同目录下

### 源码版本
需要 Python 3.7 或更高版本，安装依赖：
```bash
# Windows
pip install -r requirements.txt

# Linux 需要先安装 tkinter
sudo apt-get install python3-tk  # Ubuntu/Debian
sudo dnf install python3-tkinter # Fedora
sudo pacman -S tk               # Arch Linux
```

同样需要安装 FFmpeg 并确保可以在命令行中使用。

### 批处理脚本版本
`.bat` 文件是 Windows 系统的可执行脚本，使用要求同可执行文件版本。

## 参数说明
- 切片时长：每个GIF的时长（秒）
- 切片间隔：视频分割的间隔时间（秒）
- GIF尺寸：输出GIF的宽度（高度自动等比例缩放）
- GIF质量：数值越小文件越小，但质量也越低

## 开发说明
本项目使用 GitHub Actions 自动构建 exe 文件：
- 每次发布新版本标签时自动构建
- 可在 Actions 页面手动触发构建
- 构建产物在 [Releases](../../releases) 页面下载

## 系统要求
- Windows 7/8/10/11
- FFmpeg (用于视频处理)
- 2GB 以上可用内存（视频大小不同，需求不同）
- 分辨率：1280x720 或更高

## 注意事项
1. 首次处理大视频时可能较慢，请耐心等待
2. GIF文件可能较大，建议适当调整参数
3. 确保有足够的磁盘空间
4. 如遇到问题，请检查 FFmpeg 是否正确安装

## 问题反馈
如有问题或建议，请在 [Issues](../../issues) 页面提交。

![头像](https://avatars.githubusercontent.com/u/11767608?v=4)
```


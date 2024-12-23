# 视频切片转GIF用网页预览

一键将视频分割成动图预览网页

![界面预览](01.png)

网页预览

![网页预览](02.gif)

## 使用方法

### 可执行文件版本
从 [Releases](../../releases) 页面下载最新的 exe 文件。

使用前准备：
1. 下载并安装 [FFmpeg](https://github.com/BtbN/FFmpeg-Builds/releases)
2. 将 FFmpeg 添加到系统环境变量
   - 或者直接将 ffmpeg.exe 和 ffprobe.exe 放在程序同目录下

### 源码版本
".py"结尾的文件是源码，需要安装以下依赖：
```bash
pip install -r requirements.txt
```

同样需要安装 FFmpeg 并确保可以在命令行中使用。

### 批处理脚本
".bat"结尾的文件是 win 系统的可执行脚本，使用要求同可执行文件版本。

## 自动构建
本项目使用 GitHub Actions 自动构建 exe 文件。每次发布新版本时会自动打包。
可在 [Releases](../../releases) 页面下载最新版本。

![头像](https://avatars.githubusercontent.com/u/11767608?v=4)
```


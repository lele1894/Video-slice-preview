@echo off
setlocal enabledelayedexpansion
chcp 65001
REM 定义选项
set "option1=1.视频截取"
set "option2=2.抽取合并视频"
set "option3=3.无"

REM 显示选项
echo 请选择你要执行的操作:
echo %option1%
echo %option2%
echo %option3%

REM 读取用户输入
set /p choice="请输入你的选择 (1-3): "

REM 根据用户输入执行命令
if "%choice%"=="1" goto option1
if "%choice%"=="2" goto option2
if "%choice%"=="3" goto option3

REM 跳转到对应选项的标签
:option1
echo 你选择了 %option1%
REM 在这里添加你要执行的命令
set /p ks="要转换的视频:"
set /p sj1="截取开头秒(00:00:00):"
set /p sj2="截取结尾秒(00:00:00):"
ffmpeg -ss %sj1% -to %sj2% -i %ks% -c copy -avoid_negative_ts make_zero %ks:~0,-4%_1.mp4"
pause
exit
:option2
echo 你选择了 %option2%
REM 在这里添加你要执行的命令
set /p input_file="要转换的视频:"
set output_folder=output
set /p clip_duration="每分钟截取几秒:"
echo "本片有以下秒:"
ffprobe -v error -select_streams v:0 -show_entries stream=duration -of default=noprint_wrappers=1:nokey=1 %input_file%
set /p time="影片有多少秒:"

if not exist %output_folder% mkdir %output_folder%

for /l %%i in (0,60,%time%) do (
    set /a "start_time=%%i"
    ffmpeg -ss !start_time! -t %clip_duration% -i %input_file% -c copy -avoid_negative_ts make_zero %output_folder%\output_%%i.mp4
    echo file '%output_folder%\output_%%i.mp4' >> list.txt
)

ffmpeg -f concat -safe 0 -i list.txt -c copy final_output.mp4 -y

rd /S /Q "output" 
del list.txt
pause
exit
:option3
echo 你选择了 %option3%
REM 在这里添加你要执行的命令
pause
REM 结束批处理
endlocal
exit

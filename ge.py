#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import codecs
import os
import subprocess

def run_ffmpeg(inputfile, outputfile, ss, to):
    import subprocess
    from subprocess import PIPE

    duration = str(datetime.strptime(to, timeFormat) - datetime.strptime(ss, timeFormat))

    command = ['ffmpeg']
    command.extend(['-ss', '%s' % ss, '-t', '%s' % duration])
    command.extend(['-i', '%s' % inputfile])
    command.extend(['-c', 'copy'])
    command.extend(['-loglevel','info'])
    command.extend(['-y','-hide_banner'])
    command.extend(['%s' % outputfile])

    print(' '.join(command))

    try:
        proc = subprocess.Popen(command, stdout=PIPE, stderr=PIPE)
        errs = ""
        for line in iter(proc.stderr.readline, b''):
                line = line.decode('utf-8').rstrip()
                errs += line
        outs, _errs = proc.communicate()
        outs = outs.decode('utf-8')
        errs = errs + '\n' + _errs.decode('utf-8')
        if errs:
                print("ffmpeg warning: %s",errs)
        else:
            print("ffmpeg stdout: %s\nffmpeg stderr: %s",outs, errs)
            print("ffmpeg encode success")
    except FileNotFoundError:
        print("encode_ffmpeg")
        print("ffmpeg: input file not found. continue")
    except subprocess.SubprocessError as e:
        print("encode_ffmpeg")
        print("ffmpeg: failed %s",e)

def generate_script(start_time, end_time, title):
    f = codecs.open('cut.ps1','w',encoding='utf-8') # powershell script
    f.write('\ufeff') # add utf-8 BOM for Windows Powershell compatibility
    f.write('# 分幕' + os.linesep)
    for i in range(0,len(start_time)):
        timeFormat = '%H:%M:%S.%f'
        duration = str(datetime.strptime(end_time[i], timeFormat) - datetime.strptime(start_time[i], timeFormat))
        command = '.\\ffmpeg.exe' + ' -ss ' + start_time[i] + ' -t ' + duration + ' -i \"《向阳的星光》歌舞剧.mp4\"' + ' -c copy \"' + title[i] + '.mp4\"' + os.linesep
        f.write(command)

start_time = ['00:04:47.06', '00:05:34.01', '00:15:54.24', '00:28:37.00', '00:36:09.05', '00:47:54.14', '01:02:11.07', '01:10:12.11', '01:20:14.24', '01:28:03.21', '01:37:15.17']
end_time = ['00:05:34.01', '00:15:50.20', '00:28:31.13', '00:36:09.05', '00:47:38.12', '01:01:50.09', '01:10:05.00', '01:20:14.24', '01:27:16.28', '01:37:07.13', '01:40:09.17']
title = ['报幕', '第一幕 加入', '第二幕 阁楼', '第三幕 更衣室', '第四幕 救场',
'第五幕 请柬', '第六幕 酒会', '第七幕 最后的准备', '第八幕 新的演出', '谢幕', '握手']

f = codecs.open('cut.ps1','w',encoding='utf-8') # powershell script
f.write('\ufeff') # add utf-8 BOM for Windows Powershell compatibility
f.write('# 分幕' + os.linesep)
for i in range(0,len(start_time)):
    timeFormat = '%H:%M:%S.%f'
    duration = str(datetime.strptime(end_time[i], timeFormat) - datetime.strptime(start_time[i], timeFormat))
    command = '.\\ffmpeg.exe' + ' -ss ' + start_time[i] + ' -t ' + duration + ' -i \"《向阳的星光》歌舞剧.mp4\"' + ' -c copy \"' + title[i] + '.mp4\"' + os.linesep
    f.write(command)


f.write(os.linesep + '# 歌曲' + os.linesep)
start_time = ['00:05:34.01', '00:21:16.06', '00:23:53.12', '00:33:09.09', '00:40:35.06', '00:49:26.04', '00:58:16.27',
'01:05:30.15', '01:12:40.13', '01:21:17.25', '00:04:47.06', '00:36:09.05']
end_time = ['00:07:10.07', '00:22:11.01', '00:28:02.27', '00:35:36.23', '00:44:59.01', '00:51:30.18', '01:01:06.22',
'01:08:54.08', '01:16:59.20', '01:25:34.03', '00:05:34.01', '00:38:56.17']
title = ['《主题曲》严佼君 金莹玥 许逸 熊沁娴 刘菊子', '《破茧》严佼君', '《月光下》张昕 郝婉晴', '《对峙》严佼君 郝婉晴',
'《人间规则》严佼君(张昕 郝婉晴) 金莹玥 许逸 熊沁娴 刘菊子', '《纽约梦》吴燕文', '《破茧》郝婉晴 严佼君', '《黑天鹅》郝婉晴',
'《人鱼》郝婉晴 张昕 严佼君 吴燕文 何晓玉', '《降落伞》郝婉晴 张昕', '《小枫报幕一》吕一', '《小枫报幕二》吕一']

for i in range(0,len(start_time)):
    timeFormat = '%H:%M:%S.%f'
    duration = str(datetime.strptime(end_time[i], timeFormat) - datetime.strptime(start_time[i], timeFormat))
    command = '.\\ffmpeg.exe' + ' -ss ' + start_time[i] + ' -t ' + duration + ' -i \"《向阳的星光》歌舞剧.mp4\"' + ' -c copy \"' + title[i] + '.mp4\"' + os.linesep
    f.write(command)


f.close()

run_ffmpeg("《向阳的星光》歌舞剧.mp4", "报幕.mp4", "00:04:47.06", "00:05:34.01")


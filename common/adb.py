# -*- coding: utf-8 -*-
import os
import sys
import subprocess

adb_path = ''


def get_path():
    global adb_path
    try:
        adb_path = 'adb '
        subprocess.Popen([adb_path], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
        return adb_path
    except FileNotFoundError:
        if os.name == 'nt':
            adb_path = os.path.join('Tools', "adb", 'adb.exe ')
            try:
                subprocess.Popen(
                    [adb_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return adb_path
            except FileNotFoundError:
                pass
        print('请安装 ADB 及驱动并配置环境变量')
        sys.exit()


def run(command):
    global adb_path
    if adb_path == '':
        adb_path = get_path()
    return os.popen('{}{}'.format(adb_path, command))

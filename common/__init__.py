# -*- coding: utf-8 -*-
import os
import sys
import subprocess


def get_adb_path():
    try:
        adb_path = 'adb'
        subprocess.Popen([adb_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return adb_path
    except FileNotFoundError:
        if os.name=='nt':
            adb_path = os.path.join('Tools', "adb", 'adb.exe')
            try:
                subprocess.Popen([adb_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return adb_path
            except FileNotFoundError:
                pass
        print('请安装 ADB 及驱动并配置环境变量')
        sys.exit()


adb = get_adb_path() + ' '

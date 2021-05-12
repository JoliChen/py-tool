# -*- coding: utf-8 -*-
# @Time    : 2019/7/15 10:34 AM
# @Author  : Joli
# @Email   : 99755349@qq.com

import subprocess

from jonlin.utils import Log

log = Log.Logger(__file__)

def run(cmd):
    log.d(cmd)
    ret = subprocess.run(cmd, shell=True)
    return ret.returncode

def stdout(cmd):
    log.d(cmd)
    ret = subprocess.run(cmd, shell=True, **{'stdout': subprocess.PIPE})
    # log.d('retcode:%d, stdout:%s' % (ret.returncode, ret.stdout))
    return ret.stdout.decode('utf-8')
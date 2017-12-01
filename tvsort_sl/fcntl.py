# coding=utf-8
from __future__ import unicode_literals

# Variables with simple values

FASYNC = 64

FD_CLOEXEC = 1

F_DUPFD = 0
F_FULLFSYNC = 51
F_GETFD = 1
F_GETFL = 3
F_GETLK = 7
F_GETOWN = 5
F_RDLCK = 1
F_SETFD = 2
F_SETFL = 4
F_SETLK = 8
F_SETLKW = 9
F_SETOWN = 6
F_UNLCK = 2
F_WRLCK = 3

LOCK_EX = 2
LOCK_NB = 4
LOCK_SH = 1
LOCK_UN = 8


def fcntl(fd, op, arg=0):
    return 0


def ioctl(fd, op, arg=0, mutable_flag=True):
    if mutable_flag:
        return 0
    else:
        return ""


def flock(fd, op):
    return


def lockf(fd, operation, length=0, start=0, whence=0):
    return

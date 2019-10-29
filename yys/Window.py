# -*- coding: UTF-8 -*-
import ctypes
import inspect
import threading
import time
import tkinter as tk
from concurrent.futures import thread
import tkinter
from tkinter import *
from tkinter import scrolledtext, messagebox

from yysScript.yys.yys import YuHunTwoWindow, YuHunOneWindow

MSG = []
tasks = []
NeedCloseGame = False
NeedCloseSystem=False

def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


def YuhunTwo(LogUI,NeedCloseGame,NeedCloseSystem,):
    """
    御魂副本双开
    :return:
    """
    messagebox.showinfo('提示', '请确保两个帐号都已经进入组队房间并且阵容锁定')
    t = threading.Thread(target=YuHunTwoWindow, args=(LogUI,NeedCloseGame,NeedCloseSystem,))
    t.start()
    tasks.append(t)


def YuhunOne(LogUI,NeedCloseGame,NeedCloseSystem,):
    """
    御魂副本单开
    :return:
    """
    messagebox.showinfo('提示', '请确保帐号已经阵容锁定')
    t = threading.Thread(target=YuHunOneWindow, args=(LogUI,NeedCloseGame,NeedCloseSystem,))
    t.start()
    tasks.append(t)


def StopAll(LogUI):
    """

    :return:
    """
    try:
        global tasks
        for i in tasks:
            stop_thread(i)
        tasks = []
        if LogUI is not None:
            LogUI.insert(END,
                         time.strftime('%Y-%m-%d %H:%M:%S',
                                       time.localtime(time.time())) + '脚本停止\n')
            LogUI.insert(END, '全部动作停止\n')
            LogUI.see(END)
    except Exception as e:
        if LogUI is not None:
            tasks=[]
            LogUI.insert(END,
                         time.strftime('%Y-%m-%d %H:%M:%S',
                                       time.localtime(time.time())) + '脚本停止异常,可能已经停止,请重启再试\n')
            LogUI.see(END)
            print(e)


def Closing(app):
    try:
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            StopAll(None)
            app.destroy()
    except Exception:
        sys.exit(-1)


def ShortCut(event):
    """
    按f4 停止脚本
    :param event:
    :return:
    """
    # print("event.char =", event.char)
    # print("event.keycode =", event.keycode)
    # F4停止
    global app
    if event.keycode == 115:
        StopAll(Window.LogUI)


def ChangeEndActionWithGame():
    """
    选择是否体力用完关闭游戏
    :return:
    """
    global NeedCloseGame
    NeedCloseGame = not NeedCloseGame
    print('NeedCloseGame', str(NeedCloseGame))

def ChangeEndActionWithSystem():
    """
    选择是否体力用完是否关机
    :return:
    """
    global NeedCloseSystem
    NeedCloseSystem = not NeedCloseSystem
    print('NeedCloseSystem',NeedCloseSystem)

class Window:
    def __init__(self):
        self.initWidgets()

    def initWidgets(self):
        self.app = tk.Tk()  # 根窗口的实例(root窗口)
        self.app.geometry('600x200')
        self.app.resizable(0, 0)  # 阻止Python GUI的大小调整
        frame1 = Frame(self.app, padx=20)
        frame1.pack(side=LEFT, fill=BOTH)
        t1 = tk.Label(frame1, text='护肝脚本', font=("华文行楷", 22), borderwidth=2).pack(side=TOP, fill=X, expand=YES)

        frame2 = Frame(self.app)
        t1 = tk.Label(frame2, text='日志', borderwidth=2, font=('微软雅黑', 10), height=1).pack(side=TOP, fill=X, expand=YES)
        t3 = scrolledtext.ScrolledText(frame2, font=('微软雅黑', 10))
        t3.pack(side=TOP, fill=X, expand=YES)
        frame2.pack(side=RIGHT, fill=BOTH, expand=YES)
        Button(frame1, command=lambda: YuhunOne(t3,NeedCloseGame,NeedCloseSystem), text='自动御魂副本', width=20).pack(side=TOP, expand=YES)
        Checkbutton(frame1, text='体力用完自动关闭游戏', command=ChangeEndActionWithGame).pack(side=TOP,anchor='w')
        Checkbutton(frame1, text='体力用完自动关机', command=ChangeEndActionWithSystem).pack(side=TOP,anchor='w')
        # Button(frame1, command=lambda: YuhunTwo(t3), text='御魂副本双开', width=20).pack(side=TOP, expand=YES)
        Button(frame1, command=lambda: StopAll(t3), text='停止', width=20).pack(side=TOP, expand=YES)

        self.app.protocol("WM_DELETE_WINDOW", lambda: Closing(self.app))
        Window.LogUI = t3
        self.app.bind("<Key>", ShortCut)
        self.app.mainloop()  # 窗口的主事件循环，必须的。


if __name__ == '__main__':
    app = Window()

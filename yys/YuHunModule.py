# -*- coding: utf-8 -*-
import datetime
import logging
import os
import random
import time
from tkinter import END

import cv2
import numpy
import numpy as np
import pyautogui
from PIL import ImageGrab
from matplotlib import pyplot as plt

pyautogui.FAILSAFE = False
logging.basicConfig(format="%(asctime)s :%(levelname)s:%(message)s", datefmt="%d-%M-%Y %H:%M:%S", level=logging.DEBUG)
# 初始化SIFT探测器
SIFT = cv2.xfeatures2d.SIFT_create()


def ComputeScreenShot(screenShot):
    """
    由于屏幕分辨率高，计算耗时，这里优化一下
    :return:
    """
    kp2, des2 = SIFT.detectAndCompute(screenShot, None)
    return kp2, des2


def GetLocation(target, kp2, des2):
    """
    获取目标图像在截图中的位置
    :param target:
    :param screenShot:
    :return: 返回坐标(x,y) 与opencv坐标系对应
    """
    MIN_MATCH_COUNT = 10
    img1 = target  # cv2.cvtColor(target,cv2.COLOR_BGR2GRAY)# 查询图片
    # img2 = screenShot
    # img2 = cv2.cvtColor(screenShot, cv2.COLOR_BGR2GRAY)  # 训练图片
    # img2 = cv2.resize(img2, dsize=None, fx=0.5, fy=0.5, interpolation=cv2.INTER_NEAREST)
    # 用SIFT找到关键点和描述符

    kp1, des1 = SIFT.detectAndCompute(img1, None)

    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=4)
    search_params = dict(checks=50)

    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)
    good = []
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good.append(m)
    if len(good) > MIN_MATCH_COUNT:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        matchesMask = mask.ravel().tolist()
        h, w = img1.shape
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        if M is not None:
            dst = cv2.perspectiveTransform(pts, M)
            arr = np.int32(dst)  #
            midPosArr = arr[0] + (arr[2] - arr[0]) // 2
            midPos = (midPosArr[0][0], midPosArr[0][1])
            # show=cv2.circle(img2,midPos,30,(255,255,255),thickness=5)
            # cv2.imshow('s',show)
            # cv2.waitKey()
            # cv2.destroyAllWindows()
            return midPos
        else:
            return None
    else:
        return None


def CheatPos(originPos, factor=5):
    """
    对原始点击坐标进行随机偏移，防止封号
    :param originPos:原始坐标
    :return:
    """
    x, y = random.randint(-factor, factor), random.randint(-factor, factor)
    newPos = (originPos[0] + x, originPos[1] + y)
    return newPos


def Click(targetPosition):
    """
    点击屏幕上的某个点
    :param targetPosition:
    :return:
    """
    if targetPosition is None:
        print('未检测到目标')
    else:

        pyautogui.moveTo(targetPosition, duration=0.20)
        pyautogui.click()
        time.sleep(random.randint(500, 1000) / 1000)

        # time.sleep(random.randint(100, 150) / 1000)


def loadImgs():
    """
    加载所有需要检测的目标图像
    :return:
    """
    obj = {}
    path = os.getcwd() + '/img'
    file_list = os.listdir(path)

    for file in file_list:
        name = file.split('.')[0]
        file_path = path + '/' + file
        a = cv2.imread(file_path, 0)
        obj[name] = a

    return obj


def GetScreenShot():
    """
    获取屏幕截图
    :return:
    """
    screen = ImageGrab.grab()
    # screen.save('screen.jpg')
    # screen = cv2.imread('screen.jpg')
    screen = cv2.cvtColor(numpy.asarray(screen), cv2.COLOR_RGB2BGR)
    logging.info('截屏成功')
    return screen


class YuHun():
    def __init__(self):
        self._flag = False
        self.NeedCloseGame=False
        self.NeedCloseSystem=False

    def Run(self, LogUI, NeedCloseGame, NeedCloseSystem):
        imgs = loadImgs()
        LogUI.insert(END,
                     time.strftime('%Y-%m-%d %H:%M:%S ',
                                   time.localtime(time.time())) + '开始挑战\n')
        Count = 1
        while self._flag is not True:
            logging.debug('开始挑战')
            screen = GetScreenShot()
            WindowShape = screen.shape
            result = []

            # 为了优化速度，把计算屏幕截图的特征提取出来，避免重复运算
            kp2, des2 = ComputeScreenShot(screen)
            for i in ['tili60', 'tili80', 'auto', 'jieshou2', 'jieshou1', 'end1', 'end2', 'reject', 'queding',
                      'tiaozhan']:
                obj = imgs[i]
                # begin = time.clock()
                pos = GetLocation(obj, kp2, des2)
                # logging.debug('检测结算目标图像')
                # print(time.clock()-begin)
                if pos is not None:
                    if i == 'tili60' or i == 'tili80':
                        print('window.py', NeedCloseSystem)
                        if self.NeedCloseSystem:
                            print('log')
                            os.system('shutdown -s -t 60')
                            return
                        if not self.NeedCloseGame:
                            # 需要手动关闭游戏
                            LogUI.insert(END,
                                         time.strftime('%Y-%m-%d %H:%M:%S ',
                                                       time.localtime(time.time())) + '体力用完，需要手动关闭加成或游戏\n')
                            return
                        # 结束进程
                        hasProcess = True
                        while hasProcess:
                            if 'onmyoji' in os.popen('tasklist /FI "IMAGENAME eq onmyoji.exe"').read():
                                os.system('TASKKILL /F /IM onmyoji.exe')
                                hasProcess = True
                            else:
                                hasProcess = False
                        # 线程结束返回
                        return
                    elif i == 'end1':
                        time.sleep(random.randint(300, 800) / 1000)
                        pos = CheatPos(pos, 50)
                    elif i == 'end2':
                        newPos = (pos[0] + 80, pos[1] + 80)
                        pos = CheatPos(newPos, 5)
                    elif i == 'tiaozhan':
                        LogUI.insert(END,
                                     time.strftime('%Y-%m-%d %H:%M:%S ',
                                                   time.localtime(time.time())) + '第' + str(Count) + '轮开始\n')
                        Count += 1
                    elif i == 'reject':
                        pos = CheatPos(pos, 3)
                    else:
                        pos = CheatPos(pos, 10)
                    result.append(pos)

                    LogUI.see(END)
                else:
                    result.append(None)
            # 开始检查结果
            for i in result:
                if i is not None:
                    print(WindowShape[1] * 0.06)
                    print(WindowShape[0] * 0.96)
                    if i[0] < WindowShape[1] * 0.06 or i[1] > WindowShape[0] * 0.96:
                        continue
                    else:
                        Click(i)
                    if len(LogUI.get('1.0', 'end-1c')) > 6000:
                        LogUI.delete(1.0, END)  # 使用 delete
                        LogUI.insert(END, ' 清空日志\n')
                        LogUI.see(END)

    def Terminate(self):
        self._flag = True


# def YuHunTwoWindow(LogUI, NeedCloseGame, NeedCloseSystem):
#     """
#     自动御魂,双开模式
#     """
#     imgs = loadImgs()
#     LogUI.insert(END,
#                  time.strftime('%Y-%m-%d %H:%M:%S ',
#                                time.localtime(time.time())) + '开始挑战\n')
#     Count = 1
#     while True:
#
#         logging.debug('开始挑战')
#         screen = GetScreenShot()
#         WindowShape = screen.shape
#         result = []
#
#         # 为了优化速度，把计算屏幕截图的特征提取出来，避免重复运算
#         kp2, des2 = ComputeScreenShot(screen)
#         for i in ['tili60', 'tili80', 'auto', 'jieshou2', 'jieshou1', 'end1', 'end2', 'reject', 'queding', 'tiaozhan']:
#             obj = imgs[i]
#             # begin = time.clock()
#             pos = GetLocation(obj, kp2, des2)
#             # logging.debug('检测结算目标图像')
#             # print(time.clock()-begin)
#             if pos is not None:
#                 if i == 'tili60' or i == 'tili80':
#                     print('window.py', NeedCloseSystem)
#                     if NeedCloseSystem:
#                         print('log')
#                         os.system('shutdown -s -t 60')
#                         return
#                     if not NeedCloseGame:
#                         # print('体力用完，需要手动关闭加成或游戏')
#                         LogUI.insert(END,
#                                      time.strftime('%Y-%m-%d %H:%M:%S ',
#                                                    time.localtime(time.time())) + '体力用完，需要手动关闭加成或游戏\n')
#                         return
#                     # 结束进程
#                     hasProcess = True
#                     while hasProcess:
#                         if 'onmyoji' in os.popen('tasklist /FI "IMAGENAME eq onmyoji.exe"').read():
#                             os.system('TASKKILL /F /IM onmyoji.exe')
#                             hasProcess = True
#                         else:
#                             hasProcess = False
#                     # 线程结束返回
#                     return
#                 elif i == 'end1':
#                     time.sleep(random.randint(300, 800) / 1000)
#                     pos = CheatPos(pos, 50)
#                 elif i == 'end2':
#                     newPos = (pos[0] + 80, pos[1] + 80)
#                     pos = CheatPos(newPos, 5)
#                 elif i == 'tiaozhan':
#                     LogUI.insert(END,
#                                  time.strftime('%Y-%m-%d %H:%M:%S ',
#                                                time.localtime(time.time())) + '第' + str(Count) + '轮开始\n')
#                     Count += 1
#                 elif i == 'reject':
#                     pos = CheatPos(pos, 3)
#                 else:
#                     pos = CheatPos(pos, 10)
#                 result.append(pos)
#
#                 LogUI.see(END)
#             else:
#                 result.append(None)
#         # 开始检查结果
#         for i in result:
#             if i is not None:
#                 print(WindowShape[1] * 0.06)
#                 print(WindowShape[0] * 0.96)
#                 if i[0] < WindowShape[1] * 0.06 or i[1] > WindowShape[0] * 0.96:
#                     continue
#                 else:
#                     Click(i)
#                 if len(LogUI.get('1.0', 'end-1c')) > 6000:
#                     LogUI.delete(1.0, END)  # 使用 delete
#                     LogUI.insert(END, ' 清空日志\n')
#                     LogUI.see(END)


if __name__ == '__main__':
    pass

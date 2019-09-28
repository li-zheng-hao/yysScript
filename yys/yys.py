# -*- coding: utf-8 -*-
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

logging.basicConfig(format="%(asctime)s :%(levelname)s:%(message)s", datefmt="%d-%M-%Y %H:%M:%S", level=logging.DEBUG)
# 初始化SIFT探测器
SIFT = cv2.xfeatures2d.SIFT_create()


def GetLocation(target, screenShot):
    """
    获取目标图像在截图中的位置
    :param target:
    :param screenShot:
    :return: 返回坐标(x,y) 与opencv坐标系对应
    """
    MIN_MATCH_COUNT = 5
    img1 = target  # 查询图片
    img2 = screenShot  # 训练图片
    # result = cv2.matchTemplate(screenShot, target, cv2.TM_CCOEFF_NORMED)
    # location = numpy.where(result >= 0.8)
    # n, ex, ey = 1, 0, 0
    # for pt in zip(*location[::-1]):  # 其实这里经常是空的
    #     x, y = pt[0] + 20, pt[1] + 20
    #     show=cv2.circle(target, (x, y), 10, (0, 0, 255), 3)
    #     cv2.imshow('s',show)
    #     cv2.waitKey()
    #     cv2.destroyAllWindows()
    # res = cv2.matchTemplate(screenShot, target, cv2.TM_CCOEFF)
    # min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    #
    # left_top = max_loc  # 左上角
    # right_bottom = (left_top[0] + target.shape[0]//2, left_top[1] + target.shape[1]//2)  # 右下角
    # # return right_bottom
    # show=cv2.rectangle(screenShot, left_top, right_bottom, 255, 2)  # 画出矩形位置
    # cv2.imshow('s',show)
    # cv2.waitKey()
    # cv2.destroyAllWindows()
    # s=1

    # 用SIFT找到关键点和描述符
    kp1, des1 = SIFT.detectAndCompute(img1, None)
    kp2, des2 = SIFT.detectAndCompute(img2, None)

    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
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
        newPos = CheatPos(targetPosition)
        time.sleep(random.randint(200, 500) / 1000)
        pyautogui.moveTo(newPos, duration=0.1)
        pyautogui.click(newPos)
        time.sleep(random.randint(100, 200) / 1000)


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
    screen.save('screen.jpg')
    screen = cv2.imread('screen.jpg')
    logging.info('截取一帧')
    return screen


def YuHunTwoWindow(LogUI):
    """
    自动御魂,双开模式
    """
    imgs = loadImgs()
    PassTime=1
    while True:
        LogUI.insert(END, '开始挑战\n')

        logging.debug('开始挑战')
        isStageOnePass=False
        # 开始挑战
        while isStageOnePass==False:
            screen=GetScreenShot()
            for i in ['tiaozhan']:
                obj = imgs[i]
                pos = GetLocation(obj, screen)
                if not pos == None:
                    isStageOnePass=True
                    Click(pos)
                    time.sleep(0.1)


        logging.debug('结算奖励')
        isStageTwoPass=False
        clickCount = 0
        # 结算奖励 双开计算两次
        while isStageTwoPass==False:
            screen = GetScreenShot()
            for i in ['end1', 'end2']:
                obj = imgs[i]
                pos = GetLocation(obj, screen)
                logging.debug('检测结算目标图像')
                if not pos == None:
                    logging.info('结算点击'+str(clickCount)+'次')
                    Click(pos)
                    if clickCount == 4:
                        isStageTwoPass=True
                    clickCount += 1


        isStageThreePass=False
        invitedParter = False
        clickCount=0
        while isStageThreePass==False:
            screen = GetScreenShot()
            if invitedParter == True:
                break
            logging.debug('第一次邀请队友并自动组队')
            # 邀请队友

            for i in ['queding', 'jieshou1']:
                obj = imgs[i]
                pos = GetLocation(obj, screen)
                if not pos == None:
                    clickCount += 1
                    Click(pos)
                    if clickCount == 2:
                        invitedParter = True
                        isStageThreePass=True
                    continue

        logging.info('已通关副本'+str(PassTime)+'次')
        PassTime+=1
        LogUI.insert(END, '已经通关'+str(PassTime)+'次\n')

if __name__ == '__main__':
    pass
    # begin=time.clock()
    # a=cv2.imread('img/ying.jpg',0)
    # b=cv2.imread('img/screenshot3.png',0)
    # res=GetLocation(a,b)
    # print(time.clock()-begin)
    # res1=Click(res)
    # print(res,res1)

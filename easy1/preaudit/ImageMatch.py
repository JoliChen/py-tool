# -*- coding: UTF-8 -*-

import cv2
import numpy as np
import os
import os.path
from matplotlib import pyplot as plt

# 文件读取并显示
# img = cv2.imread("kitchen.jpeg")
# print("hello opencv "+ str(type(img)))
# # print(img)
# cv2.namedWindow("Image")
# cv2.imshow("Image",img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()


# img = cv2.imread('kitchen.jpeg', 1)
# temp = cv2.imread('Light.png', 1)
# w,h = temp.shape[::-1]
#
# print(w,h,sep="  ")
# # print(img)
# cv2.namedWindow("Image")
# cv2.imshow("Image", img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()


# img = cv2.imread('kitchen.jpeg', 0)
# img2 = img.copy()
# template = cv2.imread('Light.png', 0)
# w, h = template.shape[::-1]
# print(template.shape)
#
# # All the 6 methods for comparison in a list
# methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
#            'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']
#
# for meth in methods:
#     img = img2.copy()
#     method = eval(meth)
#
#     # Apply template Matching
#     res = cv2.matchTemplate(img, template, method)
#     min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
#
#     # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
#     if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
#         top_left = min_loc
#     else:
#         top_left = max_loc
#     bottom_right = (top_left[0] + w, top_left[1] + h)
#
#     cv2.rectangle(img, top_left, bottom_right, 255, 2)
#
#     plt.subplot(121), plt.imshow(res, cmap='gray')
#     plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
#     plt.subplot(122), plt.imshow(img, cmap='gray')
#     plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
#     plt.suptitle(meth)
#
#     plt.show()

# image = cv2.imread("kitchen.jpeg", 0)
# hist = cv2.calcHist([image],
#                     [0],
#                     None,
#                     [256],
#                     [0, 256])
# plt.plot(hist),plt.xlim([0,256])
# plt.show()

# # hist = cv2.calcHist([image],[0,1,2],None,[256,256,256],[[0,255],[0,255],[0,255]])
# # cv2.imshow("img",image)
# cv2.imshow("hist", hist)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# image = cv2.imread("kitchen.jpeg", 0)
# hist = plt.hist(image.ravel(), 256, [0, 256])
# plt.show(hist)

def hist_similar(lhist, rhist, lpixal,rpixal):
    rscale = rpixal/lpixal
    rhist = rhist/rscale
    assert len(lhist) == len(rhist)
    likely =  sum(1 - (0 if l == r else float(abs(l - r)) / max(l, r)) for l, r in zip(lhist, rhist)) / len(lhist)
    if likely == 1.0:
        return [1.0]
    return likely


def get_histGBR(path):
    img = cv2.imread(path)

    pixal = img.shape[0] * img.shape[1]
    # print(pixal)
    # scale = pixal/100000.0
    # print(scale)
    total = np.array([0])
    for i in range(3):
        histSingle = cv2.calcHist([img], [i], None, [256], [0, 256])
        total = np.vstack((total, histSingle))
    # plt.plot(total)
    # plt.xlim([0, 768])
    # plt.show()
    return (total, pixal)


if __name__ == '__main__':
    targetHist, targetPixal = get_histGBR('test.jpg')
    rootdir = "/Users/YM/Desktop/DCIM"
    # aHist = get_histGBR('a.png')
    # bHist = get_histGBR('Light.png')
    #
    # print(hist_similar(aHist, bHist))
    resultDict = {}
    for parent, dirnames, filenames in os.walk(rootdir):
        # for dirname in dirnames:
        #     print("parent is: " + parent)
        #     print("dirname is: " + dirname)
        for filename in filenames:
            if (filename[-3:] == 'jpg'):
                jpgPath = os.path.join(parent, filename)
                testHist, testPixal = get_histGBR(jpgPath)
                # print(hist_similar(targetHist,testHist)[0])
                resultDict[jpgPath]=hist_similar(targetHist,testHist,targetPixal,testPixal)[0]

    # print(resultDict)
    # for each in resultDict:
    #     print(each, resultDict[each],sep="----")
    sortedDict = sorted(resultDict.items(), key=lambda asd: asd[1], reverse=True)
    for i in range(5):
        print(sortedDict[i])

# 作者：快要没时间了
# 链接：https://www.jianshu.com/p/5fb6d4e9ad05
# 來源：简书
# 著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。
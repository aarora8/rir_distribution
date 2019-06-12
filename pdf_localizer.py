import numpy as np
import os
import xml.dom.minidom as minidom
from PIL import Image
import fitz

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

pageid = -1
xml_path = '/Users/ashisharora/text2.xml'
doc = minidom.parse(xml_path)
page1 = doc.getElementsByTagName('page')
count = 0


xMin_list = dict()
xMax_list = dict()
yMin_list = dict()
yMax_list = dict()
width_list = list()
height_list = list()

# fig,ax = plt.subplots(1)

fig = plt.figure()
ax = fig.add_subplot(111, aspect='equal')

for page in page1:
    pageid += 1
    print("pageID is as follows:")
    print(pageid)
    width = float(page.getAttribute('width'))
    height = float(page.getAttribute('height'))
    width_list.append(width)
    height_list.append(height)

    word1 = page.getElementsByTagName('word')
    wordid = 0
    xMin_list[pageid] = list()
    yMin_list[pageid] = list()
    xMax_list[pageid] = list()
    yMax_list[pageid] = list()
    for word in word1:
        wordid += 1
        # print(wordid)
        xMin = float(word.getAttribute('xMin'))
        yMin = float(word.getAttribute('yMin'))
        xMax = float(word.getAttribute('xMax'))
        yMax = float(word.getAttribute('yMax'))
        xMin_list[pageid].append(xMin)
        yMin_list[pageid].append(yMin)
        xMax_list[pageid].append(xMax)
        yMax_list[pageid].append(yMax)


doc = fitz.Document('/Users/ashisharora/Desktop/A11_MissionReport.pdf')
page = doc.loadPage(0)
pix = page.getPixmap()
mode = "RGBA" if pix.alpha else "RGB"
img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)

xMin_page_list = xMin_list[0]
yMin_page_list = yMin_list[0]
xMax_page_list = xMax_list[0]
yMax_page_list = yMax_list[0]
for i in range(len(xMin_page_list)):
    xMin = xMin_page_list[i]
    xMax = xMax_page_list[i]
    yMin = yMin_page_list[i]
    yMax = yMax_page_list[i]
    rect1 = patches.Rectangle((xMin, yMin), xMax - xMin, yMax - yMin, linewidth=1, edgecolor='r',
                              facecolor='none')
    ax.add_patch(rect1)
ax.imshow(img)
# plt.show()
fig.savefig('/Users/ashisharora/Desktop/dct/plots/img1.png', dpi=600)
# input("Press the <ENTER> key to continue...")

# for i in range(len(doc)):
#     page = doc.loadPage(i)
#     pix = page.getPixmap()
#     mode = "RGBA" if pix.alpha else "RGB"
#     img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
#     xMin_page_list = xMin_list[i]
#     yMin_page_list = yMin_list[i]
#     xMax_page_list = xMax_list[i]
#     yMax_page_list = yMax_list[i]
#     for j in range(len(xMin_page_list)):
#         xMin = xMin_page_list[j]
#         xMax = xMax_page_list[j]
#         yMin = yMin_page_list[j]
#         yMax = yMax_page_list[j]
#         rect1 = patches.Rectangle((xMin, yMin), xMax - xMin, yMax - yMin, linewidth=1, edgecolor='r',
#                               facecolor='none')
#         ax.add_patch(rect1)
#     ax.imshow(img)
#     plt.show()
#     input("Press the <ENTER> key to continue...")
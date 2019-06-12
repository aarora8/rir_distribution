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

xMin_dict = dict()
xMax_dict = dict()
yMin_dict = dict()
yMax_dict = dict()
width_list = list()
height_list = list()
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
    xMin_dict[pageid] = list()
    yMin_dict[pageid] = list()
    xMax_dict[pageid] = list()
    yMax_dict[pageid] = list()
    for word in word1:
        wordid += 1
        xMin = float(word.getAttribute('xMin'))
        yMin = float(word.getAttribute('yMin'))
        xMax = float(word.getAttribute('xMax'))
        yMax = float(word.getAttribute('yMax'))
        xMin_dict[pageid].append(xMin)
        yMin_dict[pageid].append(yMin)
        xMax_dict[pageid].append(xMax)
        yMax_dict[pageid].append(yMax)


def get_linedict_from_pagelist(xMin_page_list, yMin_page_list, xMax_page_list, yMax_page_list):
    xMin_line_dict = dict()
    xMax_line_dict = dict()
    yMin_line_dict = dict()
    yMax_line_dict = dict()
    xMin_line_dict[0] = list()
    xMax_line_dict[0] = list()
    yMin_line_dict[0] = list()
    yMax_line_dict[0] = list()
    prev_yMin = yMin_page_list[0]
    line_id = 0
    for i in range(len(yMin_page_list)):
        curr_yMin = yMin_page_list[i]
        if prev_yMin != curr_yMin:
            prev_yMin = curr_yMin
            line_id += 1
            xMin_line_dict[line_id] = list()
            xMax_line_dict[line_id] = list()
            yMin_line_dict[line_id] = list()
            yMax_line_dict[line_id] = list()
        xMin_line_dict[line_id].append(xMin_page_list[i])
        yMin_line_dict[line_id].append(yMin_page_list[i])
        xMax_line_dict[line_id].append(xMax_page_list[i])
        yMax_line_dict[line_id].append(yMax_page_list[i])
    return xMin_line_dict, yMin_line_dict, xMax_line_dict, yMax_line_dict


def get_linelist_from_linedict(xMin_line_dict, yMin_line_dict, xMax_line_dict, yMax_line_dict):
    xMin_line_list = list()
    xMax_line_list = list()
    yMin_line_list = list()
    yMax_line_list = list()
    for lineid in sorted(xMin_line_dict.keys()):
        xMin_list = xMin_line_dict[lineid]
        xMax_list = xMax_line_dict[lineid]
        yMin_list = yMin_line_dict[lineid]
        yMax_list = yMax_line_dict[lineid]
        xMin = xMin_list[0]
        xMax = xMax_list[-1]
        yMin = yMin_list[0]
        yMax = yMax_list[0]
        xMin_line_list.append(xMin)
        xMax_line_list.append(xMax)
        yMin_line_list.append(yMin)
        yMax_line_list.append(yMax)
    return xMin_line_list, yMin_line_list, xMax_line_list, yMax_line_list


filtered_count = 0
filtered_count1 = 0
doc = fitz.Document('/Users/ashisharora/Desktop/A11_MissionReport.pdf')
img_path = '/Users/ashisharora/Desktop/dct/pdf_imgs2/'
for pageid in range(len(doc)):
    full_dir_path = img_path + str(pageid)
    # os.mkdir(full_dir_path)
    page = doc.loadPage(pageid)
    pix = page.getPixmap()
    mode = "RGBA" if pix.alpha else "RGB"
    img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
    xMin_page_list = xMin_dict[pageid]
    yMin_page_list = yMin_dict[pageid]
    xMax_page_list = xMax_dict[pageid]
    yMax_page_list = yMax_dict[pageid]
    if len(yMax_page_list) == 0:
        print(pageid)
        continue
    print(pageid)
    xMin_line_dict, yMin_line_dict, xMax_line_dict, yMax_line_dict = get_linedict_from_pagelist(xMin_page_list, yMin_page_list, xMax_page_list, yMax_page_list)
    xMin_line_list, yMin_line_list, xMax_line_list, yMax_line_list = get_linelist_from_linedict(xMin_line_dict, yMin_line_dict, xMax_line_dict, yMax_line_dict)
    rect_list = list()
    for lineid in range(len(xMin_line_list)):
        xMin = xMin_line_list[lineid]
        xMax = xMax_line_list[lineid]
        yMin = yMin_line_list[lineid]
        yMax = yMax_line_list[lineid]
        rect1 = patches.Rectangle((xMin, yMin), xMax - xMin, yMax - yMin, linewidth=1, edgecolor='r',
                              facecolor='none')
        box = (xMin, yMin, xMax, yMax)
        if (xMax <= xMin) or (yMax <= yMin):
            print(lineid)
            filtered_count += 1
            continue
        if (xMax - xMin) <=30 or (yMax - yMin) <= 2:
            print(lineid)
            filtered_count1 += 1
            continue
        ax.add_patch(rect1)
        region_initial = img.crop(box)
        img_name = str(pageid) + '_' + str(lineid) +'.png'
        full_img_path = full_dir_path + '/' + img_name
        # region_initial.save(full_img_path, quality=100)
    ax.imshow(img)
    img_name = str(pageid) + '.png'
    full_img_path = img_path + img_name
    fig.savefig(full_img_path, dpi=600)
    ax.clear()

print(filtered_count)
print(filtered_count1)
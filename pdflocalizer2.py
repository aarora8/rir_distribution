import pdfplumber
import numpy as np
import os
import xml.dom.minidom as minidom
import xmltodict


text_file = os.path.join('/Users/ashisharora/text1.xml')
text_fh_r = open(text_file, 'r')

text_file_write = os.path.join('/Users/ashisharora/text2.xml')
text_fh_w = open(text_file_write, 'w')

count = 0
with open(text_file, 'r') as f:
    for line in f:
        croppedline = line.split('>')[0]
        new_line = ''
        if 'page' in croppedline :
            new_line = croppedline + '>\n'
        if 'DocumentList' in croppedline :
            new_line = croppedline + '>\n'
        if 'word' in croppedline:
            new_line = croppedline + '></word>\n'
        text_fh_w.write(new_line)

# doc = fitz.Document('/Users/ashisharora/Desktop/A11_MissionReport.pdf')
# page = doc.loadPage(0)
# pix = page.getPixmap()
# mode = "RGBA" if pix.alpha else "RGB"
# img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)

# xMin_page_list = xMin_list[0]
# yMin_page_list = yMin_list[0]
# xMax_page_list = xMax_list[0]
# yMax_page_list = yMax_list[0]
# for i in range(len(xMin_page_list)):
#     xMin = xMin_page_list[i]
#     xMax = xMax_page_list[i]
#     yMin = yMin_page_list[i]
#     yMax = yMax_page_list[i]
#     rect1 = patches.Rectangle((xMin, yMin), xMax - xMin, yMax - yMin, linewidth=1, edgecolor='r',
#                               facecolor='none')
#     ax.add_patch(rect1)
# ax.imshow(img)
# fig.savefig('/Users/ashisharora/Desktop/dct/plots/img1.png', dpi=600)

# fig,ax = plt.subplots(1)

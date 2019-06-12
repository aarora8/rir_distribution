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

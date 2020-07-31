import requests
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import re
import os
from googletrans import Translator
translator = Translator()


def is_float(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return True


def pdf_to_text(input_path):
    """
    @param input_path: pdf path
    """
    fp = open(input_path, 'rb')
    rsrcmgr = PDFResourceManager()
    out_fp = StringIO()
    la_params = LAParams()
    la_params.detect_vertical = True
    device = TextConverter(rsrcmgr, out_fp, codec='utf-8', laparams=la_params)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for page in PDFPage.get_pages(fp, pagenos=None, maxpages=0, password=None, caching=True, check_extractable=True):
        interpreter.process_page(page)
    text = out_fp.getvalue()
    fp.close()
    device.close()
    out_fp.close()
    
    # 改行で分割する
    lines = text.splitlines()

    outputs = []
    output = ""

    # 除去するutf8文字
    replace_strs = [b'\x00']

    is_blank_line = False

    # 分割した行でループ
    for line in lines:

        # byte文字列に変換
        line_utf8 = line.encode('utf-8')

        # 余分な文字を除去する
        for replace_str in replace_strs:
            line_utf8 = line_utf8.replace(replace_str, b'')

        # strに戻す
        line = line_utf8.decode()

        # 連続する空白を一つにする
        line = re.sub("[ ]+", " ", line)

        # 前後の空白を除く
        line = line.strip()
        #print("aft:[" + line + "]")

        # 空行は無視
        if len(line) == 0:
            is_blank_line = True
            continue

        # 数字だけの行は無視
        if is_float(line):
            continue

        # 1単語しかなく、末尾がピリオドで終わらないものは無視
        if line.split(" ").count == 1 and not line.endswith("."):
            continue

        #前の行からの続きの場合
        if not is_blank_line and output.endswith("-"):
            output = output[:-1]
        #それ以外の場合は、単語の切れ目として半角空白を入れる
        else:
            output += " "

        #print("[" + str(line) + "]")
        output += str(line)
        is_blank_line = False

    outputs.append(output)
    
    return outputs



def main(input_path, output_path):
    '''
    @param input_path: input pdf path
    @param output_path: output text file path
    '''
    text = pdf_to_text(input_path)
    text_ja = translator.translate(text, src='en', dest='ja')
    print(text_ja[0].text)
    input()



if __name__ == '__main__':
    input_path = '/home/hiroaki-k4/Pictures/1804.02767.pdf'
    output_path = '/home/hiroaki-k4/my_project/translate/sample.txt'
    main(input_path, output_path)
    
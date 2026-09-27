import re

from app.models.Paragraph import Paragraph


def clean_text(text):
    # 去除特殊符号
    text = text.replace("\ufffe", "")
    # 去除空格
    text = text.strip()
    #多个空格合并成一个,清洗整个页面文本的头和尾
    text = re.sub(r" +", " ", text)
    #保留段落结构
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text
def split_paragraphs(page_text,page_number):
    paragraphs = page_text.split("\n\n")
    paragraph_list = []
    for paragraph in paragraphs:
        #清洗每一个切出来的 Paragraph 的头和尾
        paragraph = paragraph.strip()
        #不是空字符串才能封装成对象放进paragraph列表中
        if paragraph:
            paragraph_list.append(Paragraph(text = paragraph,
                           pages = [page_number]))
    #列表推导式
    '''等价于
    paragraphs_list = []
    for p in paragraphs:
        p= p.strip()
        if p:
            paragraphs_list.append(p)
    '''
    return paragraph_list





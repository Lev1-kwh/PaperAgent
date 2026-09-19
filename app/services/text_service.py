import re
def clean_text(text):
    # 去除特殊符号
    text = text.replace("\ufffe", "")
    # 去除空格
    text = text.strip()
    #多个空格合并成一个
    text = re.sub(r" +", " ", text)
    #保留段落结构
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text
def split_paragraphs(text):
    paragraphs = text.split("\n\n")
    paragraphs = [
        p.strip()
        for p in paragraphs
        if p.strip()
    ]#列表推导式
    '''等价于
    paragraphs_list = []
    for p in paragraphs:
        p= p.strip()
        if p:
            paragraphs_list.append(p)
    '''
    return paragraphs






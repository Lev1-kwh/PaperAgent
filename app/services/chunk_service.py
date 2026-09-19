def split_long_paragraph(paragraph, chunk_size):
    #创建空列表用于存储切分好的短段落
    chunks = []
    #对目标长段落进行遍历，下标每次跳跃chunk_size,然后再切分为长度为chunk_size的字符串
    for i in range(0, len(paragraph),chunk_size ):
        chunks.append(paragraph[i:i+chunk_size])
    return chunks
def chunk_paragraphs(paragraphs, chunk_size,):
    #新建空列表用于存储chunk
    chunk_list =[]
    #空字符串临时容器用于判断当前容量是否能够装下一个段落
    current_chunk = ""
    #遍历已经分好的段落
    for p in paragraphs:
        #先考虑超长段落的情况
        if len(p)>chunk_size:
        #同时也得考虑超长段落之前的短段落
        #若临时容器已有短段落则存入chunk_list中并且重置临时容器
            if current_chunk :
                chunk_list.append(current_chunk)
                current_chunk =""
            ##对超长段落进行切分
            split_p =   split_long_paragraph(p,chunk_size)
            chunk_list.extend(split_p)
        #chunk_list.extend(split_p)等价于for chunk in split_p...
        #短段落情况
        else:
            # （短段落处理）判断加入当前段落后是否超过限制
            if current_chunk:
                # 当前已有内容，需要加换行符
                new_length = len(current_chunk) + len(p) + 1
            else:
                # 第一次加入，没有换行符
                new_length = len(p)
            if new_length <= chunk_size:
                # 当前chunk为空，直接加入
                if not current_chunk:
                    current_chunk = p
                # 已经有内容，用换行符连接
                else:
                    current_chunk += "\n" + p
            else:
                # 当前chunk装不下了
                # 先保存旧chunk
                chunk_list.append(current_chunk)
                # 开启新的chunk
                current_chunk = p
        #最后将循环结束时临时容器的段落存进chunk_list
    if current_chunk:
            chunk_list.append(current_chunk)
    return chunk_list
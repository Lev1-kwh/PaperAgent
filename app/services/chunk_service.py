

from app.models.chunk import  Chunk


def split_long_paragraph(paragraph, chunk_size,paper_id):
    #创建空列表用于存储切分好的短段落
    chunks = []
    #对目标长段落进行遍历，下标每次跳跃chunk_size,然后再切分为长度为chunk_size的字符串
    for i in range(0, len(paragraph.text),chunk_size ):
        chunks.append(Chunk(chunk_id = i,
                            paper_id = paper_id,
                            text = paragraph.text[i:i+chunk_size],
                      pages = paragraph.pages))
    return chunks
def chunk_paragraphs(paragraphs, chunk_size,paper_id):
    #新建空列表用于存储chunk
    chunk_list =[]
    #空字符串临时容器用于判断当前容量是否能够装下一个段落
    current_chunk = ""
    #临时容器中段落隶属的页码
    current_pages =[]
    #遍历已经分好的段落
    for paragraph in paragraphs:
        #先考虑超长段落的情况
        if len(paragraph.text)>chunk_size:
        #同时也得考虑超长段落之前的短段落
        #若临时容器已有短段落则存入chunk_list中并且重置临时容器
            if current_chunk :
                chunk_list.append(Chunk(
                    chunk_id = -1,
                    paper_id = paper_id,
                    text = current_chunk,
                    pages = list(set(current_pages))
                ))
                current_chunk =""
                current_pages=[]
            ##对超长段落进行切分
            split_chunks =   split_long_paragraph(paragraph,chunk_size,paper_id)
            chunk_list.extend(split_chunks)
        #chunk_list.extend(split_p)等价于for chunk in split_p...
        #短段落情况
        else:
            # （短段落处理）判断加入当前段落后是否超过限制
            if current_chunk:
                # 当前已有内容，需要加换行符
                new_length = len(current_chunk) + len(paragraph.text) + 1
            else:
                # 第一次加入，没有换行符
                new_length = len(paragraph.text)
            if new_length <= chunk_size:
                # 当前chunk为空，直接加入
                if not current_chunk:
                    current_chunk = paragraph.text
                # 已经有内容，用换行符连接
                else:
                    current_chunk += "\n" + paragraph.text
                current_pages.extend(paragraph.pages)
            else:
                # 当前chunk装不下了
                # 先保存旧chunk
                chunk_list.append(Chunk(
                    chunk_id = -1,
                    paper_id = paper_id,
                    text = current_chunk,
                    pages = list(set(current_pages))
                ))
                # 开启新的chunk
                current_chunk = paragraph.text
                current_pages = paragraph.pages.copy()

        #最后将循环结束时临时容器的段落存进chunk_list
    if current_chunk:
            chunk_list.append(
                Chunk(
                    chunk_id = -1,
                    paper_id = paper_id,
                    text = current_chunk,
                    pages = list(set(current_pages))
                ))
    for index, chunk in enumerate(chunk_list):
            chunk.chunk_id =index
    return chunk_list
#current_chunks跟curren_pages存的永远是短段落的数据
#假如是长段落则直接把长段落切分成目标长度短段落然后封装成chunk对象存进chunk列表
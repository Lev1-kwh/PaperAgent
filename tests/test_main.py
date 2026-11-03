from unittest.mock import patch, MagicMock
from datetime import datetime
import pymupdf
import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database.paper import Paper
from fastapi.testclient import TestClient
from app.main import app
from app.models.paper import Question
from app.services.paper_service import delete_paper



def test_main():
   client = TestClient(app)
   response = client.get("/")
   assert response.status_code == 200
   assert response.json() == {"message": "PaperAgent is running"}
def test_list_papers():
   # Mock（模拟）测试：
# patch() 中的字符串表示真实的模块路径，不是虚构的函数名。
# app.routers.paper.get_all_papers 表示 app/routers/paper.py 模块中的 get_all_papers 名称。
# 因为路由通过 from app.services.paper_service import get_all_papers 导入函数，
# 所以测试时应替换路由实际查找函数的位置，而不是函数最初定义的位置。
# return_value=[] 表示 Mock 函数被调用时直接返回空列表，避免查询真实数据库。
# with 代码块结束后，patch 会自动恢复原来的函数，不影响正式业务代码
   with patch("app.routers.paper.get_all_papers",return_value = []):
      client = TestClient(app)
      response = client.get("/papers")
      assert response.status_code == 200
      assert response.json() == []
def test_list_papers_with_data():
   mock_paper = Paper(
      paper_id="test-paper-001",
      title="DNA Fountain",
      author="Erlich",
      filename="dna_fountain.pdf",
      created_at=datetime(2026, 10, 24, 10, 0, 0)
   )
   with patch("app.routers.paper.get_all_papers",return_value = [mock_paper]):
      client = TestClient(app)
      response = client.get("/papers")
      assert response.status_code == 200
      assert response.json()[0]["title"] == "DNA Fountain"
      assert len(response.json()) == 1
      assert response.json()[0]["created_at"] == "2026-10-24T10:00:00"
      #json:list[dict],列表里面装字典。
      #[mock_paper]:list[Paper],列表中直接装Paper对象
      #[0]["title"]:取第一个字典中的title字段的值
def test_show_paper_with_data():
      mock_paper = Paper(
                        paper_id="test-paper-001",
                        title= "DNA Fountain",
                        author = "zhangsan",
                        filename="dna_fountain.pdf",
                        created_at=datetime(2026, 10, 26, 10, 0, 0)
      )

      with patch("app.routers.paper.get_paper_by_id",return_value = mock_paper):
         client = TestClient(app)
         response = client.get("/papers/test-paper-001")
         assert response.status_code == 200
         assert response.json()["paper_id"] == "test-paper-001"
         assert response.json()["title"] == "DNA Fountain"
         assert response.json()["author"] == "zhangsan"
         assert response.json()["created_at"] == "2026-10-26T10:00:00"

def test_show_paper_not_found():
   with patch("app.routers.paper.get_paper_by_id",return_value = None):
      client = TestClient(app)
      response = client.get("/papers/test-paper-001")
      assert response.status_code == 404
      assert response.json() == {"detail": "Paper not found"}

def test_upload_non_pdf():
   file = {
      "file":("test.txt",b"hello world","text/plain"),
   }
   data={
      "title":"测试论文",
      "author":"测试作者"   }
   client = TestClient(app)
   response = client.post("/papers/upload", files=file,data=data)
   assert response.status_code == 400
   assert response.json() == {"detail": "只允许上传pdf文件"}

#tmp_path 是 pytest 提供的内置 fixture，
# 会为每个测试提供独立的临时目录。
# 测试完成后，pytest 会负责清理该目录。
def test_upload_success(tmp_path):
   # 新建一个空白PDF文档
   doc = pymupdf.open()
   # 添加一页，并写入一段测试文字
   page = doc.new_page()
   page.insert_text((72, 72), "PaperAgent test PDF")
   # 将pdf转换为字节数据
   pdf_bytes = doc.tobytes()
   # 关闭pdf文档
   doc.close()
   #创建模拟数据库Session
   #spec=Session 表示让MagicMock参考SQLAIchemy的Session类型，
   # 限制它只能模拟这个类型所具有的属性和方法，
   # 也就是可以调用add(),commit()等方法但是不会真的访问数据库

   mock_session = MagicMock(spec=Session)
   with patch("app.routers.paper.os.path.abspath",return_value=str(tmp_path)):
      with patch("app.routers.paper.SessionLocal",return_value=mock_session):
         #chunk_paragraphs模拟返回一个文本列表
         with patch("app.routers.paper.chunk_paragraphs",return_value = ["mock chunk"]):
            #embed_chunks模拟返回一个向量列表
            with patch("app.routers.paper.embed_chunks",return_value = [[0.1,0.2]]):
               #add_chunks不需要返回值，上传函数只需要调用它完成写入操作；
               # 而默认的Mock不会真正写入Chroma
               with patch("app.routers.paper.add_chunks"):
                        client = TestClient(app)
                        response = client.post("/papers/upload", files={
                           "file": ("test.pdf",pdf_bytes,"application/pdf")
                        },
                             data={
                                "title":"测试论文",
                                "author":"测试作者"
                             } )
                        assert response.json()["title"] == "测试论文"
                        assert response.status_code == 201
                        assert response.json()["author"]=="测试作者"
                        assert response.json()["message"]=="上传成功"
                        #验证模拟的数据库Session的commit()方法恰好被调用了一次
                        mock_session.commit.assert_called_once()
                        assert response.json()["chunk_count"]==1
def test_upload_commit_failure(tmp_path):
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), "PaperAgent test PDF")
    pdf_bytes = doc.tobytes()
    doc.close()
    mock_session = MagicMock(spec=Session)
    #模拟数据库提交失败
    #side_effect:控制调用时发生什么
    #assert_calles_once():检查调用实际发生了几次
    mock_session.commit.side_effect = RuntimeError("模拟数据库提交失败")
    with patch("app.routers.paper.os.path.abspath", return_value=str(tmp_path)):
        with patch("app.routers.paper.SessionLocal", return_value=mock_session):
            # chunk_paragraphs模拟返回一个文本列表
            with patch("app.routers.paper.chunk_paragraphs", return_value=["mock chunk"]):
                # embed_chunks模拟返回一个向量列表
                with patch("app.routers.paper.embed_chunks", return_value=[[0.1, 0.2]]):
                    # add_chunks不需要返回值，上传函数只需要调用它完成写入操作；
                    # 而默认的Mock不会真正写入Chroma
                    with patch("app.routers.paper.add_chunks") as mock_add_chunks:
                        with patch("app.routers.paper.delete_chunks") as mock_delete_chunks:
                            client = TestClient(app)
                            #这里的含义是：我们预期这次请求会抛出 RuntimeError，
                            # 并且异常消息包含指定文字。
                            # 如果没有抛出预期异常，测试就会失败。
                            with pytest.raises(RuntimeError,match="模拟数据库提交失败"):
                                client.post("/papers/upload",
                                            files={"file": ("test.pdf",pdf_bytes,"application/pdf")},
                                            data={"title":"测试论文","author":"测试作者"})
                            mock_session.rollback.assert_called_once()
                            mock_session.commit.assert_called_once()
                            mock_add_chunks.assert_called_once()
                            mock_delete_chunks.assert_called_once()
def test_upload_chroma_failure(tmp_path):
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), "PaperAgent test PDF")
    pdf_bytes = doc.tobytes()
    doc.close()
    mock_session = MagicMock(spec=Session)
    with patch("app.routers.paper.os.path.abspath",return_value=str(tmp_path)):
        with patch("app.routers.paper.SessionLocal", return_value=mock_session):
            with patch("app.routers.paper.chunk_paragraphs", return_value=["mock chunk"]):
                with patch("app.routers.paper.embed_chunks", return_value=[[0.1, 0.2]]):
                    with patch("app.routers.paper.delete_chunks") as mock_delete_chunks:
                        with patch("app.routers.paper.add_chunks",side_effect = RuntimeError("模拟Chroma写入失败")) as mock_insert_chunks:
                            client = TestClient(app)
                            with pytest.raises(RuntimeError,match="模拟Chroma写入失败"):
                                client.post("/papers/upload",
                                                   files={"file": ("test.pdf",pdf_bytes,"application/pdf")},
                                                   data={"title":"模拟论文",
                                                         "author":"模拟作者"})
                            mock_insert_chunks.assert_called_once()
                            mock_delete_chunks.assert_called_once()
                            #查找临时目录下所以.pdf文件，并确认结果为空列表
                            assert list(tmp_path.glob("*.pdf")) == []
def test_delete_paper_success():
    #return_value指的是service层的返回值而不是router层的返回值
    with patch("app.routers.paper.delete_paper",return_value=True):
        client = TestClient(app)
        response = client.delete("/papers/test-paper-001")
        assert response.status_code == 200
        assert response.json()["paper_id"] == "test-paper-001"
        assert response.json()["message"] == "Paper deleted"
def test_delete_paper_not_found():
    with patch("app.routers.paper.delete_paper",return_value=False):
        client = TestClient(app)
        response = client.delete("/papers/test-paper-001")
        assert response.status_code == 404
        assert response.json()["detail"] == "Paper not found"
def test_delete_paper_failure():
    with patch("app.routers.paper.delete_paper",side_effect=RuntimeError("模拟删除失败")):
        client = TestClient(app)
        '''当 delete_paper() 抛出 RuntimeError 时：
1. 删除路由捕获这个异常。
2. 路由将它转换为 HTTPException(500)。
3. FastAPI 把它转换成正常的 HTTP 响应。
4. client.delete() 返回 Response 对象。'''
        response = client.delete("/papers/test-paper-001")
        assert response.status_code == 500
        assert response.json()["detail"] == "Delete failed"


def test_delete_paper_service_not_found():
    mock_session = MagicMock(spec=Session)
    #第一次 return_value 表示 scalars() 调用后返回的对象；
    # 第二次 return_value 表示 one_or_none() 调用后返回的结果。
    mock_session.scalars.return_value.one_or_none.return_value = None
    # 设置模拟客户端的行为：
    # 当业务代码调用 get_collection(name="papers") 时，
    # 返回我们创建的 mock_collection。
    mock_chroma_client = MagicMock()
    mock_collection = MagicMock()
    mock_chroma_client.get_collection.return_value = mock_collection
    with patch("app.services.paper_service.SessionLocal", return_value=mock_session):
        with patch("app.services.paper_service.chromadb.PersistentClient",return_value=mock_chroma_client):
            result = delete_paper("missing-paper")
            assert result is False
            assert mock_collection.delete.call_count == 0
            assert mock_session.close.call_count == 1
def test_delete_paper_service_success():
    mock_paper = Paper(
        paper_id="test-paper-001",
        title="DNA Fountain",
        author="Erlich",
        filename="dna_fountain.pdf",
        created_at=datetime(2026, 10, 24, 10, 0, 0)
    )
    mock_session = MagicMock(spec=Session)
    mock_session.scalars.return_value.one_or_none.return_value = mock_paper
    mock_chroma_client = MagicMock()
    mock_collection = MagicMock()
    #进入delete_paper()后调用get_collection()时调用对象为mock_client,
    #调用后返回的对象变为mock_collection
    mock_chroma_client.get_collection.return_value = mock_collection
    with patch("app.services.paper_service.SessionLocal", return_value=mock_session):
        with patch("app.services.paper_service.chromadb.PersistentClient", return_value=mock_chroma_client):
            result = delete_paper("test-paper-001")
            assert result is True
            assert mock_collection.delete.call_count == 1
            assert mock_session.delete.call_count == 1
            assert mock_session.commit.call_count == 1
            assert mock_session.close.call_count == 1
def test_delete_paper_service_commit_failure():
    mock_session = MagicMock(spec=Session)
    mock_session.scalars.return_value.one_or_none.return_value = Paper(
        paper_id="test-paper-001",
        title="DNA Fountain",
        author="Erlich",
        filename="dna_fountain.pdf",
        created_at=datetime(2026, 10, 24, 10, 0, 0)
    )
    mock_chroma_client = MagicMock()
    mock_collection = MagicMock()
    mock_chroma_client.get_collection.return_value = mock_collection
    mock_session.commit.side_effect = RuntimeError("模拟数据库提交失败")
    with patch("app.services.paper_service.SessionLocal", return_value=mock_session):
        with patch("app.services.paper_service.chromadb.PersistentClient", return_value=mock_chroma_client):
            '''进入 with 代码块。
                执行 delete_paper()。
                如果发生 RuntimeError，立即中断当前代码块剩余语句。
                pytest.raises() 捕获这个异常。
                检查异常类型是否符合预期。
                如果符合，测试继续执行 with 后面的代码'''
            with pytest.raises(RuntimeError,match="模拟数据库提交失败"):
                 delete_paper("test-paper-001")

            #因此断言不能写在该代码块内
            assert mock_collection.delete.call_count == 1
            assert mock_session.delete.call_count == 1
            assert mock_session.commit.call_count == 1
            assert mock_session.rollback.call_count == 1
            assert mock_session.close.call_count == 1
def test_delete_paper_service_chroma_failure():
    mock_session = MagicMock(spec=Session)
    mock_session.scalars.return_value.one_or_none.return_value = Paper(
        paper_id="test-paper-001",
        title="DNA Fountain",
        author="Erlich",
        filename="dna_fountain.pdf",
        created_at=datetime(2026, 10, 24, 10, 0, 0)
    )
    mock_chroma_client = MagicMock()
    mock_collection = MagicMock()
    mock_chroma_client.get_collection.return_value = mock_collection
    mock_collection.delete.side_effect = RuntimeError("模拟Chroma删除失败")
    with patch("app.services.paper_service.SessionLocal", return_value=mock_session):
        with patch("app.services.paper_service.chromadb.PersistentClient", return_value=mock_chroma_client):
            with pytest.raises(RuntimeError,match="模拟Chroma删除失败"):
                 delete_paper("test-paper-001")
            assert mock_collection.delete.call_count == 1
            assert mock_session.delete.call_count == 0
            assert mock_session.commit.call_count == 0
            assert mock_session.rollback.call_count == 1
            assert mock_session.close.call_count == 1
def test_ask_paper_success():
    mock_session = MagicMock(spec=Session)
    mock_paper = Paper(
        paper_id="test-paper-001",
        title="DNA Fountain",
        author="Erlich",
        filename="dna_fountain.pdf",
        created_at=datetime(2026, 10, 24, 10, 0, 0)
    )
    mock_question = Question(paper_id="test-paper-001",
                             question="这是一个模拟问题",)
    mock_answer = "这是一段模拟回答"
    mock_result = {"answer": mock_answer,"sources": [ ]}
    #session.scalars(statement) 被调用时，返回一个 Mock 对象。
    #这个 Mock 对象调用 .first() 时，返回我们指定的 mock_paper。
    mock_session.scalars.return_value.first.return_value = mock_paper
    with patch("app.routers.paper.SessionLocal", return_value=mock_session):
        with patch("app.routers.paper.ask_paper",return_value=mock_result):
            client = TestClient(app)
            response = client.post("/papers/ask",json = {
                "paper_id":mock_question.paper_id,
                "question":mock_question.question})
            assert response.status_code == 200
            assert response.json() == {"answer": mock_answer,"sources": []}
def test_ask_paper_empty_question():
    mock_question = Question(paper_id="test-paper-001",
                             question="")
    client = TestClient(app)
    response = client.post("/papers/ask",json = {"paper_id":mock_question.paper_id,
                                                 "question":mock_question.question})
    assert response.status_code == 400
    assert response.json()["detail"] == "问题不能为空"
def test_ask_paper_not_found():
    mock_session = MagicMock(spec=Session)
    mock_session.scalars.return_value.first.return_value = None
    mock_question = Question(paper_id="test-paper-001",question="测试问题")
    with patch("app.routers.paper.SessionLocal", return_value=mock_session):
        with patch("app.routers.paper.ask_paper")as mock_ask_paper:
            client = TestClient(app)
            response = client.post("/papers/ask",json = {"paper_id":mock_question.paper_id,
                                                         "question":mock_question.question})
            assert mock_ask_paper.call_count == 0
            assert mock_session.close.call_count == 1
            assert response.status_code == 404
            assert response.json()["detail"] == "论文不存在"
def test_ask_paper_rag_failure():
    mock_paper = Paper(
        paper_id="test-paper-001",
        title="DNA Fountain",
        author="Erlich",
        filename="dna_fountain.pdf",
        created_at=datetime(2026, 11, 3, 20, 0, 0)
    )
    mock_session = MagicMock(spec=Session)
    mock_question = Question(paper_id="test-paper-001", question="测试问题")
    mock_session.scalars.return_value.first.return_value = mock_paper
    with patch("app.routers.paper.SessionLocal", return_value=mock_session):
        with patch("app.routers.paper.ask_paper")as mock_ask_paper:
            mock_error = RuntimeError("模拟RAG服务失败")
            #被抛出的真正实例 Exception e,用于下面detail的字符串参数
            mock_ask_paper.side_effect = mock_error
            client = TestClient(app)
            response = client.post("/papers/ask",json = {"paper_id":mock_paper.paper_id,
                                                         "question":mock_question.question})
            assert response.status_code == 500
            assert response.json()["detail"] == f"论文问答失败{str(mock_error)}"
            assert mock_session.close.call_count == 1
            assert mock_ask_paper.call_count == 1

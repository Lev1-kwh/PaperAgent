import os

import sqlalchemy
from sqlalchemy.orm import sessionmaker

# __file__ 是本模块文件自身的路径（锚点），不受程序从哪个目录启动影响
# dirname 砍掉最后一层：database.py → app/database 目录 → 再上一层 → app 目录
# 数据库文件历史上一直放在 app 目录下（app/database.db），保持一致，旧数据无需迁移
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
database_url = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
engine = sqlalchemy.create_engine(database_url)
SessionLocal = sessionmaker(bind=engine)


#encoding=utf-8
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine, PrimaryKeyConstraint, Text, DateTime, Boolean, LargeBinary
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import datetime

# 连接psql数据库
engine = create_engine('postgresql://postgres:860514@localhost:5432/bookstore')
Base = declarative_base()

## 书(在init_books.py中已建立)
class Book(Base):
    __tablename__ = 'book'
    book_id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    author = Column(Text, nullable=True)
    publisher = Column(Text, nullable=True)
    original_title = Column(Text, nullable=True)
    translator = Column(Text, nullable=True)
    pub_year = Column(Text, nullable=True)
    pages = Column(Integer, nullable=True)
    price = Column(Integer, nullable=True)
    currency_unit = Column(Text, nullable=True)
    binding = Column(Text, nullable=True)
    isbn = Column(Text, nullable=True)
    author_intro = Column(Text, nullable=True)
    book_intro = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)
    picture = Column(LargeBinary, nullable=True)

class Search_tag(Base):
    __tablename__ = 'search_tag'
    tag = Column(Text, nullable=False)
    book_id = Column(Integer, ForeignKey('book.book_id'), nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint('book_id', 'tag'),
        {},
    )

# 搜索标签表
def insert_tag():
    DBSession = sessionmaker(bind = engine)
    session = DBSession()
    Base.metadata.create_all(engine)

    row = session.execute("SELECT book_id, tag FROM book;").fetchall()
    for i in row:
        temp = i.tag.replace("'", "").replace("[", "").replace("]", "").split(", ")
        for j in temp:
            session.execute(
                "INSERT into search_tag(tag, book_id) VALUES ('%s', %d)" % (j, int(i.book_id))
            )
    session.commit()
    session.close()

def init():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Base.metadata.create_all(engine)
    session.commit()
    session.close()

if __name__ == "__main__":
    # 创建数据库
    init()
    start = datetime.datetime.now()
    # 插入搜索标签表
    insert_tag()
    end = datetime.datetime.now()
    print("spend {} sec".format((end-start).seconds))

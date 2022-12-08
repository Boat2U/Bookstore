import os
import sqlite3 as sqlite
import random
import base64
import simplejson as json
import time
from sqlalchemy import create_engine  #, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine, PrimaryKeyConstraint, Text, DateTime, Boolean, LargeBinary
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import datetime
# from datetime import datetime,time


class Bookinit: # 加载book info
    id: str
    title: str
    author: str
    publisher: str
    original_title: str
    translator: str
    pub_year: str
    pages: int
    price: int
    currency_unit: str
    binding: str
    isbn: str
    author_intro: str
    book_intro: str
    content: str
    tags: [str]
    pictures: [bytes]

    def __init__(self):
        self.tags = []
        self.pictures = []


# 自己的数据库
engine = create_engine('postgresql://postgres:860514@localhost:5432/postgres')
Base = declarative_base()
DBSession = sessionmaker(bind=engine)
session = DBSession()
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

class BookDB:
    def __init__(self):
        parent_path = os.path.dirname(os.path.dirname(__file__))
        self.book_db = os.path.join(parent_path, "fe/data/book.db")
        # self.book_lx = os.path.join(parent_path, )

    def get_book_count(self):
        conn = sqlite.connect(self.book_db)
        cursor = conn.execute("SELECT count(id) FROM book")
        row = cursor.fetchone()
        return row[0]

    def get_book_info(self, start, end) -> [Book]:
        books = []
        conn = sqlite.connect(self.book_db)
        cursor = conn.execute(
            "SELECT id, title, author, "
            "publisher, original_title, "
            "translator, pub_year, pages, "
            "price, currency_unit, binding, "
            "isbn, author_intro, book_intro, "
            "content, tags, picture FROM book ORDER BY id "
            "LIMIT ? OFFSET ?", (end, start))
        for row in cursor:
            book = Bookinit()
            book.id = row[0]
            book.title = row[1]
            book.author = row[2]
            book.publisher = row[3]
            book.original_title = row[4]
            book.translator = row[5]
            book.pub_year = row[6]
            book.pages = row[7]
            book.price = row[8]
            book.currency_unit = row[9]
            book.binding = row[10]
            book.isbn = row[11]
            book.author_intro = row[12]
            book.book_intro = row[13]
            book.content = row[14]
            tags = row[15]
            picture = row[16]

            for tag in tags.split("\n"):
                if tag.strip() != "":
                    book.tags.append(tag)
            for i in range(0, random.randint(0, 9)):
                if picture is not None:
                    encode_str = base64.b64encode(picture).decode('utf-8')
                    book.pictures.append(encode_str)
            books.append(book)
            print('tags:',book.tags)
            print('tags.decode:',tags.decode('utf-8'))
        return books


    def init_book_db(self,start,end):
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        conn = sqlite.connect(self.book_db)
        cursor = conn.execute(
            "SELECT id, title, author, "
            "publisher, original_title, "
            "translator, pub_year, pages, "
            "price, currency_unit, binding, "
            "isbn, author_intro, book_intro, "
            "content, tags, picture FROM book ORDER BY id "
            "LIMIT ? OFFSET ?", (end, start))
        for row in cursor:
            book = Book()
            book.id = row[0]
            book.title = row[1]
            book.author = row[2]
            book.publisher = row[3]
            book.original_title = row[4]
            book.translator = row[5]
            book.pub_year = row[6]
            book.pages = row[7]
            book.price = row[8]
            book.currency_unit = row[9]
            book.binding = row[10]
            book.isbn = row[11]
            book.author_intro = row[12]
            book.book_intro = row[13]
            book.content = row[14]
            tags = row[15]
            picture = row[16]
            tag_list = []
            for tag in tags.split("\n"):
                if tag.strip() != "":
                    tag_list.append(tag) # 不能直接book.tag.append()
            book.tags = str(tag_list)
            book.picture = picture
            session.add(book)
        session.commit()
        
        session.close()

    # def send_info(self):
    #     bookdb.init_book_db(0, bookdb.get_book_count())

    # def init_book_db_multipool(self, start, end):
    #     conn = sqlite.connect(self.book_db)
    #     cursor = conn.execute(
    #         "SELECT id, title, author, "
    #         "publisher, original_title, "
    #         "translator, pub_year, pages, "
    #         "price, currency_unit, binding, "
    #         "isbn, author_intro, book_intro, "
    #         "content, tags, picture FROM book ORDER BY id "
    #         "LIMIT ? OFFSET ?", (end, start))
    #     self.main1(cursor)
    #     session.commit()
    #     session.close()

    # def row_iter(self,row):
    #     book = Book()
    #     book.id = row[0]
    #     book.title = row[1]
    #     book.author = row[2]
    #     book.publisher = row[3]
    #     book.original_title = row[4]
    #     book.translator = row[5]
    #     book.pub_year = row[6]
    #     book.pages = row[7]
    #     book.price = row[8]

    #     book.currency_unit = row[9]
    #     book.binding = row[10]
    #     book.isbn = row[11]
    #     book.author_intro = row[12]
    #     book.book_intro = row[13]
    #     book.content = row[14]
    #     tags = row[15]

    #     picture = row[16]
    #     # tagenum=MyEnum(enum.Enum)
    #     thelist = []  # 由于没有列表类型，故使用将列表转为text的办法
    #     for tag in tags.split("\n"):
    #         if tag.strip() != "":
    #             # book.tags.append(tag)
    #             thelist.append(tag)
    #     book.tags = str(thelist)  # 解析成list请使用eval()
    #     book.picture = None
    #     # thelistforpic=[]
    #     # for i in range(0, random.randint(0, 9)):
    #     if picture is not None:
    #         ##以下为查看图片代码
    #         # with open('code.png', 'wb') as fn:  # wb代表二进制文件
    #         #     fn.write(picture)
    #         # img = mpimg.imread('code.png', 0)
    #         # plt.imshow(img)
    #         # plt.axis('off')
    #         # plt.show()

    #         # encode_str = base64.b64encode(picture).decode('utf-8')
    #         # # book.pictures.append(encode_str)
    #         # print(type(encode_str))
    #         book.picture = picture

    #     session.add(book)
    # def main1(self,groups):  # nothing:3.12s nothing2:3.207s
    #     from multiprocessing.pool import Pool
    #     pool = Pool(os.cpu_count())
    #     #groups = [x for x in range(MAX_NUM)] 要遍历的东西
    #     pool.map(self.row_iter, groups)
    #     pool.close()
    #     pool.join()

    # def send_info_multipool(self):
    #     bookdb.init_book_db_multipool(0, bookdb.get_book_count())#count=100 or 整张表

def build_connect():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Base.metadata.create_all(engine)
    session.commit()
    session.close()

if __name__ == '__main__':
    bookdb = BookDB()
    build_connect()
    start = datetime.datetime.now()
    bookdb.init_book_db(0, bookdb.get_book_count())
<<<<<<< HEAD
    end = datetime.datetime.now()
    print("spend {} sec".format((end-start).seconds))
=======
    endtime = time.time()
    print('创建数据库成功，共用时：',endtime-starttime)
>>>>>>> 9cc3895abbf588c474d2fd08d81fcc0f0680b800

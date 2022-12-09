from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine, PrimaryKeyConstraint, Text, DateTime, Boolean, LargeBinary
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# 连接psql数据库
engine = create_engine('postgresql://postgres:860514@localhost:5432/bookstore')
Base = declarative_base()

# 建表

## 用户表
class Users(Base):
    __tablename__ = 'usr'
    user_id = Column(String(128), primary_key=True)
    password = Column(String(128), nullable=False)
    balance = Column(Integer, nullable=False)
    token = Column(String(512), nullable=False)
    terminal = Column(String(256), nullable=False)


## 用户-商店关系表
class User_store(Base):
    __tablename__ = 'user_store'
    user_id = Column(String(128), ForeignKey('usr.user_id'), nullable=False, index=True)
    store_id = Column(String(128), nullable=False, unique=True, index=True)
    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'store_id'),
        {}
    )


## 书
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


## 商店表(含书本信息)
class Store(Base):
    __tablename__ = 'store'
    store_id = Column(String(128), ForeignKey('user_store.store_id'), nullable=False, index=True)
    book_id = Column(Integer, ForeignKey('book.book_id'), nullable=False, index=True)
    stock_level = Column(Integer, nullable=False)  # 库存
    price = Column(Integer, nullable=False)  # 售价
    __table_args__ = (
        PrimaryKeyConstraint('store_id', 'book_id'),
        {},
    )


# 下面是订单相关的表

## 已付款 status: 0-未发货 1-已发货未收货 2-已收货
class New_order_paid(Base):
    __tablename__ = 'new_order_paid'
    order_id = Column(String(128), primary_key=True)
    buyer_id = Column(String(128), ForeignKey('usr.user_id'), nullable=False)
    store_id = Column(String(128), ForeignKey('user_store.store_id'), nullable=False)
    price = Column(Integer, nullable=False)
    purchase_time = Column(DateTime, nullable=False)
    status = Column(Integer, nullable=False)


## 未付款
class New_order_unpaid(Base):
    __tablename__ = 'new_order_unpaid'
    order_id = Column(String(128), primary_key=True)
    buyer_id = Column(String(128), ForeignKey('usr.user_id'), nullable=False)
    store_id = Column(String(128), ForeignKey('user_store.store_id'), nullable=False)
    price = Column(Integer, nullable=False)
    purchase_time = Column(DateTime, nullable=False)


## 已取消订单
class New_order_cancel(Base):
    __tablename__ = 'new_order_cancel'
    order_id = Column(String(128), primary_key=True)
    buyer_id = Column(String(128), ForeignKey('usr.user_id'), nullable=False)
    store_id = Column(String(128), ForeignKey('user_store.store_id'), nullable=False)
    price = Column(Integer, nullable=False)
    cancel_time = Column(DateTime, nullable=False)


## 订单明细表
class New_order_detail(Base):
    __tablename__ = 'new_order_detail'
    order_id = Column(String(128), nullable=False)
    book_id = Column(Integer, nullable=False)
    count = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint('order_id', 'book_id'),
        {}
    )


# 连接数据库
def init():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Base.metadata.create_all(engine)  # 创建所有继承于Base的类对应的表
    session.commit()
    session.close()


# 少量测试用例
def test_sample():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    # 创建 测试用户
    test_user_1 = Users(
        user_id = '小红',
        password = '123456',
        balance = 100,
        token = '***',
        terminal = 'Edge'
    )
    test_user_2 = Users(
        user_id = '小蓝',
        password = '123456',
        balance = 200,
        token = '***',
        terminal = 'Edge'
    )
    session.add_all([test_user_1, test_user_2])
    session.commit()

    # 创建 测试用户-商店
    test_user_store_1 = User_store(
        user_id = '小红',
        store_id = '一号书店'
    )
    test_user_store_2 = User_store(
        user_id = '小红',
        store_id = '二号书店'
    )
    session.add_all([test_user_store_1, test_user_store_2])
    session.commit()

    # 创建 测试商店
    test_store_1 = Store(
        store_id = '一号书店',
        book_id = 1,
        stock_level = 10,
        price = 2000 # 价格单位是分
    )
    test_store_2 = Store(
        store_id = '二号书店',
        book_id = 2,
        stock_level = 10,
        price = 2580 # 价格单位是分
    )
    session.add_all([test_store_1, test_store_2])
    session.commit()

    # 创建 测试订单
    test_order_paid = New_order_paid(
        order_id = 'order1',
        buyer_id = '小蓝',
        store_id = '一号书店',
        price = 2000,
        purchase_time = datetime.now(),
        status = 0  # 未发货
    )
    test_order_detail_paid = New_order_detail(
        order_id = 'order1',
        book_id = 1,
        count = 2,
        price = 4000
    )
    test_order_unpaid = New_order_unpaid(
        order_id = 'order2',
        buyer_id = '小蓝',
        store_id = '二号书店',
        price = 2580,
        purchase_time = datetime.now()
    )
    test_order_detail_unpaid = New_order_detail(
        order_id = 'order2',
        book_id = 2,
        count = 1,
        price = 2580
    )
    session.add_all([test_order_paid, test_order_detail_paid, test_order_unpaid, test_order_detail_unpaid])
    session.commit()

    session.close()

if __name__ == '__main__':
    # 连接数据库
    init()
    # 执行测试用例
    test_sample()

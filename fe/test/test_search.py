import time
import pytest
from fe.access.new_seller import register_new_seller
from fe.access.book import Book
from fe.access import book
from fe.access import auth
from fe import conf
import uuid
import random
class TestSearch:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.auth = auth.Auth(conf.URL)
        self.title = "test_title_{}".format(str(uuid.uuid1()))#random.choice(["很","在"])
        self.publisher = "test_publisher_{}".format(str(uuid.uuid1()))
        self.isbn = "test_isbn_{}".format(str(uuid.uuid1()))
        self.book_intro = "test_book_intro_{}".format(str(uuid.uuid1()))
        self.content = "test_book_intro_{}".format(str(uuid.uuid1()))
        self.tag = "test_tag_{}".format(str(uuid.uuid1()))#random.choice(["小说","励志"])
        self.author = "test_author_{}".format(str(uuid.uuid1()))
        self.store_id = "test_store_id_{}".format(str(uuid.uuid1()))

        yield

    def test_search_random(self):
        assert self.auth.search_author_store(author=self.author) == 200
        assert self.auth.search_author_store(store_id=self.store_id) == 200
        assert self.auth.search_author_store(author=self.author, store_id=self.store_id) == 200

        assert self.auth.search_bookintro_content(book_intro=self.book_intro) == 200
        assert self.auth.search_bookintro_content(content=self.content) == 200
        assert self.auth.search_bookintro_content(book_intro=self.book_intro, store_id=self.store_id) == 200
        assert self.auth.search_bookintro_content(content=self.content, store_id=self.store_id) == 200
        assert self.auth.search_bookintro_content(book_intro=self.book_intro, content=self.content, store_id=self.store_id) == 200
        
        assert self.auth.search_tag(self.tag) == 200
        assert self.auth.search_tag(self.tag, store_id=self.store_id) == 200

        assert self.auth.search_title_publisher_isbn(title=self.title) == 200
        assert self.auth.search_title_publisher_isbn(publisher=self.publisher) == 200
        assert self.auth.search_title_publisher_isbn(isbn=self.isbn) == 200
        assert self.auth.search_title_publisher_isbn(title=self.title, store_id=self.store_id) == 200
        assert self.auth.search_title_publisher_isbn(publisher=self.publisher, store_id=self.store_id) == 200
        assert self.auth.search_title_publisher_isbn(isbn=self.isbn, store_id=self.store_id) == 200
        assert self.auth.search_title_publisher_isbn(title=self.title, isbn=self.isbn) == 200
        assert self.auth.search_title_publisher_isbn(title=self.title, publisher=self.publisher) == 200
        assert self.auth.search_title_publisher_isbn(publisher=self.publisher, isbn=self.isbn) == 200
        assert self.auth.search_title_publisher_isbn(title=self.title, isbn=self.isbn, store_id=self.store_id) == 200
        assert self.auth.search_title_publisher_isbn(title=self.title, publisher=self.publisher, store_id=self.store_id) == 200
        assert self.auth.search_title_publisher_isbn(publisher=self.publisher, isbn=self.isbn, store_id=self.store_id) == 200
        assert self.auth.search_title_publisher_isbn(title=self.title, publisher=self.publisher, isbn=self.isbn) == 200
        assert self.auth.search_title_publisher_isbn(title=self.title, publisher=self.publisher, isbn=self.isbn, store_id=self.store_id) == 200

    def test_search_fixed(self):
        title=["早年毛泽东","人类本性与社会秩序","垃圾之歌"]
        publisher=["台海出版社","人民文学出版社",""]
        author=["(美)查尔斯.霍顿.库利","李锐","余秋雨"]
        isbn=["9787508016450","9787500424581","9787205019648"]
        book_intro=["方法","反映","角度"]
        content=["暗示和选择","湖南第一师范","见贤思齐"]
        tags=["人类学","政治学","哥特"]
        self.store_id = "store_s_1_2_38d34e0a-76c0-11ed-8476-1cbfc037e342" # 某一个店铺
        self.title = random.choice(title)
        self.publisher = random.choice(publisher)
        self.author = random.choice(author)
        self.isbn = random.choice(isbn)
        self.book_intro = random.choice(book_intro)
        self.content = random.choice(content)
        self.tag = random.choice(tags)

        assert self.auth.search_author_store(author=self.author) == 200
        assert self.auth.search_author_store(store_id=self.store_id) == 200
        assert self.auth.search_author_store(author=self.author, store_id=self.store_id) == 200

        assert self.auth.search_bookintro_content(book_intro=self.book_intro) == 200
        assert self.auth.search_bookintro_content(content=self.content) == 200
        assert self.auth.search_bookintro_content(book_intro=self.book_intro, store_id=self.store_id) == 200
        assert self.auth.search_bookintro_content(content=self.content, store_id=self.store_id) == 200
        assert self.auth.search_bookintro_content(book_intro=self.book_intro, content=self.content, store_id=self.store_id) == 200
        
        assert self.auth.search_tag(self.tag) == 200
        assert self.auth.search_tag(self.tag, store_id=self.store_id) == 200

        assert self.auth.search_title_publisher_isbn(title=self.title) == 200
        assert self.auth.search_title_publisher_isbn(publisher=self.publisher) == 200
        assert self.auth.search_title_publisher_isbn(isbn=self.isbn) == 200
        assert self.auth.search_title_publisher_isbn(title=self.title, store_id=self.store_id) == 200
        assert self.auth.search_title_publisher_isbn(publisher=self.publisher, store_id=self.store_id) == 200
        assert self.auth.search_title_publisher_isbn(isbn=self.isbn, store_id=self.store_id) == 200
        assert self.auth.search_title_publisher_isbn(title=self.title, isbn=self.isbn) == 200
        assert self.auth.search_title_publisher_isbn(title=self.title, publisher=self.publisher) == 200
        assert self.auth.search_title_publisher_isbn(publisher=self.publisher, isbn=self.isbn) == 200
        assert self.auth.search_title_publisher_isbn(title=self.title, isbn=self.isbn, store_id=self.store_id) == 200
        assert self.auth.search_title_publisher_isbn(title=self.title, publisher=self.publisher, store_id=self.store_id) == 200
        assert self.auth.search_title_publisher_isbn(publisher=self.publisher, isbn=self.isbn, store_id=self.store_id) == 200
        assert self.auth.search_title_publisher_isbn(title=self.title, publisher=self.publisher, isbn=self.isbn) == 200
        assert self.auth.search_title_publisher_isbn(title=self.title, publisher=self.publisher, isbn=self.isbn, store_id=self.store_id) == 200
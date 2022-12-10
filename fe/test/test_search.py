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
        self.title = "test_title_{}".format(time.time())
        self.publisher = "test_publisher_{}".format(str(uuid.uuid1()))
        self.isbn = "test_isbn_{}".format(str(uuid.uuid1()))
        self.book_intro = "test_book_intro_{}".format(str(uuid.uuid1()))
        self.content = "test_book_intro_{}".format(str(uuid.uuid1()))
        self.tag = "test_tag_{}".format(str(uuid.uuid1()))
        self.author = "test_author_{}".format(str(uuid.uuid1()))
        self.store_id = "test_store_id_{}".format(str(uuid.uuid1()))

        yield

    def test_search_random(self):

        assert self.auth.search_author_store(author=self.author,store_id='') == 527
        assert self.auth.search_author_store(store_id=self.store_id) == 527
        assert self.auth.search_author_store(author=self.author, store_id=self.store_id) == 527

        assert self.auth.search_bookintro_content(book_intro=self.book_intro) == 527
        assert self.auth.search_bookintro_content(content=self.content) == 527
        assert self.auth.search_bookintro_content(book_intro=self.book_intro, store_id=self.store_id) == 527
        assert self.auth.search_bookintro_content(content=self.content, store_id=self.store_id) == 527
        assert self.auth.search_bookintro_content(book_intro=self.book_intro, content=self.content, store_id=self.store_id) == 527
        
        assert self.auth.search_tag(self.tag) == 527
        assert self.auth.search_tag(self.tag, store_id=self.store_id) == 527

        assert self.auth.search_title_publisher_isbn(title=self.title) == 527
        assert self.auth.search_title_publisher_isbn(publisher=self.publisher) == 527
        assert self.auth.search_title_publisher_isbn(isbn=self.isbn) == 527
        assert self.auth.search_title_publisher_isbn(title=self.title, store_id=self.store_id) == 527
        assert self.auth.search_title_publisher_isbn(publisher=self.publisher, store_id=self.store_id) == 527
        assert self.auth.search_title_publisher_isbn(isbn=self.isbn, store_id=self.store_id) == 527
        assert self.auth.search_title_publisher_isbn(title=self.title, isbn=self.isbn) == 527
        assert self.auth.search_title_publisher_isbn(title=self.title, publisher=self.publisher) == 527
        assert self.auth.search_title_publisher_isbn(publisher=self.publisher, isbn=self.isbn) == 527
        assert self.auth.search_title_publisher_isbn(title=self.title, isbn=self.isbn, store_id=self.store_id) == 527
        assert self.auth.search_title_publisher_isbn(title=self.title, publisher=self.publisher, store_id=self.store_id) == 527
        assert self.auth.search_title_publisher_isbn(publisher=self.publisher, isbn=self.isbn, store_id=self.store_id) == 527
        assert self.auth.search_title_publisher_isbn(title=self.title, publisher=self.publisher, isbn=self.isbn) == 527
        assert self.auth.search_title_publisher_isbn(title=self.title, publisher=self.publisher, isbn=self.isbn, store_id=self.store_id) == 527

    def test_search_fixed(self):
        self.title="早年毛泽东"
        self.publisher="辽宁人民出版社"
        self.author="李锐"
        self.isbn="9787205019648"
        book_intro=["方法","反映","角度"] # 12没有
        self.book_intro = random.choice(book_intro)
        content=["心忧天下","湖南第一师范","党的建设"]
        self.content=random.choice(content)
        tags=["darkwave","人物传记","哥特"]
        self.tag = random.choice(tags)
        self.store_id = "store_s_1_1_09eb7403-76cf-11ed-a512-1cbfc037e342" # 某一个店铺

        assert self.auth.search_author_store(author=self.author,store_id='') == 200
        assert self.auth.search_author_store(store_id=self.store_id) == 200
        assert self.auth.search_author_store(author=self.author, store_id=self.store_id) == 200

        assert self.auth.search_bookintro_content(book_intro=self.book_intro) == 527
        assert self.auth.search_bookintro_content(content=self.content) == 200
        assert self.auth.search_bookintro_content(book_intro=self.book_intro, store_id=self.store_id) == 527 #
        assert self.auth.search_bookintro_content(content=self.content, store_id=self.store_id) == 200
        assert self.auth.search_bookintro_content(book_intro=self.book_intro, content=self.content, store_id=self.store_id) == 527
        
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

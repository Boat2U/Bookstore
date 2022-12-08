import uuid
import pytest

from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.book import Book

class Test_cancel:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.store_id = "test_send_book_store_id_{}".format(str(uuid.uuid1()))
        self.seller_id = "test_send_seller_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_send_buyer_id_{}".format(str(uuid.uuid1()))

        self.gen_book = GenBook(self.seller_id, self.store_id)
        self.seller = self.gen_book.seller
        self.password = self.buyer_id
        self.buyer = register_new_buyer(self.buyer_id, self.password)

        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False, max_book_count=5)
        self.buy_book_info_list = self.gen_book.buy_book_info_list
        assert ok

        self.total_price = 0  # 购买书所需的总价格,确保buyer能够支付得起
        for item in self.buy_book_info_list:
            book: Book = item[0]
            num = item[1]
            self.total_price = self.total_price + book.price * num
        code = self.buyer.add_funds(self.total_price + 1000000)
        assert code == 200

        code, self.order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        yield

    def test_ok_cancel_paid(self): # 取消已支付订单成功
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.buyer.cancel_order(self.buyer_id,self.order_id)
        assert code == 200

    def test_ok_cancel_unpaid(self): # 取消未支付订单成功
        code = self.buyer.cancel_order(self.buyer_id, self.order_id)
        assert code == 200

    def test_non_exist_buyer(self):
        code = self.buyer.cancel_order(self.buyer_id+'_x',self.order_id)
        assert code != 200
    
    def test_non_exist_order(self):
        code = self.buyer.cancel_order(self.buyer_id,self.order_id+'_x')
        assert code != 200

    def test_cannot_cancel_send_order(self): # 取消已发货订单失败
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.seller.send_books(self.seller_id, self.order_id)
        assert code == 200
        code = self.buyer.cancel_order(self.buyer_id, self.order_id)
        assert code != 200

    def test_cannot_cancel_receive_order(self): # 取消已收货订单失败
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.seller.send_books(self.seller_id, self.order_id)
        assert code == 200
        code = self.buyer.receive_books(self.buyer_id, self.order_id)
        assert code == 200
        code = self.buyer.cancel_order(self.buyer_id, self.order_id)
        assert code != 200
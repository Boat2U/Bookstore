import sqlalchemy.exc as SQLAlchemyError
from model import error
from model import db_conn


class Seller(db_conn.DBConn):

    def __init__(self):
        db_conn.DBConn.__init__(self)

    # 进书
    def add_book(self, user_id: str, store_id: str, book_id: str, book_json_str: str, stock_level: int):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)

            self.session.execute("INSERT into store(store_id, book_id, book_info, stock_level)"
                              "VALUES ('%s', '%s', '%s', '%s')", (store_id, book_id, book_json_str, stock_level))
            self.session.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    # 更新书店库存
    def add_stock_level(self, user_id: str, store_id: str, book_id: str, add_stock_level: int):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)

            self.session.execute("UPDATE store SET stock_level = stock_level + %d "
                              "WHERE store_id = %s AND book_id = %d", (add_stock_level, store_id, book_id))
            self.session.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    # 开店
    def create_store(self, user_id: str, store_id: str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)
            self.session.execute("INSERT into user_store(store_id, user_id)"
                              "VALUES ('%s', '%s')", (store_id, user_id))
            self.session.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    # 卖家发货
    def send_books(self, seller_id, order_id):
        try:
            # 先判断卖家是否存在
            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)
            # 再判断订单状态
            row = self.session.execute(
                "SELECT status, store_id FROM new_order_paid WHERE order_id = '%s'" % (order_id,)
            ).fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)
            elif row[0] != 0:
                return 521, 'sent successfully'
            # 判断该卖家是否拥有该店铺
            u_id = self.session.execute(
                "SELECT user_id FROM user_store WHERE store_id = '%s';" % (row[1],)
            ).fetchone()
            if u_id[0] != seller_id:
                return error.error_authorization_fail()
            # 一切正常
            self.session.execute(
                "UPDATE new_order_paid set status = 1 where order_id = '%s' ;" % (order_id)
            )
            self.session.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

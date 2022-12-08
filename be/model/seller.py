import json
import sqlalchemy
import sqlalchemy.exc as SQLAlchemyError
from be.model import error
from be.model import db_conn


class Seller(db_conn.DBConn):

    def __init__(self):
        db_conn.DBConn.__init__(self)

    # # 进书
    # def add_book(self, user_id: str, store_id: str, book_id: str, price:int,book_json_str: str, stock_level: int):
    #     try:
    #         if not self.user_id_exist(user_id):
    #             return error.error_non_exist_user_id(user_id)
    #         if not self.store_id_exist(store_id):
    #             return error.error_non_exist_store_id(store_id)
    #         if self.book_id_exist(int(book_id)):
    #             return error.error_exist_book_id(book_id)

    #         self.session.execute("INSERT into store(store_id, book_id, stock_level,price) VALUES ('%s', %d,  %d,%d)"% (store_id, int(book_id), stock_level,price))
    #         self.session.commit()
    #     except SQLAlchemyError.IntegrityError:
    #         return error.error_exist_book_id(str(book_id))
    #     return 200, "ok"
    def add_book(self, user_id: str, store_id: str, book_id: str, price:int,book_json_str: str, stock_level: int):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            book_id=int(book_id)
            # 书库是否有该书(注：不是商店是否存在该书,故不能用error.error_non_exist_book_id)
            row = self.session.execute("SELECT book_id FROM book WHERE book_id = '%s';" % (book_id,)).fetchone()
            # if row is None:
            #     return 515, "non exist book id {}"

            if row is None:
                book = json.loads(book_json_str)
                thelist = []  # 由于没有列表类型，故使用将列表转为text的办法
                for tag in book.get('tags'):
                    if tag.strip() != "":
                        # book.tags.append(tag)
                        thelist.append(tag)
                book['tags'] = str(thelist)  # 解析成list请使用eval(
                if book.get('picture') is not None:
                    self.session.execute(
                    "INSERT into book( book_id, title,author,publisher,original_title,translator,"
                    "pub_year,pages,original_price,currency_unit,binding,isbn,author_intro,book_intro,"
                    "content,tags,picture) VALUES ( :book_id, :title,:author,:publisher,:original_title,:translator,"
                    ":pub_year,:pages,:original_price,:currency_unit,:binding,:isbn,:author_intro,:book_intro,"
                    ":content,:tags,:picture)" , {'book_id':book['id'], 'title':book['title'],'author':book['author'],
                     'publisher':book['publisher'],'original_title':book['original_title'],'translator':book['translator'],
                    'pub_year':book['pub_year'],'pages':book['pages'],'original_price':book['price'],'currency_unit':book['currency_unit'],
                    'binding':book['binding'],'isbn':book['isbn'],'author_intro':book['author_intro'],'book_intro':book['book_intro'],
                     'content':book['content'],'tags':book['tags'],'picture':book['picture']})
                else:
                    self.session.execute(
                        "INSERT into book( book_id, title,author,publisher,original_title,translator,"
                        "pub_year,pages,original_price,currency_unit,binding,isbn,author_intro,book_intro,"
                        "content,tags) VALUES ( :book_id, :title,:author,:publisher,:original_title,:translator,"
                        ":pub_year,:pages,:original_price,:currency_unit,:binding,:isbn,:author_intro,:book_intro,"
                        ":content,:tags)",
                        {'book_id': book['id'], 'title': book['title'], 'author': book['author'],
                         'publisher': book['publisher'], 'original_title': book['original_title'],
                         'translator': book['translator'],
                         'pub_year': book['pub_year'], 'pages': book['pages'], 'original_price': book['price'],
                         'currency_unit': book['currency_unit'],
                         'binding': book['binding'], 'isbn': book['isbn'], 'author_intro': book['author_intro'],
                         'book_intro': book['book_intro'],
                         'content': book['content'], 'tags': book['tags']})


            self.session.execute("INSERT into store(store_id, book_id, stock_level,price) VALUES ('%s', %d,  %d,%d)"% (store_id, int(book_id), stock_level,price))
            self.session.commit()
        except SQLAlchemyError.IntegrityError:
            return error.error_exist_book_id(str(book_id))
        return 200, "ok"

    # 更新书店库存
    def add_stock_level(self, user_id: str, store_id: str, book_id: str, add_stock_level: int):
        # # 判断卖家是否拥有该店铺
        # row = self.session.execute("SELECT user_id FROM user_store WHERE store_id = '%s';" % (store_id,)).fetchone()
        # if row is None:
        #     return error.error_non_exist_store_id(store_id)
        # if row.user_id != user_id:
        #     return error.error_non_exist_user_id(user_id)

        # if not self.book_id_exist(int(book_id)):
        #     return error.error_non_exist_book_id(book_id)       

        # self.session.execute("UPDATE store SET stock_level = stock_level + %d "
        #                     "WHERE store_id = %s AND book_id = %d"% (add_stock_level, store_id, book_id, int(book_id)))
        # self.session.commit()
        # return 200, "ok"
        try:
            row = self.session.execute("SELECT user_id FROM user_store WHERE store_id = '%s';" % (store_id,)).fetchone()
            if row is None:
                return error.error_non_exist_store_id(store_id)
            if row.user_id != user_id:
                return error.error_non_exist_user_id(user_id)
            if not self.book_id_exist(int(book_id)):
                return error.error_non_exist_book_id(book_id)

            self.session.execute("UPDATE store SET stock_level = stock_level + %d "
                                 "WHERE store_id = '%s' AND book_id = %d" % (add_stock_level, store_id, int(book_id)))
            self.session.commit()
        except ValueError:
            code, mes = error.error_non_exist_book_id(book_id)
            return code,mes
        return 200, "ok"

    # 开店
    def create_store(self, user_id: str, store_id: str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)
            self.session.execute("INSERT into user_store(store_id, user_id) VALUES ('%s', '%s')"%(store_id, user_id))
            self.session.commit()
        except SQLAlchemyError.IntegrityError:
            return error.error_exist_store_id(store_id)
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
            if row[0] != 0:
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

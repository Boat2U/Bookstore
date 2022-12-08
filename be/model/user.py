# import jwt
# import time
# import logging
# from model import error
# import base64
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# import sqlalchemy.exc as SQLAlchemyError
# # from init_db.init_database import Users,Book
# # from init_db.init_search_database import Search_book_intro
# from model import db_conn

# # encode a json string like:
# #   {
# #       "user_id": [user name],
# #       "terminal": [terminal code],
# #       "timestamp": [ts]} to a JWT
# #   }


# def jwt_encode(user_id: str, terminal: str) -> str:
#     encoded = jwt.encode(
#         {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
#         key=user_id,
#         algorithm="HS256",
#     )
#     return encoded.encode("utf-8").decode("utf-8")


# # decode a JWT to a json string like:
# #   {
# #       "user_id": [user name],
# #       "terminal": [terminal code],
# #       "timestamp": [ts]} to a JWT
# #   }
# def jwt_decode(encoded_token, user_id: str) -> str:
#     decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
#     return decoded

# # class db():
# #     def __init__(self):
# #         engine = create_engine('postgresql://postgres:CJY1111804@localhost:5432/postgres')
# #         Base = declarative_base()
# #         DBSession = sessionmaker(bind=engine)
# #         self.session = DBSession() 

# class User(db_conn.DBConn):
#     token_lifetime: int = 3600  # 3600 second

#     def __init__(self):
#         db_conn.DBConn.__init__(self)

#     def __check_token(self, user_id, db_token, token) -> bool:
#         try:
#             if db_token != token:
#                 return False
#             jwt_text = jwt_decode(encoded_token=token, user_id=user_id) # 得到所有token信息
#             ts = jwt_text["timestamp"]
#             if ts is not None: # 时间戳存在
#                 now = time.time()
#                 if self.token_lifetime > now - ts >= 0: # 还未超时
#                     return True
#         except jwt.exceptions.InvalidSignatureError as e:
#             logging.error(str(e))
#             return False

#     def register(self, user_id: str, password: str):
#         try:
#             terminal = "terminal_{}".format(str(time.time())) # 终端init
#             token = jwt_encode(user_id, terminal) # token init
#             self.session.execute( 
#                 "INSERT into usr(user_id, password, balance, token, terminal) "
#                 "VALUES ('%s', '%s', %d, '%s', '%s');", (user_id, password, 0, token, terminal) ) # 注册用户init
#             self.session.commit()
#         except SQLAlchemyError:
#             return error.error_exist_user_id(user_id)
#         return 200, "ok"

#     def check_token(self, user_id: str, token: str) -> (int, str):
#         row = self.session.query(Users).filter(Users.user_id==user_id).first()
#         if row is None: # 查无此人
#             return error.error_authorization_fail()
#         db_token = row.token
#         if not self.__check_token(user_id, db_token, token): # token不对
#             return error.error_authorization_fail()
#         return 200, "ok"

#     def check_password(self, user_id: str, password: str) -> (int, str):
#         row = self.session.query(Users).filter(Users.user_id==user_id).first()
#         if row is None: # 查无此人
#             return error.error_authorization_fail()

#         if password != row.password: # 密码错误
#             return error.error_authorization_fail()

#         return 200, "ok"

#     def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):
#         token = ""
#         try:
#             code, message = self.check_password(user_id, password) # 密码没问题
#             if code != 200: # 返回不对
#                 return code, message, ""

#             token = jwt_encode(user_id, terminal) # 得到token所有信息
#             cursor = self.session.execute( 
#                 "UPDATE user set token= '%s' , terminal = '%s' where user_id = '%s'" %
#                 (token, terminal, user_id)) # 更新用户token，terminal

#             if cursor is None: # 有可能不行这句话
#                 return error.error_authorization_fail() + ("", )
#             self.session.commit()
#         except SQLAlchemyError as e:
#             return 528, "{}".format(str(e)), ""
#         except BaseException as e:
#             return 530, "{}".format(str(e)), ""
#         return 200, "ok", token

#     def logout(self, user_id: str, token: str) -> bool:
#         try:
#             code, message = self.check_token(user_id, token) # 检查token
#             if code != 200:
#                 return code, message

#             terminal = "terminal_{}".format(str(time.time()))
#             dummy_token = jwt_encode(user_id, terminal)

#             cursor = self.session.execute(
#                 "UPDATE usr SET token = '%s' WHERE user_id='%s'" % (dummy_token, user_id))

#             if cursor is None:
#                 return error.error_authorization_fail()

#             self.session.commit()
#         except SQLAlchemyError as e:
#             return 528, "{}".format(str(e))
#         except BaseException as e:
#             return 530, "{}".format(str(e))
#         return 200, "ok"

#     def unregister(self, user_id: str, password: str) -> (int, str):
#         try:
#             code, message = self.check_password(user_id, password)
#             if code != 200:
#                 return code, message

#             cursor = self.session.execute("DELETE from usr where user_id='%s'" % (user_id))
#             if cursor.rowcount == 1: # 用户存在，且只有一个
#                 self.session.commit()
#             else:
#                 return error.error_authorization_fail()
#         except SQLAlchemyError as e:
#             return 528, "{}".format(str(e))
#         except BaseException as e:
#             return 530, "{}".format(str(e))
#         return 200, "ok"

#     def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
#         try:
#             code, message = self.check_password(user_id, old_password)
#             if code != 200:
#                 return code, message

#             terminal = "terminal_{}".format(str(time.time()))
#             token = jwt_encode(user_id, terminal)
#             cursor = self.session.execute(
#                 "UPDATE user set password = '%s', token= '%s' , terminal = '%s' where user_id = '%s'" % 
#                 (new_password, token, terminal, user_id)) # 更新密码
#             if cursor is None:
#                 return error.error_authorization_fail()

#             self.session.commit()
#         except SQLAlchemyError as e:
#             return 528, "{}".format(str(e))
#         except BaseException as e:
#             return 530, "{}".format(str(e))
#         return 200, "ok"

import jwt
import time
import logging
from be.model import error
import base64
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sqlalchemy.exc as SQLAlchemyError
from init_db.init_database import Users
from be.model import db_conn

# encode a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }


def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded.encode("utf-8").decode("utf-8")


# decode a JWT to a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }
def jwt_decode(encoded_token, user_id: str) -> str:
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded

class User(db_conn.DBConn):
    token_lifetime: int = 3600  # 3600 second

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def __check_token(self, user_id, db_token, token) -> bool:
        try:
            if db_token != token:
                return False
            jwt_text = jwt_decode(encoded_token=token, user_id=user_id) # 得到所有token信息
            ts = jwt_text["timestamp"]
            if ts is not None: # 时间戳存在
                now = time.time()
                if self.token_lifetime > now - ts >= 0: # 还未超时
                    return True
        except jwt.exceptions.InvalidSignatureError as e:
            logging.error(str(e))
            return False

    def register(self, user_id: str, password: str):
        # terminal = "terminal_{}".format(str(time.time()))
        # try:
        #     token=""
        #     self.session.execute(  "INSERT INTO usr (user_id, password, balance, token, terminal) values (:user_id, :password, 0, :token, :terminal)",{"user_id":user_id,"password": password,"token":token,"terminal":terminal })
        #     self.session.commit()
        # except SQLAlchemyError.IntegrityError:
        #     return error.error_exist_user_id(user_id)

        # return 200, "ok"
        try:
            terminal = "terminal_{}".format(str(time.time())) # 终端init
            token = jwt_encode(user_id, terminal) # token init
            self.session.execute( 
                "INSERT INTO usr (user_id, password, balance, token, terminal) values (:user_id, :password, 0, :token, :terminal)",{"user_id":user_id,"password": password,"token":token,"terminal":terminal }) # 注册用户init
            self.session.commit()
        except SQLAlchemyError.IntegrityError:
            return error.error_exist_user_id(user_id)
        return 200, "ok"

    def check_token(self, user_id: str, token: str):
        row = self.session.query(Users).filter(Users.user_id==user_id).first()
        if row is None: # 查无此人
            return error.error_authorization_fail()
        db_token = row.token
        if not self.__check_token(user_id, db_token, token): # token不对
            return error.error_authorization_fail()
        return 200, "ok"

    def check_password(self, user_id: str, password: str):
        row = self.session.query(Users).filter(Users.user_id==user_id).first()
        if row is None: # 查无此人
            return error.error_authorization_fail()

        if password != row.password: # 密码错误
            return error.error_authorization_fail()

        return 200, "ok"

    def login(self, user_id: str, password: str, terminal: str):
        # token = ""
        # user = self.session.execute("SELECT password from usr where user_id=:user_id",{"user_id":user_id}).fetchone()
        # if user is None or  password != user.password:
        #     code, message=error.error_authorization_fail()
        #     return code, message,token
        # token = jwt_encode(user_id, terminal)
        # self.session.execute(
        #     "UPDATE usr set token= '%s' , terminal = '%s' where user_id = '%s'"% (token, terminal, user_id) )
        # self.session.commit()
        # return 200, "ok", token
        token = ""
        try:
            code, message = self.check_password(user_id, password) # 密码没问题
            if code != 200: # 返回不对
                return code, message, ""

            token = jwt_encode(user_id, terminal) # 得到token所有信息
            cursor = self.session.execute(
                "UPDATE usr set token= '%s' , terminal = '%s' where user_id = '%s'"
                % (token, terminal, user_id) )
            self.session.commit()
            if cursor is None: # 有可能不行这句话
                return error.error_authorization_fail() + ("", )
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            return 530, "{}".format(str(e)), ""
        return 200, "ok", token

    def logout(self, user_id: str, token: str) -> bool:
        try:
            code, message = self.check_token(user_id, token) # 检查token
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            dummy_token = jwt_encode(user_id, terminal)

            cursor = self.session.execute(
                "UPDATE usr SET token = '%s' WHERE user_id='%s'" % (dummy_token, user_id))

            if cursor is None:
                return error.error_authorization_fail()

            self.session.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def unregister(self, user_id: str, password: str):
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message

            cursor = self.session.execute("DELETE from usr where user_id='%s'"% (user_id))
            if cursor.rowcount == 1:
                self.session.commit()
            else:
                return error.error_authorization_fail()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"


    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        try:
            code, message = self.check_password(user_id, old_password)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            cursor = self.session.execute(
                "UPDATE usr set password = '%s', token = '%s', terminal = '%s' where user_id = '%s'"
                %(new_password,token,terminal,user_id), ) # 更新密码
            
            if cursor is None:
                return error.error_authorization_fail()

            self.session.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def search_title_publisher_isbn(self,title='',publisher='',isbn='',store_id='')->(int,[dict]):
        result=[]
        if title!='':
            title='WHERE title='+title
        else:
            title='WHERE title IS NOT NULL'
        if publisher!='':
            publisher='WHERE publisher='+publisher
        else:
            publisher='WHERE publisher IS NOT NULL'
        if isbn!='':
            isbn='WHERE isbn='+isbn
        else:
            isbn='WHERE isbn IS NOT NULL'

        if store_id!='':
            queries=self.session.execute(
            "WITH sub AS (SELECT * FROM book WHERE book_id IN (SELECT book_id FROM store WHERE store_id='%s')) "
            "SELECT title,author,publisher,pub_year,pages,price,isbn,book_intro,tags,picture FROM sub "
            "'%s' AND '%s' AND '%s'"% (store_id,title,publisher,isbn)).fetchall()
        else:
            queries=self.session.execute(
                "SELECT title,author,publisher,pub_year,pages,price,isbn,book_intro,tags,picture FROM book "
                "'%s' AND '%s' AND '%s'"% (title,publisher,isbn)).fetchall()
        self.session.commit()

        for i in range(len(queries)):
            query=queries[i]
            q_title,q_author,q_publisher,q_pubyear,q_pages,q_price,q_isbn,q_bookintro,q_tags,q_picture=query

            try:
                picture=base64.b64decode(q_picture)
                result.append(
                    {'title':q_title,'author':q_author,'publisher':q_publisher,'pub_year':q_pubyear,'pages':q_pages,
                    'price':q_price,'isbn':q_isbn,'book_intro':q_bookintro,'tags':q_tags,'picture':picture}
                )
            except:
                result.append(
                    {'title':q_title,'author':q_author,'publisher':q_publisher,'pub_year':q_pubyear,'pages':q_pages,
                    'price':q_price,'isbn':q_isbn,'book_intro':q_bookintro,'tags':q_tags,'picture':''}
                )
        return 200,result

    def search_bookintro_content(self,book_intro='',content='',store_id='')->(int,[dict]):
        result=[]
        if book_intro!='' and content=='':
            book_intro="WHERE book_intro LIKE \'%"+book_intro+"%\'"
        elif content!='' and book_intro=='':
            content="WHERE content LIKE \'%"+content+"%\'"
        else:
            book_intro="WHERE book_intro LIKE \'%"+book_intro+"%\'"
            content="AND content LIKE \'%"+content+"%\'"

        # sub_queries=self.session.query(Search_book_intro.book_id).filter(Search_book_intro.book_intro==book_intro).subquery()
        # queries=self.session.query(Book).filter(Book.book_id=sub_queries.book_id)

        if store_id!='':
            queries=self.session.execute(
                "WITH sub AS (SELECT * FROM book WHERE book_id IN (SELECT book_id FROM store WHERE store_id='%s')) "
                "SELECT title,author,publisher,pub_year,pages,price,isbn,book_intro,tags,picture FROM sub "
                "'%s' '%s' " % (store_id,book_intro,content)
            ).fetchall()
        else:
            queries=self.session.execute(
                "SELECT title,author,publisher,pub_year,pages,price,isbn,book_intro,tags,picture FROM book "
                "'%s' '%s' " % (book_intro,content)
            ).fetchall()
        self.session.commit()
        # q_title=query.title
        # q_author=query.author
        # q_publisher=query.publisher
        # q_pubyear=query.pub_year
        # q_pages=query.pages
        # q_price=query.price
        # q_isbn=query.isbn
        # q_bookintro=query.book_intro
        # q_tags=query.tags
        # q_picture=query.picture

        for i in range(len(queries)):
            query=queries[i]
            q_title,q_author,q_publisher,q_pubyear,q_pages,q_price,q_isbn,q_bookintro,q_tags,q_picture=query

            try:
                picture=base64.b64decode(q_picture)
                result.append(
                    {'title':q_title,'author':q_author,'publisher':q_publisher,'pub_year':q_pubyear,'pages':q_pages,
                    'price':q_price,'isbn':q_isbn,'book_intro':q_bookintro,'tags':q_tags,'picture':picture}
                )
            except:
                result.append(
                    {'title':q_title,'author':q_author,'publisher':q_publisher,'pub_year':q_pubyear,'pages':q_pages,
                    'price':q_price,'isbn':q_isbn,'book_intro':q_bookintro,'tags':q_tags,'picture':''}
                )
        return 200,result

    def search_tag(self,tag='',store_id='')->(int,[dict]):
        result=[]
        if store_id!='':
            queries=self.session.execute(
                "WITH sub AS (SELECT * FROM book WHERE book_id IN (SELECT book_id FROM store WHERE store_id='%s')) "
                "SELECT title,author,publisher,pub_year,pages,price,isbn,book_intro,tags,picture FROM sub "
                "WHERE book_id IN "
                "(SELECT book_id FROM search_tag WHERE tag='%s')" % (store_id,tag)
            ).fetchall()
        else:
            queries=self.session.execute(
                "SELECT title,author,publisher,pub_year,pages,price,isbn,book_intro,tags,picture FROM book "
                "WHERE book_id IN "
                "(SELECT book_id FROM search_tag WHERE tag='%s')" % (tag)
            ).fetchall()
        self.session.commit()

        for i in range(len(queries)):
            query=queries[i]
            q_title,q_author,q_publisher,q_pubyear,q_pages,q_price,q_isbn,q_bookintro,q_tags,q_picture=query

            try:
                picture=base64.b64decode(q_picture)
                result.append(
                    {'title':q_title,'author':q_author,'publisher':q_publisher,'pub_year':q_pubyear,'pages':q_pages,
                    'price':q_price,'isbn':q_isbn,'book_intro':q_bookintro,'tags':q_tags,'picture':picture}
                )
            except:
                result.append(
                    {'title':q_title,'author':q_author,'publisher':q_publisher,'pub_year':q_pubyear,'pages':q_pages,
                    'price':q_price,'isbn':q_isbn,'book_intro':q_bookintro,'tags':q_tags,'picture':''}
                )
        return 200,result

    def search_author_store(self,author='',store_id='')->(int,[dict]): # 只店铺查找在这儿
        result=[]
        if store_id=='':
            if author=='':
                queries=self.session.execute(
                    "SELECT title,author,publisher,pub_year,pages,price,isbn,book_intro,tags,picture FROM book "
                ).fetchall()
            else:
                queries=self.session.execute(
                    "SELECT title,author,publisher,pub_year,pages,price,isbn,book_intro,tags,picture FROM book "
                    "WHERE author='%s'" %(author)
                ).fetchall()
        else:
            if author=='':
                queries=self.session.execute(
                    "SELECT title,author,publisher,pub_year,pages,price,isbn,book_intro,tags,picture FROM book "
                    "WHERE book_id IN (SELECT book_id FROM store WHERE store_id='%s')"
                    % (store_id)
                ).fetchall()
            else:
                queries=self.session.execute(
                    "SELECT title,author,publisher,pub_year,pages,price,isbn,book_intro,tags,picture FROM book "
                    "WHERE author='%s' AND book_id IN (SELECT book_id FROM store WHERE store_id='%s')" 
                    % (author,store_id)
                ).fetchall()
        self.session.commit()

        for i in range(len(queries)):
            query=queries[i]
            q_title,q_author,q_publisher,q_pubyear,q_pages,q_price,q_isbn,q_bookintro,q_tags,q_picture=query

            try:
                picture=base64.b64decode(q_picture)
                result.append(
                    {'title':q_title,'author':q_author,'publisher':q_publisher,'pub_year':q_pubyear,'pages':q_pages,
                    'price':q_price,'isbn':q_isbn,'book_intro':q_bookintro,'tags':q_tags,'picture':picture}
                )
            except:
                result.append(
                    {'title':q_title,'author':q_author,'publisher':q_publisher,'pub_year':q_pubyear,'pages':q_pages,
                    'price':q_price,'isbn':q_isbn,'book_intro':q_bookintro,'tags':q_tags,'picture':''}
                )
        return 200,result
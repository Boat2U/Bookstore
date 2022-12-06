import jwt
import time
import logging
from model import error
import base64
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sqlalchemy.exc as SQLAlchemyError
from init_db.init_database import Users
from model import db_conn

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

# class db():
#     def __init__(self):
#         engine = create_engine('postgresql://postgres:CJY1111804@localhost:5432/postgres')
#         Base = declarative_base()
#         DBSession = sessionmaker(bind=engine)
#         self.session = DBSession() 

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
        try:
            terminal = "terminal_{}".format(str(time.time())) # 终端init
            token = jwt_encode(user_id, terminal) # token init
            self.session.execute( 
                "INSERT into usr(user_id, password, balance, token, terminal) "
                "VALUES (?, ?, ?, ?, ?);", (user_id, password, 0, token, terminal) ) # 注册用户init
            self.session.commit()
        except SQLAlchemyError:
            return error.error_exist_user_id(user_id)
        return 200, "ok"

    def check_token(self, user_id: str, token: str) -> (int, str):
        row = self.session.query(Users).filter(Users.user_id==user_id).first()
        if row is None: # 查无此人
            return error.error_authorization_fail()
        db_token = row.token
        if not self.__check_token(user_id, db_token, token): # token不对
            return error.error_authorization_fail()
        return 200, "ok"

    def check_password(self, user_id: str, password: str) -> (int, str):
        row = self.session.query(Users).filter(Users.user_id==user_id).first()
        if row is None: # 查无此人
            return error.error_authorization_fail()

        if password != row.password: # 密码错误
            return error.error_authorization_fail()

        return 200, "ok"

    def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):
        token = ""
        try:
            code, message = self.check_password(user_id, password) # 密码没问题
            if code != 200: # 返回不对
                return code, message, ""

            token = jwt_encode(user_id, terminal) # 得到token所有信息
            # cursor = self.conn.execute( 
            #     "UPDATE user set token= '%s' , terminal = ? where user_id = '%s'" %
            #     (token, terminal, user_id)) # 更新用户token，terminal
            cursor=self.session.query(Users).filter(Users.user_id==user_id).first()

            if cursor is None:
                return error.error_authorization_fail() + ("", )
            self.session.commit()
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
                "UPDATE usr SET token = ? WHERE user_id=?", (dummy_token, user_id))

            if cursor is None:
                return error.error_authorization_fail()

            self.session.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def unregister(self, user_id: str, password: str) -> (int, str):
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message

            cursor = self.conn.execute("DELETE from user where user_id='%s'" % (user_id))
            if cursor.rowcount == 1: # 用户存在，且只有一个
                self.conn.commit()
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
                "UPDATE user set password = ?, token= ? , terminal = ? where user_id = ?", 
                (new_password, token, terminal, user_id)) # 更新密码
            if cursor is None:
                return error.error_authorization_fail()

            self.session.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"


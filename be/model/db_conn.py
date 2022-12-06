from model import store
import sqlalchemy.exc as SQLAlchemyError
from sqlalchemy import create_engine,MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class DBConn:
    def __init__(self):
        self.engine = create_engine('postgresql://postgres:xxx@localhost:5432/bookstore')
        self.Base = declarative_base()
        self.metadata = MetaData()
        self.DBSession = sessionmaker(bind = self.engine)
        self.session = self.DBSession()

    def user_id_exist(self, user_id):
        cursor = self.session.execute("SELECT user_id FROM usr WHERE user_id = '%s';"% (user_id,))
        row = cursor.fetchone()
        if row is None:
            return False
        else:
            return True

    def book_id_exist(self, store_id, book_id):
        cursor = self.session.execute("SELECT book_id FROM store WHERE book_id = %d;"% (int(book_id),))
        row = cursor.fetchone()
        if row is None:
            return False
        else:
            return True

    def store_id_exist(self, store_id):
        cursor = self.session.execute("SELECT store_id FROM user_store WHERE store_id = '%s';"% (store_id,))
        row = cursor.fetchone()
        if row is None:
            return False
        else:
            return True

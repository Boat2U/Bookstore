import  jwt
from datetime import datetime
import json
import sqlalchemy
import sqlalchemy.exc as SQLAlchemyError
from be.model import error
from be.model import db_conn
import uuid
import time
from flask import jsonify
import threading
from datetime import timedelta

to_be_overtime={}
def overtime_append(key,value): # 对to_be_overtime进行操作
    global to_be_overtime
    if key in to_be_overtime:
        to_be_overtime[key].append(value)
    else:
        to_be_overtime[key]=[value]

class TimerClass(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.event = threading.Event()

    def thread(self):
        Buyer().auto_cancel(to_be_overtime[(datetime.utcnow() + timedelta(seconds=1)).second])

    def run(self):  # 每秒运行一次 将超时订单删去
        global to_be_overtime
        # schedule.every().second.do(thread)#每秒开一个线程去auto_cancel,做完的线程自动退出
        while not self.event.is_set():
            self.event.wait(1)
            if (datetime.utcnow() + timedelta(seconds=1)).second in to_be_overtime:
                self.thread()
            # schedule.run_pending()

    def cancel_timer(self):
        self.event.set()

tmr = TimerClass()#####################在无需测试自动取消订单test时删去 单独测取消订单请在test.sh中用
# #coverage run --timid --branch --source fe,be --concurrency=thread -m pytest -v  -k fe/test/test_new_order.py --ignore=fe/data
tmr.start()###################在无需测试自动取消订单test时删去

def tostop():
    global tmr
    tmr.cancel_timer()


def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded.encode("utf-8").decode("utf-8")


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self, obj)

# decode a JWT to a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }
def jwt_decode(encoded_token, user_id: str) -> str:
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded

class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(self, user_id, store_id, id_and_count):
        order_id = ""
        try:
            # 用户id不存在
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) +  (order_id,)
            # 商铺不存在
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) +  (order_id,)
            order_id = user_id  + str(uuid.uuid1())
            book_list = []

            # 查看是否有该书
            for book_id, count in id_and_count:
                book_id=int(book_id)
                book = self.session.execute(
                    "SELECT book_id,stock_level,price FROM store WHERE store_id = '%s' AND book_id = %d" % (store_id, book_id)).fetchone()
                if book is None: # 不存在该书
                    code, mes = error.error_non_exist_book_id(str(book_id))
                    return code, mes, " "
                if book[1] < count: # 数量不够
                    code, mes = error.error_stock_level_low(str(book_id))
                    return code, mes, " "
                book_list.append([book_id, count, book[2]])
            
            sum = 0
            for book_id, count, price in book_list:
                sum += count * price # 订单价格
                # 更新书本数量，如果取消订单需加回订单数
                cursor = self.session.execute(
                    "UPDATE store set stock_level = stock_level - %d WHERE store_id = '%s' and book_id = %d  and stock_level >=%d" % (count, store_id, book_id, count))
                if cursor.rowcount == 0:
                    code, mes = error.error_stock_level_low(book_id)
                    return code, mes, " "

                self.session.execute(
                    "INSERT INTO new_order_detail(order_id, book_id, count, price) VALUES('%s',%d, %d, %d);" % (order_id, book_id, count, price))
            
            timenow = datetime.utcnow() # 下单时间
            self.session.execute( # 加入新的待支付订单
                "INSERT INTO new_order_unpaid(order_id, buyer_id,store_id,price, purchase_time) VALUES('%s', '%s','%s',%d,:timenow);" % (
                    order_id, user_id, store_id, sum),{'timenow':timenow})
            overtime_append(timenow.second,order_id)
            self.session.commit()
            return 200, "ok", order_id
        except ValueError:
            code, mes = error.error_non_exist_book_id(book_id)
            return code, mes, " "
        except SQLAlchemyError.IntegrityError:
            code, mes = error.error_duplicate_bookid()
            return code, mes, " "

    def payment(self, buyer_id, password, order_id):
        # 该订单是否支付
        # 查询该订单的用户名、价格、商店id
        row = self.session.execute(
            "SELECT buyer_id,price,store_id FROM new_order_unpaid WHERE order_id = '%s'" % (order_id,)).fetchone()
        if row is None:
            return error.error_invalid_order_id(order_id)
        price = row[1]
        store_id = row[2]
        if row[0] != buyer_id:
            return error.error_authorization_fail()

        # 查询该订单用户的余额、密码
        row = self.session.execute(
            "SELECT balance, password FROM usr WHERE user_id = '%s';" % (buyer_id)).fetchone()
        if row is None: # 用户不存在
            return error.error_non_exist_user_id(buyer_id)
        if row[0] < price: # 用户余额小于待支付订单
            error.error_not_sufficient_funds(order_id)
        if row[1] != password: # 用户密码输入错误
            return error.error_authorization_fail()
        
        # 更新买家余额
        row = self.session.execute(
            "UPDATE usr set balance = balance - %d WHERE user_id = '%s' AND balance >= %d" % (
                price, buyer_id, price))
        if row.rowcount == 0:
            return error.error_not_sufficient_funds(order_id)
        
        # 更新卖家余额
        storeinfo = self.session.execute( # 找到卖家id
            "SELECT user_id FROM user_store WHERE store_id = '%s';" % (store_id,)).fetchone()
        row = self.session.execute( # 更新卖家余额
            "UPDATE usr set balance = balance + %d WHERE user_id = '%s'" % (price, storeinfo[0]))
        if row.rowcount == 0:
            return error.error_non_exist_user_id(buyer_id)

        # 从待支付订单中删除
        row = self.session.execute("DELETE FROM new_order_unpaid WHERE order_id = '%s'" % (order_id,))
        if row.rowcount == 0:
            return error.error_invalid_order_id(order_id)

        # 加入已支付订单
        timenow = datetime.utcnow()
        self.session.execute(
            "INSERT INTO new_order_paid(order_id, buyer_id,store_id,price,status,purchase_time) VALUES('%s', '%s','%s',%d,'%s',:timenow);" % (
                order_id, buyer_id, store_id, price, 0),{'timenow':timenow})
        self.session.commit()
        return 200, "ok"

    def add_funds(self, user_id, password, add_value):
        user = self.session.execute("SELECT password from usr where user_id='%s'" % (user_id,)).fetchone()
        if user is None:
            return error.error_non_exist_user_id(user_id)
        
        # if  password != user.password:
        if  password != user.password:
            return error.error_authorization_fail()# 密码错误，返回401"authorization fail."
        self.session.execute(
            "UPDATE usr SET balance = balance + %d WHERE user_id = '%s'"%
            (add_value, user_id))
        self.session.commit()
        return 200, "ok"

    def receive_books(self, buyer_id, order_id): # 手动收货
        if not self.user_id_exist(buyer_id): # 用户不存在
            return error.error_non_exist_user_id(buyer_id)

        row = self.session.execute("SELECT buyer_id,status FROM new_order_paid WHERE order_id = '%s'" % (order_id,)).fetchone()
        if row is None: # 订单不存在，返回错误
            return error.error_invalid_order_id(order_id)

        if row[0] != buyer_id: # 用户错误
            return error.error_authorization_fail()

        if row[1] == 0: # status为0，书还未发货
            return 522, "book hasn't been sent to costumer"
        if row[1] == 2: # status为2，书已经收货
            return 523, "book has been received"
        self.session.execute( # status为1，更新状态为2
            "UPDATE new_order_paid set status=2 where order_id = '%s' ;" % (order_id))
        self.session.commit()
        return 200, "ok"

    def search_order(self, buyer_id): # 查找该用户所有订单
        if not self.user_id_exist(buyer_id): # 用户不存在
            return error.error_non_exist_user_id(buyer_id), " "
            
        ret=[]

        # 已支付订单
        records_paid = self.session.execute(
            " SELECT new_order_detail.order_id,title,new_order_detail.price,count,status,purchase_time,new_order_paid.price "
            "FROM new_order_paid,new_order_detail,book WHERE book.book_id=new_order_detail.book_id and "
            "new_order_paid.order_id=new_order_detail.order_id and new_order_paid.buyer_id = '%s' order by new_order_detail.order_id" % (buyer_id)).fetchall()

        # 未支付订单
        records_unpaid = self.session.execute(
            "SELECT new_order_detail.order_id,title,new_order_detail.price,count,purchase_time,new_order_unpaid.price "
            "FROM new_order_unpaid,new_order_detail,book WHERE book.book_id=new_order_detail.book_id and "
            "new_order_unpaid.order_id=new_order_detail.order_id and buyer_id = '%s'" % (buyer_id)).fetchall()
        
        # 该用户没有订单
        if len(records_paid) == 0 and len(records_unpaid) == 0: 
            return 200, 'ok', " "

        # 遍历已支付订单
        if len(records_paid)!=0:
            statusmap = ['未发货', '已发货', '已收货'] # status的映射
            for i in range(len(records_paid)):
                record=records_paid[i] # 当前的订单信息
                status=record[4] # 当前订单状态
                details = []
                details.append({'title': record[1], 'price': record[2], 'count': record[3]})
                ret.append({'order_id':record[0],'status':statusmap[status],'time':json.dumps(record[5],cls=DateEncoder),'total_price':record[6],'detail':details})

        # 遍历未支付订单
        if len(records_unpaid)!=0:
            for i in range(len(records_unpaid)):
                record=records_unpaid[i] # 当前的订单信息
                details = []
                details.append({'title': record[1], 'price': record[2], 'count': record[3]})
                ret.append({'order_id':record[0],'status':'未付款','time':json.dumps(record[4],cls=DateEncoder),'total_price':record[5],'detail':details})
                
        return 200, 'ok', ret
  

    def cancel_order(self,buyer_id, order_id):
        if not self.user_id_exist(buyer_id): # 用户错误
            return error.error_non_exist_user_id(buyer_id)
        if not self.order_id_exist(order_id): # 订单号错误
            return error.error_invalid_order_id(order_id)

        # 在未支付订单查找
        records_unpaid = self.session.execute("Select store_id,price FROM new_order_unpaid WHERE order_id = '%s' and buyer_id='%s'" % (order_id,buyer_id)).fetchone()
        if records_unpaid is not None: # 未支付订单直接删除  # 不要直接用len(records_unpaid)
            store_id=records_unpaid[0]
            price=records_unpaid[1]
            self.session.execute("DELETE FROM new_order_unpaid WHERE order_id = '%s'" % (order_id,))
        # 不是未支付订单
        else: 
            # 在已支付且未发货订单查找
            records_paid = self.session.execute("Select store_id,price FROM new_order_paid WHERE order_id = '%s' and buyer_id='%s' and status='0'" % (order_id,buyer_id)).fetchone()
            if records_paid is None: # 已发货订单不能取消
                return error.error_invalid_order_id(order_id)
            else: # 未发货订单
                # return 200, 'ok'
                store_id = records_paid[0]
                price = records_paid[1]
                self.session.execute("DELETE FROM new_order_paid WHERE order_id = '%s' and status='0'" % (order_id,))
                # 更新买家余额
                self.session.execute("UPDATE user set balance = balance + %d WHERE user_id = '%s'" % (price, buyer_id))
                # 找到商店的卖家并更新余额
                seller_id = self.session.execute("SELECT user_id FROM user_store WHERE store_id = '%s';" % (store_id,)).fetchone()
                self.session.execute("UPDATE user set balance = balance - %d WHERE user_id = '%s'" % (price, seller_id[0]))
                # self.session.execute("UPDATE user set balance = balance - %d WHERE user_id in (SELECT user_id FROM user_store WHERE store_id = '%s')" % (price, store_id))

        now_time = datetime.utcnow()
        self.session.execute("INSERT INTO new_order_cancel(order_id, buyer_id,store_id,price,cancel_time) VALUES('%s', '%s','%s',%d,:timenow);" % (order_id, buyer_id, store_id, price), {'timenow': now_time})
        # 更新库存
        self.session.execute("Update store Set stock_level = stock_level + count from new_order_detail Where new_order_detail.book_id = store.book_id and store.store_id = '%s' and new_order_detail.order_id = '%s'" % (store_id,order_id))
        self.session.commit()
        return 200, 'ok'

    def auto_cancel(self,order_id_list):
        exist_order_need_cancel=0
        # 遍历订单表
        for order_id in order_id_list:
            store = self.session.execute("Select buyer_id,store_id,price FROM new_order_unpaid WHERE order_id = '%s'" % (order_id)).fetchone()
            if store is not None: # 是未付款订单
                buyer_id=store[0]
                store_id=store[1]
                price=store[2]
                self.session.execute("DELETE FROM new_order_unpaid WHERE order_id = '%s'" % (order_id,)) # 删除订单
                timenow = datetime.utcnow()
                self.session.execute( # 加入已取消订单表
                    "INSERT INTO new_order_cancel(order_id, buyer_id,store_id,price,cancel_time) VALUES('%s', '%s','%s',%d,:timenow);" % (
                        order_id, buyer_id, store_id, price), {'timenow': timenow})
                self.session.commit()
                exist_order_need_cancel = 1
        return 'no_such_order' if exist_order_need_cancel==0 else "auto_cancel_done"
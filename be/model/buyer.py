import  jwt
from datetime import datetime
import json
import sqlalchemy
from be.model.db import db
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
    return encoded.decode("utf-8")


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
                code, mes = error.error_non_exist_user_id(user_id)
                return code, mes, order_id
            # 商铺不存在
            if not self.store_id_exist(store_id):
                code, mes = error.error_non_exist_store_id(store_id)
                return code, mes, order_id
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
                "INSERT INTO new_order_pend(order_id, buyer_id,store_id,price,pt) VALUES('%s', '%s','%s',%d,:timenow);" % (
                    order_id, user_id, store_id, sum),{'timenow':timenow})
            overtime_append(timenow.second,order_id)
            self.session.commit()
            return 200, "ok", order_id
        except ValueError:
            code, mes = error.error_non_exist_book_id(book_id)
            return code, mes, " "
        except sqlalchemy.exc.IntegrityError:
            code, mes = error.error_duplicate_bookid()
            return code, mes, " "

    def payment(self, buyer_id, password, order_id):
        # 该订单是否支付
        # 查询该订单的用户名、价格、商店id
        row = self.session.execute(
            "SELECT buyer_id,price,store_id FROM new_order_pend WHERE order_id = '%s'" % (order_id,)).fetchone()
        if row is None:
            return error.error_invalid_order_id(order_id)
        price = row[1]
        store_id = row[2]
        if row[0] != buyer_id:
            return error.error_authorization_fail()

        # 查询该订单用户的余额、密码
        row = self.session.execute(
            "SELECT balance, password FROM user WHERE user_id = '%s';" % (buyer_id)).fetchone()
        if row is None: # 用户不存在
            return error.error_non_exist_user_id(buyer_id)
        if row[0] < price: # 用户余额小于待支付订单
            error.error_not_sufficient_funds(order_id)
        if row[1] != password: # 用户密码输入错误
            return error.error_authorization_fail()
        
        # 更新买家余额
        row = self.session.execute(
            "UPDATE user set balance = balance - %d WHERE user_id = '%s' AND balance >= %d" % (
                price, buyer_id, price))
        if row.rowcount == 0:
            return error.error_not_sufficient_funds(order_id)
        
        # 更新卖家余额
        storeinfo = self.session.execute( # 找到卖家id
            "SELECT user_id FROM user_store WHERE store_id = '%s';" % (store_id,)).fetchone()
        row = self.session.execute( # 更新卖家余额
            "UPDATE user set balance = balance + %d WHERE user_id = '%s'" % (price, storeinfo[0]))
        if row.rowcount == 0:
            return error.error_non_exist_user_id(buyer_id)

        # 从待支付订单中删除
        row = self.session.execute("DELETE FROM new_order_pend WHERE order_id = '%s'" % (order_id,))
        if row.rowcount == 0:
            return error.error_invalid_order_id(order_id)

        # 加入已支付订单
        timenow = datetime.utcnow()
        self.session.execute(
            "INSERT INTO new_order_paid(order_id, buyer_id,store_id,price,status,pt) VALUES('%s', '%s','%s',%d,'%s',:timenow);" % (
                order_id, buyer_id, store_id, price, 0),{'timenow':timenow})
        self.session.commit()
        return 200, "ok"

    def add_funds(self, user_id, password, add_value):
            user = self.session.execute("SELECT password from user where user_id='%s'" % (user_id,)).fetchone()
            if user is None:
                return error.error_non_exist_user_id(user_id)
            
            if  password != user.password:
                return error.error_authorization_fail()# 密码错误，返回401"authorization fail."
            self.session.execute(
                "UPDATE user SET balance = balance + %d WHERE user_id = '%s'"%
                (add_value, user_id))
            self.session.commit()
            return 200, "ok"

    def receive_books(self, buyer_id, order_id):
        row = self.session.execute("SELECT buyer_id,status FROM new_order_paid WHERE order_id = '%s'" % (order_id,)).fetchone()
        if row is None:
            return error.error_invalid_order_id(order_id)
        if row[0] != buyer_id: # 用户错误
            return error.error_authorization_fail()

        if row[1] == 0: # status为0，书还未收到
            return 522, "book hasn't been sent to costumer"
        if row[1] == 2: # status为2，书已经收到
            return 523, "book has been received"
        self.session.execute( # status为1，更新状态为2
            "UPDATE new_order_paid set status=2 where order_id = '%s' ;" % (order_id))
        self.session.commit()
        return 200, "ok"

    def search_order(self, buyer_id):
        if not self.user_id_exist(buyer_id):
            code, mes = error.error_non_exist_user_id(buyer_id)
            return code, mes, " "
        ret=[]
        # 已支付订单
        records=self.session.execute(
            " SELECT new_order_detail.order_id,title,new_order_detail.price,count,status,pt,new_order_paid.price "
            "FROM new_order_paid,new_order_detail,book WHERE book.book_id=new_order_detail.book_id and "
            "new_order_paid.order_id=new_order_detail.order_id and new_order_paid.buyer_id = '%s' order by new_order_detail.order_id" % (buyer_id)).fetchall()
        if len(records)!=0:
            last_order_id = records[0][0] # 上一条订单
            statusmap = ['未发货', '已发货', '已收货']
            details=[]
            for i in range(len(records)):
                record=records[i]
                now_order_id=record[0] # 该条订单
                if now_order_id==last_order_id :
                    details.append({'title':record[1],'price':record[2],'count':record[3]})
                else:
                    status=records[i-1][4]
                    ret.append({'order_id':last_order_id,'status':statusmap[status],'time':json.dumps(records[i-1][5],cls=DateEncoder),'total_price':records[i-1][6],'detail':details})
                    details = []
                    details.append({'title': record[1], 'price': record[2], 'count': record[3]})
                last_order_id=now_order_id
            status= records[- 1][4]
            ret.append({'order_id': last_order_id, 'status': statusmap[status], 'time': json.dumps(records[- 1][5],cls=DateEncoder),'total_price':records[i-1][6],
                        'detail': details})
        # 待付款订单
        records = self.session.execute(
            "SELECT new_order_detail.order_id,title,new_order_detail.price,count,pt,new_order_pend.price "
            "FROM new_order_pend,new_order_detail,book WHERE book.book_id=new_order_detail.book_id and "
            "new_order_pend.order_id=new_order_detail.order_id and buyer_id = '%s'" % (buyer_id)).fetchall()
        if len(records)!=0:
            last_order_id = records[0][0]
            details=[]
            for i in range(len(records)):
                record=records[i]
                now_order_id=record[0]
                if now_order_id==last_order_id :
                    details.append({'title':record[1],'price':record[2],'count':record[3]})
                else:
                    ret.append({'order_id':last_order_id,'status':'未付款','time':json.dumps(records[i-1][4],cls=DateEncoder),'total_price':records[i-1][5],'detail':details})
                    details = []
                    details.append({'title': record[1], 'price': record[2], 'count': record[3]})
                last_order_id=now_order_id
            ret.append({'order_id': last_order_id, 'status':'未付款', 'time': json.dumps(records[- 1][4],cls=DateEncoder),'total_price':records[i-1][5],
                        'detail': details})
        if len(ret) != 0:
            return 200, 'ok', ret
        else:
            return 200, 'ok', " "

    def cancel_order(self,buyer_id, order_id):
        if not self.user_id_exist(buyer_id):
            code, mes = error.error_non_exist_user_id(buyer_id)
            return code, mes

        # 在未支付订单查找
        order_info = self.session.execute("Select store_id,price FROM new_order_pend WHERE order_id = '%s' and buyer_id='%s'" % (order_id,buyer_id)).fetchone()
        if order_info is not None: # 未支付订单直接删除
            store_id=order_info[0]
            price=order_info[1]
            self.session.execute("DELETE FROM new_order_pend WHERE order_id = '%s'" % (order_id,))
    
        else: #不是未支付订单
            # 在已支付且未发货订单查找
            order_info = self.session.execute("Select store_id,price FROM new_order_paid WHERE order_id = '%s' and buyer_id='%s' and status='0'" % (order_id,buyer_id)).fetchone()
            if order_info is not None:
                store_id = order_info[0]
                price = order_info[1]
                self.session.execute("DELETE FROM new_order_paid WHERE order_id = '%s' and status='0'" % (order_id,))
                # 找到商店的卖家并更新余额
                user_id = self.session.execute("SELECT user_id FROM user_store WHERE store_id = '%s';" % (order_info[0],)).fetchone()
                self.session.execute("UPDATE user set balance = balance - %d WHERE user_id = '%s'" % (order_info[1], user_id[0]))
                # 更新买家余额
                self.session.execute("UPDATE user set balance = balance + %d WHERE user_id = '%s'" % (order_info[1], buyer_id))
            else: # 已发货订单无法取消
                return error.error_invalid_order_id(order_id)
        timenow = datetime.utcnow()
        self.session.execute(
            "INSERT INTO new_order_cancel(order_id, buyer_id,store_id,price,pt) VALUES('%s', '%s','%s',%d,:timenow);" % (
                order_id, buyer_id, store_id, price), {'timenow': timenow})
        # 更新库存
        self.session.execute(
                    "Update store Set stock_level = stock_level +  count from new_order_detail Where new_order_detail.book_id = store.book_id and store.store_id = '%s' and new_order_detail.order_id = '%s'" % (store_id,order_id))
        self.session.commit()
        return 200, 'ok'

    def auto_cancel(self,order_id_list):
        exist_order_need_cancel=0
        # 遍历订单表
        for order_id in order_id_list:
            store = self.session.execute("Select buyer_id,store_id,price FROM new_order_pend WHERE order_id = '%s'" % (order_id)).fetchone()
            if store is not None: # 是未付款订单
                buyer_id=store[0]
                store_id=store[1]
                price=store[2]
                self.session.execute("DELETE FROM new_order_pend WHERE order_id = '%s'" % (order_id,)) # 删除订单
                timenow = datetime.utcnow()
                self.session.execute( # 加入已取消订单表
                    "INSERT INTO new_order_cancel(order_id, buyer_id,store_id,price,pt) VALUES('%s', '%s','%s',%d,:timenow);" % (
                        order_id, buyer_id, store_id, price), {'timenow': timenow})
                self.session.commit()
                exist_order_need_cancel = 1
        return 'no_such_order' if exist_order_need_cancel==0 else "auto_cancel_done"
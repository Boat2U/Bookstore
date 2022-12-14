import requests
from urllib.parse import urljoin
# from be.model.user import User as User_



class Auth:
    def __init__(self, url_prefix):
        self.url_prefix = urljoin(url_prefix, "auth/")

    def login(self, user_id: str, password: str, terminal: str) -> (int, str):
        json = {"user_id": user_id, "password": password, "terminal": terminal}
        url = urljoin(self.url_prefix, "login")
        r = requests.post(url, json=json)
        return r.status_code, r.json().get("token")

    def register(
        self,
        user_id: str,
        password: str
    ) -> int:
        json = {
            "user_id": user_id,
            "password": password
        }
        url = urljoin(self.url_prefix, "register")
        r = requests.post(url, json=json)
        return r.status_code

    def password(self, user_id: str, old_password: str, new_password: str) -> int:
        json = {
            "user_id": user_id,
            "oldPassword": old_password,
            "newPassword": new_password,
        }
        url = urljoin(self.url_prefix, "password")
        r = requests.post(url, json=json)
        return r.status_code

    def logout(self, user_id: str, token: str) -> int:
        json = {"user_id": user_id}
        headers = {"token": token}
        url = urljoin(self.url_prefix, "logout")
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def unregister(self, user_id: str, password: str) -> int:
        json = {"user_id": user_id, "password": password}
        url = urljoin(self.url_prefix, "unregister")
        r = requests.post(url, json=json)
        return r.status_code

    def search_title_publisher_isbn(self, title='',publisher='',isbn='',store_id='') -> int:
        json = {"title": title,"publisher":publisher,"isbn":isbn,"store_id":store_id}
        url = urljoin(self.url_prefix, "search_title_publisher_isbn")
        r = requests.post(url, json=json)
        return r.status_code

    def search_bookintro_content(self, book_intro='',content='',store_id='') -> int:
        json = {"book_intro": book_intro,"content":content,"store_id":store_id}
        url = urljoin(self.url_prefix, "search_bookintro_content")
        r = requests.post(url, json=json)
        return r.status_code

    def search_tag(self, tag='',store_id='') -> int:
        json = {"tag": tag,"store_id":store_id}
        url = urljoin(self.url_prefix, "search_tag")
        r = requests.post(url, json=json)
        return r.status_code

    def search_author_store(self, author='',store_id='') -> int:
        json = {"author": author,"store_id":store_id}
        url = urljoin(self.url_prefix, "search_author_store")
        r = requests.post(url, json=json)
        return r.status_code

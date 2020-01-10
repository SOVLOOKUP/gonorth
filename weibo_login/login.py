
import pymongo
from pymongo.errors import DuplicateKeyError

from selelogin import login



LOCAL_MONGO_HOST = '192.168.160.166'
LOCAL_MONGO_PORT = 27017
DB_NAME = 'sina'



if __name__ == '__main__':
    # 在目录中新建一个account.txt文件，输入账号和密码
    
    file_path = 'account.txt'
    with open(file_path, 'r') as f:
        lines = f.readlines()
    mongo_client = pymongo.MongoClient(LOCAL_MONGO_HOST, LOCAL_MONGO_PORT)
    mongo_client[DB_NAME].authenticate('root','123456')
    collection = mongo_client[DB_NAME]["account"]

    for line in lines:
        line = line.strip()
        username = line.split('----')[0]
        password = line.split('----')[1]
        print('=' * 10 + username + '=' * 10)
        try:
            cookie_str = login(username, password)
        except Exception as e:
            print(e)
            continue
        print('获取cookie成功')
        print('Cookie:', cookie_str)
        try:
            collection.insert_one(
                {"_id": username, "password": password, "cookie": cookie_str, "status": "success"})
        except DuplicateKeyError as e:
            collection.find_one_and_update({'_id': username}, {'$set': {'cookie': cookie_str, "status": "success"}})

import json
import os
import sqlite3
from pprint import pprint
from typing import List, Dict

from dingding_message import config
from dingding_message import log

"""
time和message字段比较复杂，是两个JSON串
需要考虑这两个字段的json序列化
"""
db = sqlite3.connect(
    os.path.join(config.db_path, "dingding_message.db"), check_same_thread=False
)
message_json_key = ("message", "time")

logger = log.get_logger()


def exists():
    """判断表结构是否存在"""
    res = db.execute("select * from sqlite_master where tbl_name='message'")
    return res.fetchone() is not None


def to_json(cursor: sqlite3.Cursor, row):
    """将一行数据和cursor转化为一个dict"""
    a = {}
    for col, row_value in zip(cursor.description, row):
        a[col[0]] = row_value
    return a


def encode_message(message: Dict):
    """把message各个字段转换成json串"""
    for json_key in message_json_key:
        message[json_key] = json.dump(message[json_key])
    return message


def decode_message(message: Dict):
    """把message各个字段由json串转换成Dict"""
    for json_key in message_json_key:
        message[json_key] = json.loads(message[json_key])
    return message


def init_structure():
    """初始化表结构"""
    db.execute("drop table if exists message")
    db.execute(
        "create table message(id varchar(30),time varchar(200),message varchar(2000),token varchar(200),user_id varchar(200) )"
    )
    db.commit()


def insert(message_id: str, time: Dict, message: Dict, token: str, user_id: str):
    time = json.dumps(time)
    message = json.dumps(message)
    cur = db.execute(
        "insert into message(id,time,message,token,user_id) values(?,?,?,?,?)",
        (message_id, time, message, token, user_id),
    )
    db.commit()
    return cur.rowcount


def delete_one(message_id: str):
    cur = db.execute("delete from message where id=?", (message_id,))
    db.commit()
    return cur.rowcount


def update(message_id: str, time: Dict, message: Dict, token: str) -> int:
    time = json.dumps(time)
    message = json.dumps(message)
    cur = db.execute(
        "update message set time=?,message=?,token=? where id=?",
        (time, message, token, message_id),
    )
    db.commit()
    return cur.rowcount


def select_all() -> List[Dict]:
    res = db.execute("select * from message")
    ans = [decode_message(to_json(res, row)) for row in res.fetchall()]
    return ans


def select_one(message_id: str) -> Dict:
    res = db.execute("select * from message where id=?", (message_id,))
    ans = to_json(res.fetchone())
    ans = decode_message(ans)
    return ans


def delete_all():
    res = db.execute("delete from message")
    db.commit()
    return res.rowcount


if not exists():
    init_structure()
if __name__ == "__main__":
    # print(exists())
    # init_structure()
    # delete_all()
    # init_structure()
    # res = select()
    # print(res)
    # delete(3368074347149230000)
    # delete("3368076994315845632")
    pprint(select_all())

import json
import threading

import flask
from flask import request

from dingding_message import dao, ding, log
from dingding_message import snow_flake

logger = log.get_logger()

app = flask.Flask(__name__)
snow = snow_flake.SnowFlake()


@app.route("/")
def haha():
    return "hello"


@app.route("/api/insert_message")
def insert_message():
    data = request.args["data"]
    data = json.loads(data)
    message = data["message"]
    time = data["time"]
    token = data["token"]
    user_id = "weiyinfu"
    message_id = str(snow.get_id())
    if time["interval_count"] == 0:
        # 只运行一次
        ding.take_effect(time, message, token, message_id)
        return "ok"
    else:
        res = dao.insert(message_id, time, message, token, user_id)
        if res == 1:
            ding.take_effect(time, message, token, message_id)
            return "ok"
        else:
            return "error"


@app.route("/api/delete_message")
def delete_message():
    message_id = request.args["message_id"]
    logger.info(f"deleting message_id={message_id}")
    res = dao.delete_one(message_id)
    logger.info(f"delete result is {res}")
    if res:
        ding.remove_job_by_id(message_id)
        return "ok"
    else:
        return "error"


@app.route("/api/update_message")
def update_message():
    data = json.loads(request.args["data"])
    message_id = data["id"]
    time = data["time"]
    message = data["message"]
    token = data["token"]
    res = dao.update(message_id, time, message, token)
    if res == 1:
        ding.remove_job_by_id(message_id)
        ding.take_effect(time, message, token, message_id)
        return "ok"
    else:
        return "error"


@app.route("/api/select_message")
def select_message():
    return json.dumps(dao.select_all())


@app.route("/api/get_interval_list")
def get_interval_list():
    return json.dumps(ding.interval_list)


def init_worker():
    message_list = dao.select_all()
    for message in message_list:
        ding.take_effect(message["time"], message["message"], message["token"], message['id'])


def main():
    init_worker()
    worker_thread = threading.Thread(target=ding.worker)
    worker_thread.start()
    app.run(debug=False, port=9876)


if __name__ == "__main__":
    main()

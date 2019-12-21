# -*- coding: utf-8 -*-
import json

import requests

SHOW_AVATAR = "0"  # 不隐藏头像
HIDE_AVATAR = "1"  # 隐藏头像


class ButtonDirection:
    VERTICAL = "1"
    HORIZONTAL = "0"


class DingDing(object):
    def __init__(self, token):
        self.url = self.parse_token(token)

    def parse_token(self, token):
        ding_url_pre = "https://oapi.dingtalk.com/robot/send?access_token=%s"
        token = token.strip()
        if len(token) == 64:
            return ding_url_pre % token

        if len(token) == 114:
            return token

        raise ValueError("token Error")

    def send_text(self, text, at_mobiles=None, at_all=False):
        """
        例子: send_text('天气不错', ['13333333333'])
        :param text: 消息类型，此时固定为:text
        :param at_mobiles: 被@人的手机号 ['13333333333', ]
        :param at_all: @所有人时:true,否则为:false
        :return:
        """
        if at_mobiles is None:
            at_mobiles = []
        data = {
            "msgtype": "text",
            "text": {"content": text},
            "at": {"atMobiles": at_mobiles, "isAtAll": at_all},
        }
        return self._post(data)

    def send_link(self, title, text, message_url="", pic_url=""):
        data = {
            "msgtype": "link",
            "link": {
                "text": text,
                "title": title,
                "picUrl": pic_url,
                "messageUrl": message_url,
            },
        }
        return self._post(data)

    def send_markdown(self, title, text, at_mobiles=None, at_all=False):
        """发送markdown格式

        :param title: 首屏会话透出的展示内容
        :param text: markdown格式的消息
        :param at_mobiles: 被@人的手机号(在text内容里要有@手机号)
        :param at_all: @所有人时:true,否则为:false
        :return:
        """
        data = {
            "msgtype": "markdown",
            "markdown": {"title": title, "text": text},
            "at": {"atMobiles": at_mobiles, "isAtAll": at_all},
        }
        return self._post(data)

    def send_single_action_card(
        self,
        title,
        text,
        single_title,
        single_url,
        button_orientation=ButtonDirection.HORIZONTAL,
        hide_avatar=SHOW_AVATAR,
    ):
        """整体跳转ActionCard类型

        :param title: 首屏会话透出的展示内容
        :param text: markdown格式的消息
        :param single_title: 单个按钮的方案。(设置此项和singleURL后btns无效。)
        :param single_url: 点击singleTitle按钮触发的URL
        :param button_orientation: 0-按钮竖直排列，1-按钮横向排列
        :param hide_avatar: 0-正常发消息者头像,1-隐藏发消息者头像
        :return:
        """
        data = {
            "actionCard": {
                "title": title,
                "text": text,
                "hideAvatar": hide_avatar,
                "btnOrientation": button_orientation,
                "singleTitle": single_title,
                "singleURL": single_url,
            },
            "msgtype": "actionCard",
        }
        return self._post(data)

    def send_action_card(
        self,
        title,
        text,
        buttons,
        button_orientation=ButtonDirection.HORIZONTAL,
        hide_avatar=SHOW_AVATAR,
    ):
        """独立跳转ActionCard类型

        :param title: 首屏会话透出的展示内容
        :param text: markdown格式的消息
        :param buttons: 按钮的信息：title-按钮方案，actionURL-点击按钮触发的URL
        :param button_orientation: 0-按钮竖直排列，1-按钮横向排列
        :param hide_avatar: 0-正常发消息者头像,1-隐藏发消息者头像
        :return:
        """
        for btn in buttons:
            for k in ("title", "actionURL"):
                assert k in btn,f'{k} not in {btn}'
        data = {
            "actionCard": {
                "title": title,
                "text": text,
                "hideAvatar": hide_avatar,
                "btnOrientation": button_orientation,
                "btns": buttons,
            },
            "msgtype": "actionCard",
        }
        return self._post(data)

    def send_feed_card(self, rows):
        """FeedCard类型
        例子: send_feed_card([('学vue','https://cn.vuejs.org/','https://cn.vuejs.org/images/logo.png'),
                     ('哪家强', 'https://cn.vuejs.org/', 'https://cn.vuejs.org/images/logo.png')])
        :param rows: [(title, messageURL, picURL), (...)]
        :return:
        """
        for row in rows:
            for k in ("title", "messageURL", "picURL"):
                assert k in row,f'{k} not in {row}'
        data = {"feedCard": {"links": rows}, "msgtype": "feedCard"}
        return self._post(data)

    def _post(self, data):
        resp = requests.post(
            self.url,
            data=bytes(json.dumps(data, ensure_ascii=False), encoding="utf8"),
            headers={"Content-Type": "application/json"},
        )
        return resp.json()

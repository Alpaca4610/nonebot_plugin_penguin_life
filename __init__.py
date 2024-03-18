from config import Config
import nonebot
import requests
import re
import json

from nonebot import on_command,require
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageSegment, Bot, MessageEvent

require("nonebot_plugin_apscheduler")
require("nonebot_plugin_saa")

from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_saa import Text, MessageFactory, SaaTarget, Mention, Reply,enable_auto_select_bot
from .config import Config

enable_auto_select_bot()
notice_list =[]

plugin_config = Config.parse_obj(nonebot.get_driver().config.dict())

token = plugin_config.token

all_ = on_command("本部洗衣", block=False, priority=1)
@all_.handle()
async def _(bot: Bot,event: MessageEvent, msg: Message = CommandArg()):

    response_json = get_status("202302071714530000012067133598")
    items = response_json['data']['items']
    names = []
    for item in items:
        if item['status'] == 1:
            names.append(item['name'])

    names_str = '\n'.join(names)

    msgs = []
    temp = {
        "type": "node",
        "data": {
        "name": "本部洗衣机状态播报",
        "uin": bot.self_id,
        "content": MessageSegment.text("当前可用洗衣机为：\n" + names_str)
        }
    }       
    msgs.append(temp)
    await bot.call_api("send_group_forward_msg",group_id=event.group_id,messages=msgs)

all_yanbei = on_command("雁北洗衣机", block=False, priority=1)
@all_yanbei.handle()
async def _(bot: Bot,event: MessageEvent, msg: Message = CommandArg()):

    response_json = get_status("202401041041470000069996565184")
    items = response_json['data']['items']
    names = []
    for item in items:
        if item['status'] == 1:
            names.append(item['name'])

    names_str = '\n'.join(names)

    msgs = []
    temp = {
        "type": "node",
        "data": {
        "name": "雁北洗衣机状态播报",
        "uin": bot.self_id,
        "content": MessageSegment.text("当前可用洗衣机为：\n" + names_str)
        }
    }       
    msgs.append(temp)
    await bot.call_api("send_group_forward_msg",group_id=event.group_id,messages=msgs)

all_yanbei = on_command("雁南洗衣机", block=False, priority=1)
@all_yanbei.handle()
async def _(bot: Bot,event: MessageEvent, msg: Message = CommandArg()):

    response_json = get_status("202401041044000000069996552384")
    items = response_json['data']['items']
    names = []
    for item in items:
        if item['status'] == 1:
            names.append(item['name'])

    names_str = '\n'.join(names)

    msgs = []
    temp = {
        "type": "node",
        "data": {
        "name": "雁南洗衣机状态播报",
        "uin": bot.self_id,
        "content": MessageSegment.text("当前可用洗衣机为：\n" + names_str)
        }
    }       
    msgs.append(temp)
    await bot.call_api("send_group_forward_msg",group_id=event.group_id,messages=msgs)

search_ = on_command("本部洗衣机", block=False, priority=1)
@search_.handle()
async def _(bot: Bot,event: MessageEvent, msg: Message = CommandArg()):
    content = msg.extract_plain_text()
    if content == "" or content is None:
        await search_.finish(MessageSegment.text("楼层不能为空！"),at_sender = True)
    response_json = get_status("202302071714530000012067133598")
    res = query_status(content,response_json)
    await search_.finish(res,at_sender = True)

help_ = on_command("洗衣帮助", block=False, priority=1)
@help_.handle()
async def _():
    await help_.finish("洗衣助手：\n本部洗衣————查看本部空闲洗衣机\n本部洗衣机 学X楼X层—————查看本部指定楼层洗衣机状态\n本部洗衣机提醒 学X楼X层————设置洗衣机空闲提醒\n雁北洗衣机————查看沙河雁北空闲洗衣机\n雁南洗衣机————查看沙河雁南空闲洗衣机")

notice_ = on_command("本部洗衣机提醒", block=False, priority=1)
@notice_.handle()
async def _(bot: Bot,event: MessageEvent, target: SaaTarget, msg: Message = CommandArg()):
    global notice_list
    content = msg.extract_plain_text()
    if content == "" or content is None:
        await notice_.finish(MessageSegment.text("楼层不能为空！"),at_sender = True)
    response_json = get_status("202302071714530000012067133598")
    res = query_status(content,response_json)
    if res != "当前楼层暂无可用洗衣机哦":
        await notice_.finish("当前楼层存在空闲洗衣机：\n"+res,at_sender = True)
    else:
        notice_list.append({'id': event.get_user_id(), 'messageid': event.message_id, 'data': content, 'target':target})
        print(notice_list)
        await notice_.finish("提醒添加成功",at_sender = True)

@scheduler.scheduled_job("cron", minute ="*/1", id="job_0")
async def run_every_1_minute():
    global notice_list
    if notice_list:
        remove_list = []
        response_json = get_status("202302071714530000012067133598")
        print("向服务器请求状态")
        for i in notice_list:
            res = query_status(i['data'],response_json)
            if res != "当前楼层暂无可用洗衣机哦":
                msg = Text("当前楼层存在空闲洗衣机！冲冲冲\n" + res)
                mention = Mention(user_id=i['id'])
                msg = MessageFactory([msg, mention, Reply(message_id=i['messageid'])])
                await msg.send_to(i['target'])
                remove_list.append(i)
        notice_list = [i for i in notice_list if i not in remove_list]

def get_status(shopId):
    global token
    url = "https://userapi.qiekj.com//machineModel/near/machines"
    headers = {
    'Host': 'userapi.qiekj.com',
    'Connection': 'keep-alive',
    'Content-Length': '146',
    'xweb_xhr': '1',
    'channel': 'wechat',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF XWEB/8447',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': '*/*',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://servicewechat.com/wx52cfa5fc8d32a43d/69/page-frame.html',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    }

    data = {
    'shopId': shopId,
    'machineTypeId': 'c9892cb4-bd78-40f6-83c2-ba73383b090a',
    'pageSize': '200',
    'page': '1',
    'token': token
    }

    response = requests.post(url, headers=headers, data=data)
    response_json = response.json()

    return response_json


def query_status(location_str,data):
    match = re.match(r'学(\d+)楼(\d+)层', location_str)
    if not match:
        return "输入的字符串格式不正确，请按照'学X楼X层'的格式输入"

    building, floor = match.groups()
    items = data['data']['items']

    name_str = '北邮学{}楼{}层'.format(building, floor)
    available_machines = []

    for item in items:
        if name_str in item['name'] and item['status'] == 1:
            available_machines.append(item['name'])

    return "当前空闲的洗衣机为：\n"+'\n'.join(available_machines) if available_machines else "当前楼层暂无可用洗衣机哦"

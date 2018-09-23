#-*- coding: utf-8 -*-

import re
import datetime
import requests

from collections import defaultdict



# 从字典中获取值
# 如果不存在则返回None
def getAttr(kwargs, key):
    if key in kwargs:
        return kwargs[key]
    return None


# 用户类
# 本来应该叫upper但仔细想想好像并不是每个人都是upper2333
class user(object):
    def __init__(
        self,               
        mid,                # 用户的唯一标志符
        name=None,          # 用户名
        sex=None,           # 性别, 字符串型
        face=None,          # 头像的url
        regtime=None,       # 注册时间戳
        birthday=None,      # 破蛋日， 字符串型
        sign=None,          # 个人说明
        level=None,         # 等级
        vip_type=None,      # vip类型
        vip_status=None,    # vip状态
        following=None,     # 关注了几个人
        follower=None       # 有多少粉丝
    ):
        self.mid = mid
        self.name = name
        self.sex = sex
        self.face = face
        self.regtime = regtime if regtime else int(datetime.datetime.now().timestamp())
        self.birthday = birthday
        self.sign = sign
        self.level = level if level else 0
        self.vip_type = vip_type
        self.vip_status = vip_status
        self.following = following if following else 0
        self.follower = follower if follower else 0

# 投稿类
class submit(object):
    def __init__(
        self,
        aid,                # 视频唯一标识符 俗称aid
        videos=1,           # 分p数
        type_name=None,     # 分区名，取最后一个(比如鬼畜.音MAD, 就是音MAD)
        copyright=None,     # 版权类型, 1为原创， 2为转载
        pic=None,           # 封面
        title=None,         # 标题
        publish_date=None,  # 发布时间
        create_time=None,   # 也是一个时间, 不过比较莫名其妙就是了
        descibe=None,       # 介绍
        attribute=None,     # 
        duration=None,      # 持续时长， 如果多p的话为p1的时长, 单位秒
        owner_mid=None,     # up主的mid
        owner_name=None,    # up主的用户名
        owner_face=None,    # up主的头像
        cid=None,           # 视频的cid
        width=None,         # 视频宽度，单位像素
        height=None,        # 视频高度，单位像素
        view=None,          # 播放量
        reply=None,         # 回复数
        favorite=None,      # 收藏数
        coin=None,          # 硬币数
        share=None,         # 分享次数
        rank=None,          # 历史最高排名
        like=None,          # 推荐数
        dislike=None        # 不推荐数
    
    ):
        pass
        
# 获取用户
# kwargs会作为参数传给requests.
def get_user(mid, **kwargs):
    pass



def test(a, **values):
    print(getAttr(values, 'b'))


if __name__ == "__main__":
    u = user(25, "233")
    print(u.__dict__.items())
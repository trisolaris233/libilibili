#-*- coding: utf-8 -*-

import re
import copy
import datetime
import requests

# from collections import defaultdict
# from collections.abc import Iterable  



GET_UP_INFO_URL = "https://space.bilibili.com/ajax/member/GetInfo"

GET_FOLLOW_INFO_URL = "https://api.bilibili.com/x/relation/stat"

GET_UPPER_SUBMIT_INFO_URL = "https://space.bilibili.com/ajax/member/getSubmitVideos"


# 此header用于获取UP主的个人信息
# 关键字段: 
#   referer: 为某一用户的个人空间地址
#   host: 必须为space.bilibili.com
GET_UP_INFO_HEADER = {
    'Accept':
    'application/json, text/plain, */*',
    'Accept - Encoding':
    'gzip, deflate, br',
    'Accept-Language':
    'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Cookie':
    'finger=1c12d260; DedeUserID=152683670; DedeUserID__ckMd5=6e5488f6b82b890d; fts=1537678069; UM_distinctid=16604c14c8d1df-0a5b0cf28ae475-5701732-1fa400-16604c14c8e91b; rpdid=oqqwwimkqwdoskmxmqopw; BANGUMI_SS_1177_REC=34489; BANGUMI_SS_24588_REC=232473; CURRENT_FNVAL=8; BANGUMI_SS_3271_REC=82961; BANGUMI_SS_24571_REC=231926; stardustvideo=1; sid=d35bnves; SESSDATA=10c41556%2C1540345600%2C7eee939f; bili_jct=bda61d2ce5a96d2f1b67ab23dd4bcd67; LIVE_BUVID=AUTO2515377536013436; buvid3=13D8FDAA-DB92-40DD-A836-CBC83FC438116716infoc; _dfcaptcha=5f7d4556f5c0d31020bf5d9bdab89739; bp_t_offset_152683670=166989062909847236; CNZZDATA2724999=cnzz_eid%3D1723892295-1537674572-https%253A%252F%252Fwww.bilibili.com%252F%26ntime%3D1537759951',
    'Host':
    'space.bilibili.com',
    'Referer':
    'https://space.bilibili.com/152683670/',
    'UserAgent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'
}

GENERAL_HEADERS = {
    'Accept':
    'application/json, text/plain, */*',
    'Accept - Encoding':
    'gzip, deflate, br',
    'Accept-Language':
    'zh-CN,zh;',
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'
}

USER_GENERAL_INFO_ROOT = 'data'
USER_GENERAL_INFO_ATTR = [
    'mid','name', 'sex', 'face', 'regtime', 'birthday', 'sign',
    ['level_info', 'current_level'], ['vip', 'vipType'],
    ['vip', 'vipStatus']
]

USER_FOLLOWING_INFO_ROOT = 'data'
USER_FOLLOWING_INFO_ATTR = [
    'following', 'follower'
]

UPPER_SUBMIT_SUMMARY_ROOT = ['data', 'vlist']
UPPER_SUBMIT_SUMMARY_ATTR = [
    'aid', 'typeid', 'play', 'pic', 'description',
    'copyright', 'title', 'created', 'length', 'video_review',
    'favorites'
]

# 用户类
# 本来应该叫upper但仔细想想好像并不是每个人都是upper2333
class user(object):
    def __init__(
        self,               
        mid,                # 用户的唯一标志符
        name=None,          # 用户名
        sex=None,           # 性别, 字符串型
        face=None,          # 头像的url
        regtime=int(datetime.datetime.now().timestamp()),   # 注册时间戳
        birthday=None,      # 破蛋日， 字符串型
        sign=None,          # 个人说明
        level=0,            # 等级
        vip_type=0,         # vip类型
        vip_status=0,       # vip状态
        following=0,        # 关注了几个人
        follower=0,         # 有多少粉丝
        submits=[]          # 投稿列表(简要信息)
    ):
        self.mid = mid
        self.name = name
        self.sex = sex
        self.face = face
        self.regtime = regtime
        self.birthday = birthday
        self.sign = sign
        self.level = level
        self.vip_type = vip_type
        self.vip_status = vip_status
        self.following = following
        self.follower = follower
        self.submits = submits

    def __bool__(self):
        return self.name != None and self.mid > 0


# 投稿摘要
# 显示投稿的部分信息
class submit_summary(object):
    def __init__(
        self,               
        aid=0,              # 视频的aid
        tid=0,              # 分区id
        play=0,             # 播放量
        pic=None,           # 封面图url
        description=None,   # 介绍
        copyright=1,        # 版权
        title=None,         # 标题
        created_time=       # 发布时间
        int(datetime.datetime.now().timestamp()),
        duration=0,         # 时长
        danmaku=0,          # 弹幕数量
        favorites=0,        # 收藏数
        author_mid=0,       # up主mid
        author_name=None,   # up主用户名
    ):
        self.aid = aid
        self.tid = tid
        self.play = play
        self.pic = pic
        self.description = description
        self.copyright = copyright
        self.title = title
        self.created_time = created_time
        self.duration = duration
        self.danmaku = danmaku
        self.favorites = favorites
        self.author_mid = author_mid
        self.author_name = author_name


# url类
class url(object):
    def __init__(
        self,
        method='get',
        link=None,
        accept_type="json",
        args = {},
    ):
        self.method = method
        self.link=link
        self.accept_type = accept_type
        self.args=args


class resource(object):
    def __init__(self, data=[]):
        self.data = data       
        
# 投稿类
class submit(object):
    def __init__(
        self,
        aid,                # 视频唯一标识符 俗称aid
        videos=1,           # 分p数
        type_id=0,          # 分区id
        type_name=None,     # 分区名，取最后一个(比如鬼畜.音MAD, 就是音MAD)
        copyright=1,        # 版权类型, 1为原创， 2为转载
        pic=None,           # 封面
        title=None,         # 标题
        publish_date=       # 发布时间
        int(datetime.datetime.now().timestamp()),  
        created_time=       # 也是一个时间, 不过比较莫名其妙就是了
        int(datetime.datetime.now().timestamp()),   
        descibe=None,       # 介绍
        attribute=None,     # 
        duration=[],        # 持续时长
        owner_mid=0,        # up主的mid
        owner_name=None,    # up主的用户名
        owner_face=None,    # up主的头像
        cid=[],             # 视频的cid
        width=[],           # 视频宽度，单位像素
        height=[],          # 视频高度，单位像素
        view=0,             # 播放量
        reply=0,            # 回复数
        favorite=0,         # 收藏数
        coin=0,             # 硬币数
        share=0,            # 分享次数
        rank=0,             # 历史最高排名
        like=0,             # 推荐数
        dislike=0,          # 不推荐数
        danmaku=0           # 弹幕数
    ):
        pass


def _set_user_general_info(user):
    pass

# 从字典中获取值
# 如果不存在则返回None
def get_attr(kwargs, key):
    if isinstance(key, list) and isinstance(kwargs, dict):
        if len(key) > 1:
            return get_attr(kwargs[key[0]], key[1:])
        elif len(key) != 0:
            return kwargs[key[0]]
        return None
    return kwargs[key] if isinstance(kwargs, dict) and key in kwargs else None


# 从HEADER中取得csrf值
# csrf作为调用一些接口的必要参数
def get_csrf():
    search_res = re.search("bili_jct=(.*?);", get_attr(GET_UP_INFO_HEADER, 'Cookie'))
    return search_res.group(1) if search_res and search_res.group(1) else None


# 获取用户的投稿
def get_num_submit(mid, **kwargs):
    try:
        response = requests.get(
            "%s?mid=%d&page=1&pagesize=1" % (
                GET_UPPER_SUBMIT_INFO_URL,
                mid
            ),
            headers=GENERAL_HEADERS,
            **kwargs
        )
        return get_attr(response.json(), ['data', 'count'])
    except:
        return 0

# 下载url置顶的资源
def download_url(url_g, **kwargs):
    # print(kwargs)
    try:
        method = url_g.method
        link = url_g.link
        accept_type = url_g.accept_type
        args = url_g.args
        # print("method:%s, link=%s, accept_type=%s, args=%s" % (method, link, accept_type, args))
    except:
        print("failed to get propery")
        return None

    # get请求
    if method.upper() == "GET":
        get_url = "%s?" % link
        # print(get_url[:-1])
        
        try:
            for key in list(args.keys()):
                get_url = "%s%s=%s&" % (get_url, key, args[key])
        except:
            return None
        # print(get_url[:-1])
        
        # 下载资源
        response = requests.get(
            get_url,
            **kwargs
        )
    # post请求
    elif method.upper() == "POST":
        response = requests.post(
            link,
            data=args,
            **kwargs
        )
    
    # 处理下载到的资源
    try:
        return {
            'TEXT': response.text,
            'CONTENT': response.content,
            'CODE' : response.status_code,
        }[accept_type.upper()]
    except:
        try:
            return response.json() if accept_type.upper() == "JSON" else response
        except:
            return response
    

# 获取用户的url
# kwargs会在一定情况下作为参数传给requests(则devide_submit=True时)
# kwargs支持的参数:
#   has_summary: 如果为真， 则返回带有submit summary的url. 默认为假
# 返回值:
#   返回一个url对象列表
def get_user_urls(mid, **kwargs):
    res = []
    has_summary = kwargs.pop('has_summary', False)

    # 添加取得用户基本参数的url
    res.append(
        url(
            "post",
            GET_UP_INFO_URL,
            "json",
            {
                'csrf': get_csrf(),
                'mid': mid
            }
        )
    )

    # 添加取得用户粉丝数和关注数的url
    res.append(
        url(
            "get",
            GET_FOLLOW_INFO_URL,
            "json",
            {
                'vmid': mid
            }
        )
    )

    # 获取投稿摘要url
    if has_summary:
        res.append(
            url(
                "get",
                GET_UPPER_SUBMIT_INFO_URL,
                "json",
                {
                    'mid': mid,
                    'page': 1,
                    'pagesize': get_num_submit(mid, **kwargs)
                }
            )
        )
    
    return res

# 下载用户的urls, 返回resource对象
def download_user_urls(urls, **kwargs):
    res = []
    hs = [
        GET_UP_INFO_HEADER,
        GENERAL_HEADERS,
        GET_UP_INFO_HEADER
    ]
    length = len(urls)
    try:
        for i in range(0, min(length, len(hs))):
            res.append(download_url(urls[i], headers=hs[i]))
    except:
        return None
    return resource(res)

# 解析资源, res为resource对象
# 因为url下载下来的资源可能需要多个才能集合成一个对象, resource用来包装urls获得的资源
def parse_user_urls(res):
    info = []
    roots = [
        USER_GENERAL_INFO_ROOT,
        USER_FOLLOWING_INFO_ROOT,
        UPPER_SUBMIT_SUMMARY_ROOT
    ]
    attrs = [
        USER_GENERAL_INFO_ATTR,
        USER_FOLLOWING_INFO_ATTR,
        UPPER_SUBMIT_SUMMARY_ATTR
    ]
    count = 0
    res_user = user(0)
    summary_keys = list(vars(submit_summary()).keys())
    user_keys = list(vars(res_user).keys())

    for i in range(0, len(res.data)):
        info.append(res.data[i]) 

    for i in range(0, len(info) - 1):
        data = get_attr(info[i], roots[i])
        for j in range(0, len(attrs[i])):
            # print("res_user.__dict__[%s]=%s" % (user_keys[count], attrs[i][j]))
            res_user.__dict__[user_keys[count]] = get_attr(data, attrs[i][j])
            count = count + 1


    if len(info) > 2:
        data = get_attr(info[2], UPPER_SUBMIT_SUMMARY_ROOT)
        submits_list = []
        for i in data:
            summary = submit_summary()
            for j in range(0, len(UPPER_SUBMIT_SUMMARY_ATTR)):
                summary.__dict__[summary_keys[j]] = get_attr(i, UPPER_SUBMIT_SUMMARY_ATTR[j])
            submits_list.append(copy.deepcopy(summary))
        res_user.submits = submits_list
    
    return res_user


# 获取用户
# kwargs会作为参数传给requests.
# 额外支持的kwargs:
#   has_summary： 如果为真，则返回带有submit summary的user对象 默认为假
# 返回值:
#   返回user对象(中途失败则返回不完全或者为空的user对象)
'''
此方法会阻塞调用1-3次requests, 如果是投稿较多的up延迟或许比较明显， 如果单线程， 对数据量要求不是
很高的情况下可以使用此方法，方便直接返回user对象. 不然则鼓励使用支持多线程的方法获取， 效率更高。
'''
def get_user(mid, **kwargs):
    return parse_user_urls(download_user_urls(get_user_urls(mid, **kwargs)))
    # has_summary = kwargs.pop('has_summary', False)
    # # has_summary = get_attr(kwargs, 'has_summary')
    # # if 'has_summary' in kwargs:
    # #     kwargs.pop('has_summary')

    # post_url = GET_UP_INFO_URL
    # post_data = {
    #     'csrf': get_csrf(),
    #     'mid':mid
    # }
    # user_obj = user(mid)
    
    # try:
    #     response = requests.post(
    #         post_url,
    #         data=post_data,
    #         headers=GET_UP_INFO_HEADER,
    #         **kwargs
    #     )
    #     response_json = response.json()
    # except:
    #     print("failed to connect the host")
    #     return user_obj
    
    # user_data = get_attr(response_json, 'data')
    # data_attributes = [
    #     'name', 'sex', 'face', 'regtime', 'birthday', 'sign',
    #     ['level_info', 'current_level'], ['vip', 'vipType'],
    #     ['vip', 'vipStatus']
    # ]

    # # 获取up主基本参数
    # try:
    #     user_keys = list(vars(user_obj).keys())
    #     for i in range(1, min(len(data_attributes), len(user_keys))):
    #         user_obj.__dict__[user_keys[i]] = get_attr(user_data, data_attributes[i - 1])  
    # except:
    #     print("failed to get general infomation of user")
    #     return user_obj

    # # 获取up主的粉丝数与关注数
    # try:
    #     response = requests.get(
    #         "%s?vmid=%d" % (GET_FOLLOW_INFO_URL, mid),
    #         headers=GENERAL_HEADERS,
    #         **kwargs
    #     )
    #     response_json = response.json()
    #     follow_data = get_attr(response_json, 'data')
    #     user_obj.follower = get_attr(follow_data, 'follower')
    #     user_obj.following = get_attr(follow_data, 'following')
    # except:
    #     print("failed to get response")
    #     return user_obj

    # # 判断是否返回投稿信息
    # # print("???")
    # if has_summary:
    #     # print(get_num_submit(mid))
    #     try:
    #         response = requests.get(
    #             "%s?mid=%d&page=1&pagesize=%d" % (
    #                 GET_UPPER_SUBMIT_INFO_URL,
    #                 mid,
    #                 get_num_submit(mid, **kwargs)
    #             ),
    #             headers=GENERAL_HEADERS,
    #             **kwargs
    #         )
            
    #         summary_attributes = [
    #             'aid', 'typeid', 'play', 'pic', 'description',
    #             'copyright', 'title', 'created', 'length', 'video_review',
    #             'favorites'
    #         ]
    #         for each in get_attr(response.json(), ['data', 'vlist']):
    #             # print(each)
    #             summary_obj = submit_summary()
    #             summary_keys = list(vars(summary_obj).keys())

    #             # 遍历属性逐个赋值
    #             for i in range(0, min(len(summary_keys), len(summary_attributes))):
    #                 summary_obj.__dict__[summary_keys[i]] = get_attr(each, summary_attributes[i])

    #             user_obj.submits.append(summary_obj)

    #     except:
    #         print("failed to get the infomation of submits.")
    #         return user_obj

    # return user_obj


if __name__ == "__main__":
    # print(download_url(
    #     url(
    #         "post",
    #         "https://space.bilibili.com/ajax/member/GetInfo",
    #         "json",
    #         {
    #             'csrf':get_csrf(),
    #             'mid':398510
    #         }
    #     ),
    #     headers=GET_UP_INFO_HEADER
    # ))
    # get_user_urls(398510, has_summary=True)
    # res = get_user_urls(398510, has_summary=True)
    u = parse_user_urls(download_user_urls(get_user_urls(152683670, has_summary=True)))
    print(vars(u))
    # print(vars(u))
    print(vars(get_user(1)))
    # print(vars(u))
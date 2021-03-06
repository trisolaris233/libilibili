#-*- coding: utf-8 -*-

import re
import copy
import datetime
import requests

from bs4 import BeautifulSoup

# from collections import defaultdict
# from collections.abc import Iterable  

'''
----------------------------------global-------------------------------------
'''

# 获取u用户基本信息
GET_UP_INFO_URL = "https://space.bilibili.com/ajax/member/GetInfo"
# 获取用户关注数与粉丝数
GET_FOLLOW_INFO_URL = "https://api.bilibili.com/x/relation/stat"
# 获取up主投稿信息(简要)
GET_UPPER_SUBMIT_INFO_URL = "https://space.bilibili.com/ajax/member/getSubmitVideos"
# 获取视频
GET_UPPER_SUBMIT_DETAIL_URL = "https://api.bilibili.com/x/web-interface/view"
# 获取弹幕
GET_DANMAKU_URL = "https://api.bilibili.com/x/v1/dm/list.so"
# 获取历史弹幕
GET_HISTORY_DANMAKU_URL = "https://api.bilibili.com/x/v2/dm/history"
# 获取番剧索引
GET_BANGUMI_INDEX_URL = "https://bangumi.bilibili.com/media/web_api/search/result"
# 获取番剧播放信息
GET_BANGUMI_PLAY_INFO_URL = "https://bangumi.bilibili.com/ext/web_api/season_count"

# 此header用于获取UP主的个人信息
# 关键字段: 
#   referer: 为某一用户的个人空间地址
#   host: 必须为space.bilibili.com
GET_UP_INFO_HEADERS = {
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

GET_SUBMIT_DETAIL_HEADERS  = {
    'Accept':
    'application/json, text/plain, */*',
    'Accept - Encoding':
    'gzip, deflate, br',
    'Accept-Language':
    'zh-CN,zh;',
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063',
    'Host':
    'api.bilibili.com',
}

GET_HISTORY_DANMAKU_HEADERS = {
    'Accept':
    'application/json, text/plain, */*',
    'Accept - Encoding':
    'gzip, deflate, br',
    'Accept-Language':
    'zh-CN,zh;',
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063',
    'Host':
    'api.bilibili.com',
    'Cookie':
    'finger=1c12d260; DedeUserID=152683670; DedeUserID__ckMd5=6e5488f6b82b890d; fts=1537678069; UM_distinctid=16604c14c8d1df-0a5b0cf28ae475-5701732-1fa400-16604c14c8e91b; rpdid=oqqwwimkqwdoskmxmqopw; BANGUMI_SS_1177_REC=34489; BANGUMI_SS_24588_REC=232473; CURRENT_FNVAL=8; BANGUMI_SS_3271_REC=82961; BANGUMI_SS_24571_REC=231926; stardustvideo=1; sid=d35bnves; SESSDATA=10c41556%2C1540345600%2C7eee939f; bili_jct=bda61d2ce5a96d2f1b67ab23dd4bcd67; LIVE_BUVID=AUTO2515377536013436; buvid3=13D8FDAA-DB92-40DD-A836-CBC83FC438116716infoc; _dfcaptcha=5f7d4556f5c0d31020bf5d9bdab89739; bp_t_offset_152683670=166989062909847236; CNZZDATA2724999=cnzz_eid%3D1723892295-1537674572-https%253A%252F%252Fwww.bilibili.com%252F%26ntime%3D1537759951'
}

GET_BANGUMI_INDEX_HEADERS = {
    'Accept':
    'application/json, text/plain, */*',
    'Accept - Encoding':
    'gzip, deflate, br',
    'Accept-Language':
    'zh-CN,zh;',
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063',
    'Host':
    'bangumi.bilibili.com'
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
    'favorites', 'mid', 'author'
]


UPPER_SUBMIT_ROOT = 'data'
UPPER_SUBMIT_ATTR = [
    'aid', 'videos', 'tid', 'tname', 'copyright', 'pic',
    'title', 'pubdate', 'ctime', 'desc', 'attribute', ['stat', 'view'],
    ['stat', 'reply'], ['stat', 'favorite'], ['stat', 'coin'], ['stat', 'share'],
    ['stat', 'his_rank'], ['stat', 'like'], ['stat', 'dislike'], ['stat', 'danmaku'],
    ['owner', 'mid'], ['owner', 'name'], ['owner', 'face']
]
UPPER_SUBMIT_PART_ROOT = ['data', 'pages']
UPPER_SUBMIT_PART_ATTR = [
    'duration', 'cid', ['dimension', 'width'], ['dimension', 'height']
]

BANGUMI_INDEX_ROOT = ['result', 'data']
BANGUMI_INDEX_ITEM_ATTR = [
    'cover', 'index_show', 'is_finish', 'link', 'media_id',
    ['order', 'follow'], ['order', 'play'], ['order', 'pub_date'],['order', 'renewal_time'],
    ['order', 'score'], 'season_id', 'title'
]

BANGUMI_PLAY_INFO_ROOT = 'result'
BANGUMI_PLAY_INFO_ATTR = [
    'coins', 'danmakus', 'favorites', 'views'
]

'''
----------------------------------global-------------------------------------
'''




'''
----------------------------------class-------------------------------------
'''
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
        unfinished = False
    ):
        self.method = method
        self.link=link
        self.accept_type = accept_type
        self.args=args
        self.unfinished = unfinished


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
        publish_time=       # 发布时间
        int(datetime.datetime.now().timestamp()),  
        created_time=       # 也是一个时间, 不过比较莫名其妙就是了
        int(datetime.datetime.now().timestamp()),   
        description=None,   # 介绍
        attribute=None,     #
        view=0,             # 播放量
        reply=0,            # 回复数
        favorite=0,         # 收藏数
        coin=0,             # 硬币数
        share=0,            # 分享次数
        rank=0,             # 历史最高排名
        like=0,             # 推荐数
        dislike=0,          # 不推荐数
        danmaku=0,          # 弹幕数
        owner_mid=0,        # up主的mid
        owner_name=None,    # up主的用户名
        owner_face=None,    # up主的头像
        duration=[],        # 持续时长
        cid=[],             # 视频的cid
        width=[],           # 视频宽度，单位像素
        height=[]          # 视频高度，单位像素
        
    ):
        self.aid = aid
        self.videos = videos
        self.type_id = type_id
        self.type_name = type_name
        self.copyright = copyright
        self.pic = pic
        self.title = title
        self.publish_time = publish_time
        self.created_time = created_time
        self.description = description
        self.attribute = attribute
        self.view = view
        self.reply = reply
        self.favorite = favorite
        self.coin = coin
        self.share = share
        self.rank = rank
        self.like = like
        self.dislike = like
        self.danmaku = danmaku
        self.owner_mid = owner_mid
        self.owner_name = owner_face
        self.owner_face = owner_face
        self.duration = duration
        self.cid = cid
        self.width = width
        self.height = height


# 弹幕类
class danmaku(object):
    def __init__(
        self,
        cid=0,              # 视频cid
        appear_time=-1,     # 出现时间
        dtype=0,            # 弹幕类型
        font_size=0,        # 字号
        color=None,         # 颜色
        send_time = None,   # 时间戳
        pool = 0,           # 弹幕池
        sender_mid = 0,     # 发送者的加密id
        rowid = 0,          # 行号
        content = ""        # 内容
    ):
        self.cid = cid
        self.appear_time = appear_time
        self.dtype = dtype
        self.font_size = font_size
        self.color = color
        self.send_time = send_time
        self.pool = pool
        self.sender_mid = sender_mid
        self.rowid = rowid
        self.content = content


# 番剧类
class bangumi(object):
    def __init__(
        self,
        cover=None,         # 番剧封面
        index_show=0,       # 番剧分p数
        is_finish=1,        # 是否完结
        link=None,          # 番剧地址
        media_id=0,         # media_id
        follow=0,           # 追番人数（以万为单位）
        play=0,             # 播放量（以万为单位）
        publish_time=       # 开播时间
        int(datetime.datetime.now().timestamp()),
        renewal_time=       # 莫名其妙的时间
        int(datetime.datetime.now().timestamp()),
        score=0,            # 评分
        season_id=0,        # season_id
        title=None,         # 标题
        coins=0,            # 投币
        danmakus=0,         # 弹幕
        favorites=0,        # 追番
        views=0             # 播放量
    ):
        self.cover = cover
        self.index_show = index_show
        self.is_finish = is_finish
        self.link = link
        self.media_id = media_id
        self.follow = follow
        self.play = play
        self.publish_time = publish_time
        self.renewal_time = renewal_time
        self.score = score
        self.season_id = season_id
        self.title = title
        self.coins = coins
        self.danmakus = danmakus
        self.favorites = favorites
        self.views = views

'''
----------------------------------class-------------------------------------
'''

'''
----------------------------------tools-------------------------------------
'''
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
    search_res = re.search("bili_jct=(.*?);", get_attr(GET_UP_INFO_HEADERS, 'Cookie'))
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
    response.encoding = 'utf-8'
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
    
'''
----------------------------------tools-------------------------------------
'''

    
'''
----------------------------------user-------------------------------------
'''
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
        GET_UP_INFO_HEADERS,
        GENERAL_HEADERS,
        GET_UP_INFO_HEADERS
    ]

    try:
        for i in range(0, min(len(urls), len(hs))):
            res.append(download_url(urls[i], headers=hs[i]))
    except:
        return None
    return resource(res)

# 解析资源, res为resource对象
# 因为url下载下来的资源可能需要多个才能集合成一个对象, resource用来包装urls获得的资源
def parse_user_res(res):

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
    return parse_user_res(download_user_urls(get_user_urls(mid, **kwargs)))
'''
----------------------------------user-------------------------------------
'''

'''
----------------------------------submits-------------------------------------
'''
def get_submit_urls(aid, **kwargs):
    res = []
    res.append(url(
        "get",
        GET_UPPER_SUBMIT_DETAIL_URL,
        "json",
        {
            'aid': aid
        }
    ))

    return res


def download_submit_urls(urls, **kwargs):
    res = []
    hs = [
        GET_SUBMIT_DETAIL_HEADERS
    ]

    try:
        for i in range(0, min(len(urls), len(hs))):
            res.append(download_url(urls[i], headers=hs[i]))
    except:
        return resource(res)
    return resource(res)


def parse_submit_res(res):
    info = []
    roots = [
        UPPER_SUBMIT_ROOT
    ]
    attrs = [
        UPPER_SUBMIT_ATTR
    ]
    count = 0
    res_submit = submit(0)
    submit_keys = list(vars(res_submit).keys())

    for i in range(0, len(res.data)):
        info.append(res.data[i])

    try:
        for i in range(0, len(info)):
            data = get_attr(info[i], roots[i])
            for j in range(0, len(attrs[i])):
                res_submit.__dict__[submit_keys[count]] = get_attr(data, attrs[i][j])
                count = count + 1
    except:
        return res_submit

    # 获取视频分p信息
    if len(info) > 0:
        data = get_attr(info[0], UPPER_SUBMIT_PART_ROOT)
        reslist = [
            [],[],[],[]
        ]
        for i in range(0, len(data)):
            for j in range(0, len(UPPER_SUBMIT_PART_ATTR)):
                reslist[j].append(get_attr(data[i], UPPER_SUBMIT_PART_ATTR[j]))
        for i in range(0, 4):
            res_submit.__dict__[submit_keys[count + i]] = reslist[i]

    return res_submit

def get_submit(aid, **kwargs):
    return parse_submit_res(download_submit_urls(get_submit_urls(aid, **kwargs)))
'''
----------------------------------submits-------------------------------------
'''


'''
----------------------------------danmaku-------------------------------------
'''

# kwargs可用的参数:
#   date="2018-10-02"   表示获取历史弹幕， 默认获取当前弹幕
def get_danmaku_urls(cid, **kwargs):
    date = kwargs.pop("date", None)
    return [url(
            "get",
            GET_HISTORY_DANMAKU_URL,
            "text",
            {
                "type":1,
                "date":date,
                "oid":cid
            }
        )] if date else [
            url(
                "get",
                GET_DANMAKU_URL,
                "text",
                {
                    "oid":cid
                }
            )
        ]

def download_danmaku_urls(urls, **kwargs):
    try:
        return resource(
            [
                urls[0].args['oid'],
                download_url(urls[0], headers=GENERAL_HEADERS if "list" in urls[0].link else GET_HISTORY_DANMAKU_HEADERS)
            ]
        )
    except:
        return None

def prase_danmaku_res(res):
    try:
        cid = res.data[0]
        text = res.data[1]
    except:
        return danmaku()

    res_list = []
    soup = BeautifulSoup(text, 'lxml')
    danmakus = soup.find_all('d')
    danmaku_keys = list(vars(danmaku()).keys())

    # 遍历所有弹幕标签
    for item in danmakus:
        dproperty = item.get('p')
        dps = dproperty.split(',')
        danmaku_tmp = danmaku(cid)
        for i in range(1, len(dps)):
            danmaku_tmp.__dict__[danmaku_keys[i]] = dps[i - 1]
        danmaku_tmp.content = item.get_text()
        res_list.append(danmaku_tmp)
    
    return res_list
            
def get_danmaku(cid, **kwargs):
    return prase_danmaku_res(download_danmaku_urls(get_danmaku_urls(cid, **kwargs)))       

'''
----------------------------------danmaku-------------------------------------
'''


'''
----------------------------------reply-------------------------------------
'''



'''
----------------------------------reply-------------------------------------
'''

'''
----------------------------------bangumi-------------------------------------
'''

def get_bangumi_num():
    return get_attr(download_url(
        url(
            "get",
            GET_BANGUMI_INDEX_URL,
            "json",
            {
                "sort":1,
                "order":1,
                "st":1,
                "page":1,
                "pagesize":1,
                "season_type":1
            }
        ),
        headers=GET_BANGUMI_INDEX_HEADERS
    ), ['result', 'page', 'total'])

# kwargs支持的参数:
#   sort: 1 or 0 升序or降序 默认降序
#   order: [0-5]    默认3(按追番人数排序)
#   get_play_info: 是否获取播放信息, 硬币数之类
#   get_play_info会显著降低效率, 因为番剧基本信息可以一次获取多个， 而精确播放信息却是单独分布的. 除非必要， 否则不建议使用get_play_info
#   多线程环境下，建议使用不带get_play_info的get_bangumi_urls配合get_bangumi_play_info使用
def get_bangumi_urls(page, pagesize, **kwargs):
    get_play_info = kwargs.pop('get_play_info', False)
    url_index = url(
        "get",
        GET_BANGUMI_INDEX_URL,
        "json",
        {
            "page": page,
            "pagesize": pagesize,
            "st":1,
            "season_type": 1,
            "sort": kwargs.pop('sort', 0),
            "order": kwargs.pop('order', 3)
        }
    )
    res = []
    res_url = [] if get_play_info else [url_index]
    if get_play_info:
        res.append(download_url(url_index, headers=GET_BANGUMI_INDEX_HEADERS))
        for i in range(0, pagesize):
            res_url.append(
                url(
                    "get",
                    GET_BANGUMI_PLAY_INFO_URL,
                    "json",
                    {
                        "season_id": get_attr(get_attr(res[0], BANGUMI_INDEX_ROOT)[i], 'season_id'),
                        "season_type": 1
                    }
                )
            )
    return res, res_url
    # res = [
    #     url(
    #         "get",
    #         GET_BANGUMI_INDEX_URL,
    #         "json",
    #         {
    #             "page": page,
    #             "pagesize": pagesize,
    #             "st":1,
    #             "season_type": 1,
    #             "sort": kwargs.pop('sort', 0),
    #             "order": kwargs.pop('order', 3)
    #         }
    #     )
    # ]
    # if kwargs.pop('get_play_info', False):
    #     res.append(
    #         url(
    #             "get",
    #             "get_play_info",
    #             "json",
    #             {
    #                 "season_id": None,
    #                 "season_type": 1
    #             },
    #             True
    #         )
    #     )
    # return res


def get_bangumi_paly_info_urls(season_id, **kwargs):
    res_url = []
    res_url.append(
        url(
            "get",
            GET_BANGUMI_PLAY_INFO_URL,
            "json",
            {
                "season_id": season_id,
                "season_type": 1
            }
        )
    )
    return res_url

def download_bangumi_play_info_urls(urls, **kwargs):
    res_list = [download_url(urls[0], headers=GET_BANGUMI_INDEX_HEADERS)]
    return resource(res_list)

def prase_bangumi_play_info(res):
    data = get_attr(res.data[0], BANGUMI_PLAY_INFO_ROOT)
    bangumi_keys = list(vars(bangumi()).keys())

    bangumi_temp = bangumi()
    for j in range(12, 16):
        bangumi_temp.__dict__[bangumi_keys[j]] = get_attr(data, BANGUMI_PLAY_INFO_ATTR[j - 12])
    
    return bangumi_temp


def get_bangumi_play_info(season_id, **kwargs):
    return prase_bangumi_play_info(download_bangumi_play_info_urls(get_bangumi_paly_info_urls(season_id, **kwargs)))
# 历史遗留函数, 不用管
def bangumi_callback(url_list, index, res, **kwargs):
    current = url_list[index]
    if current.unfinished:
        data = get_attr(res[index - 1], BANGUMI_INDEX_ROOT)
        current.link = GET_BANGUMI_PLAY_INFO_URL
        current.args['season_id'] = get_attr(data[0], 'season_id')
        for i in range(1, len(data)):
            url_list.append(
                url(
                    "get",
                    GET_BANGUMI_PLAY_INFO_URL,
                    "json",
                    {
                        "season_id": get_attr(data[i], 'season_id'),
                        "season_type": 1
                    }
                )
            )

def download_bangumi_urls(urls, **kwargs):
    res_list= kwargs.pop('res', [])
    # count = 0
    for i in range(0, len(urls)):
        res_list.append(
            download_url(
                urls[i],
                headers=GET_BANGUMI_INDEX_HEADERS
            )
        )
        # count = count + 1
    
    # for i in range(count, len(urls)):
    #     res_list.append(
    #         download_url(
    #             urls[i], headers=GET_BANGUMI_INDEX_HEADERS
    #         )
    #     )


    return resource(res_list)

def prase_bangumi_res(res):
    res_list = []
    data = get_attr(res.data[0], BANGUMI_INDEX_ROOT)
    bangumi_keys = list(vars(bangumi()).keys())

    for i in range(0, len(data)):
        bangumi_temp = bangumi()
        for j in range(0, len(BANGUMI_INDEX_ITEM_ATTR)):
            bangumi_temp.__dict__[bangumi_keys[j]] = get_attr(data[i], BANGUMI_INDEX_ITEM_ATTR[j])
        res_list.append(bangumi_temp)

    for i in range(1, len(res.data)):
        for j in range(0, len(BANGUMI_PLAY_INFO_ATTR)):
            res_list[i - 1].__dict__[bangumi_keys[len(BANGUMI_INDEX_ITEM_ATTR) + j]] = get_attr(
                get_attr(res.data[i], BANGUMI_PLAY_INFO_ROOT), BANGUMI_PLAY_INFO_ATTR[j]
            )
    
    return res_list

def get_bangumi(page, pagesize, **kwargs):
    res = get_bangumi_urls(page, pagesize, **kwargs)
    return prase_bangumi_res(download_bangumi_urls(res[1], res=res[0]))
    # return prase_bangumi_res(download_bangumi_urls(get_bangumi_urls(page, pagesize, **kwargs), callback=bangumi_callback))

'''
----------------------------------bangumi-------------------------------------
'''

if __name__ == "__main__":
    # rlist = prase_bangumi_res(download_bangumi_urls(get_bangumi_urls(1, 5, get_play_info=True), callback=bangumi_callback))
    # for i in range(0, len(rlist)):
    #     print(vars(rlist[i]))

    s = get_bangumi(1, 20)
    for i in s:
        print(vars(get_bangumi_play_info(i.season_id)))
        
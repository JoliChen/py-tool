# -*- coding: UTF-8 -*-

import base64
import hashlib
import random
import time
from XcHelper.common.WordUtils import JWords

class JThirdPartyNetApi:

    @staticmethod
    def __md5__(src):
        m2 = hashlib.md5()
        m2.update(src.encode("utf8"))
        return m2.hexdigest()

    @classmethod
    def randReq(cls):
        i = random.randint(1, 5)
        if (i == 1) :
            return cls.__rand__dict()
        if (i == 2) :
            return cls.__rand__baidu()
        if (i == 3) :
            return cls.__rand__juhe()
        if (i == 4) :
            return cls.__rand__MapAPI()
        if (i == 5) :
            return cls.__rand__rss()

    @classmethod
    def __rand__baidu(cls):
        i = random.randint(1, 5)
        if (i == 1) :
            return cls.__req__BaiduOCR()
        if (i == 2) :
            return cls.__req__BaiduTodayhistory()
        if (i == 3) :
            return cls.__req__BaiduWeather()
        if (i == 4) :
            return cls.__req__BaiduAstro()
        if (i == 5) :
            return cls.__req__BaiduAqi()

    @classmethod
    def __rand__juhe(cls):
        i = random.randint(1, 5)
        if (i == 1) :
            return cls.__req__JuheJoke()
        if (i == 2) :
            return cls.__req__JuheCharconvert()
        if (i == 3) :
            return cls.__req__JuheChengyu()
        if (i == 4) :
            return cls.__req__JuheXhzd()
        if (i == 5) :
            return cls.__req__JuheCalendar()

    @classmethod
    def __rand__MapAPI(cls):
        i = random.randint(1, 3)
        if (i == 1) :
            return cls.__req__SinaIpLookup()
        if (i == 2) :
            return cls.__req__DituPL()
        if (i == 3) :
            return cls.__req__DituRegeo()

    @classmethod
    def __rand__dict(cls):
        i = random.randint(1, 2)
        if (i == 1) :
            return cls.__req__JinShanCiBa()
        if (i == 2) :
            return cls.__req__GoogleTranslate()

    @classmethod
    def __rand__rss(cls):
        i = random.randint(1, 7)
        if (i == 1) :
            return cls.__req__AppleMusic()
        if (i == 2) :
            return cls.__req__ItunesMusic()
        if (i == 3) :
            return cls.__req__RssBooks()
        if (i == 4) :
            return cls.__req__RssMovies()
        if (i == 5) :
            return cls.__req__RssPodcast()
        if (i == 6) :
            return cls.__req__RssItunesU()
        if (i == 7) :
            return cls.__req__RssMusicVideos()

    # 金山词霸
    @classmethod
    def __req__JinShanCiBa(cls):
        id = random.randint(10000, 99999)
        name = JWords.rand_lowers(6, 20)
        auth = cls.__md5__(str(id) + name).upper()
        return {
            'url':'http://open.iciba.com/ds_open.php',
            'args': {'id':id, 'name':name, 'auth':auth},
            'method':'UBGET'
        }

    # 百度OCR文字识别企业版
    @classmethod
    def __req__BaiduOCR(cls):
        return {
            'url':'http://apis.baidu.com/idl_baidu/baiduocrpay/idlocrpaid',
            'args':{
                'apikey':cls.__md5__(JWords.rand_lowers(1, 32)),
                'fromdevice':random.choice(('iPhone', 'iPad')),
                'clientip':'10.10.10.0',
                'detecttype':'LocateRecognize',
                'imagetype':1,
                'image':base64.encodebytes(JWords.rand_lowers(1, 1000).encode('utf-8'))
            },
            'method':'UBPOST'
        }

    # 百度历史上的今天
    @classmethod
    def __req__BaiduTodayhistory(cls):
        apikey = cls.__md5__(JWords.rand_lowers(1, 32))
        month = random.randint(1, 12)
        day = random.randint(1, 30)
        return {
            'url':'http://apis.baidu.com/netpopo/todayhistory/query',
            'args': {
                'apikey':apikey, 'month':month, 'day':day
            },
            'method':'UBGET'
        }

    # 百度天气预报
    @classmethod
    def __req__BaiduWeather(cls):
        apikey = cls.__md5__(JWords.rand_lowers(1, 32))
        area = random.randint(101010100, 909090900)
        return {
            'url': 'http://apis.baidu.com/tianyiweather/basicforecast/weatherapi',
            'args': {'apikey':apikey, 'area':area},
            'method': 'UBGET'
        }

    # 百度星座运势
    @classmethod
    def __req__BaiduAstro(cls):
        apikey = cls.__md5__(JWords.rand_lowers(1, 32))
        astroid = random.randint(1, 12)
        date = '""'
        return {
            'url': 'http://apis.baidu.com/netpopo/astro/fortune',
            'args': {'apikey':apikey, 'astroid':astroid, 'date':date},
            'method': 'UBGET'
        }

    # 百度城市空气质量指数
    @classmethod
    def __req__BaiduAqi(cls):
        apikey = cls.__md5__(JWords.rand_lowers(1, 32))
        return {
            'url': 'http://apis.baidu.com/netpopo/aqi/city',
            'args': {'apikey':apikey},
            'method': 'UBGET'
        }

    # 聚合笑话大全
    @classmethod
    def __req__JuheJoke(cls):
        key = cls.__md5__(JWords.rand_lowers(1, 32))
        pagesize = random.randint(1, 20)
        page = random.randint(1, pagesize)
        sort = random.choice(('desc', 'asc'))
        ts = time.time()
        return {
            'url': 'http://v.juhe.cn/joke/content/list.php',
            'args': {'key':key,'page':page, 'pagesize':pagesize, 'sort':sort, 'time':time},
            'method': 'UBGET'
        }

    # 聚合简繁字体转换
    @classmethod
    def __req__JuheCharconvert(cls):
        key = cls.__md5__(JWords.rand_lowers(1, 32))
        text = JWords.rand_lowers(1, 64)
        type = random.randint(0, 2)
        return {
            'url': 'http://japi.juhe.cn/charconvert/change.from',
            'args': {'key':key, 'text':text, 'type':type},
            'method': 'UBGET'
        }

    # 聚合成语查询
    @classmethod
    def __req__JuheChengyu(cls):
        key = cls.__md5__(JWords.rand_lowers(1, 32))
        word = JWords.rand_lowers(1, 64)
        dtype = random.choice(('xml', 'json'))
        return {
            'url': 'http://v.juhe.cn/chengyu/query',
            'args': {'key':key, 'word':word, 'dtype':dtype},
            'method': 'UBGET'
        }

    # 聚合新华字典
    @classmethod
    def __req__JuheXhzd(cls):
        key = cls.__md5__(JWords.rand_lowers(1, 32))
        word = JWords.rand_lowers(1, 64)
        dtype = random.choice(('xml', 'json'))
        return {
            'url': 'http://v.juhe.cn/xhzd/query',
            'args': {'key':key, 'word':word, 'dtype':dtype},
            'method': 'UBGET'
        }

    # 聚合万年历
    @classmethod
    def __req__JuheCalendar(cls):
        key = cls.__md5__(JWords.rand_lowers(1, 32))
        date = '%d-%d-%d' % (random.randint(2012, 2020), random.randint(1, 12), random.randint(1, 30))
        return {
            'url': 'http://v.juhe.cn/calendar/day',
            'args': {'key':key, 'date':date},
            'method': 'UBPOST'
        }

    # 谷歌翻译
    @classmethod
    def __req__GoogleTranslate(cls):
        text = ''
        for i in range(random.randint(1, 10)):
            text += JWords.rand_lowers(3, 8) + ' '
        import urllib.parse
        text = urllib.parse.quote(text)
        hl = random.choice(('ko', 'ja', 'de', 'it', 'fr'))
        sl = random.choice(('nl', 'en', 'lt', 'ar', 'fi'))
        tl = random.choice(('ko', 'ja', 'de', 'it', 'fr'))
        ie = 'UTF-8'
        oe = 'UTF-8'
        return {
            'url': 'http://translate.google.cn/translate_a/t',
            'args': {
                'client':'t',
                'text':text,
                'hl':hl,
                'sl':sl,
                'tl':tl,
                'ie':ie,
                'oe':oe,
                'multires':1,
                'otf':1,
                'pc':1,
                'it':'srcd_gms.1378',
                'ssel':4,
                'tsel':6,
                'sc':1
            },
            'method': 'UBGET'
        }

    # 百度翻译
    @classmethod
    def __req__BaiduTranslate(cls):
        text = ''
        for i in range(random.randint(1, 10)):
            text += JWords.rand_lowers(3, 8) + ' '
        hl = random.choice(('ko', 'ja', 'de', 'it', 'fr'))
        sl = random.choice(('nl', 'en', 'lt', 'ar', 'fi'))
        tl = random.choice(('ko', 'ja', 'de', 'it', 'fr'))
        return {
            'url': 'http://fanyi.baidu.com/translate',
            'args': {
                'query':1,
                'keyfrom':'baidu',
                'smartresult':'dict',
                'lang':'auto2%s#%s/%s/%s' % (hl, sl, tl, text)
            },
            'method': 'UBGET'
        }

    # IP地址查询
    @classmethod
    def __req__SinaIpLookup(cls):
        return {
            'url': 'http://int.dpool.sina.com.cn/iplookup/iplookup.php',
            'args': {'format':'json'},
            'method': 'UBGET'
        }

    # 获取用户经纬度
    @classmethod
    def __req__DituPL(cls):
        return {
            'url': 'http://ditu.amap.com/service/pl/pl.json',
            'args': {'rand':time.time()},
            'method': 'UBPOST'
        }

    # 获取用户附近建筑
    @classmethod
    def __req__DituRegeo(cls):
        longitude = random.random() * 360 - 180
        latitude  = random.random() * 180 - 90
        return {
            'url': 'http://ditu.amap.com/service/regeo',
            'args': {'longitude':longitude, 'latitude':latitude},
            'method': 'UBGET'
        }

    # 查询AppleMusic
    @classmethod
    def __req__AppleMusic(cls):
        rageo = random.choice(('us', 'in', 'fr', 'ca', 'ja', 'ko', 'it', 'de'))
        ranks = random.choice(('hot-tracks', 'new-releases', 'top-albums', 'top-songs'))
        count = random.choice((10, 25, 50, 100))
        limit = random.choice(('explicit', 'non-explicit'))
        ftype = random.choice(('json', 'atom', 'rss'))
        return {
            'url': 'https://rss.itunes.apple.com/api/v1/%s/apple-music/%s/all/%d/%s.%s' % (rageo, ranks, count, limit, ftype),
            'args': None,
            'method': 'UBGET'
        }

    # 查询ItunesMusic
    @classmethod
    def __req__ItunesMusic(cls):
        rageo = random.choice(('us', 'in', 'fr', 'ca', 'ja', 'ko', 'it', 'de'))
        ranks = random.choice(('hot-tracks', 'new-music', 'recent-releases', 'top-albums', 'top-songs'))
        count = random.choice((10, 25, 50, 100))
        limit = random.choice(('explicit', 'non-explicit'))
        ftype = random.choice(('json', 'atom', 'rss'))
        return {
            'url': 'https://rss.itunes.apple.com/api/v1/%s/itunes-music/%s/all/%d/%s.%s' % (rageo, ranks, count, limit, ftype),
            'args': None,
            'method': 'UBGET'
        }

    # 查询图书
    @classmethod
    def __req__RssBooks(cls):
        rageo = random.choice(('us', 'in', 'fr', 'ca', 'ja', 'ko', 'it', 'de'))
        ranks = random.choice(('top-free', 'top-paid'))
        count = random.choice((10, 25, 50, 100))
        limit = random.choice(('explicit', 'non-explicit'))
        ftype = random.choice(('json', 'atom', 'rss'))
        return {
            'url': 'https://rss.itunes.apple.com/api/v1/%s/books/%s/all/%d/%s.%s' % (
            rageo, ranks, count, limit, ftype),
            'args': None,
            'method': 'UBGET'
        }

    # 查询电影
    @classmethod
    def __req__RssMovies(cls):
        rageo = random.choice(('us', 'in', 'fr', 'ca', 'ja', 'ko', 'it', 'de'))
        ranks = random.choice(('top-movies'))
        count = random.choice((10, 25, 50, 100))
        limit = random.choice(('explicit', 'non-explicit'))
        ftype = random.choice(('json', 'atom', 'rss'))
        return {
            'url': 'https://rss.itunes.apple.com/api/v1/%s/movies/%s/all/%d/%s.%s' % (
                rageo, ranks, count, limit, ftype),
            'args': None,
            'method': 'UBGET'
        }

    # 查询播客
    @classmethod
    def __req__RssPodcast(cls):
        rageo = random.choice(('us', 'in', 'fr', 'ca', 'ja', 'ko', 'it', 'de'))
        ranks = random.choice(('top-podcasts'))
        count = random.choice((10, 25, 50, 100))
        limit = random.choice(('explicit', 'non-explicit'))
        ftype = random.choice(('json', 'atom', 'rss'))
        return {
            'url': 'https://rss.itunes.apple.com/api/v1/%s/podcasts/%s/all/%d/%s.%s' % (
                rageo, ranks, count, limit, ftype),
            'args': None,
            'method': 'UBGET'
        }

    # 查询课程
    @classmethod
    def __req__RssItunesU(cls):
        rageo = random.choice(('us', 'in', 'fr', 'ca', 'ja', 'ko', 'it', 'de'))
        ranks = random.choice(('top-itunes-u-courses'))
        count = random.choice((10, 25, 50, 100))
        limit = random.choice(('explicit', 'non-explicit'))
        ftype = random.choice(('json', 'atom', 'rss'))
        return {
            'url': 'https://rss.itunes.apple.com/api/v1/%s/itunes-u/%s/all/%d/%s.%s' % (
                rageo, ranks, count, limit, ftype),
            'args': None,
            'method': 'UBGET'
        }

    # 查询课程
    @classmethod
    def __req__RssMusicVideos(cls):
        rageo = random.choice(('us', 'in', 'fr', 'ca', 'ja', 'ko', 'it', 'de'))
        ranks = random.choice(('top-music-videos'))
        count = random.choice((10, 25, 50, 100))
        limit = random.choice(('explicit', 'non-explicit'))
        ftype = random.choice(('json', 'atom', 'rss'))
        return {
            'url': 'https://rss.itunes.apple.com/api/v1/%s/music-videos/%s/all/%d/%s.%s' % (
                rageo, ranks, count, limit, ftype),
            'args': None,
            'method': 'UBGET'
        }
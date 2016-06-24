# -*- coding: UTF-8 -*-

import xml.etree.ElementTree as ET
import timeHelper
import re
import requests
import json
RESPONSE_TEXT_TEMPLATE = '''
<xml>
<ToUserName><![CDATA[{TO_USER}]]></ToUserName>
<FromUserName><![CDATA[{FROM_USER}]]></FromUserName>
<CreateTime>{TIME_STEMP}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[{RESPONSE_CONTENT}]]></Content>
</xml>
'''  

class msgHandler:
    def __init__(self, data):
        self.data = data
        self.dict = self._xmlToDict(self.data)
        if self.dict['MsgType'] == 'event':
            self.worker = eventHandler(self.dict['FromUserName'],self.dict['Event'])
        else:
            self.worker = txtmsgHandler(self.dict['FromUserName'],self.dict['Content'])

    def response(self):
        responseDict = self.responseDict()
        text = self.responseXML(responseDict)
        return text
    
    
    def _xmlToDict(self, xmlText):
        xmlDict = {}
        itemlist = ET.fromstring(xmlText)
        for child in itemlist:
            xmlDict[child.tag] = child.text
        print xmlDict
        return xmlDict
    
    def responseXML(self, dataDict):
        if dataDict:
            text = RESPONSE_TEXT_TEMPLATE 
            for key, value in dataDict.items():
                parameter = '{%s}' % key
                text = text.replace(parameter, value)
            print text
        else:
            text = ''
        return text
    
    def responseDict(self):
        responseDict = {}
        try:
            responseDict['RESPONSE_CONTENT'] = self.worker.response.encode('UTF-8')
            responseDict['TO_USER'] = self.dict['FromUserName']
            responseDict['FROM_USER'] = self.dict['ToUserName']
            responseDict['TIME_STEMP'] = str(timeHelper.unixTimeStamp())
        except:
            pass
        return responseDict
    
    
class eventHandler:
    MSG_WELCOME = u'欢迎您关注我，输入SteamStore的AppID可以查询游戏国区史低价格哦，想了解我，就请发送“帮助”或“？”'
    def __init__(self, user, event):
        if event == 'subscribe':
            self.response = self.MSG_WELCOME


class txtmsgHandler:
    MSG_HELP = u'输入SteamStore的AppID可以查询游戏国区史低价格哦，其他功能仍在开发中'
    MSG_SUCCESS = [u'存储完成', u'我存好了，随时来查哦',u'搞定，收工']

    def __init__(self, user, reqMsg):
        self.req = reqMsg.lower()
        self.response = self.MSG_HELP
        self._handle_req()            

    def _handle_req(self):
        if self.req in ['help', '帮助', '?', u'？']: return
        else:
            url = 'http://steamdb.sinaapp.com/app/'+self.req+'/data.js?v=34'
            r=requests.get(url)
            m=re.search('{[\w\W]*}',r.text)
            if m:
                data=json.loads(m.group(0))
                t = data.get('type')
                if t!= 'na':
                    name = data.get('name',0)
                    cut = data['price_history']['steam']['cut']
                    price = data['price_history']['steam']['cn']
                    if cut == 0:
                        cut =100
                    lowest = int(cut*price*.01)
                    self.response = u'游戏名称:%s\n国区价格:%s\n国区史低折扣:%s%%off ¥%s'%(name,price,cut,lowest)
                else:
                    self.response = u'AppID不存在哦!'  
            else:        
                self.response = u'AppID不存在哦!'    
            return
    def _get_success_response(self):
        import random
        return self.MSG_SUCCESS[random.randint(0,len(self.MSG_SUCCESS)-1)]
    def _get_steam_info(self):
        #url = 'http://steamdb.sinaapp.com/app/'+id+'/data.js?v=34'
        #r=requests.get(url)
        return self.req
        #m=re.search('{[\w\W]*}',r.text)
        #if m:
        #    data=json.loads(m.group(0))
        #    name = data['name']
        #    cut = data['price_history']['steam']['cut']
        #    price = data['price_history']['steam']['cn']
        #    lowest = int(data['price_history']['steam']['cut']*data['price_history']['steam']['cn']*.01)
        #    return name,cut,price,lowest
        #else:
        #    return 0,0,0,0

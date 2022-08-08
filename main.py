import json
import sys
import os
import threading
from time import sleep
import requests
import urllib3
import psutil

#屏蔽安全警告
urllib3.disable_warnings()
#设置线程参数
event = threading.Event()

class AuthToken(object):

    #获取LOL运行端口及密钥信息
    
    def __init__(self):
        self.url = None
        self.host = '127.0.0.1'
        self.agreement = "https://"
        self.port = None
        self.token = None
        self.id = None
        self.auto = 0

    def get_info(self):
        cmds = list[str]
        for process in psutil.process_iter():
            if process.name().removesuffix(".exe") == "LeagueClientUx":
                cmds = process.cmdline()
                break
        
        for cmd in cmds:
            ary = cmd.split("=")
            if ary[0] == "--remoting-auth-token":
                self.token = ary[1]
            if ary[0] == "--app-port":
                self.port = ary[1]

        self.url = self.agreement + "riot:" + str(self.token) + "@" + self.host + ":" + str(self.port)
        return self.url

class App(AuthToken):
    @staticmethod
    def tips():

        #菜单

        print("1.开启自动接受")
        print("2.关闭自动接受")
        print("3.开启自动开始匹配")
        print("4.关闭自动开始匹配")
        print("5.开启秒选")

    def clientInfo(self):

        #获取客户端状态

        while True:
            api = "/lol-gameflow/v1/gameflow-phase"
            text = requests.get(self.url + api, verify=False)
            status = text.json()

            event.wait()
            print(status)
            if status == "ReadyCheck" and self.auto==1:
                app.autoAccept()
                print(1)
            '''
            elif status == "Lobby":
                App.autoStart()
            '''
            sleep(1)

    def myInfo(self):

        #获取用户id

        api = "/lol-summoner/v1/current-summoner"
        info = requests.get(self.url+api, verify=False).json()
        self.id = info['accountId']

    def autoStart(self):

        #开始匹配

        api = "/lol-lobby/v2/lobby/matchmaking/search"
        requests.post(self.url+api, verify=False)

    def autoAccept(self):

        #接受对局

        api = "/lol-lobby-team-builder/v1/ready-check/accept"
        requests.post(self.url+api, verify=False)

    def champSelect(self):
        
        #自动选择英雄

        api = "/lol-champ-select-legacy/v1/session"
        session = requests.get(self.url+api, verify=False).json()

        actions = session['actions'][0]
        myTeam = session['myTeam']
        cellId = None
        actionId = None
        me = {}

        for player in myTeam:
            if player['summonerId'] == self.id:
                cellId = player['cellId']
        
        for action in actions:
            if action['actorCellId'] == cellId:
                actionId = action['id']
                me = action
        
        me['championId'] = 55
        me['completed'] = True

        pickApi = "/lol-champ-select-legacy/v1/session/actions/" + str(actionId)
        requests.patch(self.url+pickApi, verify=False, json=me)

#主程序

if __name__ == '__main__':
    app = App()

    try:
        app.get_info()
        app.myInfo()
    except Exception as res:
        print(f'错误信息：{res}， 退出')
        sys.exit()
    
    client_thread = threading.Thread(target=app.clientInfo, daemon=True)
    client_thread.start()

    event.set()
    app.auto = 1
    os.popen("自动接受已开启")

    '''
    while True:
        app.tips()
        try:
            selection = int(input("请选择："))
        except Exception as res:
            print(f'错误信息：{res}，请选择正确的功能')
            continue

        if selection == 1:
            if app.auto == 0:
                app.auto = 1
                os.popen("自动接受已开启")
        elif selection == 2:
            if app.auto == 1:
                app.auto = 0
                os.popen("自动接受已关闭")
    '''

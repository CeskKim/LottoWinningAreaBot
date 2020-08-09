import json
import LottoInfoGet as LIG
from decimal import Decimal
import os
import requests
from botocore.vendored import requests
from emoji import emojize

TelToken = os.environ['token']
TelUrl = "https://api.telegram.org/bot{}/".format(TelToken)

def Recv_Message(Text, Chat_id):
    LAreaCntRecv = LIG.LottoAreaQuery(Text)

    RecvText = ""
    RecvUrl = ""

    if int(len(LAreaCntRecv)) == 0:
        RecvText = "안녕하세요 로또 명당 정보 봇 입니다. 지역 을 입력해주세요 :stuck_out_tongue_winking_eye:"
        RecvUrl = TelUrl + "sendMessage?text={}&chat_id={}".format(emojize(RecvText, use_aliases=True), Chat_id)
        print(RecvUrl)
        requests.get(RecvUrl)

    else:

        for Ln in range(0, len(LAreaCntRecv)):
            # 텔레그램 엔터 -> %0A
            RecvText = "● 로또 판매점 정보 ●%0A"
            RecvText = RecvText + "판매점:" + " " + LAreaCntRecv[Ln][0] + "%0A주소:" + " " + LAreaCntRecv[Ln][1] + "%0A당첨횟수:" + " " + str(LAreaCntRecv[Ln][2]) + "회"
            RecvText = RecvText + "%0A1등:" + " " + str(LAreaCntRecv[Ln][3]) + "회" + "%0A2등:" + " " + str(LAreaCntRecv[Ln][4]) + "회"
            RecvUrl = TelUrl + "sendMessage?text={}&chat_id={}".format(RecvText, Chat_id)
            requests.get(RecvUrl)


class fakefloat(float):

    def __init__(self, value):
        self._value = value

    def __repr__(self):
        return str(self._value)


def defaultencode(LAreaCntRecv):
    if isinstance(LAreaCntRecv, Decimal):
        return fakefloat(LAreaCntRecv)
    raise TypeError(repr(LAreaCntRecv) + " is not JSON serializable")

def lambda_handler(event, context):
    Telmessage = json.loads(event['body'])
    Chat_id = Telmessage['message']['chat']['id']
    Reply = Telmessage['message']['text']
    # Chat_id = 100
    # Reply = '야후'
    Recv_Message(Reply, Chat_id)

    return {
        'statusCode': 200

    }


import requests as req
import ast
from bs4 import BeautifulSoup
import pymysql
import os

host = os.environ['host']
user = os.environ['user']
passwd = os.environ['passwd']
db = os.environ['db']

Conn = pymysql.connect(host=host, port=3306, user=user, passwd=passwd, db=db, charset='utf8')


def LottoDbQuery():
    try:
        Cur = Conn.cursor()
        SqlCommand = 'SELECT Max(WinNo) FROM tbllottonumber'
        Cur.execute(SqlCommand)
        Row = Cur.fetchone()
        MaxWinNo = Row[0]
    except pymysql.Error as e:
        print(e)
    finally:
        Cur.close()


def LottoDbSave():
    """
        DB 연결 및 DB기준 당첨번호 세팅
        1.DB기준 당첨번호 와 현재 기준 당첨번호와 비교(현재 당첨번호 - DB기준 당첨번호)
          1.1 차이: 0 > -> 해당 차이 만큼 로또 지역판매점을 DB에 삽입
          1.2 차이: 0 < -> 해당 차이가 0보다 작은 경우는 DB에 이미 해당 데이터가 있는 경우로 중지
          1.3 초기 세팅은 동행복권 판매점 조회의 최저 값으로 강제 세팅
    """
    LDBNo = LottoDbQuery()
    LNoUrl = 'https://www.dhlottery.co.kr/gameResult.do?method=byWin'
    LNoParse = BeautifulSoup(req.get(LNoUrl).text, 'html.parser').find('h4').get_text()
    LCurNo = int(LNoParse[0:LNoParse.find('회')])

    if LDBNo == None:
        LDBNo = 892

    if (LCurNo - LDBNo) > 0:
        BegNo = LDBNo
        EndNo = LCurNo
    else:
        return

    LAreaUrl = 'https://dhlottery.co.kr/store.do?method=topStore&pageGubun=L645'

    LAreaData = '''
           method: topStore
           nowPage: 
           rankNo:
           gameNo: 5133
           drwNo:
           schKey: all
           schVal:
           '''.splitlines()

    for No in range(BegNo + 1, EndNo + 1):

        """
            공통 사항
            1.당첨 회차
        """
        WinNo = No

        """
            데이터 입력 순서
            1.당첨번호 데이터 입력 -> 판매점 정보 데이터 입력
        """

        LNumberUrl = 'https://dhlottery.co.kr/gameResult.do?method=byWin&drwNo='
        LNumberDataParse = str(
            BeautifulSoup(req.get(LNumberUrl + str(No)).text, 'html.parser').find('meta', {'id': 'desc'})['content'])
        LNumberDataBegin = LNumberDataParse.find('당첨번호') + 5
        LNumberDataEnd = LNumberDataParse.find('.')
        LNumberDataRst = LNumberDataParse[LNumberDataBegin:LNumberDataEnd].replace('+', ',').split(',')

        if len(LNumberDataRst[0]) > 0:
            WinOne = int(LNumberDataRst[0])
            WinTwo = int(LNumberDataRst[1])
            WinThree = int(LNumberDataRst[2])
            WinFour = int(LNumberDataRst[3])
            WinFive = int(LNumberDataRst[4])
            WinSix = int(LNumberDataRst[5])
            WinBonus = int(LNumberDataRst[6])

            LNumberDbSend = []
            LNumberDbSend = [WinNo, WinOne, WinTwo, WinThree, WinFour, WinFive, WinSix, WinBonus]

            try:
                Cur = Conn.cursor()
                Cur.callproc('_SLottoNumberSave', LNumberDbSend)
            except pymysql.Error as e:
                print(e)
            finally:
                Cur.close()

        DrawNo = 'drwNo :' + str(WinNo)
        LAreaData[5] = DrawNo
        LAreaTrim = ast.literal_eval(
            ''.join(str(list(filter(lambda TrimLine: len(TrimLine.replace(' ', '')) > 1, LAreaData))).split()))

        LAreaSplit = {}
        for SPLine in LAreaTrim:
            Key, Value = SPLine.split(':', 1)
            LAreaSplit[Key] = Value

        """
           시작, 종료페이지 설정
           1.2등 당첨지점 포함 해당 회차의 1등,2등 전체 판매점을 세팅하기 위해 시작, 종료페이지 설정           
        """
        LAreaPageNoParse = BeautifulSoup((req.post(LAreaUrl, data=LAreaSplit)).text, 'html.parser').find_all('div', {'class': 'paginate_common'})
        LAreaPageNoList = [NLine.get_text().split() for NLine in LAreaPageNoParse]

        LAreaBegPageNo = int(min(map(min, LAreaPageNoList)))
        LAreaEndPageNo = int(max(map(max, LAreaPageNoList)))

        for PageNo in range(LAreaBegPageNo, LAreaEndPageNo + 1):
            for SName, SNo in LAreaSplit.items():
                if SName == 'nowPage':
                    LAreaSplit[SName] = PageNo

            LAreaAllParse = BeautifulSoup((req.post(LAreaUrl, data=LAreaSplit)).text, 'html.parser').find_all('div', {'class': 'group_content'})

            """
               판매점 가공 작업
               1.현 HTML 구조 2,3,4페이지 이동 -> 1등 판매점은 동일하게 조회되는 구조
                1.1 페이지가 아닌 나머지 페이지 조회시 1등 판매점은 제외시키는 가공 작업
                  1.1.1 1등 판매점의 최대 번호를 제외한 부분만 삽입 작업 진행                     
            """
            if PageNo == 1:
                LAreaFirstParse = BeautifulSoup((req.post(LAreaUrl, data=LAreaSplit)).text, 'html.parser').find('div', {'class': 'group_content'}).find('tbody')
                LAreaFirstList = []
                for TotLine in LAreaFirstParse.find_all('tr'):
                    LAreaFirstListInfo = []
                    for MidLine in TotLine.find_all('td'):
                        LineInfo = (MidLine.get_text()).strip('\r\n\t')
                        LAreaFirstListInfo.append(LineInfo)
                    LAreaFirstList.append(LAreaFirstListInfo)
                LAreaFirstNoList = [FLine[0] for FLine in LAreaFirstList]
                LAreaFirstEndNo = int(max(map(max, LAreaFirstNoList)))

            LAreaTbody = [Tbody.select_one('tbody') for Tbody in LAreaAllParse]

            LAreaTd = []
            for Tag in LAreaTbody:
                TrTag = Tag.select('tr')
                for TdTag in TrTag:
                    if PageNo == 1:
                        LAreaTd.append(TdTag.text.split())
                    else:
                        if int(TdTag.text.split()[0]) > LAreaFirstEndNo:
                            LAreaTd.append(TdTag.text.split('\n'))

            LottoSend = []
            """
               데이터 삽입 
                1.1페이지를 제외한 나머지 페이지는 구조가 상이 하여 구분하여 삽입 작업
                 1.1 1페이지가 아닌 나머지 페이지 조회시 1등 판매점은 제외시키는 가공 작업(등수, 주소 부분)                                            
            """
            for Value in range(0, len(LAreaTd)):

                LAreaRst = list(filter(None, LAreaTd[Value]))
                Serl = LAreaRst[0]
                StoreName = LAreaRst[1]

                if PageNo == 1:
                    RankNo = 1
                    Addr = ' '.join(LAreaRst[3:6])
                    if Value >= LAreaFirstEndNo:
                        RankNo = 2
                else:
                    RankNo = 2
                    Addr = LAreaRst[2]

                LottoSend = [WinNo, RankNo, Serl, StoreName, Addr]

                try:
                    Cur = Conn.cursor()
                    Cur.callproc('_SLottoAreaSave', LottoSend)
                except pymysql.Error as e:
                    print(e)
                finally:
                    Cur.close()



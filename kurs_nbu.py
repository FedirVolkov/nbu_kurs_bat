'''приклад коду для бат-файла:
@echo off
start cmd.exe /d /k "C:\Users\Home\AppData\Local\Programs\Python\Python38-32\python.exe C:\Users\Home\kurs_nbu.py"
exit /b
'''

from datetime import date
import requests
from decimal import Decimal as dc
today=date.today().strftime("%d.%m.%Y")
base=["USD", "EUR", "RUB", "PLN", "CZK", "GBP", "CAD", "CNY"]
acts = {1: "репорт в файл", 2: "курс валюти", 3: "конвертер в гривню", 4: "конвертер", 5: "репорт на дату"}
coms = [str(k) for k in acts]
d, c = False, False

def try_func(function):
    global d, c
    try:
        if not c and not d:
            print(function())
        elif d and not c:
            print(function(d))
            d = False
        elif c and not d:
            print(function(cur2 = c))
            с = False
        elif d and c:
            print(function(d, c))
            d, c = False, False
        return("Добре!")
    except Exception as exception:
        return(str(type(exception).__name__)+":", exception)
        
def get_cur_dic(date = today):
    url = 'https://bank.gov.ua/ua/markets/exchangerates?date='+date+'&period=daily'
    try:
        nbu_req = requests.get(url)
        ver = "Verified"
    except:
        nbu_req = requests.get(url, verify=False)
        ver = "Not verified"
    nbu_list=nbu_req.text.split("\n")
    cur_dic={"UAH":["Українська гривня", dc(1)]}
    for i, line in enumerate(nbu_list):
        if "на дату" in line:
            day=line.strip()[63:73]+"\n"
        if '="Код літерний' in line:
            list_cur=[nbu_list[i+j].strip() for j in range(7)]
            cur_dic[list_cur[0][30:33]]=[" ".join(list_cur[4].split()[:-1]), \
                                         dc(list_cur[6][32:list_cur[6].find("</td>")].replace(",", ".")) / \
                                         int(list_cur[1][42:list_cur[1].find("</td>")])]
    nbu_req.close()
    return ver, day, cur_dic

def daily_report(date = today):
    ver, day, cur_dic = get_cur_dic(date)
    daily_report=[ver, day] + [cur+" "+str(cur_dic[cur][1]) for cur in base]
    print(*daily_report, sep="\n")

def report_in_file(date = today):
    ver, day, cur_dic = get_cur_dic(date)
    text = ver + "\n" + day
    for i, k in cur_dic.items():
        if i in base:
            text+="\n"+i+" "+str(k[1])
    rates=open("rates.txt", "a")
    rates.write(text+"\n\n")
    rates.close()
    print(ver, day)
    return("Репорт збережено в rates.txt.")
    
def get_kurs(date = today):
    ver, day, cur_dic = get_cur_dic(date)
    cur = input("Валюта, Enter - повний список: ").upper()
    while cur not in cur_dic or cur == "":
        if cur:
            print("Валюти"+cur+"немає.")
        else:
            print(*cur_dic)
        cur = input("Валюта, Enter - повний список, exit - вихід: ").upper()
        if cur in "EXIT":
            return "\n"
    else:
        return(str(cur_dic[cur][1])+" гривень за один "+cur_dic[cur][0]+".")
        
def convert_cur(date = today, cur2 = "UAH"):
    ver, day, cur_dic = get_cur_dic(date)
    print("З валюти?")
    msg_c = ", ".join([str(i)+" - "+el for i, el in enumerate(base)])
    cn = input("l - повний список валют, Enter - короткий список: ").upper()
    if cn == "l":
        print(*cur_dic)
        cn = input("Валюта:").upper()
        if cn == "":
            cn = "USD"
    elif cn == "":
        print(msg_c)
        cn = input("Валюта:").upper()
        if cn == "":
            cn = "USD"
    cur = (base[int(cn)] if cn.isdigit() else cn)
    if cur not in cur_dic:
        return "Валюти "+cur+" немає."
    print(cur)
    if cur2 != "UAH":
        print("В яку валюту?")
        cn2 = input("l - повний список валют, Enter - короткий список: ").upper()
        if cn2 == "l":
            print(*cur_dic)
            cn2 = input("Валюта:").upper()
            if cn2 == "":
                cn2 = "UAH"
        elif cn2 == "":
            print(msg_c)
            cn2 = input("Валюта:").upper()
            if cn2 == "":
                cn2 = "UAH"
        cur2 = (base[int(cn2)] if cn2.isdigit() else cn2)
    if cur2 not in cur_dic:
        return "Валюти "+cur+" немає."
    print(cur2)
    while True:
        try:
            x = input("Сума, через крапку, Enter - 100: ")
            if x == "":
                x = 100
            x = float(x)
        except ValueError:
            continue
        break
    result = float((cur_dic[cur][1]*dc(x))/cur_dic[cur2][1])
    print(ver, day)
    return(str(x)+" "+cur+" = "+str(round(result, 2))+" "+cur2)

def response_to_com(num):
    global d, c
    if num not in range(1,6):
        return None
    else:
        msg_res = "На дату? Формат - дд.мм.рррр. Enter - зараз: "
        if num == 1:
            print(try_func(report_in_file))
        elif num == 2:
            d = input(msg_res)
            print(try_func(get_kurs))
        elif num == 3:
            d = input(msg_res)
            print(try_func(convert_cur))
        elif num == 4:
            d = input(msg_res)
            c = True
            print(try_func(convert_cur))
        elif num == 5:
            d = input(msg_res)
            print(try_func(daily_report))
            
            
act = input("Enter - курс валют зараз, 0 - список команд: ")
if act == "":
    daily_report()
    act = True
elif act in coms:
    response_to_com(int(act))
elif act == "0":
    print(*(f"{a} - {b}" for a, b in acts.items()))

while act:
    act = input("Щось ще? 0 - список команд, Enter - завершення: ")
    while act == "0":
        print(*(f"{a} - {b}" for a, b in acts.items()))
        act = input("Enter - завершення: ")
    if act in coms:
        response_to_com(int(act))
    else:
        break
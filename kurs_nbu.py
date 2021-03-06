from datetime import datetime
import requests
from decimal import Decimal as dc
today = datetime.today().strftime("%d.%m.%Y")
base = ["USD", "EUR", "RUB", "PLN", "CZK", "GBP", "CAD", "CNY"]
acts = {"0": "список команд", "1": "репорт в файл", "2": "курс валюти", \
"3": "конвертер в гривню", "4": "конвертер", "5": "репорт на дату", \
"6": "повний репорт", "7": "дивитись репорти", "Enter": "завершення"}
help = ", ".join(f"{k} - {v}" for k, v in acts.items())

def try_func(function, arg1 = False, arg2 = False):
    arg1 = today if not arg1 else arg1
    try:
        if arg2:
            print(function(arg1, arg2))
        else:
            print(function(arg1))
        return "Добре!"
    except Exception as exception:
        return "try_func report: " + "\nError name: " \
        + str(type(exception).__name__)+"\nException: " + str(exception)
        
def get_cur_dic(date = today):
    url = 'https://bank.gov.ua/ua/markets/exchangerates?date=' + date + '&period=daily'
    try:
        nbu_req = requests.get(url)
        ver = "Verified"
    except:
        nbu_req = requests.get(url, verify = False)
        ver = "Not verified"
    nbu_list=nbu_req.text.split("\n")
    cur_dic={"UAH":["Українська гривня", dc(1)]}
    for i, line in enumerate(nbu_list):
        if "на дату" in line:
            day = line.strip()[63:73]+"\n"
        if '="Код літерний' in line:
            list_cur = [nbu_list[i+j].strip() for j in range(7)]
            cur_dic[list_cur[0][30:33]] = [" ".join(list_cur[4].split()[:-1]), \
                                         dc(list_cur[6][32:list_cur[6].find("</td>")].replace(",", ".")) / \
                                         int(list_cur[1][42:list_cur[1].find("</td>")])]
    nbu_req.close()
    return ver, day, cur_dic

def daily_report(date = today, full = False):
    ver, day, cur_dic = get_cur_dic(date)
    if full:
        daily_report = [ver, day] + \
        [key + " " + val[0] + " " + str(val[1]) for key, val in cur_dic.items()]
    else:
        daily_report = [ver, day] + \
        [cur + " " + str(cur_dic[cur][1]) for cur in base]
    return "\n".join(daily_report)
    
def report_in_file(date = today):
    ver, day, cur_dic = get_cur_dic(date)
    text = ver + "\n" + day
    for i, k in cur_dic.items():
        if i in base:
            text += "\n" + i + " " + str(k[1])
    rates = open("rates.txt", "a")
    rates.write(text + "\n\n")
    rates.close()
    print(ver, day)
    return "Репорт збережено в rates.txt."

def read_rates(date):
    rates = open("rates.txt", "r")
    text = rates.read()
    rates.close()
    format_read = input("d - на дату, Enter - останнi репорти: ")
    if format_read:
        while True:
            try:
                date_read = input("Дата, формат - дд.мм.рррр, Enter - зараз: ")
                if date_read == "":
                    date_text = date
                    break
                date_text = datetime.strptime(date_read, "%d.%m.%Y").date().strftime("%d.%m.%Y")
                if date_text not in text:
                    print("Такої дати немає!")
                    continue
            except ValueError:
                print("Невiрне значення!")
                continue
            break
        start = text.find(date_text) - 9
        end = text.find("Verified", start + 1) - 2
        return text[start:end]
    else:
        while True:
            try:
                n = input("Скiльки останнiх репортiв вiдобразити? (Enter - 2, 0 - всi): ")
                n = int(n) if n else 2
            except ValueError:
                print("Невiрне значення!")
                continue
            break
        rates = open("rates.txt", "r")
        rates_list= rates.readlines()
        rates.close()
        return "".join(rates_list[-(n*12):])
    
def get_kurs(date = today):
    ver, day, cur_dic = get_cur_dic(date)
    cur = input("Валюта, Enter - повний список: ").upper()
    while (cur not in cur_dic) or cur == "":
        if cur:
            print("Валюти " + cur + " немає.")
        else:
            for key, val in cur_dic.items():
                print(key + " " + val[0])
        cur = input("Валюта, Enter - повний список, exit - вихiд: ").upper()
        if cur.startswith("EX"):
            return "\n"
    return str(cur_dic[cur][1]) + " гривень за одиницю валюти " + cur_dic[cur][0] + "."
        
def convert_cur(date = today, cur2 = "UAH"):
    ver, day, cur_dic = get_cur_dic(date)
    base_codes = ", ".join([str(i) + " - " + el for i, el in enumerate(base)])
    full_list = [key + " " + val[0] for key, val in cur_dic.items()]
    
    def get_cur(n):
        msg = f"Валюта {n} (m - повний список валют, s - короткий, Enter - за умовчанням): "
        cn = input(msg).upper()
        while cn == "M" or cn == "S":
            if cn == "M":
                print(*full_list, sep="\n")
            elif cn == "S":
                print(base_codes)
            cn = input(msg).upper()
        if cn == "" and n == 1:
            cn = "USD"
        elif cn == "" and n == 2:
            cn = "UAH"
        if cn.isdigit():
            if int(cn) in range(len(base)):
                cn = base[int(cn)]
        return cn
        
    print("З валюти?")
    while True:
        cur1 = get_cur(1)
        if cur1 not in cur_dic: print(f"Валюти {cur1} немає.")
        else: break
    print(cur1, cur_dic[cur1][0])
    if cur2 != "UAH":
        print("В яку валюту?")
        while True:
            cur2 = get_cur(2)
            if cur2 not in cur_dic: print(f"Валюти {cur2} немає.")
            else: break
    print(cur2, cur_dic[cur2][0])
    while True:
        try:
            x = input("Сума, через крапку, Enter - 100: ")
            if x == "":
                x = 100
            x = float(x)
        except ValueError:
            continue
        break
    result = float((cur_dic[cur1][1] * dc(x)) / cur_dic[cur2][1])
    print(ver, day)
    return str(x) + " " + cur1 + " = " + str(round(result, 2)) + " " + cur2

def response_to_com(com):
    if com == "0":
        print(help)
    elif com == "1":
        print(try_func(report_in_file))
    elif com in "23456":
        date = input("На дату? Формат - дд.мм.рррр. Enter - зараз: ")
        if com == "2":
            print(try_func(get_kurs, date))
        elif com == "3":
            print(try_func(convert_cur, date))
        elif com == "4":
            print(try_func(convert_cur, date, True))
        elif com == "5":
            print(try_func(daily_report, date))
        elif com == "6":
            print(try_func(daily_report, date, True))
    elif com == "7":
        print(try_func(read_rates))
    elif com == "Enter":
        print("Натиснути на Enter, а не ввести це слово!")
    else:
        print("Не знаю, що робити.")
            
            
act = input("Команда, Enter - курс валют зараз: ")
if act == "":
    print(daily_report())
elif act in acts:
    response_to_com(act)
else:
    print(help)

while True:
    act = input("Щось ще? 0 - список команд: ")
    if act in acts:
        response_to_com(act)
    elif act == "":
        break
    else:
        print("Enter - завершення")

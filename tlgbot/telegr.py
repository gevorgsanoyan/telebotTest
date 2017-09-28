import datetime
import requests
import datetime
import sqlite3
import os
import time
import json
import requests
import time
import telebot
from client.ACRA_Web_Inquire import getACRA
from client.ACRA_Web_Inquire import getACRANew
from client.ACRA_Update import update_ACRA
from client.ACRA_PDF_Report import pdf_gen
import sqlite3
from telebot import types

url="http://t.me/SEFInternational_bot"
name="SEFInternational"
username="SEFInternational_bot"


TOKEN = "xxxxxxxxxxxxxx"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

list_items = []
list_items.append("Կատարել ԱՔՌԱ մոնիթորինգ հարցում")
list_items.append("Ստանալ վերջին ԱՔՌԱ մոնիթորինգ հարցումը")
list_items.append("Նոր հայտի ԱՔՌԱ հարցում")


newclientDic = {}

class newClient:
    def __init__(self, socN):
        self.socN = socN
        self.fname = None
        self.lname = None
        self.dob = None



def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js

def get_updates():
    url = URL + "getUpdates"
    js = get_json_from_url(url)
    print(js)
    return js

def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)

def get_last_chat_id(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    #text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return chat_id

def send_message(text, chat_id):
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)

def get_client_info(soc):
    conn = sqlite3.connect(os.path.join(BASE_DIR, "db.sqlite3"))
    curs = conn.cursor()
    firstname = "Անուն"
    lastname = "Ազգանուն"
    try:
        client = list(curs.execute("SELECT id, name FROM client_client WHERE trim(soc) = " + soc))
    except:
        client = list(curs.execute("SELECT id, name FROM client_client WHERE soc = 11111"))

    if len(client) > 0:
        firstname = str(client[0][1])

    return (firstname, lastname)

def getACRA_Pdf(soc):
    pdfDir = BASE_DIR + "/media/acrapdfs/"
    fname = soc + ".pdf"
    fname = pdfDir + "/" + fname
    try:
        f = open(fname, 'rb')
    except:
        f = None
    return f


def acraLogInput(tuserId, aType, soc):
    conn = sqlite3.connect(os.path.join(BASE_DIR, "db.sqlite3"))
    curs = conn.cursor()
    sqlStm = "INSERT INTO client_acra_log (type, date, soc, user_id) VALUES('"+ aType + "', datetime() ,'" + soc + "', " + str(tuserId)  +")"
    curs.execute(sqlStm)
    conn.commit()

bot = telebot.TeleBot(TOKEN)
@bot.message_handler(commands=['acra', 'start'])
def acra(message):
    conn = sqlite3.connect(os.path.join(BASE_DIR, "db.sqlite3"))
    curs = conn.cursor()

    u = list(curs.execute("SELECT user_id FROM staff_profile WHERE postal_code = " + str(message.from_user.id)))

    if len(u) > 0:
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)

        for item in list_items:
            markup.add(item)
        msg = bot.reply_to(message, "Ընտրեք գործողության տեսակը", reply_markup=markup)
        bot.register_next_step_handler(msg, acraCommandeResponse)
    else:
        bot.send_message(message.chat.id, "Դուք չունեք իրավասություն նման գործողություն իրականացնելու համար:")
        # bot.send_message(message.chat.id, "Խնդրում ենք սպասել համակարգի ադմինիստրատորի կողմից իրավասության հաստատմանը:")
        bot.send_message(message.chat.id, "Խնդրում ենք կապվել համակարգի ադմինիստրատորին՝ 077799763; 093766460 ")
        adm = list(curs.execute("SELECT postal_code FROM staff_profile WHERE first_name_arm = " + "'admin'" )) # Sending message to admin, that someone new with used acura service
        bot.send_message(adm[0][0], str(message.chat.id) + " նշված օգտատերը ցանկանում է օգտվել ԱՔՌԱ հարցումների ծառայությունից Telegram messenger-ի միջոցով:")


def acraCommandeResponse(message):
    if message.text == list_items[0]:
        msg = bot.send_message(message.chat.id, "Մուտքագրեք սոց.քարտի համարը ԱՔՌԱ հարցում կատարելու համար")
        bot.register_next_step_handler(msg, acraMonStep)

    if message.text == list_items[1]:
        msg = bot.send_message(message.chat.id, "Մուտքագրեք սոց.քարտի համարը վերջին հարցման արդյունքները ստանալու համար")
        bot.register_next_step_handler(msg, acraLastReport)

    if message.text == list_items[2]:
        msg = bot.send_message(message.chat.id, "Մուտքագրեք սոց.քարտի համարը նոր հաճախորդի ԱՔՌԱ հարցում կատարելու համար")
        bot.register_next_step_handler(msg, newclientAcra)


def acraMonStep(message):
    socN = message.text
    fname, lname = get_client_info(socN)
    acraLogInput(message.chat.id,"Monitoring", socN)
    bot.send_message(message.chat.id, "Կատարվում է ԱՔՌԱ հարցում " + fname + ", սոց.քարտի համար - " + socN + "-ի համար:")
    bot.send_message(message.chat.id, "Խնդրում ենք սպասել...")
    if fname != "Անուն":
        acraT = getACRA(fname, lname, socN)
    else:
        acraT = "Error"
    astatus = acraT[1:3]
    if astatus == "OK":
        bot.send_message(message.chat.id, "Հարցումը կատարվեց բարեհաջող:")
        update_ACRA(socN)

        bot.send_message(message.chat.id, "Խնդրում եմ սպասել: Ֆայլը կցվում է...")
        pdf_gen(str(socN))
        f = getACRA_Pdf(socN)

        if f != None:
            bot.send_document(message.chat.id, f)
        else:
            bot.send_message(message.chat.id, "Տեղի է ունեցել խափանում: Խնդրում ենք կրկին փորձել:")
    else:
        bot.send_message(message.chat.id, "Հարցման սխալ: Խնդրում ենք կրկին փորձել:")

    acra(message)


def acraLastReport(message):
    socN = message.text
    acraLogInput(message.chat.id, "ACRA last report", socN)
    try:
        bot.send_message(message.chat.id, "Խնդրում եմ սպասել: Ֆայլը կցվում է...")
        pdf_gen(str(socN))
        f = getACRA_Pdf(socN)
        bot.send_document(message.chat.id, f)
    except Exception as e:
        bot.send_message(message.chat.id, "Տվյալների անճշտության պատճառով տեղի է ունեցել խափանում: Խնդրում ենք կրկին փորձել:")

    acra(message)


def newclientAcra(message):
    chat_id = message.chat.id
    mtxt = message.text
    nc = newClient(mtxt)
    newclientDic[chat_id] = nc
    acraLogInput(message.chat.id, "New client monitoring", nc.socN)
    bot.send_message(message.chat.id, "Մուտքագրվել է հետևյալ սոց.քարտի համարը` " + message.text)
    tfname, tlname = get_client_info(nc.socN)
    if tfname != "Անուն":
        nc.fname = tfname
        nc.lname = tlname
        msg = bot.send_message(message.chat.id, "Մուտքագրված սոց.քարտը համապատասխանում է հետևյալ հաճախորդին` " + tfname)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add("Հաստատել", "Մուտքագրել նորից")
        msg = bot.reply_to(message, "Հաստատեք մուտքագրված տվյալները", reply_markup=markup)
        bot.register_next_step_handler(msg, newclientInputAppruve)
    else:
        msg = bot.send_message(message.chat.id, "Մուտքագրեք նոր հաճախորդի անունը")
        bot.register_next_step_handler(msg, newclientNameInput)


def newclientNameInput(message):
    chat_id = message.chat.id
    mtxt = message.text
    nc = newclientDic[chat_id]
    nc.fname = mtxt
    msg = bot.send_message(message.chat.id, "Մուտքագրեք նոր հաճախորդի ազգանունը")
    bot.register_next_step_handler(msg, newclientLastNameInput)

def newclientLastNameInput(message):
    chat_id = message.chat.id
    mtxt = message.text
    nc = newclientDic[chat_id]
    nc.lname = mtxt
    msg = bot.send_message(message.chat.id, "Մուտքագրված հաճախորդի տվյալներն են՝ " + nc.fname + " " + nc.lname + ", սոց.քարտի համար - " + nc.socN)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add("Հաստատել", "Մուտքագրել նորից")
    msg = bot.reply_to(message, "Հաստատեք մուտքագրված տվյալները", reply_markup=markup)
    bot.register_next_step_handler(msg, newclientInputAppruve)


def newclientInputAppruve(message):
    chat_id = message.chat.id
    nc = newclientDic[chat_id]
    if message.text == "Մուտքագրել նորից":
        msg = bot.send_message(message.chat.id, "Մուտքագրեք սոց.քարտի համարը նոր հաճախորդի ԱՔՌԱ հարցում կատարելու համար")
        bot.register_next_step_handler(msg, newclientAcra)
    if message.text == "Հաստատել":
        msg = bot.send_message(message.chat.id, "Ստուգվում են տվյալները ԱՔՌԱ հարցում կատարելուց առաջ՝ հետևյալ հաճախորդի " + nc.fname + " " + nc.lname + ", սոց.քարտ " + nc.socN + "-ի համար:")
        try:
            tfname, tlname = get_client_info(nc.socN)
            if tfname == "Անուն":
                cFullName = nc.fname + " " + nc.lname
                conn = sqlite3.connect(os.path.join(BASE_DIR, "db.sqlite3"))
                curs = conn.cursor()
                sqlStm = "INSERT INTO client_client(client_id_as, name, soc) VALUES('-123456' ,'" + cFullName + "', '" + nc.socN + "')"
                curs.execute(sqlStm)
                conn.commit()
                # print(r)

            bot.send_message(message.chat.id, "Խնդրում ենք սպասել...")

            acraT = getACRANew(nc.fname, nc.lname, nc.socN, str(chat_id))
            print(acraT)
            astatus = acraT[1:3]

            if astatus == "OK":
                bot.send_message(message.chat.id, "Հարցումը կատարվեց բարեհաջող:")
                bot.send_message(message.chat.id, "Խնդրում եմ սպասել: Ֆայլը կցվում է...")
                print('test0')
                print(str(int(nc.socN)))
                print('test')
                pdf_gen(str(int(nc.socN)))


                print('test2')
                f = getACRA_Pdf(str(nc.socN))
                print('test3')
                update_ACRA(str(nc.socN))
                print('test4')
                if f != None:
                    bot.send_document(message.chat.id, f)
                else:
                    bot.send_message(message.chat.id, "Տեղի է ունեցել խափանում: Խնդրում ենք կրկին փորձել:")
            else:
                bot.send_message(message.chat.id, "Տեղի է ունեցել հարցման խափանում: Խնդրում ենք կրկին փորձել:")
                acra(message)
        except Exception as dbe:
            bot.send_message(message.chat.id, "Տեղի է ունեցել համակարգային խափանում: Խնդրում եմ, կրկին փորձել:")
            print(dbe)
            acra(message)






if __name__ == '__main__':
    print("Bot Running")
    bot.polling(none_stop=True)

# This is a simple echo tb using the decorator mechanism.
# It echoes any incoming text messages.

import telebot
import urllib3
import datetime
import os
import urllib
import xml.sax.saxutils as saxutils
import re
from telebot import util
from timezonefinder import TimezoneFinder
import pytz
import datetime
import configparser
import DB
from DB import ConfigSectionMap
from google.cloud import translate

#import BaseHTTPServer
from cgi import parse_header, parse_multipart
from sys import version as python_version

if python_version.startswith('3'):
    from urllib.parse import parse_qs
    from http.server import BaseHTTPRequestHandler
    from http.server import HTTPServer
else:
    from urlparse import parse_qs
    from BaseHTTPServer import BaseHTTPRequestHandler
    from BaseHTTPServer import HTTPServer

import ssl
import logging
import json
import requests
from telebot import types
import io
import cgi
from pprint import pprint
from sqlalchemy import create_engine, exists
from sqlalchemy.orm import relationship, sessionmaker
import pycountry
import memcache

urllib3.disable_warnings()

cfg = configparser.ConfigParser()
cfg.read("config.cfg")
mysql_cfg = ConfigSectionMap("mysql")
telegram_cfg = ConfigSectionMap("telegram")
apps_cfg = ConfigSectionMap("apps")

connection_str = 'mysql://'+mysql_cfg['user']+':'+mysql_cfg['password']+'@'+mysql_cfg['host']+':'+mysql_cfg['port']+'/'+mysql_cfg['db']
engine = create_engine(connection_str,echo=False)
Session = sessionmaker(bind=engine)
session = Session()
client = translate.Client()
list_language = client.get_languages()
memc = memcache.Client(['127.0.0.1:11211'], debug=1)

#API_TOKEN = '164293029:AAEUp2f6ORf0rwZaeFR2lDtKPVteWVcM2xw'
API_TOKEN = telegram_cfg['token']

WEBHOOK_HOST = apps_cfg['webhook_host'] 
WEBHOOK_PORT = int(apps_cfg['webhook_port'])  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = apps_cfg['webhook_listen']   # In some VPS you may need to put here the IP addr

WEBHOOK_SSL_CERT = apps_cfg['webhook_ssl_cert']   # Path to the ssl certificate
WEBHOOK_SSL_PRIV = apps_cfg['webhook_ssl_priv']   # Path to the ssl private key

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (API_TOKEN)

command = ['host','whois','dig','ping','traceroute','curl','fail2ban-client','telnet']
cmd_custom = ['ssl','googler']

tf = TimezoneFinder()

def do_reg(self,arg1,arg2):
    return str(os.popen(arg1+ ' ' + arg2))

def do_ssl(self,arg):
    return 'curl --insecure -servername %s -v https://%s 2>&1 | awk "BEGIN { cert=0 } /^\* Server certificate:/ { cert=1 } /^\*/ { if (cert) print }"'%(arg,arg)

def do_googler(self,arg):
    a = ""
    cmd = 'googler --json '+ arg
    print(cmd)
    l = json.load(os.popen(cmd))
    c = 0
    print (l)
    for i in l:
        c = c+1
        a = a + str(c).rjust(3) + '. ' + str(i['title']) + "\n" + " ".rjust(3) + '  ' + str(i['url']) + "\n"
        print (l)
    print(a)
    return a

cmdlist = {
'ssl' : do_ssl,
'googler' : do_googler,
}


logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

tb = telebot.TeleBot(API_TOKEN)

# WebhookHandler, process webhook calls
class WebhookHandler(BaseHTTPRequestHandler):
    server_version = "WebhookHandler/1.0"

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        if self.path == WEBHOOK_URL_PATH and \
           'content-type' in self.headers and \
           'content-length' in self.headers and \
           self.headers['content-type'] == 'application/json':
#            json_string = self.rfile.read(int(self.headers['content-length']))
            length = int(self.headers['content-length'])
            a = parse_qs(
                self.rfile.read(length), keep_blank_values=1)
#            aa = list(a)
#            aa = aa[0]
#            json_string = aa.split('b\'')[1].strip('\'').strip('\n')
            aa = list(a)
            json_string = str(aa[0],'utf-8')
        
  #          print("json_string: "+str(json_string))
   #         pprint(json_string)
            self.send_response(200)
            self.end_headers()

            update = telebot.types.Update.de_json(json_string)
            tb.process_new_messages([update.message])
        else:
            self.send_error(403)
            self.end_headers()


# Handle '/start' and '/help'
@tb.message_handler(commands=['help', 'start'])
def send_welcome(message):
    m = message
    if not session.query(exists().where(DB.Profile.chat_id == m.chat.id)).scalar():
        p= DB.Profile()
        p.chat_id = m.chat.id
        p.user_id = m.from_user.id
        p.username = m.from_user.username
        p.first_name = m.from_user.first_name
        p.last_name = m.from_user.last_name
        p.language_code = m.from_user.language_code
        session.add(p)
        session.commit()
        txt = "Hi " + p.first_name + ". This is the first time you chat me, May I know your email address?"
        tb.reply_to(m,txt)       
    else:
        p = session.query(DB.Profile).filter_by(chat_id=m.chat.id).first()
        txt = "Welcome back "+p.first_name+", How can I help you?"
        tb.reply_to(m,txt)

@tb.message_handler(commands=['xlsrk1'])
def pdfrk(m):
    try:
      tt = m.text.split('xlsrk1 ')[1]
    except:
      tt = '18'
    if tt:
        tt1 = tt.split('#')
        print(str(tt1))
        print(len(tt1))
        if (len(tt1) == 3):
            norek = tt1[0]
            tawal = tt1[1]
            takhir = tt1[2]
            tawal1 = tawal.replace('/','-')
            takhir1 = takhir.replace('/','-')
        else:
            print('paramater kurang/lebih')
    url = 'wget -O /home/wafa/rktsijyp/rk_'+norek+'_'+tawal1+'_'+takhir1+'.xls "http://3.0.0.163/ReportServer/Pages/ReportViewer.aspx?%2fREKENING_KORAN%2fDD_ONLINE_V2&NOREK_VARCHAR='+norek+'&TANGGAL_AWAL_DATETIME='+tawal+'&TANGGAL_AKHIR_DATETIME='+takhir+'&rc:Schema=False&rs:Format=EXCEL"';
    print(url)
    os.system(url)
    photo = open('/home/wafa/rktsijyp/rk_'+norek+'_'+tawal1+'_'+takhir1+'.xls', 'rb')
    tb.send_document(m.chat.id, photo)

@tb.message_handler(commands=['xlsrk'])
def xlsrk(m):
    try:
      tt = m.text.split('xlsrk ')[1]
    except:
      tt = '18'
    if tt:
        tt1 = tt.split('#')
        print(str(tt1))
        print(len(tt1))
        if (len(tt1) == 3):
            norek = tt1[0]
            tawal = tt1[1]
            takhir = tt1[2]
            tawal1 = tawal.replace('/','-')
            takhir1 = takhir.replace('/','-')
        else:
            print('paramater kurang/lebih')
    url = 'wget -O /home/wafa/rktsijyp/rk_'+norek+'_'+tawal1+'_'+takhir1+'.xls "http://172.18.41.72/ReportServer/Pages/ReportViewer.aspx?%2fREKENING_KORAN%2fDD_ONLINE_BRIVA&NOREK_VARCHAR='+norek+'&TANGGAL_AWAL_DATETIME='+tawal+'&TANGGAL_AKHIR_DATETIME='+takhir+'&rc:Schema=False&rs:Format=EXCEL"';
    print(url)
    os.system(url)
    photo = open('/home/wafa/rktsijyp/rk_'+norek+'_'+tawal1+'_'+takhir1+'.xls', 'rb')
    tb.send_document(m.chat.id, photo)


@tb.message_handler(commands=['tid'])
def tid(m):
    #if m.text == '/tid'
    #  tt = ''
    #else
    try:
      tt = m.text.split()[1]
    except:
      tt = ''

    page = urllib.urlopen('http://131.103.5.214/atm/tid.php?cmd=tid&tid='+tt)
    tb.send_message(m.chat.id, page.read())

@tb.message_handler(commands=['go'])
def go(m):
    #if m.text == '/tid'
    #  tt = ''
    #else
    try:
      tt = m.text.split()[1]
    except:
      tt = ''

    page = urllib.urlopen('http://172.18.65.42/simonpots/class/way4.php?cmd=go&tid='+tt)
    tb.send_message(m.chat.id, page.read())

@tb.message_handler(commands=['sc'])
def sc(m):
    #if m.text == '/tid'
    #  tt = ''
    #else
    try:
      tt = m.text.split()[1]
    except:
      tt = ''

    page = urllib.urlopen('http://172.18.65.42/simonpots/class/way4.php?cmd=sc&tid='+tt)
    tb.send_message(m.chat.id, page.read())

@tb.message_handler(commands=['stat'])
def stat(m):
    #if m.text == '/tid'
    #  tt = ''
    #else
    try:
      tt = m.text.split()[1]
    except:
      tt = ''

    page = urllib.urlopen('http://172.18.65.42/simonpots/class/way4.php?cmd=detail&tid='+tt)
    tb.send_message(m.chat.id, page.read())

@tb.message_handler(commands=['captjayapura'])
def captjayapura(m):
    os.system('wkhtmltoimage --quality 80 --crop-h 400 --crop-w 1000 --crop-x 0 --crop-y 0 --format png "http://172.18.65.42/statusatm/dashboard_cabang.pl?REGID=18&REGNAME=Jayapura" /home/wafa/shoots/jayapura.png')
    photo = open('/home/wafa/shoots/jayapura.png', 'rb')
    tb.send_photo(m.chat.id, photo)

@tb.message_handler(commands=['captkanwil'])
def captkanwil(m):
    try:
      tt = m.text.split()[1]
    except:
      tt = '18'
 
    os.system('wkhtmltoimage --quality 80 --crop-h 850 --crop-w 1100 --crop-x 0 --crop-y 0 --format png "http://172.18.65.42/statusatm/dashboard_cabang.pl?REGID='+tt+'" /home/wafa/shoots/kanwil-'+tt+'.png')
    photo = open('/home/wafa/shoots/kanwil-'+tt+'.png', 'rb')
    tb.send_photo(m.chat.id, photo)


@tb.message_handler(commands=['captjke'])
def captjke(m):
    os.system('wkhtmltoimage --quality 80 --crop-h 400 --crop-w 1000 --crop-x 0 --crop-y 0 --format png --username "admin_jyp" --password "password"  "http://131.103.5.214/atm/jke.php" /home/wafa/shoots/jke.png')
    photo = open('/home/wafa/shoots/jke.png', 'rb')
    tb.send_photo(m.chat.id, photo)


@tb.message_handler(commands=['captselindo'])
def captselindo(m):
    os.system('wkhtmltoimage --quality 80 --crop-h 560 --crop-w 1200 --crop-x 0 --crop-y 0 --format png "http://172.18.65.42/statusatm/dashboard_3.pl" /home/wafa/shoots/selindo.png')
    photo = open('/home/wafa/shoots/selindo.png', 'rb')
    tb.send_photo(m.chat.id, photo)

@tb.message_handler(commands=['chatid'])
def edctid(m):
    tb.send_message(m.chat.id, "chatid: "+str(m.chat.id))



@tb.message_handler(commands=['edctid'])
def edctid(m):
    try:
      tt = m.text.split()[1]
    except:
      tt = ''
    page = urllib.urlopen('http://131.103.5.214/atm/edcbandung.php?cmd=tid&tid='+tt)
    tb.send_message(m.chat.id, striphtml(page.read()))

@tb.message_handler(commands=['nopmerchant'])
def nopmerchant(m):
    try:
      tt = m.text.split()[1]
    except:
      tt = ''
    page = urllib.urlopen('http://131.103.5.214/atm/edcall.php?cmd=nopmerchant&REGID='+tt)
    splitted_text = util.split_string(striphtml(page.read()), 3000)
    for text in splitted_text:
            tb.send_message(m.chat.id, text)
    #tb.send_message(m.chat.id, striphtml(page.read()))

@tb.message_handler(commands=['nopbrilinks'])
def nopbrilinks(m):
    try:
      tt = m.text.split()[1]
    except:
      tt = ''
    page = urllib.urlopen('http://131.103.5.214/atm/edcbandung.php?cmd=nopbrilinks&REGID='+tt)
    #tb.send_message(m.chat.id, striphtml(page.read()))
    splitted_text = util.split_string(striphtml(page.read()), 3000)
    for text in splitted_text:
            tb.send_message(m.chat.id, text)
 

@tb.message_handler(commands=['probmerchant'])
def probmerchant(m):
    try:
      tt = m.text.split()[1]
    except:
      tt = ''
    page = urllib.urlopen('http://131.103.5.214/atm/edcbandung.php?cmd=probmerchant&REGID='+tt)
#    tb.send_message(m.chat.id, striphtml(page.read()))
    splitted_text = util.split_string(striphtml(page.read()), 3000)
    for text in splitted_text:
            tb.send_message(m.chat.id, text)
 
@tb.message_handler(commands=['probbrilinks'])
def probbrilinks(m):
    try:
      tt = m.text.split()[1]
    except:
      tt = ''
    page = urllib.urlopen('http://131.103.5.214/atm/edcbandung.php?cmd=probbrilink&REGID='+tt)
#    tb.send_message(m.chat.id, striphtml(page.read()))
    splitted_text = util.split_string(striphtml(page.read()), 3000)
    for text in splitted_text:
            tb.send_message(m.chat.id, text)
 


@tb.message_handler(commands=['edcnama'])
def edcnama(m):
    try:
      tt = m.text.split()[1]
    except:
      tt = ''
    page = urllib.urlopen('http://131.103.5.214/atm/edcbandung.php?cmd=edcnama&nama='+tt)
    tb.send_message(m.chat.id, striphtml(page.read()))



def striphtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

@tb.message_handler(commands=['co'])
def co(m):
    try:
      tt = m.text.split()[1]
    except:
      tt = '00'
 
    page = urllib.urlopen('http://131.103.5.214/atm/tidall.php?cmd=co&kanwil='+tt)
#    tb.send_message(m.chat.id, page.read())
    splitted_text = util.split_string(striphtml(page.read()), 3000)
    for text in splitted_text:
            tb.send_message(m.chat.id, text)
 

@tb.message_handler(commands=['summaryall'])
def summaryall(m):
    page = urllib.urlopen('http://131.103.5.214/atm/tid.php?cmd=summaryall')
    tb.send_message(m.chat.id, page.read())

@tb.message_handler(commands=['reportuko'])
def reportuko(m):
    page = urllib.urlopen('http://131.103.5.214/atm/reportukobandung.php')
#    tb.send_message(m.chat.id, page.read())
    splitted_text = util.split_string(striphtml(page.read()), 3000)
    for text in splitted_text:
            tb.send_message(m.chat.id, text)
 


@tb.message_handler(commands=['cdm'])
def cdm(m):
    try:
      tt = m.text.split()[1]
    except:
      tt = '00'
    page = urllib.urlopen('http://131.103.5.214/atm/cdmall.php?REGID='+tt)
#    tb.send_message(m.chat.id, page.read())
    splitted_text = util.split_string(striphtml(page.read()), 3000)
    for text in splitted_text:
            tb.send_message(m.chat.id, text)
 

@tb.message_handler(commands=['status'])
def status(m):
    page = urllib.urlopen('http://131.103.5.214/atm/tid.php?cmd=status')
    tb.send_message(m.chat.id, page.read())


@tb.message_handler(commands=['cl'])
def cl(m):
    try:
      tt = m.text.split()[1]
    except:
      tt = '00'
 
    page = urllib.urlopen('http://131.103.5.214/atm/tidall.php?cmd=cl&kanwil='+tt)
#    tb.send_message(m.chat.id, page.read())
    splitted_text = util.split_string(striphtml(page.read()), 3000)
    for text in splitted_text:
            tb.send_message(m.chat.id, text)
 
@tb.message_handler(commands=['offline'])
def offline(m):
    try:
      tt = m.text.split()[1]
    except:
      tt = '00'
 
    page = urllib.urlopen('http://131.103.5.214/atm/tidall.php?cmd=offline&kanwil='+tt)
#    tb.send_message(m.chat.id, page.read())
    splitted_text = util.split_string(striphtml(page.read()), 3000)
    for text in splitted_text:
            tb.send_message(m.chat.id, text)
 
@tb.message_handler(commands=['df'])
def df(m):
    try:
      tt = m.text.split()[1]
    except:
      tt = '00'
 
    page = urllib.urlopen('http://131.103.5.214/atm/tidall.php?cmd=df&kanwil='+tt)
#    tb.send_message(m.chat.id, page.read())
    splitted_text = util.split_string(striphtml(page.read()), 3000)
    for text in splitted_text:
            tb.send_message(m.chat.id, text)
 
@tb.message_handler(commands=['cekbranch'])
def cekbranch(m):
    try:
      tt = m.text.split()[1]
    except:
      tt = ''
 
    page = urllib.urlopen('http://172.18.65.58/~wafa/testping.php?bc='+tt)
    result = page.read()
    result = result.replace('<pre>','')
    result = result.replace('</pre>','\n')
    print("pingatm "+tt+" "+str(m.chat.id))
    tb.send_message(m.chat.id, result)

@tb.message_handler(commands=['cekip'])
def cekip(m):
    try:
      tt = m.text.split()[1]
    except:
      tt = ''
    page = urllib.urlopen('http://172.18.65.58/~wafa/testping.php?ip='+tt)
    result = page.read()
    result = result.replace('<pre>','')
    result = result.replace('</pre>','\n')
    tb.send_message(m.chat.id, result)

@tb.message_handler(commands=['pingatm'])
def pingatm(m):
    try:
      tt = m.text.split()[1]
    except:
      tt = ''
    page1 = urllib.urlopen('http://131.103.5.214/atm/tid.php?cmd=showip&tid='+tt)
    ipatm = page1.read()
    page = urllib.urlopen('http://172.18.65.58/~wafa/testping.php?cip='+ipatm)
    result = page.read()
    result = result.replace('<pre>','')
    result = result.replace('</pre>','\n')
    print("pingatm "+tt+" "+ipatm+" "+str(m.chat.id))
    tb.send_message(m.chat.id, result)



# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@tb.message_handler(content_types=['location'])
def test_loc(message):
    m = message
    longitude = m.location.longitude
    latitude = m.location.latitude
    tz = tf.timezone_at(lng=longitude, lat=latitude)
    fmt = '%Y-%m-%d %H:%M:%S %Z%z'
    loc = pytz.timezone(tz)
    dt = datetime.datetime.now()
    loc_time = loc.localize(dt)
    tb.reply_to(m,"based on your location, here is your timezone: "+tz)
    tb.reply_to(m,"your localtime is: "+loc_time.strftime(fmt))
    tb.send_location(m.chat.id,latitude,longitude)
 

@tb.message_handler(func=lambda message: True)
def echo_message(message):
    m = message
    if not session.query(exists().where(DB.Profile.chat_id == m.chat.id)).scalar():
        p= DB.Profile()
        p.chat_id = m.chat.id
        p.user_id = m.from_user.id
        p.username = m.from_user.username
        p.first_name = m.from_user.first_name
        p.last_name = m.from_user.last_name
        p.language_code = m.from_user.language_code
        session.add(p)
        session.commit()
    else:
        p = session.query(DB.Profile).filter_by(chat_id=m.chat.id).first()
    if not bool(p.email):
        match = re.search(r'[\w\.-]+@[\w\.-]+',m.text)
        if bool(match):
            p.email = match.group(0)
            session.commit()
            tb.reply_to(m,"Thank you, your email "+p.email+" has been recorded to our database")
            tb.send_message(m.chat.id,"You can ask me anything")
        else:
            tb.reply_to(m,"Hi "+p.first_name+", May I know your email?")
    else:
        lang = client.detect_language(m.text)
        if not lang['language'] == p.language_code and float(lang['confidence']) > 0.2 :
            print(lang['language'])
            #country = pycountry.countries.get(alpha_2=lang['language'].upper())
            lang_idx = next((i for i, sublist in enumerate(list_language) if lang['language'] in sublist['language']), -1)
            print(list_language[lang_idx]['name'])
            reply = "I detected your language is " + list_language[lang_idx]['name']
            if not lang['language'] == 'en':
                rr = client.translate(reply,target_language=lang['language'])
                tb.reply_to(m,rr['translatedText'])
            else:
                tb.reply_to(m,reply)
        else:
            try:
                mm = m.text.split(' ',1)
            except:
                mm = ''
            if mm[0] in command:
                cmd=mm[0] + ' ' + mm[1]
                out = str(os.popen(cmd).read())
                splitted = util.split_string(out,3000)
                for text in splitted:
                    tb.reply_to(m,'cmd:' + mm[0] + ' ' + mm[1]+'\n' + text)
            elif mm[0] in cmd_custom:
                out = str(cmdlist[mm[0]](0,mm[1]))
                splitted = util.split_string(out,3000)
                for text in splitted:
                    tb.reply_to(m,'cmd:' + mm[0] + ' ' + mm[1]+'\n' + text)
            else:
                tb.reply_to(message, message.text)




def listener(messages):
    for m in messages:
        print (str(m))

tb.set_update_listener(listener)

tb.remove_webhook()



#tb.polling(none_stop=True,interval=1)
#tb.polling()

# Set webhook
tb.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH,
               certificate=open(WEBHOOK_SSL_CERT, 'r'))


# Start server
httpd = HTTPServer((WEBHOOK_LISTEN, WEBHOOK_PORT),
                                  WebhookHandler)

httpd.socket = ssl.wrap_socket(httpd.socket,
                               certfile=WEBHOOK_SSL_CERT,
                               keyfile=WEBHOOK_SSL_PRIV,
                               server_side=True)

httpd.serve_forever()



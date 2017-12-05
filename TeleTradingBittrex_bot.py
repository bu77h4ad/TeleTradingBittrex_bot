from bittrex import Bittrex, API_V2_0, API_V1_1, BUY_ORDERBOOK, TICKINTERVAL_ONEMIN
from configparser import ConfigParser
import time
import requests
import pprint
from APItelegram import telegram

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

# Читаем настройки из файла
cfg = ConfigParser()
cfg.read('TeleTradingBittrex_bot.ini')
#print(cfg.get('Data', 'telegram_token'))
#print(cfg.get('Data', 'api_key'))
#print(cfg.get('Data', 'api_secret'))
#print(cfg.getfloat('Data', 'deposit'))  # get "float" object
#print(cfg.get('Data', 'owner'))
update_id = 0

my_bittrex = Bittrex(cfg.get('Data', 'api_key'), cfg.get('Data', 'api_secret'), api_version=API_V1_1)
#url = "https://api.telegram.org/bot%(token)s/" %{"token" : cfg.get('Data', 'telegram_token')}

bot = telegram(cfg.get('Data', 'telegram_token'))
bot.delUpdates()

# Функция для Телеграм бота
#def bot(command = False, offset = '', chat_id = '', text = ''):  
#	if command == False : command = 'getUpdates?offset=' + offset
#	if chat_id != False : chat_id = '?chat_id=' + chat_id
#	if text    != False : text    = '&text='+ text
#	response = requests.get(url + command + chat_id + text)
#	return response.json()

print ("Set sell percent ->\t\t", cfg.getfloat('Data', 'sellPercent'),"%")
print ("Set deposit ->\t\t\t", cfg.getfloat('Data', 'deposit'),"%")
print ("Set bot owner ->\t\t", cfg.get('Data', 'owner'))

getMe = bot.getMe()
if getMe != True: 
	getMeStatus = 'OK!'
	userName = getMe['result']['username']
else:
	getMeStatus = 'FAIL!'
	userName = getMe
	time.sleep(30)
	quit()
print ("Init bot status ->\t\t", getMeStatus, '->\t' , userName )

balance = my_bittrex.get_balance('BTC')
balanceStatus = balance['success'] 
if balanceStatus == True:
	balanceStatus = 'OK!'
else:
	balanceStatus = 'FAIL!'
print ("Init bittrex status ->\t", balanceStatus, '->\t', "Available BTC for trading -> %(sum).8f" % {'sum' : balance['result']['Available']})

print ("TeleTradingBittrex_bot started\t OK!")
print()

# Цикл для проверки новых сообщений
while True:
	time.sleep(1)

	# проверка на новые сообщения
	last_message = bot.getMessage()

	if  last_message == False : continue	
	# Обнаружено новое сообщение, то ......
	
	# Является ли отправитель владельцем бота ?
	if cfg.get('Data', 'owner').lower() != last_message['from']['username'].lower(): 
		bot.sendMessage(chat_id = str(last_message['from']['id']), text =  "Ты не мой хозяин" )
		continue
	print ("Message from owner ->", last_message['text'])
	
	# Ответ на команду /start
	if last_message['text'] == '/start':
		bot.sendMessage(chat_id =  str(last_message['from']['id']), text = "Приветсвую тебя хозян!\nЯ твой маленький, торговый бот помошник :)")
		bot.sendMessage(chat_id =  str(last_message['from']['id']), text = "Можешь мне писать название монеты, а я её буду покупать за BTC. И оставлю ордер, на продажу этой же монеты, на 5% дороже. \nДополнительные команды :'Депозит 90' - на сколь %, от всего депозита, ты хочешь купить монету.")
		continue
	# Ответ на команду ДЕПОЗИТ
	if last_message['text'].split(' ')[0] == "Депозит" and len (last_message['text'].split(' ')) == 2 : 
		if isfloat( last_message['text'].split(' ')[1]) \
		and float(last_message['text'].split(' ')[1]) <= 100 \
		and float(last_message['text'].split(' ')[1]) > 0 : 
			cfg['Data']['deposit'] = last_message['text'].split(' ')[1]
			bot.sendMessage(chat_id =  str(last_message['from']['id']), text = "\u2757\ufe0f Депозит установлен на : " + last_message['text'].split(' ')[1] + "%")
			# сохраняем настройки в файл
			with open('tele_crypto_bot_CFG.ini', 'w') as configfile:
				cfg.write(configfile)
			continue	
		else:
			bot.sendMessage(chat_id =  str(last_message['from']['id']), text = "\u274c Депозит не установлен")
			continue

	# ответ бота на команду о покупке	
	# Существует ли такая монета ?	
	if my_bittrex.get_ticker('BTC-'+ last_message['text'])['success'] == False :
		bot.sendMessage(chat_id = str(last_message['from']['id']), text =  "\u274c Mонета '" +last_message['text'] +"' не найдена ")
		continue
	
	# Подтверждение операции
	bot.sendMessage(chat_id = str(last_message['from']['id']), text =  "\u2757\ufe0f 1. Купить '{0}' по текущей цене, на {1}% от депозита.\n\n\u2757\ufe0f 2. Поставить лимитный ордер на продажу '{0}' на {2}%  выше текуще стоимости. \n\nПодтверждаете ('Да'/'Нет') \u2753".format( last_message['text'], cfg.getfloat('Data', 'deposit'), cfg.getfloat('Data', 'sellPercent') ) )
	print ("Waiting for confim (30 sek) ...")
	y=0
	while y in range(0,30) :		
		time.sleep(1)
		y = y + 1 		
		wait_message = bot.getMessage()
		if wait_message == False : continue
		if cfg.get('Data', 'owner') == wait_message['from']['username']: 
			if wait_message['text'] in ['Да','да','ДА'] :
	 			bot.sendMessage(chat_id = str(last_message['from']['id']), text =  "\u2b55\ufe0f Операция подтверждена ")
	 			print ("Сonfirmed")
	 			break
			else:
	 			#bot.sendMessage(chat_id = str(last_message['from']['id']), text =  "\u274c Операция отменена ")
	 			y=-1
	else:
		bot.sendMessage(chat_id = str(last_message['from']['id']), text =  "\u274c Операция отменена")
		print ("Cansel")
		continue
			
	# Выполняет операции на бирже
	
	while True :		
		last_balance = my_bittrex.get_balance('BTC')['result']
		BTC = last_balance['Available'] # доступный для торговли баланс

		last_tiker = my_bittrex.get_ticker('BTC-'+ last_message['text'])['result']			
		ask = last_tiker['Ask'] # цена по которой я могу купить
		bid = last_tiker['Bid'] # цена по которой я могу продать

		# покупает заданную монету
		#ask=ask-ask/5
		text = my_bittrex.buy_limit('BTC-'+ last_message['text'], BTC / 100 * cfg.getfloat('Data', 'deposit') / ask, ask ) 		
		if text['success'] == True: 
			text = 'OK!'
		bot.sendMessage(chat_id = str(last_message['from']['id']), text =  "Ответ bittrex на покупку: \n\n" + str(text) ) 
		
		# проверяет исполнился ли ордер
		time.sleep(3)
		get_open_orders = my_bittrex.get_open_orders('BTC-' + last_message['text'])			
		if len(get_open_orders['result']) == 0: break

		# Если ордер на покупку не исполнился
		bot.sendMessage(chat_id = str(last_message['from']['id']), text =  "Не удалось выкупить весь объем.\nПовторяю...") 
		for y in range(0,len(get_open_orders['result'])) :
			OrderUuid = get_open_orders['result'][-1]['OrderUuid']						
			my_bittrex.cancel(OrderUuid)
			time.sleep(0.15)	
								

	# ставит лимитный ордер на прожажу заданной монеты	
	last_balance = my_bittrex.get_balance(last_message['text'])['result']
	xCoin = last_balance['Available'] # доступный для торговли баланс	
	bid = last_tiker = my_bittrex.get_ticker('BTC-'+ last_message['text'])['result']['Bid']			
	bid = bid / 100 * (100 + cfg.getfloat('Data', 'sellpercent'))
	text = str(my_bittrex.sell_limit('BTC-'+ last_message['text'], xCoin / 100 * cfg.getfloat('Data', 'deposit'), bid ) )
	bot.sendMessage(chat_id = str(last_message['from']['id']), text =  "Ответ bittrex на продажу: \n\n" + text ) 

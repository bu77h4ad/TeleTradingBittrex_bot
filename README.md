DONATIONS: 

	BTC fb0a34933ca0781f5e9917a52ea86d72cbb1c05b4ccfff56f9c78bdce5f8a573
	LTC LRsm54XYJxG7NJCuAntK98odJoXhwp1GBK
	ETH 0x8750793385349e2edd63e87d5c523b3b2c972b82
	ZEC t1TW9tC321fZyDQRX4spzpxar1hRBcBHU6S
CONTACT:

	Telegram: bu77h4ad

ОПИСАНИЕ БОТА

Управляется через телеграм. Пишите боту название монеты. Он будет покупать заданную монету за BТС по рыночной стоимости и 
выставлять ордер для последующей перепродажи с наценкой (на sellpercent %)


УСТАНОВКА TeleTradingBittrex_bot

- 1. создать бота в телеграм
- 2. создать API ключи на BITTREX
- 3. заполнить файл TeleTradingBittrex_bot.ini
  - 3.1. заполнить token Телеграм бота	
  - 3.2. заполнить 2 API ключа
  - 3.3 заполнить owner - это ваш username из телеграма(без знака @). что бы бот слушал только ваши команды
  - 3.4 поле deposit - это на сколько % заходите в сделку от депозита (рекомендую не больше 99)
  - 3.5 поле sellpercent - это на сколько % больше от текущей цены будете выставлять ордер на продажу
	

После запуска программы должен выдать надпись "TeleTradingBittrex_bot started	OK!" - значит бот запущен и 
готов принимать команды.

ПРИМЕР:

	сообщение боту: "LTC"
бот покупает LTC. И выставляет ордер на продажу LTC с наценкой.

	сообщение боту: "Депозит 50"
бот установит значение переменной deposit в 50. Это значит что при совершении следующих операций на бирже он будет 
закупать на 50% от своего BTC депозита

import telebot
import requests

from telebot import types
from consts_handler import TOKEN, WEATHER_API_KEY


def get_data() -> str:
    req = requests.get("https://yobit.net/api/3/ticker/btc_usd")
    response = req.json()
    sell_price = response['btc_usd']['sell']
    return f'sell price = {sell_price}'


def google_search(text: str) -> str:
    params = {'q': f'{text}'}
    req = requests.get("https://www.google.com/search", params=params)
    return req.text


def weather_forecast(lat: float, lon: float) -> str:
    params = {'lat': lat, 'lon': lon, 'appid': WEATHER_API_KEY, 'units': 'metric'}
    req = requests.get(f'http://api.openweathermap.org/data/2.5/weather', params=params)
    weather_dict = req.json()
    content = f"""
    weather: {weather_dict.get('weather')[0].get('main')}
weather conditions: {weather_dict.get('weather')[0].get('description')}
temperature: {weather_dict.get('main').get('temp')}
country: {weather_dict.get('sys').get('country')}
"""
    return content


def tg_bot(token: str) -> None:
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=['weather'])
    def location(message: types.Message) -> None:
        """ получаем гео-локацию клиента """

        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_geo = types.KeyboardButton(text="share location", request_location=True)
        keyboard.add(button_geo)
        bot.send_message(message.chat.id, "pls, share your location", reply_markup=keyboard)

    @bot.message_handler(content_types=['location'])
    def weather_forecast_giver(message: types.Message) -> None:
        """ считываем широту и долготу из сообщения-локаации, делаем запрос на сайт, отправляем погоду """

        lat = message.location.latitude
        lon = message.location.longitude
        try:
            weather_message = weather_forecast(lat, lon)
            bot.send_message(message.chat.id, weather_message)
        except Exception as ex:
            print(ex)
            bot.send_message(message.chat.id, 'smth went wrong...')

    @bot.message_handler(commands=['start'])
    def greeting(message: types.Message) -> None:
        bot.send_message(message.chat.id, f'{message.from_user.first_name} {message.from_user.last_name}, здравствуй!')
        with open('/home/fia52/Images/sticker_for_reqbot', 'rb') as sticker:
            bot.send_sticker(message.chat.id, sticker)

    @bot.message_handler(commands=['rate'])
    def send_info(message: types.Message) -> None:
        try:
            bot.send_message(message.chat.id, get_data())
        except Exception as ex:
            print(ex)
            bot.send_message(message.chat.id, 'smth went wrong...')

    bot.polling()


if __name__ == '__main__':
    tg_bot(TOKEN)

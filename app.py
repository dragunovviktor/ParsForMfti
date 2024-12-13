from random import random
import re
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from models import db, User, Place, SavedPlace, SavedRestaurant, SavedNatureOfPskov, FinalRouteInformation, SavedHotels, BestAndWorst, BestAndWorstKvas
import logging
import requests
from requests import get
from bs4 import BeautifulSoup
import lxml
from sqlalchemy.dialects.sqlite import insert
import random
import matplotlib.pyplot as plt
import os
import schedule
import time
import threading
import numpy as np
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from flask import jsonify
import math
import statistics
import psycopg2

app = Flask(__name__)
app.config.from_object('config.Config')


db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/hotels')
@login_required
def hotels():
    places = Place.query.all()
    return render_template('hotels.html', places=places)

@app.route('/restaurants')
@login_required
def restaurants():
    places = Place.query.all()
    return render_template('restaurants.html', restaurants=restaurants)



@app.route('/places')
@login_required
def places():
    places = Place.query.all()
    return render_template('places.html', places=places)

@app.route('/events')
@login_required
def events():
    places = Place.query.all()
    return render_template('events.html', places=places)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different username.', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        user = User(username=username, password=hashed_password)
        try:
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Registration successful. You are now logged in.', 'success')
            return redirect(url_for('index'))
        except IntegrityError:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'danger')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Authentication successful! Enjoy your time exploring places!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login failed. Check your username and/or password.', 'danger')
    return render_template('login.html')


@app.route('/save_restaurant', methods=['POST'])
@login_required
def save_restaurant():
    data = request.get_json()
    restaurant_name = data.get('restaurant_name')

    if not restaurant_name:
        flash('Пожалуйста, введите название ресторана.')
        return redirect(url_for('restaurants'))

    existing_restaurant = SavedRestaurant.query.filter_by(user_id=current_user.id,
                                                          restaurant_name=restaurant_name).first()
    if existing_restaurant:
        flash('Этот ресторан уже сохранен.')
        return redirect(url_for('restaurants'))

    new_restaurant = SavedRestaurant(user_id=current_user.id, restaurant_name=restaurant_name)
    db.session.add(new_restaurant)
    db.session.commit()

    flash('Ресторан успешно сохранен!')
    return redirect(url_for('restaurants'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/save/<int:place_id>', methods=['POST'])
@login_required
def save_place(place_id):
    if not SavedPlace.query.filter_by(user_id=current_user.id, place_id=place_id).first():
        saved_place = SavedPlace(user_id=current_user.id, place_id=place_id)
        db.session.add(saved_place)
        db.session.commit()
        flash('Place saved to your profile.', 'success')
    else:
        flash('Place is already saved.', 'info')
    return redirect(request.referrer)

@app.route('/profile')
@login_required
def profile():
    saved_places = SavedPlace.query.filter_by(user_id=current_user.id).all()  # Добавьте этот код
    saved_restaurants = SavedRestaurant.query.filter_by(user_id=current_user.id).all()  # Добавьте этот код
    return render_template('profile.html', saved_places=saved_places, saved_restaurants=saved_restaurants)

# С данной части кода начинается скраппинг
# Данные с парсера будут использованы на страничке nature, нужно найти сайт, где есть такие места (парки и тд, зоопарки) и пропарсить их для карточек
# Было решено использовать сайт: https://tur-ray.ru/pskovskaya-oblast-dostoprimechatelnosti.html


url_address = 'https://www.kp.ru/russia/pskov/dostoprimechatelnosti/'
name_of_place = []
description_for_place = []
information_about_place = []

def parser_for_names_of_places(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        entry_content = soup.find_all('div', class_='layout-columns')
        names = entry_content[0].find_all('p')
        for i in range(len(names)):
            information_about_place.append(names[i].get_text())
        nam_o_place = entry_content[0].find_all('h2')
        for i in range(len(nam_o_place)):
            name_of_place.append(nam_o_place[i].get_text())


        return name_of_place

result = parser_for_names_of_places(url_address)
name_of_nature = name_of_place[1:-5]

#парсер выше предназначен для получения названий мест, чтобы мы их позже смогли использовать в карточках, теперь мы хотим получить информацию о каждом из этих мест, чтобы в дальнейшем их использовать для карточек


def Pars_for_get_description(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        entry_content = soup.find_all('div', class_='layout-columns')

        names = entry_content[0].find_all('p')
        for i in range(len(names)):
            description_for_place.append(names[i].get_text())


    return description_for_place

result_for_description = Pars_for_get_description(url_address)
for_start_info_to_page = result_for_description[0]
description_for_place = description_for_place[1:]

dict_for_city_info = dict(zip(name_of_nature, description_for_place * len(name_of_nature)))
print(dict_for_city_info)

url2 = 'https://www.pskov.kp.ru/economics/'


def pars_for_events(url2):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
    }
    response = requests.get(url2, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')

        time_elements = soup.find_all('span', class_='sc-1tputnk-9')
        descr = soup.find_all('span', class_='sc-17oegr5-0 SUHig')

        time_texts = [time.get_text() for time in time_elements]
        descr = [descr.get_text() for descr in descr]

        return time_texts, descr


time_of_publications = pars_for_events(url2)[0]
events_of_publishing = pars_for_events(url2)[1]

dict_for_events = dict(zip(time_of_publications, events_of_publishing * len(time_of_publications)))

def longest_news(dict_of_events):
    sorted_dict = dict(sorted(dict_of_events.items(), key=lambda item: len(item[1].split()), reverse=True))
    return sorted_dict


itog_news = longest_news(dict_for_events)

def function_for_random_combinations_of_word(itog_news):
    for key, value in itog_news.items():
        words = value.split()
        itog_news[key] = ' '.join(random.sample(words, len(words)))
    return itog_news

print(function_for_random_combinations_of_word(itog_news))



def save_nature_places_on_start():
    with app.app_context():
        for nature_name, nature_description in dict_for_city_info.items():
            stmt = insert(SavedNatureOfPskov).values(
                nature_name=nature_name,
                nature_description=nature_description
            ).on_conflict_do_nothing()
            try:
                db.session.execute(stmt)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                continue

save_nature_places_on_start()

restaurants_ = ['Helga',
               'Dunkan',
               'Бар 903',
               'Двор Подзноева',
               'Mojo GastroBar',
               'Ресто-Бар Моя История',
               'Трапезные палаты',
               'Кафе "Пироговые палаты"']

Hotels = ['Гостиница Двор Подзноева',
          'Отель Old Estate HOTEL & SPA',
          'Гостиница Ольгинская',
          'Гостиница Пушкинъ',
          'Гостиница Каркушин Дом']


def save_nature_places_on_start():
    with app.app_context():
        for nature_name, nature_description in dict_for_city_info.items():
            stmt = insert(SavedNatureOfPskov).values(
                nature_name=nature_name,
                nature_description=nature_description
            ).on_conflict_do_nothing()
            try:
                db.session.execute(stmt)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                continue

print(dict_for_city_info)
def info_about_hotel(url):
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    hotel_cards = soup.find_all('div', class_='cad4BlZ3zBsRQ7U3')

    hotels = []

    for card in hotel_cards:
        hotel_name = card.find('a', class_='uuJfb3w6vMsf_zBY')
        if hotel_name:
            hotel_name = hotel_name.get_text(strip=True)

        price = card.find('span', class_='pRPDJ6I4aPcL6lkt')
        if price:
            price_str = price.get_text(strip=True).replace('₽', '').replace('\u2009', '').replace('\u2060', '').strip()
            try:
                price_int = int(price_str)
            except ValueError:
                price_int = None

        if hotel_name and price_int is not None:
            hotels.append({
                'name': hotel_name,
                'price': price_int,
            })

    return hotels

url = 'https://hotel.tutu.ru/c_russia/pskov/f_cheap/'

d = info_about_hotel(url)

def get_extreme_prices(hotels_info):
    if not hotels_info:
        return None, None

    valid_hotels = [hotel for hotel in hotels_info if hotel['price'] is not None]

    if not valid_hotels:
        return None, None

    cheapest_hotel = min(valid_hotels, key=lambda x: x['price'])
    most_expensive_hotel = max(valid_hotels, key=lambda x: x['price'])

    return cheapest_hotel, most_expensive_hotel

cheapest, most_expensive = get_extreme_prices(d)

def plot_prices(hotels_info, file_path):
    hotel_names = [hotel['name'] for hotel in hotels_info if hotel['price'] is not None]
    prices = [hotel['price'] for hotel in hotels_info if hotel['price'] is not None]

    plt.figure(figsize=(10, 6))
    plt.barh(hotel_names, prices, color='skyblue')

    plt.xlabel('Цена')
    plt.ylabel('Отели')
    plt.title('Цены на отели')

    plt.xticks(rotation=45)

    plt.savefig(file_path, bbox_inches='tight')
    plt.close()
hotels_info = info_about_hotel(url)

graph_path = os.path.join('static', 'hotel_prices.png')
plot_prices(hotels_info, graph_path)

if cheapest and most_expensive:
    print(f"Самый дешевый отель: {cheapest['name']} с ценой {cheapest['price']} рублей")
    print(f"Самый дорогой отель: {most_expensive['name']} с ценой {most_expensive['price']} рублей")
else:
    print("Не удалось найти отели с ценами.")

restaurants_ = ['Ресторан 1', 'Ресторан 2', 'Ресторан 3']
info_about_big_places = ['Место 1', 'Место 2', 'Место 3']
des = ['Описание 1', 'Описание 2', 'Описание 3']

def generator_of_random_routes(hotels_info):
    return (f'Возможно, сегодня неплохой идеей является сходить в ресторан {random.choice(restaurants_)}, '
            f'если же говорить про отели, то {random.choice([hotel["name"] for hotel in hotels_info if hotel["price"] is not None])}, '
            f'еще советуем посетить {random.choice(info_about_big_places)}, '
            f'почему именно это место? Не знаю!!!))) Мы приколисты, вот тебе описание рандомного места в Пскове, можешь поразмышлять, что это за место xD '
            f'{random.choice(des)}')


final_route = generator_of_random_routes(hotels_info)

def fetch_hotels_info(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Ошибка: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'lxml')

    hotels = []
    hotel_cards = soup.find_all('div', {'data-testid': 'serp-hotelcard'})

    for card in hotel_cards:
        try:
            title = card.find('p', class_='HotelCard_title__cpfvk').text.strip()

            rating = card.find('span', class_='TotalRating_content__k5u6S')
            rating = rating.text.strip() if rating else "Нет рейтинга"

            price = card.find('span', class_='HotelCard_ratePriceValue__s3HvW')
            if price:
                raw_price = price.text.strip()
                readable_price = raw_price.replace('\xa0', ' ').replace('₽', '').strip()
                hotels.append({'Название': title, 'Рейтинг': rating, 'Цена': readable_price})
            else:
                hotels.append({'Название': title, 'Рейтинг': rating, 'Цена': "Нет цены"})

        except Exception as e:
            print(f"Ошибка при обработке карточки: {e}")

    return hotels


all_hotels = []

for page_number in range(1, 19):  # Страницы от 1 до 18
    url = f"https://ostrovok.ru/hotel/russia/pskov/?page={page_number}"
    hotels_info = fetch_hotels_info(url)
    print(hotels_info)
    all_hotels.extend(hotels_info)

prices_rub = []
ratings = []
for hotel in all_hotels:
    try:
        # Обрабатываем цену
        price_rub = hotel['Цена'].replace(' ', '')
        price_rub = int(price_rub)

        # Обрабатываем рейтинг
        rating = hotel['Рейтинг']
        prices_rub.append(price_rub)
        ratings.append(rating)
    except ValueError:
        continue

median_price = np.median(prices_rub)
print(f"Медиана по ценам: {median_price} ₽")

# Преобразуем рейтинги в float и заменяем 'Нет рейтинга' на np.nan
ratings = [float(rating.replace(',', '.')) if rating != 'Нет рейтинга' else np.nan for rating in ratings]

# Преобразуем в массивы numpy
ratings = np.array(ratings, dtype=np.float64)
prices_rub = np.array(prices_rub, dtype=np.float64)

# Создаем массив отелей с ценами и рейтингами, фильтруем отели с NaN рейтингами
hotels_array = np.array([
    (price, rating, hotel)
    for price, rating, hotel in zip(prices_rub, ratings, all_hotels)
    if not np.isnan(rating)  # Исключаем отели с NaN рейтингом
])

# Считаем соотношение цена/рейтинг
price_rating_ratio = hotels_array[:, 0] / hotels_array[:, 1]

# Добавляем соотношение цена/рейтинг к массиву отелей
hotels_with_ratio = np.column_stack((hotels_array, price_rating_ratio))

# Сортируем отели по соотношению цена/рейтинг
sorted_by_ratio = hotels_with_ratio[hotels_with_ratio[:, 3].argsort()]

# Лучшие отели
best = []
for hotel in sorted_by_ratio[:5]:
    price_in_usd = hotel[0] / 107  # Переводим в доллары
    best.append(f"Название: {hotel[2]['Название']}, Цена: {hotel[0]} ₽ ({price_in_usd:.2f} $), Рейтинг: {hotel[1]}, Соотношение цена/рейтинг: {hotel[3]:.2f}")

# Худшие отели
worst = []
for hotel in sorted_by_ratio[-5:]:
    price_in_usd = hotel[0] / 107
    worst.append(f"Название: {hotel[2]['Название']}, Цена: {hotel[0]} ₽ ({price_in_usd:.2f} $), Рейтинг: {hotel[1]}, Соотношение цена/рейтинг: {hotel[3]:.2f}")

# Извлекаем названия лучших отелей
best_hotels_names = [hotel.split(",")[0].split(":")[1].strip() for hotel in best]

# Извлекаем названия худших отелей и фильтруем те, которые уже есть в списке лучших
worst_hotels_names = [hotel.split(",")[0].split(":")[1].strip() for hotel in worst]
worst_filtered = [hotel for hotel in worst if hotel.split(",")[0].split(":")[1].strip() not in best_hotels_names]

# Выводим результаты
print("Лучшие отели:")
for entry in best:
    print(entry)

print("\nХудшие отели:")
for entry in worst_filtered:
    print(entry)

'''
def save_hotels_to_db(hotels, prices_rub, ratings):
    with app.app_context():
        for i, hotel in enumerate(hotels):
            try:
                if i >= len(prices_rub) or i >= len(ratings):
                    raise IndexError(f"Data is missing for hotel {hotel['Название']}")

                rating = ratings[i]
                if rating == 'Нет рейтинга':
                    rating = "No rating"
                else:
                    rating = str(rating).strip()

                price = prices_rub[i]
                if price <= 0:
                    print(f"Invalid price for hotel {hotel['Название']}, setting it to 0.")
                    price = 0

                price_in_usd = price / 107 if price > 0 else 0

                hotel_data = {
                    'name': hotel['Название'],
                    'rating': rating,
                    'price': f"{price} ₽ ({price_in_usd:.2f} $)"
                }

                stmt = insert(SavedHotels).values(hotel_data).on_conflict_do_nothing()
                db.session.execute(stmt)

            except Exception as e:
                print(f"Error processing hotel {hotel['Название']}: {e}")

        db.session.commit()
        print("Data successfully saved to the database.")
'''


def save_hotels_to_db(hotels, prices_rub, ratings):
    with app.app_context():
        for i, hotel in enumerate(hotels):
            try:
                if i >= len(prices_rub) or i >= len(ratings):
                    raise IndexError(f"Data is missing for hotel {hotel['Название']}")

                rating = ratings[i]

                # Skip if rating is NaN
                if isinstance(rating, float) and math.isnan(rating):
                    print(f"Skipping hotel {hotel['Название']} because rating is NaN.")
                    continue

                # Handle 'Нет рейтинга' case
                if rating == 'Нет рейтинга':
                    rating = "No rating"
                else:
                    rating = str(rating).strip()

                price = prices_rub[i]
                if price <= 0:
                    print(f"Invalid price for hotel {hotel['Название']}, setting it to 0.")
                    price = 0

                price_in_usd = price / 107 if price > 0 else 0

                hotel_data = {
                    'name': hotel['Название'],
                    'rating': rating,
                    'price': f"{price} ₽ ({price_in_usd:.2f} $)"
                }

                stmt = insert(SavedHotels).values(hotel_data).on_conflict_do_nothing()
                db.session.execute(stmt)

            except Exception as e:
                print(f"Error processing hotel {hotel['Название']}: {e}")

        db.session.commit()
        print("Data successfully saved to the database.")

save_hotels_to_db(all_hotels, prices_rub, ratings)


def save_best_and_worst(best, worst):
    with app.app_context():
        for b, w in zip(best, worst):
            try:
                # Check if either 'best' or 'worst' is NaN
                if (isinstance(b, float) and math.isnan(b)) or (isinstance(w, float) and math.isnan(w)):
                    print(f"Skipping data with NaN values: best={b}, worst={w}")
                    continue

                best_and_worst_data = {
                    'best': b,
                    'worst': w
                }

                new_entry = BestAndWorst(**best_and_worst_data)

                db.session.add(new_entry)

            except Exception as e:
                print(f"Error processing best/worst data: {e}")

        db.session.commit()

save_best_and_worst(best, worst)

def delete_old_data():
    with app.app_context():
        db.session.query(SavedHotels).delete()
        db.session.query(SavedNatureOfPskov).delete()
        db.session.commit()
        print("Старые данные удалены.")


def update_all_data():
    delete_old_data()

    all_hotels = []
    for page_number in range(1, 19):
        url = f"https://ostrovok.ru/hotel/russia/pskov/?page={page_number}"
        hotels_info = fetch_hotels_info(url)
        print(hotels_info)
        all_hotels.extend(hotels_info)

    save_hotels_to_db(all_hotels)
    save_nature_places_on_start(dict_for_city_info)

    print("Все данные обновлены.")


def update_and_scrape():
    url_address = 'https://www.kp.ru/russia/pskov/dostoprimechatelnosti/'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
    }
    response = requests.get(url_address, headers=headers)
    name_of_place = []
    description_for_place = []

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        entry_content = soup.find_all('div', class_='layout-columns')
        names = entry_content[0].find_all('p')
        for i in range(len(names)):
            description_for_place.append(names[i].get_text())
        nam_o_place = entry_content[0].find_all('h2')
        for i in range(len(nam_o_place)):
            name_of_place.append(nam_o_place[i].get_text())

    name_of_nature = name_of_place[1:-5]
    dict_for_city_info = dict(zip(name_of_nature, description_for_place * len(name_of_nature)))

    with app.app_context():
        for nature_name, nature_description in dict_for_city_info.items():
            stmt = insert(SavedNatureOfPskov).values(
                nature_name=nature_name,
                nature_description=nature_description
            ).on_conflict_do_nothing()
            try:
                db.session.execute(stmt)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                continue

    print("Обновление данных в базе завершено ")


def convert_uah_to_rub(uah_amount):
    conversion_rate = 2.5  # 1 гривна = 2.5 рубля (пример)
    return round(uah_amount * conversion_rate, 2)

# Функция для парсинга данных с сайта Europa-Market
def get_kvas_data_europa(url):
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Ошибка при загрузке страницы {url}. Код статуса: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    products = soup.find_all('div', class_='card-product-block')

    kvas_data = []

    for product in products:
        title = product.find('a', class_='card-product-content__title').text.strip()
        price = product.find('span', itemprop='price')
        if price:
            price = price.text.strip()
            price = parse_price(price)  # Преобразуем цену в число
        else:
            price = 0  # Если цена не найдена, устанавливаем 0
        link = product.find('a', class_='card-product-content__title')['href']
        img = product.find('img', class_='card-product-image__image')['src']

        rating_div = product.select_one('a.card-product-content__rating > div')
        rating = None
        if rating_div:
            rating = rating_div.text.strip()

        # Извлекаем объем из названия товара
        volume = extract_volume(title)
        if price > 0:  # Только добавляем товары с ценой больше 0
            kvas_data.append({
                'title': title,
                'price': price,
                'img': f"https://cdn.europa-market.ru{img}",
                'rating': rating if rating else "Нет информации",
                'link': f"https://europa-market.ru{link}",
                'volume': volume
            })
    return kvas_data



# Функция для извлечения объема из названия товара (например, "1л", "1.5л")
def extract_volume(title):
    match = re.search(r'(\d+(\.\d+)?)\s?л', title)
    if match:
        return float(match.group(1))  # Возвращаем объем в литрах
    return 1  # Если объем не указан, считаем, что это 1 литр

# Функция для преобразования рейтинга в числовое значение
def transform_rating(rating):
    if rating == 'Нет отзывов':
        return 0
    elif 'отзыв' in rating:
        return int(rating.split()[0])
    return 0

# Функция для расчета цены за литр
def calculate_price_per_liter(price, volume):
    if volume == 0:
        return 0
    return price / volume

# Функция для вычисления математического ожидания
def calculate_expected_value(prices):
    return np.mean(prices) if prices else 0

# Функция для преобразования строки с ценой в число
def parse_price(price_str):
    """Парсит строку с ценой и возвращает числовое значение."""
    price = ''.join([c for c in price_str if c.isdigit() or c == '.'])
    try:
        return float(price) if price else 0
    except ValueError:
        return 0

# Функция для более сложного расчета рейтинга
def calculate_rating(price_per_liter, rating_score, price_mean, price_std):
    # Оценка на основе рейтинга
    rating_factor = rating_score * 0.3  # Вес рейтинга (30%)

    # Оценка на основе отклонения от математического ожидания
    price_factor = 1 - abs(price_per_liter - price_mean) / price_std  # Чем ближе цена к среднему, тем выше оценка
    price_factor = max(0, price_factor)  # Для предотвращения отрицательных значений

    # Оценка на основе соотношения цена/объем
    volume_factor = 1 / price_per_liter  # Чем меньше цена за литр, тем выше оценка

    # Итоговая оценка
    final_rating = rating_factor + price_factor + volume_factor
    return final_rating


# Функция для сохранения лучших и худших товаров в базу данных
def save_best_and_worst_kvas(best_value, worst_value):
    with app.app_context():
        try:
            best_and_worst_kvas = BestAndWorstKvas(best=best_value, worst=worst_value)
            db.session.add(best_and_worst_kvas)
            db.session.commit()
            print(f"Сохранено: Лучший — {best_value}, Худший — {worst_value}")
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка при сохранении: {e}")


prcie_of_kvas = (get_kvas_data_europa('https://europa-market.ru/catalog/kvas-1401'))
filtared_kvas = [{'title': item['title'], 'price': item['price']} for item in prcie_of_kvas]

litrazh_pattern = r'(\d+[\.,]?\d*)\s?л' #регулярОчка для получения литража
massive_for_itog_distraction = []



for item in filtared_kvas:
    # Ищем  в названии
    match = re.search(litrazh_pattern, item['title'])
    if match:
        volume = match.group(1).replace(',', '.')
        massive_for_itog_distraction.append({
            'title': item['title'],
            'price': item['price'],
            'volume': float(volume)
        })

print(massive_for_itog_distraction)


@app.route('/calculate_price', methods=['POST'])
def calculate_price():
    kvas_title = request.json['kvas_title']
    quantity_ml = float(request.json['quantity_ml'])  # Количество в миллилитрах

    selected_kvas = next((kvas for kvas in massive_for_itog_distraction if kvas['title'] == kvas_title), None)

    if selected_kvas:
        # Рассчитываем цену
        price_per_liter = selected_kvas['price']
        volume_in_liters = selected_kvas['volume']

        # Стоимость за миллилитры
        price = (price_per_liter / volume_in_liters) * (quantity_ml / 1000)
        return jsonify({'price': round(price, 2)})

    return jsonify({'error': 'Квас не найден'}), 404
'''
Хочу добавить функционал, чтобы пользователь указывал сколько миллилитров кваса он готов купить и ему выдавало цену
'''

# Функция для анализа квасов
def analyze_kvas():
    europa_url = "https://europa-market.ru/catalog/kvas-1401"

    europa_kvas_data = get_kvas_data_europa(europa_url)

    filtered_data = [item for item in europa_kvas_data if item['price'] > 0]


    prices = [item['price'] for item in filtered_data]
    expected_value = calculate_expected_value(prices)

    # Рассчитываем статистические показатели
    price_per_liter = [calculate_price_per_liter(item['price'], item['volume']) for item in filtered_data]
    price_mean = np.mean(price_per_liter)
    price_std = np.std(price_per_liter)

    if min(price_per_liter) == 0:
        filtered_data = [item for item in filtered_data if calculate_price_per_liter(item['price'], item['volume']) > 0]

    for item in filtered_data:
        item['price_per_liter'] = calculate_price_per_liter(item['price'], item['volume'])
        rating_score = transform_rating(item['rating'])
        item['rating'] = calculate_rating(item['price_per_liter'], rating_score, price_mean, price_std)

    sorted_data = sorted(filtered_data, key=lambda x: x['rating'], reverse=True)

    best_kvas = sorted_data[:5]
    worst_kvas = sorted_data[-5:]

    best_string = "\n".join([f"{item['title']} - Цена за литр: {item['price_per_liter']:.2f} руб, Рейтинг: {item['rating']:.2f}" for item in best_kvas])
    worst_string = "\n".join([f"{item['title']} - Цена за литр: {item['price_per_liter']:.2f} руб, Рейтинг: {item['rating']:.2f}" for item in worst_kvas])

    save_best_and_worst_kvas(best_string, worst_string)

    print("\n5 лучших квасов по комплексному рейтингу:")
    for item in best_kvas:
        print(f"{item['title']} - Цена за литр: {item['price_per_liter']:.2f} руб, Рейтинг: {item['rating']:.2f}")

    print("\n5 худших квасов по комплексному рейтингу:")
    for item in worst_kvas:
        print(f"{item['title']} - Цена за литр: {item['price_per_liter']:.2f} руб, Рейтинг: {item['rating']:.2f}")

analyze_kvas()

def update_kvas_data():
    with app.app_context():
        try:
            db.session.query(BestAndWorstKvas).delete()
            db.session.commit()
            print(f"Старые данные удалены. Перезапуск парсинга...")
            analyze_kvas()
            print("Данные успешно обновлены.")
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка при обновлении данных: {e}")





def start_scheduler():
    scheduler = BackgroundScheduler()

    scheduler.add_job(update_kvas_data, 'interval', hours=6)

    scheduler.start()

    print("Планировщик задач запущен. Задачи будут выполняться каждые 6 часов.")

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()




def schedule_task():
    schedule.every(6).hours.do(update_and_scrape)
    schedule.every(6).hours.do(update_all_data)

    while True:
        schedule.run_pending()
        time.sleep(1)

def start_schedule_thread():
    thread = threading.Thread(target=schedule_task)
    thread.daemon = True
    thread.start()


@app.route('/attractions')
@login_required
def attractions():
    massive_for_itog_distraction = []
    best_and_worst_kvas = BestAndWorstKvas.query.all()

    litrazh_pattern = r"(\d+[\.,]?\d*)\s*л"

    kvas_by_volume = {}


    for item in filtared_kvas:
        match = re.search(litrazh_pattern, item['title'])
        if match:
            volume = match.group(1).replace(',', '.')
            volume = float(volume)

            if volume not in kvas_by_volume:
                kvas_by_volume[volume] = []

            kvas_by_volume[volume].append(item['price'])

            massive_for_itog_distraction.append({
                'title': item['title'],
                'price': item['price'],
                'volume': volume
            })

    volume_medians = {}
    for volume, prices in kvas_by_volume.items():
        volume_medians[volume] = statistics.median(prices)

    cheaper_alternatives = {}
    for item in massive_for_itog_distraction:
        volume = item['volume']
        median_price = volume_medians[volume]
        if item['price'] > median_price:
            alternatives = [
                alt for alt in massive_for_itog_distraction
                if alt['volume'] == volume and alt['price'] < item['price']
            ]
            if alternatives:
                cheaper_alternatives[item['title']] = alternatives

    return render_template(
        'attractions.html',
        kvas_list=massive_for_itog_distraction,
        best_and_worst_kvas=best_and_worst_kvas,
        volume_medians=volume_medians,
        cheaper_alternatives=cheaper_alternatives
    )
@app.route('/get_best_kvas')
def get_best_kvas():
    best_kvas = BestAndWorstKvas.query.order_by(BestAndWorstKvas.best).limit(5).all()

    best_kvas_list = []
    for kvas in best_kvas:
        best_kvas_list.append({
            'title': kvas.best,
            'price_per_liter': 'Неизвестно',
            'rating': 'Неизвестно'
        })

    return jsonify({'best': best_kvas_list})

@app.route('/get_worst_kvas')
def get_worst_kvas():
    # Сортируем по названию кваса "worst"
    worst_kvas = BestAndWorstKvas.query.order_by(BestAndWorstKvas.worst).limit(5).all()

    # Формируем список с нужной информацией
    worst_kvas_list = []
    for kvas in worst_kvas:
        worst_kvas_list.append({
            'title': kvas.worst,  # Название худшего кваса
            'price_per_liter': 'Неизвестно',  # Пока не добавляем реальные данные
            'rating': 'Неизвестно'  # Можно добавить рейтинг, если будет обработка
        })

    return jsonify({'worst': worst_kvas_list})
@app.route('/nature')
@login_required
def nature():
    nature_places = SavedNatureOfPskov.query.all()
    itog = FinalRouteInformation.query.all()


    best_reviews = BestAndWorst.query.limit(5).all()
    worst_reviews = BestAndWorst.query.offset(5).limit(5).all()

    # Передаем данные в шаблон
    return render_template('nature.html',
                           nature_places=nature_places,
                           itog=itog,
                           best_reviews=best_reviews,
                           worst_reviews=worst_reviews)

def add_to_schedule():
    schedule.every().day.at("09:00").do(update_and_scrape)

add_to_schedule()
if __name__ == '__main__':
    schedule.every().day.at("09:00").do(analyze_kvas)
    app.run(debug=True, host='0.0.0.0', port=5000)

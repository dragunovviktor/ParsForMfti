from random import random

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from models import db, User, Place, SavedPlace, SavedRestaurant, SavedNatureOfPskov, FinalRouteInformation, SavedHotels, BestAndWorst
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


@app.route('/attractions')
@login_required
def attractions():
    places = Place.query.all()
    return render_template('attractions.html', places=places)

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


# Получаем данные с 18 страниц
all_hotels = []

for page_number in range(1, 19):  # Страницы от 1 до 18
    url = f"https://ostrovok.ru/hotel/russia/pskov/?page={page_number}"
    hotels_info = fetch_hotels_info(url)
    print(hotels_info)
    all_hotels.extend(hotels_info)  # Добавляем информацию о гостиницах в общий список

# Преобразуем цены в список чисел (в рублях)
prices_rub = []
ratings = []
for hotel in all_hotels:
    try:
        # Обрабатываем цену
        price_rub = hotel['Цена'].replace(' ', '')
        price_rub = int(price_rub)  # Преобразуем цену в число

        # Обрабатываем рейтинг
        rating = hotel['Рейтинг']
        prices_rub.append(price_rub)
        ratings.append(rating)
    except ValueError:
        continue

# Используем numpy для медианы
median_price = np.median(prices_rub)

print(f"Медиана по ценам: {median_price} ₽")

# 2. Подбор гостиницы с наименьшей ценой и наибольшим рейтингом
# Используем numpy для сортировки


ratings = [float(rating.replace(',', '.')) if rating != 'Нет рейтинга' else np.nan for rating in ratings]

ratings = np.array(ratings, dtype=np.float64)

prices_rub = np.array(prices_rub, dtype=np.float64)

hotels_array = np.array(list(zip(prices_rub, ratings, all_hotels)))

print(f"Цены: {prices_rub[:5]}, Рейтинги: {ratings[:5]}")

price_rating_ratio = hotels_array[:, 0] / hotels_array[:, 1]

hotels_with_ratio = np.column_stack((hotels_array, price_rating_ratio))

sorted_by_ratio = hotels_with_ratio[hotels_with_ratio[:, 3].argsort()]

best = []
for hotel in sorted_by_ratio[:5]:
    price_in_usd = hotel[0] / 107  # Переводим в доллары
    best.append(f"Название: {hotel[2]['Название']}, Цена: {hotel[0]} ₽ ({price_in_usd:.2f} $), Рейтинг: {hotel[1]}, Соотношение цена/рейтинг: {hotel[3]:.2f}")

worst = []
for hotel in sorted_by_ratio[-5:]:
    price_in_usd = hotel[0] / 107
    worst.append(f"Название: {hotel[2]['Название']}, Цена: {hotel[0]} ₽ ({price_in_usd:.2f} $), Рейтинг: {hotel[1]}, Соотношение цена/рейтинг: {hotel[3]:.2f}")

best_hotels_names = [hotel.split(",")[0].split(":")[1].strip() for hotel in best]
worst_hotels_names = [hotel.split(",")[0].split(":")[1].strip() for hotel in worst]

worst_filtered = [hotel for hotel in worst if hotel.split(",")[0].split(":")[1].strip() not in best_hotels_names]

print("Лучшие отели:")
for entry in best:
    print(entry)

print("\nХудшие отели:")
for entry in worst_filtered:
    print(entry)
print(ratings)
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


# Вызов функции с данными
print(ratings)
save_hotels_to_db(all_hotels, prices_rub, ratings)


def save_best_and_worst(best, worst):
    with app.app_context():
        for b, w in zip(best, worst):
            try:
                best_and_worst_data = {
                    'best': b,
                    'worst': w
                }

                stmt = insert(BestAndWorst).values(best_and_worst_data).on_conflict_do_nothing(index_elements=['best', 'worst'])
                db.session.execute(stmt)

            except Exception as e:
                print(f"Error processing best/worst data: {e}")

        db.session.commit()
        print("Лучшие и худшие гостиницы сохранены в базу")


save_best_and_worst(best, worst)

def save_best_and_worst(best, worst):
    with app.app_context():
        for b, w in zip(best, worst):
            try:
                # Prepare data for insertion
                best_and_worst_data = {
                    'best': b,
                    'worst': w
                }

                new_entry = BestAndWorst(**best_and_worst_data)

                db.session.add(new_entry)

            except Exception as e:
                print(f"Error processing best/worst data: {e}")

        # Commit the changes
        db.session.commit()
        print("Лучшие и худшие гостиницы")


save_best_and_worst(best, worst)
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

def schedule_task():
    schedule.every(6).hours.do(update_and_scrape)

    while True:
        schedule.run_pending()
        time.sleep(1)

def start_schedule_thread():
    thread = threading.Thread(target=schedule_task)
    thread.daemon = True
    thread.start()


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
    app.run(debug=True, host='0.0.0.0', port=5000)
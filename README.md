# Pleskov Tourist Guide

## 📋 О проекте
**Pleskov Tourist Guide** — это туристический портал для путешественников по Пскову. Проект предлагает:
- Подробную информацию о ресторанах и достопримечательностях города
- Рейтинг лучших и худших товаров (например, квасов)
- Аналитику по отелям и их выгодности
- Полностью рабочий функционал регистрации и сохранения предпочтений

Проект выполнен с использованием **Flask**, базы данных **PostgreSQL**, а также включает парсинг и аналитические алгоритмы.

---

## 📌 Оглавление
1. [Запуск проекта](#%D0%B7%D0%B0%D0%BF%D1%83%D1%81%D0%BA-%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0)
2. [Основные разделы](#%D0%BE%D1%81%D0%BD%D0%BE%D0%B2%D0%BD%D1%8B%D0%B5-%D1%80%D0%B0%D0%B7%D0%B4%D0%B5%D0%BB%D1%8B)
   - [Home](#home)
   - [Register](#register)
   - [Restaurants](#restaurants)
   - [Attractions (Квасы)](#attractions-%D0%BA%D0%B2%D0%B0%D1%81%D1%8B)
   - [Nature](#nature)
   - [Events](#events)
3. [Алгоритмы и формулы](#%D0%B0%D0%BB%D0%B3%D0%BE%D1%80%D0%B8%D1%82%D0%BC%D1%8B-%D0%B8-%D1%84%D0%BE%D1%80%D0%BC%D1%83%D0%BB%D1%8B)
4. [Скриншоты проекта](#%D1%81%D0%BA%D1%80%D0%B8%D0%BD%D1%88%D0%BE%D1%82%D1%8B-%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0)
5. [Контакты](#%D0%BA%D0%BE%D0%BD%D1%82%D0%B0%D0%BA%D1%82%D1%8B)

---

## 🚀 Запуск проекта

### Требования
- **Python** (3.8+)
- **MongoDB** (база данных)
- Flask и необходимые зависимости

### Шаги запуска
1. **Склонируйте репозиторий**
   ```bash
   git clone https://github.com/your-repo/pleskov-tourist-guide.git
   cd pleskov-tourist-guide
   ```

2. **Запустите скрипт сборки**
   ```bash
   ./build.sh
   ```
   Дождитесь завершения всех миграций и запуска сервера.

3. **Откройте браузер**
   Перейдите по ссылке [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## 🌟 Основные разделы

### 🏠 Home
На главной странице представлена основная информация о сервисе.
![Главная страница](https://github.com/user-attachments/assets/070993ee-8313-4cf8-988d-aca1a29646c0)

### 🔒 Register
Форма регистрации позволяет создать пользователя и сохранить данные в БД.
![Страница регистрации](https://github.com/user-attachments/assets/b3a3730c-49f8-4d2b-a05d-c3b898ec2cc8)

### 🍽 Restaurants
- Статичные карточки ресторанов
- Возможность сохранить выбранный ресторан в личный профиль
![Restaurants](https://github.com/user-attachments/assets/88755809-4789-4c95-a8e6-0ec0be4a7668)

### 🧬 Attractions (Квасы)
Функционал:
1. Парсинг данных о квасах
2. Алгоритм для определения **лучших** и **худших** квасов по цене и характеристикам
3. Калькулятор цены за миллилитр с предложением **более выгодных** квасов

**Лучшие квасы**:
![Лучшие квасы](https://github.com/user-attachments/assets/29a39e3e-3fa1-40de-80c9-c66eba24e50f)

**Худшие квасы**:
![Худшие квасы](https://github.com/user-attachments/assets/005342e3-d2ef-4464-963f-78a86238e730)

### 🌳 Nature
- Парсинг достопримечательностей и отелей
- Построение графиков цен на гостиницы
- Определение **5 лучших** и **5 худших** отелей
![Nature](https://github.com/user-attachments/assets/b65f6c8d-8494-48da-ba4f-ad6170755f6c)

### 🎉 Events
Раздел находится в разработке и носит визуальный характер.
![Events](https://github.com/user-attachments/assets/84efde46-5bd2-4fef-aaf5-04af4e428934)

---

## 🔢 Алгоритмы и формулы
**Рейтинг квасов** рассчитывается по следующей формуле:

```
Рейтинг_финальный = (Рейтинг_товара * 0.3) + 
                     (1 - abs(Цена_за_литр - Средняя_цена) / Стандартное_отклонение) + 
                     (1 / Цена_за_литр)
```

Где:
- **Цена за литр** рассчитывается для каждого кваса
- Данные нормализуются для нахождения выгодности относительно медианы

---

## 🖼 Скриншоты проекта
| Раздел             | Скриншот                                                                 |
|--------------------|-------------------------------------------------------------------------|
| Главная страница   | ![Home](https://github.com/user-attachments/assets/070993ee-8313-4cf8-988d-aca1a29646c0) |
| Регистрация        | ![Register](https://github.com/user-attachments/assets/b3a3730c-49f8-4d2b-a05d-c3b898ec2cc8) |
| Restaurants        | ![Restaurants](https://github.com/user-attachments/assets/88755809-4789-4c95-a8e6-0ec0be4a7668) |
| Лучшие квасы       | ![Best Kvass](https://github.com/user-attachments/assets/29a39e3e-3fa1-40de-80c9-c66eba24e50f) |
| Худшие квасы       | ![Worst Kvass](https://github.com/user-attachments/assets/005342e3-d2ef-4464-963f-78a86238e730) |
| Достопримечательности | ![Nature](https://github.com/user-attachments/assets/b65f6c8d-8494-48da-ba4f-ad6170755f6c) |

---


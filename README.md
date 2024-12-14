1) Сборка проекта осуществляется с помощью скрипта build.sh, необходимо дождаться полной отработки скрипта с учетом всех миграций, результатом должен быть поднятый flask сервер на локальном хосте 127.0.0.1:5000.
![говно](https://github.com/user-attachments/assets/2f154e24-6baf-4c41-a706-42aba00a4341)
2) Переходим в браузере по следующей ссылке http://localhost:5000/
![Главная страница](https://github.com/user-attachments/assets/46c3c73c-1c65-4237-bf88-acb14cb6dc8a)
Результатом должна быть страница home, где есть основная информация о сервисе.
3) Далее необходимо пройти регистрацию на портале, переходим в навбаре в блок Register.
![Внесенные поля в страницу регистрации](https://github.com/user-attachments/assets/1a68f6ff-be19-4c5d-af36-e4072a1ae110)
Результатом является страница регистрации с полностью рабочим функционалом, вводим необходимые данные в поля. Данные должны быть сохранены в БД.
4) На вкладке Restaurants отображены основные рестораны Пскова (эти данные прописаны чисто в html, это чисто для общего вида сайта, карточки можно сохранять, после нажатия кнопки “Сохранить” данные будут сохранены в бд и будут свзяанны с конкретным user.
![вкладка restaurants](https://github.com/user-attachments/assets/873fc9ba-7e91-40a7-8c6c-adec6037ad64)


6) Вклада с парсингом и обработкой данных (attractions).
На странице представлен функционал, который берет данные с сайта с квасами и обрабатывает их следующим образом: он выстраивает рейтинг квасов по цене математического отклонения, некоторых других характеристик из теории случайных величин и математической статистики, по этим параметрами определяются 5 лучших квасов, и 5 худший квасов. Рассчет идет на то, что КВАС - традиционно русский напиток, и любой русский человек при приезде в русский город захочет испить русского напитка, и тут он может узнать о лучших квасах
![Вкладка Attractions](https://github.com/user-attachments/assets/6fd91d67-8f81-450c-9a97-8d20b45fe9a6)
При нажатии кнопки Лучшие квасы 
![лучшие квасы](https://github.com/user-attachments/assets/d44923a6-f306-4e3c-be17-6467677d353d)
При нажатии кнопки Худшие квасы
![худшие квасы](https://github.com/user-attachments/assets/bd30ef4b-5364-4150-ac91-56f66ce42ede)
Данные обрабатываются с парсера, сохраняются в базу, и подтягиваются из базы данных.
При нажатии кнопки Хочу купить квас по миллилитражу (открывается интерфейс с выбором квасов и возможностью высчитать цены квасов за миллилитры, которые укажет пользователь, алгоритм сам просчитывает цену каждого кваса за миллилитр и использует это в расчетах, более того, если есть более выгодные квасы, он предлагает их).
![1](https://github.com/user-attachments/assets/f8c9dc60-32c3-4137-b470-88f373bdfafa)
![2](https://github.com/user-attachments/assets/e107ba3e-bd61-4ff1-8740-b388bc069b04)


![3](https://github.com/user-attachments/assets/f266e3f5-5c22-4771-bd59-8ede4ec32355)

8) Вкладка events на данный момент не доработана и носит чисто визуальный характер
![events](https://github.com/user-attachments/assets/e4d8fab4-c046-4d65-b60a-e5246b058646)
9) Вкладка nature
Данные сверху парсятся с сайта с достопримечательностями Пскова.
По данным с других сайтов парсятся гостиницы, по ценам строится график, снизу в результате вычисления рейтинга алгоритмом определяются 5 лучших и 5 худший отелей получаемых с парсеров. Все данные также сохраняются и получаются

![вкладка nature 1](https://github.com/user-attachments/assets/4f909523-ac94-4a92-8371-289be37c7e53)

![nature 2](https://github.com/user-attachments/assets/f0990204-0e69-454b-949e-8cca2e8206ae)

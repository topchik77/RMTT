# Инструкция по развертыванию чат-бота

## Вариант 1: Быстрый способ через ngrok (для тестирования)

### Шаги:

1. **Установите ngrok** (если еще не установлен):
   - Скачайте с https://ngrok.com/download
   - Или через npm: `npm install -g ngrok`

2. **Запустите бэкенд сервер**:
   ```bash
   cd mental_health_chatbot/backend
   pip install -r requirements.txt
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

3. **В новом терминале запустите ngrok**:
   ```bash
   ngrok http 8000
   ```

4. **Скопируйте HTTPS URL** из ngrok (например: `https://abc123.ngrok.io`)

5. **Обновите frontend/script.js**:
   - Откройте `frontend/script.js`
   - Найдите строку с `const API_URL` и замените на:
   ```javascript
   const API_URL = 'https://ваш-ngrok-url.ngrok.io';
   ```

6. **Загрузите frontend на GitHub Pages или используйте другой хостинг**:
   - Или используйте ngrok и для frontend (запустите локальный веб-сервер)

7. **Поделитесь ссылкой** на frontend с друзьями!

---

## Вариант 2: Развертывание на облачных сервисах

### Railway (рекомендуется - бесплатный тариф)

1. Зарегистрируйтесь на https://railway.app
2. Создайте новый проект
3. Подключите GitHub репозиторий
4. Выберите папку `backend` как корневую
5. Railway автоматически определит Python и установит зависимости
6. Добавьте переменную окружения `PORT` (Railway установит автоматически)
7. Обновите команду запуска: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Render

1. Зарегистрируйтесь на https://render.com
2. Создайте новый Web Service
3. Подключите репозиторий
4. Укажите:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Render предоставит URL вида `https://your-app.onrender.com`

### Heroku

1. Установите Heroku CLI
2. В папке `backend` создайте `Procfile`:
   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
3. Выполните:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

---

## Вариант 3: Развертывание на собственном сервере

1. **Загрузите файлы на сервер** (через FTP, SCP, или Git)

2. **Установите зависимости**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Настройте веб-сервер** (Nginx + Gunicorn/Uvicorn):
   ```bash
   # Установите Nginx
   sudo apt install nginx
   
   # Настройте reverse proxy для порта 8000
   ```

4. **Запустите приложение как сервис** (systemd):
   ```bash
   # Создайте файл /etc/systemd/system/chatbot.service
   ```

5. **Обновите frontend/script.js** с URL вашего сервера

---

## Настройка Frontend

После развертывания бэкенда:

1. Откройте `frontend/script.js`
2. Найдите строку с `API_URL` и замените на URL вашего бэкенда:
   ```javascript
   const API_URL = 'https://ваш-бэкенд-url.com';
   ```

3. Загрузите frontend на:
   - GitHub Pages (бесплатно)
   - Netlify (бесплатно)
   - Vercel (бесплатно)
   - Или любой другой хостинг статических файлов

---

## Быстрый тест локально с доступом извне

Если хотите быстро протестировать с друзьями:

1. Узнайте ваш локальный IP: `ipconfig` (Windows) или `ifconfig` (Linux/Mac)
2. Запустите бэкенд: `uvicorn main:app --host 0.0.0.0 --port 8000`
3. Обновите `frontend/script.js`:
   ```javascript
   const API_URL = 'http://ВАШ-IP:8000'; // Например: http://192.168.1.100:8000
   ```
4. Откройте frontend и поделитесь ссылкой
5. Убедитесь, что порт 8000 открыт в файрволе

---

## Важно!

- Для production измените `origins = ["*"]` в `main.py` на конкретные домены
- Добавьте файлы `svm_model.pkl` и `tfidf_vectorizer.pkl` в папку `backend`
- Настройте HTTPS для безопасности
- Рассмотрите использование переменных окружения для конфигурации


# Komek - Mental Health Chatbot

Виртуальный ассистент для поддержки психического здоровья, использующий машинное обучение для анализа эмоционального состояния пользователей.

## Структура проекта

```
mental_health_chatbot/
├── backend/          # FastAPI сервер
│   ├── main.py       # API endpoints
│   ├── chatbot_logic.py  # Логика чат-бота
│   ├── requirements.txt  # Python зависимости
│   ├── svm_model.pkl    # ML модель (добавьте сами)
│   └── tfidf_vectorizer.pkl  # Векторизатор (добавьте сами)
└── frontend/         # Веб-интерфейс
    ├── index.html
    ├── style.css
    └── script.js
```

## Быстрый старт

### Локальная разработка

1. **Установите зависимости**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Добавьте модели**:
   - Поместите `svm_model.pkl` и `tfidf_vectorizer.pkl` в папку `backend/`

3. **Запустите сервер**:
   ```bash
   uvicorn main:app --reload
   ```

4. **Откройте frontend**:
   - Откройте `frontend/index.html` в браузере
   - Или используйте Live Server в VS Code

### Развертывание для друзей

См. файл [DEPLOYMENT.md](DEPLOYMENT.md) для подробных инструкций.

**Быстрый способ через ngrok:**
1. Запустите бэкенд: `uvicorn main:app --host 0.0.0.0 --port 8000`
2. В новом терминале: `ngrok http 8000`
3. Скопируйте HTTPS URL из ngrok
4. Обновите `API_URL` в `frontend/script.js`
5. Загрузите frontend на GitHub Pages или Netlify
6. Поделитесь ссылкой!

## API Endpoints

- `GET /start` - Начать новую беседу
- `POST /chat` - Отправить сообщение и получить ответ

## Технологии

- **Backend**: FastAPI, scikit-learn
- **Frontend**: HTML, CSS, JavaScript
- **ML**: SVM модель для классификации эмоций

## Лицензия

Этот проект создан в образовательных целях.


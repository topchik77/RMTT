document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');

    // Настройка URL API для ngrok
    // Замените на ваш ngrok URL (получите его после запуска: ngrok http 8000)
    const NGROK_URL = 'https://charlott-undatable-presently.ngrok-free.dev';

    const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

    // Используем ngrok URL для production (когда frontend на Netlify)
    // Или localhost для локальной разработки
    let API_URL = isLocalhost ?
        'http://127.0.0.1:8000' // Локальная разработка
        :
        NGROK_URL; // Production через ngrok

    let conversationState = {};
    let retryCount = 0; // Счетчик повторных попыток
    const MAX_RETRIES = 3; // Максимальное количество попыток

    function addMessage(text, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);
        messageElement.textContent = text;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async function postToServer(endpoint, payload) {
        try {
            const response = await fetch(`${API_URL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'ngrok-skip-browser-warning': 'true' // Обход предупреждения ngrok
                },
                body: JSON.stringify(payload)
            });
            if (!response.ok) {
                const errorText = await response.text();
                console.error(`HTTP error! status: ${response.status}, body: ${errorText}`);
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Проверяем, что ответ действительно JSON
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                const text = await response.text();
                if (text.includes('<!DOCTYPE') || text.includes('<html')) {
                    console.warn("Received HTML instead of JSON from ngrok");
                    throw new Error('Ngrok returned HTML instead of JSON. Please try again.');
                }
                throw new Error('Expected JSON but got: ' + contentType);
            }

            return await response.json();
        } catch (error) {
            console.error("Error communicating with server:", error);
            console.error("API_URL:", API_URL);
            console.error("Endpoint:", endpoint);
            console.error("Full error:", error.message);

            // Более понятное сообщение об ошибке
            if (error.message.includes('JSON') || error.message.includes('HTML')) {
                addMessage("Проблема с подключением через ngrok. Попробуйте обновить страницу.", 'bot');
            } else {
                addMessage("Sorry, I'm having trouble connecting. Please check the console for details.", 'bot');
            }
            return null;
        }
    }

    async function startConversation() {
        // Эта функция теперь только обновляет состояние, если сервер доступен
        // Приветствие уже показано при загрузке страницы
        try {
            console.log("Connecting to:", `${API_URL}/start`);
            const response = await fetch(`${API_URL}/start`, {
                headers: {
                    'ngrok-skip-browser-warning': 'true' // Обход предупреждения ngrok
                }
            });

            if (!response.ok) {
                // Если ошибка, просто выходим - приветствие уже показано
                console.warn(`Server returned error status ${response.status}, but greeting is already shown`);
                return;
            }

            // Читаем текст ответа один раз
            const text = await response.text();

            // Проверяем, не HTML ли это (предупреждение ngrok)
            if (text.includes('<!DOCTYPE') || text.includes('<html') || text.trim().startsWith('<')) {
                if (retryCount < MAX_RETRIES) {
                    retryCount++;
                    console.warn(`Received HTML instead of JSON, retrying... (${retryCount}/${MAX_RETRIES})`);
                    await new Promise(resolve => setTimeout(resolve, 2000)); // Ждем 2 секунды
                    return startConversation(); // Рекурсивный вызов
                } else {
                    // После всех попыток просто выходим - приветствие уже показано
                    console.warn("Ngrok warning page detected after retries, but greeting is already shown");
                    return;
                }
            }

            // Пытаемся распарсить как JSON
            let data;
            try {
                data = JSON.parse(text);
            } catch (parseError) {
                // Если не удалось распарсить JSON, просто выходим - приветствие уже показано
                console.warn("Failed to parse JSON response, but greeting is already shown:", parseError);
                console.warn("Response text:", text.substring(0, 200)); // Показываем первые 200 символов для отладки
                return;
            }

            // Сбрасываем счетчик при успешном подключении
            retryCount = 0;

            // Успешно получили данные от сервера
            addMessage(data.reply, 'bot');
            conversationState = data.newState;
        } catch (error) {
            // Любая ошибка - просто выходим, приветствие уже показано
            console.warn("Could not connect to server on startup, but greeting is already shown:", error);
            console.log("Chat will work normally after first message");
        }
    }

    async function handleSend() {
        const message = userInput.value.trim();
        if (!message) return;

        addMessage(message, 'user');
        userInput.value = '';

        const data = await postToServer('/chat', {
            message: message,
            state: conversationState
        });
        if (data) {
            addMessage(data.reply, 'bot');
            conversationState = data.newState;
        }
    }

    sendButton.addEventListener('click', handleSend);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSend();
    });

    // Показываем приветствие сразу, а подключение к серверу делаем в фоне
    const defaultGreeting = "Hello! I'm your virtual mental health assistant. Please, tell me a little about how you've been feeling lately.";
    const defaultState = {
        'turn_count': 0,
        'scores': {
            'anxiety': 0,
            'depression': 0,
            'stress': 0
        }
    };

    // Показываем приветствие немедленно
    addMessage(defaultGreeting, 'bot');
    conversationState = defaultState;

    // Пытаемся подключиться к серверу в фоне (необязательно)
    startConversation().catch(err => {
        // Игнорируем ошибки - приветствие уже показано
        console.log("Background connection attempt failed, but greeting is already shown");
    });
});
document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');

    // Настройка URL API
    // Вариант 1: Автоматическое определение (для локальной разработки)
    const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    let API_URL = isLocalhost ?
        'http://127.0.0.1:8000' :
        window.location.origin.replace(/:\d+$/, '') + ':8000';

    // Вариант 2: Ручная настройка для production (раскомментируйте и укажите ваш URL)
    // API_URL = 'https://your-backend-url.com'; // Замените на URL вашего бэкенда
    // Примеры:
    // API_URL = 'https://your-app.onrender.com';
    // API_URL = 'https://your-app.railway.app';
    API_URL = 'https://charlott-undatable-presently.ngrok-free.dev'; // Ваш ngrok URL

    let conversationState = {};

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
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error("Error communicating with server:", error);
            addMessage("Sorry, I'm having trouble connecting. Please try again later.", 'bot');
        }
    }

    async function startConversation() {
        try {
            const response = await fetch(`${API_URL}/start`);
            const data = await response.json();
            addMessage(data.reply, 'bot');
            conversationState = data.newState;
        } catch (error) {
            console.error("Could not start conversation:", error);
            addMessage("Could not connect to the server. Please ensure it's running.", 'bot');
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

    startConversation();
});
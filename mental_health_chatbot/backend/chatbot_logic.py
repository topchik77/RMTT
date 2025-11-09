import joblib
import random

# Load the model and vectorizer at startup
try:
    model = joblib.load('svm_model.pkl')
    vectorizer = joblib.load('tfidf_vectorizer.pkl')
    print("Model and vectorizer loaded successfully.")
except FileNotFoundError:
    print("Error: Model files not found. Please ensure they are in the backend folder.")
    model = None
    vectorizer = None

# Trigger words for different mental states
TRIGGERS = {
    'anxiety': ['anxiety', 'anxious', 'worried', 'panic', 'scared', 'nervous', 'heart is racing', "can't breathe"],
    'depression': ['sad', 'lonely', 'empty', 'no energy', 'hopeless', 'crying', "don't want to do anything", 'worthless'],
    'stress': ['tired', 'stressed', 'overwhelmed', 'pressure', 'burnout', 'headache', 'everything is irritating'],
    'suicidal': ['want to die', 'no reason to live', 'end my life', 'kill myself', 'hurt myself', 'better off dead']
}

# Keywords for neutral/evasive answers
NEUTRAL_KEYWORDS = ['fine', 'okay', 'good', 'alright', 'nothing', 'not much', 'ok', 'normal']

# Pre-defined responses for the bot
RESPONSES = {
    'greeting': "Hello! I'm your virtual mental health assistant. Please, tell me a little about how you've been feeling lately.",
    'follow_up': [
        "I see. Could you tell me a bit more about that?",
        "Thank you for sharing. Is there anything else on your mind?",
        "That sounds difficult. How long have you been feeling this way?"
    ],
    'neutral_probe': [
        "That's good to hear. And how have things been for you overall recently? Sometimes we can feel 'okay' day-to-day, but still have things weighing on our minds.",
        "I'm glad to hear that. Looking back at the past week or two, has there been anything particularly challenging or rewarding for you?",
        "Okay, thank you for sharing. How would you describe your general mood lately? Has it been consistent, or have you noticed any ups and downs?"
    ],
    'anxiety_advice': "It sounds like you're experiencing a high level of anxiety. Try a grounding technique: name 5 things you can see, 4 things you can touch, 3 things you can hear, 2 things you can smell, and 1 thing you can taste. This can help bring you back to the present moment.",
    'depression_advice': "From what you've described, you may be experiencing symptoms of depression. Please know that you are not alone. Try to do one small thing that used to bring you joy. It's also very important to reach out to a professional for support.",
    'stress_advice': "You're describing a state of significant stress. It's crucial to allow yourself time to rest. Try to set aside at least 15-20 minutes a day for an activity that helps you unwind, like reading or walking. Remember that self-care is a necessity.",
    'emergency': "I hear that you are in immense pain. Your life is incredibly important. Please, reach out for help immediately. Here is the number for a crisis hotline: [INSERT YOUR COUNTRY'S CRISIS HOTLINE NUMBER HERE]. Please, call them now.",
    'default_summary': "Thank you for sharing your feelings. It's important to monitor your well-being. Remember, reaching out for professional help is a sign of strength."
}

def process_message(user_message, conversation_state):
    # 1. Highest priority: Check for emergency triggers
    for word in TRIGGERS['suicidal']:
        if word in user_message.lower():
            return RESPONSES['emergency'], get_initial_state()

    # 2. Update scores based on triggers and the ML model
    for state_key, keywords in TRIGGERS.items():
        for word in keywords:
            if word in user_message.lower():
                conversation_state['scores'][state_key] += 1
    if model and vectorizer:
        try:
            prediction = model.predict(vectorizer.transform([user_message]))[0]
            if prediction.lower() in conversation_state['scores']:
                conversation_state['scores'][prediction.lower()] += 1
            print(f"Model prediction: {prediction}")
        except Exception as e:
            print(f"Error during model prediction: {e}")

    # 3. Decide on the next response based on conversation turn
    response_text = ""
    if conversation_state['turn_count'] == 0:
        is_neutral = any(word in user_message.lower().split() for word in NEUTRAL_KEYWORDS)
        if is_neutral and not any(score > 0 for score in conversation_state['scores'].values()):
            response_text = random.choice(RESPONSES['neutral_probe'])
        else:
            response_text = random.choice(RESPONSES['follow_up'])
    elif conversation_state['turn_count'] < 2:
        response_text = random.choice(RESPONSES['follow_up'])
    else:
        if not any(s > 0 for s in conversation_state['scores'].values()):
            response_text = RESPONSES['default_summary']
        else:
            max_score_state = max(conversation_state['scores'], key=conversation_state['scores'].get)
            advice_key = f"{max_score_state}_advice"
            response_text = RESPONSES.get(advice_key, RESPONSES['default_summary'])
        
        # Reset state after providing a summary
        new_state = get_initial_state()
        new_state['turn_count'] = -1 # Will be incremented to 0
        conversation_state = new_state
        
    conversation_state['turn_count'] += 1
    return response_text, conversation_state

def get_initial_state():
    return {
        'turn_count': 0,
        'scores': {'anxiety': 0, 'depression': 0, 'stress': 0}
    }


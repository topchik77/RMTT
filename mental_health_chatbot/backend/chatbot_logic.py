import joblib
import random
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


vader_analyzer = SentimentIntensityAnalyzer()


try:
    model = joblib.load('svm_model.pkl')
    vectorizer = joblib.load('tfidf_vectorizer.pkl')
    print("Model and vectorizer loaded successfully.")
except FileNotFoundError:
    print("Error: Model files not found. Please ensure they are in the backend folder.")
    model = None
    vectorizer = None


TRIGGERS = {
    'anxiety': [
        # Basic
        'anxiety', 'anxious', 'worried', 'worry', 'worries', 'panic', 'panicked', 'panicking',
        'scared', 'afraid', 'fear', 'fearful', 'frightened', 'nervous', 'nervousness',
        # Physical symptoms
        'heart is racing', 'heart racing', 'racing heart', "can't breathe", 'can\'t breathe',
        'short of breath', 'breathless', 'hyperventilating', 'sweating', 'sweaty palms',
        'shaking', 'trembling', 'dizzy', 'dizziness', 'nausea', 'stomach ache',
        # Emotional states
        'uneasy', 'uneasiness', 'restless', 'restlessness', 'on edge', 'edgy', 'jittery',
        'apprehensive', 'apprehension', 'tense', 'tension', 'stressed', 'overwhelmed',
        'overwhelming', 'dread', 'dreadful', 'terrified', 'terror', 'horrified',
        # Expressions
        'freaking out', 'freak out', 'losing it', 'going crazy', 'can\'t calm down',
        'feeling overwhelmed', 'too much', 'can\'t handle', 'breaking down'
    ],
    'depression': [
        # Basic
        'sad', 'sadness', 'lonely', 'loneliness', 'empty', 'emptiness', 'hopeless', 'hopelessness',
        'worthless', 'worthlessness', 'crying', 'cry', 'tears', 'tearful',
        # Emotional states
        'dejected', 'miserable', 'downcast', 'despair', 'despairing', 'heartbroken', 'heartbreak',
        'grief', 'grieving', 'mournful', 'melancholy', 'melancholic', 'gloomy', 'gloom',
        'down', 'downhearted', 'disheartened', 'discouraged', 'demoralized', 'defeated',
        'depressed', 'depression', 'unhappy', 'unhappiness', 'miserable', 'misery',
        # Energy and motivation
        'no energy', 'no motivation', 'tired', 'exhausted', 'fatigued', 'lethargic', 'lethargy',
        "don't want to do anything", 'don\'t want to do anything', 'can\'t get out of bed',
        'no interest', 'lost interest', 'nothing matters', 'pointless', 'meaningless',
        # Self-perception
        'useless', 'failure', 'failed', 'not good enough', 'not worth it', 'burden',
        'better off without me', 'no one cares', 'alone', 'isolated', 'isolated'
    ],
    'stress': [
        # Basic
        'tired', 'exhausted', 'stressed', 'stress', 'stressing', 'overwhelmed', 'overwhelming',
        'pressure', 'pressured', 'pressuring', 'burnout', 'burnt out', 'burned out',
        # Physical symptoms
        'headache', 'headaches', 'migraine', 'muscle tension', 'sore', 'achy', 'aches',
        'everything is irritating', 'irritated', 'irritable', 'irritation', 'annoyed', 'annoying',
        # Emotional states
        'frustrated', 'frustration', 'frustrating', 'aggravated', 'aggravating',
        'bothered', 'bothered by', 'can\'t relax', 'can\'t unwind', 'wound up',
        'tense', 'tension', 'strained', 'straining', 'under pressure', 'pressed',
        # Work/life balance
        'too much to do', 'too many things', 'can\'t keep up', 'falling behind',
        'deadline', 'deadlines', 'rushed', 'rushing', 'hurried', 'hurrying',
        'no time', 'running out of time', 'behind schedule'
    ],
    'suicidal': [
        'want to die', 'wanting to die', 'wish i was dead', 'wish i were dead',
        'no reason to live', 'no point in living', 'life is not worth living',
        'end my life', 'ending my life', 'end it all', 'ending it all',
        'kill myself', 'killing myself', 'suicide', 'suicidal', 'take my life',
        'hurt myself', 'hurting myself', 'self harm', 'self-harm', 'cutting',
        'better off dead', 'better off without me', 'everyone would be better',
        'no one would miss me', 'world would be better', 'give up', 'giving up'
    ]
}

# Keywords for neutral/evasive answers
NEUTRAL_KEYWORDS = ['fine', 'okay', 'good', 'alright', 'nothing', 'not much', 'ok', 'normal']

# Keywords for uncertain/unknown answers
UNCERTAIN_KEYWORDS = ["don't know", "don't remember", "not sure", "unsure", "i do not know", 
                      "i don't know", "no idea", "can't remember", "forgot", "not certain",
                      "maybe", "perhaps", "possibly", "hard to say", "difficult to say"]

# Pre-defined responses for the bot
RESPONSES = {
    'greeting': "Hello! I'm your virtual mental health assistant. Please, tell me a little about how you've been feeling lately.",
    'follow_up': [
        "I see. Could you tell me a bit more about that?",
        "Thank you for sharing. Is there anything else on your mind?",
        "That sounds difficult. How long have you been feeling this way?",
        "I understand. What do you think might have contributed to these feelings?",
        "Thank you for being open with me. Can you describe what that feels like for you?",
        "I hear you. What helps you feel better when you experience this?",
        "That must be challenging. Have you noticed any patterns or triggers?",
        "I appreciate you sharing that. What's been the hardest part about this?"
    ],
    'uncertain_response': [
        "That's okay, you don't need to have all the answers. Can you tell me more about what you're experiencing right now?",
        "I understand it can be hard to pinpoint. How would you describe your general mood lately?",
        "That's perfectly fine. Sometimes feelings are complex. What's been on your mind recently?",
        "No worries. Let's focus on how you're feeling right now. What's the main thing bothering you?",
        "That's okay. Can you tell me about what's been happening in your life recently?"
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
    if 'scores' not in conversation_state:
        conversation_state = get_initial_state()
    if 'turn_count' not in conversation_state:
        conversation_state['turn_count'] = 0
    if 'last_question' not in conversation_state:
        conversation_state['last_question'] = None
    if 'used_responses' not in conversation_state:
        conversation_state['used_responses'] = []
    

    for key in ['anxiety', 'depression', 'stress']:
        if key not in conversation_state['scores']:
            conversation_state['scores'][key] = 0
    
    # 1. Highest priority: Check for emergency triggers
    for word in TRIGGERS['suicidal']:
        if word in user_message.lower():
            return RESPONSES['emergency'], get_initial_state()

    # 2. Analyze sentiment intensity using VADER
    vader_scores = vader_analyzer.polarity_scores(user_message)
    sentiment_intensity = abs(vader_scores['compound'])  # 0 to 1, higher = more intense
    
    # 3. Update scores based on triggers with intensity weighting
    for state_key, keywords in TRIGGERS.items():
        if state_key == 'suicidal':  # Skip suicidal, it's handled separately
            continue
        for word in keywords:
            if word in user_message.lower():
                if state_key in conversation_state['scores']:
                    # Weight by intensity: strong emotions get higher scores
                    base_score = 1
                    if sentiment_intensity > 0.5:  # Strong emotion
                        base_score = 2
                    elif sentiment_intensity > 0.7:  # Very strong emotion
                        base_score = 3
                    conversation_state['scores'][state_key] += base_score
                    print(f"Trigger '{word}' found for {state_key}, intensity: {sentiment_intensity:.2f}, score: +{base_score}")
    
    # 4. ML model prediction (if available)
    if model and vectorizer:
        try:
            # Transform message to features
            features = vectorizer.transform([user_message])
            
            # Check if feature dimensions match model expectations
            expected_features = model.n_features_in_ if hasattr(model, 'n_features_in_') else None
            actual_features = features.shape[1]
            
            if expected_features and actual_features != expected_features:
                print(f"Warning: Feature dimension mismatch. Model expects {expected_features}, got {actual_features}. Skipping ML prediction.")
                print("This usually means the vectorizer and model were trained with different parameters.")
                print("The bot will continue using keyword-based detection and VADER sentiment analysis.")
            else:
                prediction = model.predict(features)[0]
                if prediction.lower() in conversation_state['scores']:
                    ml_score = 1 if sentiment_intensity < 0.5 else 2
                    conversation_state['scores'][prediction.lower()] += ml_score
                print(f"Model prediction: {prediction}, intensity: {sentiment_intensity:.2f}")
        except ValueError as e:
            if "features" in str(e).lower() or "dimension" in str(e).lower():
                print(f"Feature dimension mismatch: {e}")
                print("The bot will continue using keyword-based detection and VADER sentiment analysis.")
            else:
                print(f"Error during model prediction: {e}")
        except Exception as e:
            print(f"Error during model prediction: {e}")

    # 5. Decide on the next response based on conversation turn and context
    response_text = ""
    user_msg_lower = user_message.lower()
    
 
    is_uncertain = any(keyword in user_msg_lower for keyword in UNCERTAIN_KEYWORDS)
    

    is_neutral = any(word in user_msg_lower.split() for word in NEUTRAL_KEYWORDS)
    

    def get_unique_response(response_list, used_list):
        available = [r for r in response_list if r not in used_list]
        if not available:  # If all used, reset and use all
            available = response_list
            used_list.clear()
        chosen = random.choice(available)
        used_list.append(chosen)
        return chosen
    
    if conversation_state['turn_count'] == 0:

        if is_uncertain:
            response_text = random.choice(RESPONSES['uncertain_response'])
        elif is_neutral and not any(score > 0 for score in conversation_state['scores'].values()):
            response_text = random.choice(RESPONSES['neutral_probe'])
        else:
            response_text = get_unique_response(RESPONSES['follow_up'], conversation_state['used_responses'])
    elif conversation_state['turn_count'] < 3:

        if is_uncertain:
            # If user doesn't know, don't repeat the same question
            if conversation_state['last_question'] and 'how long' in conversation_state['last_question'].lower():
                response_text = get_unique_response(RESPONSES['uncertain_response'], conversation_state['used_responses'])
            else:
                response_text = get_unique_response(RESPONSES['uncertain_response'], conversation_state['used_responses'])
        else:
            # Get a different follow-up question
            response_text = get_unique_response(RESPONSES['follow_up'], conversation_state['used_responses'])
            # Make sure it's different from last question
            if conversation_state['last_question'] == response_text:
                available = [r for r in RESPONSES['follow_up'] if r != response_text]
                if available:
                    response_text = random.choice(available)
    else:
        # End of conversation - provide summary/advice
        if not any(s > 0 for s in conversation_state['scores'].values()):
            response_text = RESPONSES['default_summary']
        else:
            max_score_state = max(conversation_state['scores'], key=conversation_state['scores'].get)
            advice_key = f"{max_score_state}_advice"
            response_text = RESPONSES.get(advice_key, RESPONSES['default_summary'])
        
        # Reset state after providing a summary
        new_state = get_initial_state()
        new_state['turn_count'] = -1 
        conversation_state = new_state
    
    # Track last question to avoid repetition
    conversation_state['last_question'] = response_text
    conversation_state['turn_count'] += 1
    
    return response_text, conversation_state

def get_initial_state():
    return {
        'turn_count': 0,
        'scores': {'anxiety': 0, 'depression': 0, 'stress': 0},
        'last_question': None,
        'used_responses': [] 
    }


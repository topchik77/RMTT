from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from chatbot_logic import process_message, get_initial_state, RESPONSES

app = FastAPI()

# Allow communication from the frontend
origins = ["*"] # For simplicity, allow all. For production, restrict this.
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    state: dict

class ChatResponse(BaseModel):
    reply: str
    newState: dict

@app.post("/chat", response_model=ChatResponse)
def chat_with_bot(request: ChatRequest):
    reply, new_state = process_message(request.message, request.state)
    return ChatResponse(reply=reply, newState=new_state)

@app.get("/start", response_model=ChatResponse)
def start_conversation():
    initial_state = get_initial_state()
    return ChatResponse(reply=RESPONSES['greeting'], newState=initial_state)


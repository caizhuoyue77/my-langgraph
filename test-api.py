from fastapi.testclient import TestClient
from api2 import app  # Assuming the API code is in a file named `main.py`

client = TestClient(app)

def test_store_memory():
    response = client.post("/store-memory", json={
        "user_name": "test_user",
        "bot_name": "test_bot",
        "messages": ["用户：我最讨厌吃榴莲了。。"]
    })
    assert response.status_code == 200
    assert "Memory stored successfully" in response.json()["response"]

def test_retrieve_memory():
    response = client.get("/retrieve-memory")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_chat_with_memory():
    response = client.post("/chat_with_memory", json={"message": "我要去买奶茶，你猜猜我要喝什么?"})
    assert response.status_code == 200
    assert "response" in response.json()
    print(response.json())

test_chat_with_memory()
from fastapi.testclient import TestClient 

from main import app, todos

client = TestClient(app)

def setup_function():
    todos.clear()

#test to verify get call works or not
def test_read_todos():
    response = client.get("/")
    assert response.status_code == 200 
    assert response.json() == [] 

def test_create_todo():
    response = client.post("/", json = {"name": "Buy groceries", "completed" : False})
    assert response.status_code == 200 
    assert response.json() == {"name": "Buy groceries", "completed" : False}

def test_read_todo():
    client.post("/", json = {"name": "Groceries", "completed": False})
    response = client.get("/1")
    assert response.status_code == 200 
    assert response.json() == {"name": "Groceries", "completed": False}

def test_update_todo():
    client.post("/", json = {"name": "Buy Groceries", "completed": False})
    response = client.put("/1", json = {"name": "Buy Vegetables", "completed": False})
    assert response.status_code == 200 
    assert response.json() == {"name": "Buy Vegetables", "completed": False}

def test_delete_todo():
    client.post("/", json = {"name": "Buy Groceries", "completed": False})
    response = client.delete("/1")
    assert response.status_code == 200
    assert response.json() == {"name": "Buy Groceries", "completed": False}

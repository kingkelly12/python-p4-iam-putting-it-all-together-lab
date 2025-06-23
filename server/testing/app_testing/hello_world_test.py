from app import app

def test_hello_world():
    with app.app_context():
        client = app.test_client()
        response = client.get('/hello')
        assert response.status_code == 200
        assert response.data == b'Hello, World!'
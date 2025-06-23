from app import create_app
app = create_app()

def test_hello_world():
    with app.app_context():
        client = app.test_client()
        response = client.get('/hello')
        assert response.status_code == 200
        assert response.data == b'Hello, World!'
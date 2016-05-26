import json
from Crypto.Cipher import AES


def test_no_session(http_client, server):
    server()
    c = http_client()
    response = c.get('/')
    assert response.status == 401


def test_start_session(http_client, server):
    server()
    c = http_client()
    init_params = {'client_name': 'test'}
    response = c.post('/auth', data=init_params)
    assert response.status == 200

    response_json = json.loads(response.read())
    assert 'challenge' in response_json

    challenge = response_json['challenge']
    text = challenge['text']
    iv = challenge['cipher_iv']
    cipher_text = AES.new('This is a key123', AES.MODE_CBC, iv).encrypt(text)
    response = init_params.copy()
    response['id'] = challenge['id']
    response['encrypted_text'] = cipher_text
    response['duration'] = 10
    response = c.post('/auth_verify', response)
    assert response.status == 200

    response_json = json.loads(response.read())
    assert response_json['success']
    session = response_json['session']
    assert 'duration' in session and 'token' in session

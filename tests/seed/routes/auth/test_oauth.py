from unittest.mock import patch
from seed.models import UserLoginHistoryModel


@patch('seed.oauth.kakao.KakaoOAuthHandler.get_tokens', return_value=('access', 'refresh'))
@patch('seed.oauth.kakao.KakaoOAuthHandler.get_user_info', return_value=('1', 'test@foobar.com'))
def test_oauth_get_tokens(get_tokens, get_user_info, client):
    response = client.post('/api/oauth', json={
        'provider': 'kakao',
        'code': 'code'
    })

    login_history = UserLoginHistoryModel.q_user_id(1)\
        .order_by(UserLoginHistoryModel.id.desc())\
        .first()

    assert response.status_code == 201
    assert login_history.success is True


@patch('seed.oauth.kakao.KakaoOAuthHandler.get_tokens', return_value=('access', 'refresh'))
@patch('seed.oauth.kakao.KakaoOAuthHandler.get_user_info', return_value=('9999999', 'test@foobar.com'))
def test_oauth_social_account_not_exists(get_tokens, get_user_info, client):
    response = client.post('/api/oauth', json={
        'provider': 'kakao',
        'code': 'code'
    })

    assert response.status_code == 404
    assert response.json()['email'] == 'test@foobar.com'


def test_oauth_not_supported_provider(client):
    response = client.post('/api/oauth', json={
        'provider': 'not_supported',
        'code': 'code'
    })

    # assert response.status_code == 400
    print(response.json())
    # assert response.json()['symbol'] == 'oauth_not_supported'

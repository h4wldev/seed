from unittest.mock import patch

from db import db

from seed.models import (
    UserModel,
    UserSocialAccountModel
)


@patch('seed.oauth.kakao.KakaoOAuthHandler.get_tokens', return_value=('access', 'refresh'))
@patch('seed.oauth.kakao.KakaoOAuthHandler.get_user_info', return_value=('1', 'test@foobar.com'))
def test_oauth_get_tokens(get_tokens, get_user_info, dummy_record, client):
    with db(commit_on_exit=False):
        with dummy_record(UserModel(email='test@foobar.com', username='foobar')) as dummy:
            social_account_model = UserSocialAccountModel(
                user_id=dummy[0].id,
                social_id='1',
                provider='kakao'
            )

            with dummy_record(social_account_model):
                response = client.post('/api/oauth', json={
                    'provider': 'kakao',
                    'code': 'code'
                })

                assert response.status_code == 201


@patch('seed.oauth.kakao.KakaoOAuthHandler.get_tokens', return_value=('access', 'refresh'))
@patch('seed.oauth.kakao.KakaoOAuthHandler.get_user_info', return_value=('1', 'test@foobar.com'))
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

    assert response.status_code == 400
    assert response.json()['detail'] == "'not_supported' is not support provider"

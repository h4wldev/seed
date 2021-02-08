
def test_user_me_get_information(client, create_token):
    token = create_token(
        subject='test@foobar.com'
    )

    response = client.get('/api/users/me', headers={
        'Authorization': f'Bearer {token.credential}'
    })

    assert response.json() == {
        'email': 'test@foobar.com',
        'username': 'test',
        'profile': {
            'display_name': 'Maud'
        },
        'meta': {
            'email_promotion': True,
            'email_notification': False,
            'is_certified': True
        },
        'social_accounts': ['kakao']
    }

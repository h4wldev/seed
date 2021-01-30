from seed.utils.crypto import AESCipher


def test_aes_cipher_encrypt_and_decrypt():
    aes_cipher = AESCipher()
    encrypted = aes_cipher.encrypt('foobar')

    assert aes_cipher.decrypt(encrypted) == 'foobar'

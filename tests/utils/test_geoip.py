from seed.utils.geoip import GeoIP


def test_geoip_init():
    geoip = GeoIP(ip='220.0.0.1')
    geoip_not_exists = GeoIP(ip='127.0.0.1')

    assert geoip.match
    assert not geoip_not_exists.match


def test_geoip_country():
    geoip = GeoIP(ip='220.0.0.1')
    geoip_not_exists = GeoIP(ip='127.0.0.1')

    assert geoip.country
    assert not geoip_not_exists.country


def test_geoip_city():
    geoip = GeoIP(ip='220.0.0.1')
    geoip_not_exists = GeoIP(ip='127.0.0.1')

    assert geoip.city
    assert not geoip_not_exists.city

from app.matching import normalize_phone_list


def test_phone_normalization():
    phones = ["083 123 4567", "27831234567", "0831234567.0", "123"]
    cleaned = normalize_phone_list(phones)
    assert cleaned == ["0831234567"]

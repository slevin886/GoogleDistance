from google_distance import GoogleDistance

search_parameters = {}


def test_prep_location_entry():
    dist = GoogleDistance('an_api_key')
    location, expected = '123 Fake   Street Boston MA', '123+Fake+Street+Boston+MA'
    result = dist.prep_location_entry(location)
    assert result == expected

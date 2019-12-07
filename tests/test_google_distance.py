"""
Testing GoogleDistance methods that don't require API calls
"""

from google_distance.get_travel_times import GoogleDistance
import pytest

search_parameters = {}


def test_prep_location_entry():
    dist = GoogleDistance('an_api_key')
    location, expected = '123 Fake   Street, Boston MA', '123+Fake+Street+Boston+MA'
    result = dist.prep_location_entry(location)
    assert result == expected
    location, expected = ['Boston MA', 'New  ,York'], 'Boston+MA|New+York'
    result = dist.prep_location_entry(location)
    assert result == expected
    with pytest.raises(AttributeError):
        dist.prep_location_entry(123)


def test_write_query_string():
    dist = GoogleDistance('an_api_key', units='metric')
    expected = 'origins=Boston+MA&destinations=Chicago+IL&mode=driving&key=an_api_key&' \
               'departure_time=now&language=en&units=metric&traffic_model=best_guess'
    query_string = dist.write_query_string('Boston MA', 'Chicago IL', departure_time='now')
    assert query_string.split('?')[1] == expected
    with pytest.raises(ValueError):  # can't specify both departure & arrival times
        dist.write_query_string('Boston MA', 'Chicago IL', departure_time='now', arrival_time='now')


def test_google_distance_init():
    with pytest.raises(TypeError):
        dist = GoogleDistance()
    with pytest.raises(ValueError):
        dist = GoogleDistance('an_api_key', mode='walking', transit_mode='bus')

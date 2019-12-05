"""
These tests only run properly if you have an active google api key set to the environment
variable API_KEY='your_api_key'
"""
import os
from google_distance.get_travel_times import GoogleDistance
from google_distance.data_classes import Driving

API_KEY = os.getenv('API_KEY')


def test_sync_run_basic():
    dist = GoogleDistance(API_KEY, units='metric')
    result = dist.run('Boston, MA, USA', 'New York, New York')
    assert isinstance(result, Driving)
    assert result.status == 'OK' and result.success
    assert dist.valid_attributes['departure_time'] == 'now'
    assert isinstance(result.meters, int) and isinstance(result.feet, float)
    assert result.feet == round(result.meters * 0.3408, 2)

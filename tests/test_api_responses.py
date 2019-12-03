from google_distance.data_classes import Driving

DRIVING_API_RESPONSE = {
    "destination_addresses": ["New York, NY, USA"],
    "origin_addresses": ["Boston, MA, USA"],
    "rows": [
        {
            "elements": [
                {
                    "distance": {"text": "217 mi", "value": 348700},
                    "duration": {"text": "3 hours 48 mins", "value": 13684},
                    "duration_in_traffic": {"text": "4 hours 20 mins", "value": 15570},
                    "status": "OK",
                }
            ]
        }
    ],
    "status": "OK",
}


def test_driving_instantiation():
    travel = Driving(DRIVING_API_RESPONSE)
    assert travel.status == 'OK' and travel.success
    assert travel.duration == 13684
    assert travel.distance == 348700

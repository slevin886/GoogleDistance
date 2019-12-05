"""
Data Classes that store and parse data from Google API calls.

There are four possible transportation modes for the API: Driving, Walking, Bicycle, Transit.
Each mode is represented by its own class that inherits from TravelTime. For each class,
You can see if the api call was successful by checking self.success (bool) and if False, you can see why
using self.status.
"""
from datetime import datetime


class TravelTime:
    """
    Base data parsing and storage class for Google Distance API response JSON.
    Child classes implement parse_mode_json to get mode specific attributes.

    Should only be used with a single origin - destination query response.
    """
    def __init__(self, json_response, **kwargs):
        self.json_response = json_response
        self.utc_time_created = datetime.utcnow()
        self.success = False
        self.status = 'Not parsed'
        self.origin = ''
        self.destination = ''
        self.distance = None
        self.duration = None
        self.__dict__.update(kwargs)
        self.parse_general_json()

    def parse_general_json(self):
        status = self.json_response.get('status')
        if status != 'OK':
            self.status = status
            return
        try:
            self.origin = self.json_response.get('origin_addresses')[0]
            self.destination = self.json_response.get('destination_addresses')[0]
            elements = self.json_response.get('rows')[0].get('elements')[0]
            if elements['status'] == 'OK':
                self.distance = elements['distance']['value']
                self.duration = elements['duration']['value']
                self.status = 'OK'
                self.success = True
            else:
                self.status = elements['status']
        except KeyError as error:
            self.status = f'JSON not fully valid. Key Error: {error}'
        except IndexError as error:
            self.status = f'JSON not fully valid, index error: {error}'

    def parse_mode_json(self):
        raise NotImplementedError('parse_mode_json is a mode specific function implemented by child classes')

    @property
    def feet(self):
        """
        Returns travel distance in feet (rounded to two decimal places)
        :return: travel distance in feet
        """
        return round(self.distance * 0.3408, 2)

    @property
    def miles(self):
        """
        Returns travel distance in miles (rounded to two decimal places)
        :return: travel distance in miles
        """
        return round(self.distance * 1609.344, 2)

    @property
    def meters(self):
        """
        Returns travel distance in meters
        :return: travel distance in meters as float
        """
        return self.distance

    def __str__(self):
        return f"Origin: {self.origin}, Destination: {self.destination}, Status: {self.status}"

    def __repr__(self):
        return f"Origin: {self.origin}, Destination: {self.destination}, Status: {self.status}"


class Driving(TravelTime):
    """
    Data Storage & Parsing when mode = 'driving'
    """
    def __init__(self, json_response, **kwargs):
        super().__init__(json_response, **kwargs)
        self.mode = 'driving'
        self.duration_in_traffic = None
        if self.status == 'OK':
            self.parse_mode_json()

    def parse_mode_json(self):
        """
        Sets the attribute for the Driving specific data 'duration_in_traffic'
        """
        try:
            element = self.json_response.get('rows')[0].get('elements')[0]
            self.duration_in_traffic = element['duration_in_traffic']['value']
        except KeyError as error:
            self.status = f'JSON not fully valid. Key Error: {error}'
            self.success = False
        except IndexError as error:
            self.status = f'JSON not fully valid, index error: {error}'
            self.success = False


class Transit(TravelTime):
    """
    Data Storage & Parsing when mode = 'transit'
    """
    def __init__(self, json_response, **kwargs):
        super().__init__(json_response, **kwargs)
        self.mode = 'transit'
        self.currency = 'No fare information available'
        self.cost = 'No fare information available'
        self.cost_text = 'No fare information available'
        if self.status == 'OK':
            self.parse_mode_json()

    def parse_mode_json(self):
        """
        Sets fare values for transit mode.
        Fare information is only infrequently available based on municipality and this will
        most often result in an exception and maintenance of the default fare values.
        """
        try:
            element = self.json_response.get('rows')[0].get('elements')[0]['fare']
            self.currency = element['currency']
            self.cost = element['value']
            self.cost_text = element['text']
        except KeyError:
            pass


class Walking(TravelTime):
    """
    Data Storage & Parsing when mode = 'walking'
    """
    def __init__(self, json_response, **kwargs):
        super().__init__(json_response, **kwargs)
        self.mode = 'walking'
        if self.status == 'OK':
            self.parse_mode_json()

    def parse_mode_json(self):
        pass


class Bicycling(TravelTime):
    """
    Data Storage & Parsing when mode = 'bicycling'
    """
    def __init__(self, json_response, **kwargs):
        super().__init__(json_response, **kwargs)
        self.mode = 'bicycling'
        if self.status == 'OK':
            self.parse_mode_json()

    def parse_mode_json(self):
        pass

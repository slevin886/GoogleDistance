"""
Data Classes that store and parse data from Google API calls
"""


class TravelTime:
    """
    Base data parsing and storage class for Google Distance API response JSON.
    Child classes implement parse_mode_json to get mode specific attributes.

    Should only be used with a single origin - destination query response.
    """
    def __init__(self, json_response, **kwargs):
        self.json_response = json_response
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
        raise NotImplementedError

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
        self.duration_in_traffic = None
        if self.status == 'OK':
            self.parse_mode_json()

    def parse_mode_json(self):
        try:
            elements = self.json_response.get('rows')[0].get('elements')[0]
            self.duration_in_traffic = elements['duration_in_traffic']['value']
        except KeyError as error:
            self.status = f'JSON not fully valid. Key Error: {error}'
            self.success = False
        except IndexError as error:
            self.status = f'JSON not fully valid, index error: {error}'
            self.success = False

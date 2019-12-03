"""
Requires active API Key for the Google Distance Matrix API
"""
# https://developers.google.com/maps/documentation/distance-matrix/intro
# place + between all words in an address in the form of: 24+Sussex+Drive+Ottawa+ON
# separate addresses with |
# all options separate with &
# can also use lat/long which are separated with comma origins=41.43206,-81.38992|-33.86748,151.20699
import asyncio
import aiohttp
import requests
from importlib import import_module


async def get_async_travel_time(session, url):
    """
    Async support function for GoogleDistance's run_async method
    :param session: API request session
    :param url: API url
    :return: API response json
    """
    async with session.get(url) as response:
        return await response.json()


class GoogleDistance:

    def __init__(self, api_key: str, mode='driving', transit_mode=None, transit_routing_preference=None,
                 language: str = 'en', avoid=None, units: str = 'imperial', traffic_model: str = 'best_guess'):
        """
        :param api_key: A valid API key for Google Distance Matrix API.
        :param mode: options are ['driving', 'walking', 'bicycling', 'transit'] w/ transit you can optionally
                     include a 'transit_mode'
        :param transit_mode: options are ['subway', 'bus', 'train', 'tram', 'rail'].
        :param language: default is English 'en'; to set a different language, find the supported languages on google
        :param avoid: bias route selection to avoid [tolls, highways, ferries, indoor].
        :param units: default is 'imperial', alternatively, use 'metric'.
        :param traffic_model: options are ['best_guess', 'pessimistic', 'optimistic'. Only works when mode is 'driving'
                              and a departure_time is used.  #TODO: input class method. Departure_time can only be in the
                              future or the current time. Determines how historical models
                              are used to determine likely traffic level.
        """
        if (transit_mode or transit_routing_preference) and mode != 'transit':
            raise Exception("'mode' must be set to 'transit' to use 'transit_mode' or 'transit_routing_preferences'")
        self.api_key = api_key
        self.units = units
        self.language = language
        self.mode = mode
        self.transit_mode = transit_mode
        self.transit_routing_preference = transit_routing_preference
        self.avoid = avoid
        self.traffic_model = traffic_model
        self._base_url = "https://maps.googleapis.com/maps/api/distancematrix/json?"


    @staticmethod
    def prep_location_entry(location):
        # TODO: see if I need to replace commas
        if isinstance(location, list):
            return '|'.join(['+'.join(loc.replace(',', ' ').split()) for loc in location])
        else:
            return '+'.join(location.replace(',', ' ').split())

    def write_query_string(self, origin, destination, departure_time='now', arrival_time=None, *args, **kwargs):
        """
        Writes the query string for the API call.

        Origins/destinations/key are required parameters of Google's API.
        :param origin: origin can be a string or a list of strings
        :param destination: destination can be a string or a list of strings
        :param departure_time: time to leave
        :param arrival_time: time to arrive
        :return: url string for the API call
        """
        origin = self.prep_location_entry(origin)
        destination = self.prep_location_entry(destination)
        options = f"origins={origin}&destinations={destination}&mode={self.mode}&key={self.api_key}"
        if departure_time and arrival_time:
            raise Exception("Can't set both a departure and arrival time")
        if departure_time:
            options += f"&departure_time={departure_time}"
        if arrival_time:
            options += f"&arrival_time={arrival_time}"
        for attribute in ['language', 'units', 'avoid', 'traffic_model', 'transit_mode', 'transit_routing_preference']:
            if getattr(self, attribute):
                options += f"&{attribute}={getattr(self, attribute)}"
        return self._base_url + options

    @staticmethod
    async def _make_async_calls(urls):
        async with aiohttp.ClientSession() as session:
            data = []
            for url in urls:
                call = asyncio.ensure_future(get_async_travel_time(session, url))
                data.append(call)
            return await asyncio.gather(*data, return_exceptions=True)

    def run_async(self, destination_objects):
        """
        Accepts a list of dictionaries where each dictionary contains, at minimum, the keys
        'origin' and 'destination'.
        :param destination_objects:
        :return:
        """
        url_list = []
        for pair in destination_objects:
            url = self.write_query_string(**pair)
            url_list.append(url)
        travel_times = asyncio.run(self._make_async_calls(url_list))
        data_class_ = getattr(import_module('api_responses'), self.mode.title())
        return [data_class_(time_json) for time_json in travel_times]

    def run(self, origin, destination, departure_time='now', arrival_time=None):
        """
        Runs a single API request and returns a json w/ the results
        :param origin: list of strings or string with origin location
        :param destination: list of strings or string with destination location
        :param departure_time: string departure time
        :param arrival_time: string arrival time- only allowed if departure_time is None
        :return: json of API response data
        """
        url = self.write_query_string(origin, destination, departure_time, arrival_time)
        data_class_ = getattr(import_module('data_classes'), self.mode.title())
        return data_class_(requests.get(url).json())

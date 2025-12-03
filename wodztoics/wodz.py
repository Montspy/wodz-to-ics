import requests

class WODZ:
    _bookings_url: str
    _cookies: dict[str, str]

    def __init__(self, bookings_url: str, cookies: dict[str, str]):
        self._bookings_url = bookings_url
        self._cookies = cookies

    def fetch_bookings(self):
        r = requests.get(self._bookings_url, cookies=self._cookies)
        
        if r.status_code != 200:
            return {}
        
        # print(r.cookies)
        
        return r.json()
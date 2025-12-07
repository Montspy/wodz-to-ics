import json
import requests

class WODZ:
    SEED_COOKIES_PATH = "/cookies/seed_cookies"
    SESSION_COOKIES_PATH = "/cookies/session_cookies"

    _bookings_url: str
    _session: requests.Session
    _current_seed_cookies: str | None

    def __init__(self, bookings_url: str, seed_cookies: str | None = None):
        self._bookings_url = bookings_url
        self._session = requests.session()
        self._current_seed_cookies = seed_cookies or ""
        self.load_cookies()

    def load_cookies(self):
        # Load last session's cookiejar
        try:
            with open(WODZ.SESSION_COOKIES_PATH, "r") as session_cookies_file:
                self._session.cookies.update(json.load(session_cookies_file))
        except FileNotFoundError:
            ...

        # Load last valid seed cookies from file
        try:
            with open(WODZ.SEED_COOKIES_PATH, "r") as seed_cookies_file:
                last_seed_cookies = seed_cookies_file.read()
        except FileNotFoundError:
            last_seed_cookies = ""

        # If new seed cookies provided, use those in session
        if self._current_seed_cookies != last_seed_cookies:
            seed_cookies = dict(
                cookie.strip().split("=")[:2]
                for cookie in self._current_seed_cookies.split(";")
                if (len(cookie.strip("=")) >= 2)
            )

            print(f"Using new seed cookies: {seed_cookies}")
            self._session.cookies.update(seed_cookies)

    def save_cookies(self):
        # Save cookiejar to file for next run
        try:
            with open(WODZ.SESSION_COOKIES_PATH, "w+") as session_cookies_file:
                json.dump(self._session.cookies.get_dict(), session_cookies_file)
        except FileNotFoundError as e:
            print(e)
            print("Is there a volume bound to /cookies ?")

        # Save seed cookies as last valid ones to file
        try:
            with open(WODZ.SEED_COOKIES_PATH, "w+") as seed_cookies_file:
                seed_cookies_file.write(self._current_seed_cookies)
        except FileNotFoundError as e:
            print(e)
            print("Is there a volume bound to /cookies ?")


    def fetch_bookings(self):
        r = self._session.get(self._bookings_url)
        
        if r.status_code != 200:
            return None
        
        if 'application/json' not in r.headers.get('Content-Type', ''):
            return None

        self.save_cookies()  # Save cookiejar and seed cookies only on success
        return r.json()
    


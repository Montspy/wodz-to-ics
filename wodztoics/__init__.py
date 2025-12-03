import os
from dotenv import dotenv_values
from wodz import WODZ

from zoneinfo import ZoneInfo
from datetime import datetime, timezone
from ical.calendar import Calendar
from ical.event import Event
from ical.types import Geo
from ical.calendar_stream import IcsCalendarStream

from geopy.geocoders import Nominatim

def load_config() -> dict[str, ]:
    DEFAULTS = {
        "API_BOOKINGS_URL": "https://wodz.app/subscriber/booking/subscriberNextBookings",
        # "PORT": 3080,
        "COOKIE": "",
        "OUTPUT_ICS": "./wodz.ics"
    }

    config = DEFAULTS

    # Replace only existing keys with os.environ
    config.update({key: os.environ[key] for key in (os.environ.keys() & config.keys())})
    # Replace only existing keys with dotenvs
    dotenvs = dotenv_values(".env")
    config.update({key: dotenvs[key] for key in (dotenvs.keys() & config.keys())})

    # Parse cookies if any
    config["parsed_cookies"] = {cookie.strip().split("=")[0]: cookie.strip().split("=")[1] for cookie in config["COOKIE"].split(";") if (len(cookie.strip("=")) >= 2) }

    print("Parsed config to:")
    print(config)

    return config

def main():
    print("WODZtoICS started")
    config = load_config()

    wodz = WODZ(config['API_BOOKINGS_URL'], config['parsed_cookies'])
    print("Fetching bookings")
    bookings = wodz.fetch_bookings()
    print(f"Got {len(bookings['bookings'])} bookings")

    geolocator = Nominatim(user_agent="WODZtoICS")

    calendar = Calendar()
    for booking in bookings['bookings']:
        if booking['session']['address'] is None:
            entity = booking['session']['business_entity']
            address = f"{entity['Address']} {entity['zipcode']} {entity['city']}"
        else:
            address = booking['session']['address']
        location = geolocator.geocode(address, country_codes=['fr'])

        comment = f"{booking['session']['maxBookingSlots'] - booking['session']['availableBookingSpots']}/{booking['session']['maxBookingSlots']}"

        def utc_to_local(utc_dt: datetime) -> datetime:
            return utc_dt.replace(tzinfo=ZoneInfo("UTC")).astimezone(tz=None)

        event_params = {
            "summary": booking['session']['training_category']['name'],
            "dtstart": utc_to_local(datetime.strptime(booking['session']['start_date'], r"%Y-%m-%d %H:%M:%S")),
            "dtend": utc_to_local(datetime.strptime(booking['session']['end_date'], r"%Y-%m-%d %H:%M:%S")),
            "geo": Geo(location.latitude, location.longitude),
            "comment": [comment],
            "location": address,
        }

        calendar.events.append(
            Event(**event_params),
        )
    
    print(f"Writing calendar file to {config['OUTPUT_ICS']}")

    os.makedirs(os.path.dirname(config['OUTPUT_ICS']), exist_ok=True)
    with open(config['OUTPUT_ICS'], "w+") as ics_file:
        ics_file.write(IcsCalendarStream.calendar_to_ics(calendar))

    print(f"Done. Exiting.")





if __name__ == "__main__":
    main()
import os
from dotenv import dotenv_values
from wodz import WODZ

from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
from ical.calendar import Calendar
from ical.event import Event
from ical.store import EventStore
from ical.calendar_stream import IcsCalendarStream
from ical.exceptions import CalendarParseError

def load_config() -> dict[str, ]:
    DEFAULTS = {
        "API_BOOKINGS_URL": "https://wodz.app/subscriber/booking/subscriberNextBookings",
        "SEED_COOKIE": "",
        "OUTPUT_ICS": "./wodz.ics"
    }

    config = DEFAULTS

    # Replace only existing keys with os.environ
    config.update({key: os.environ[key] for key in (os.environ.keys() & config.keys())})
    # Replace only existing keys with dotenvs
    dotenvs = dotenv_values(".env")
    config.update({key: dotenvs[key] for key in (dotenvs.keys() & config.keys())})

    print("Parsed config to:")
    print(config)

    return config

def main():
    print("WODZtoICS started")
    config = load_config()

    # Load existing ics
    if os.path.exists(config['OUTPUT_ICS']):
        print("Load existing calendar")
        with open(config['OUTPUT_ICS'], "r") as ics_file:
            try:
                calendar = IcsCalendarStream.calendar_from_ics(ics_file.read())
                print(f"Got calendar with {len(list(calendar.timeline))} bookings")
            except CalendarParseError as err:
                print(f"Failed to parse ics file '{config['OUTPUT_ICS']}': {err}")
    else:
        calendar = Calendar()
    
    # Delete events 10 minutes after now. They will be re-created by pulling from wodz.app API
    store = EventStore(calendar)
    localtz = datetime.now().astimezone().tzinfo
    soon = datetime.now().astimezone() + timedelta(seconds=1)
    print(f"Deleting future events to avoid dupes")
    for event in calendar.timeline_tz(localtz).start_after(soon):
        print(f"\t{event.summary} from {event.dtstart} to {event.dtend} (UID={event.uid})")
        store.delete(event.uid)

    print(f"{len(list(calendar.timeline))} bookings left in calendar")

    # Get WODZ bookings
    wodz = WODZ(config['API_BOOKINGS_URL'], config['SEED_COOKIE'])
    print("Fetching bookings from wodz.app API")
    bookings = wodz.fetch_bookings()
    if bookings is None:
        print(f"Error: failed to get bookings from wodz.app API. Exiting...")
        return
    
    print(f"Got {len(bookings['bookings'])} bookings, creating events")
    
    def utc_to_local(utc_dt: datetime) -> datetime:
        return utc_dt.replace(tzinfo=ZoneInfo("UTC")).astimezone(tz=None)
    
    for booking in bookings['bookings']:
        if booking['session']['address'] is None:
            entity = booking['session']['business_entity']
            address = f"{entity['Address']} {entity['zipcode']} {entity['city']}"
        else:
            address = booking['session']['address']

        comment = f"{booking['session']['maxBookingSlots'] - booking['session']['availableBookingSpots']}/{booking['session']['maxBookingSlots']}"

        event_params = {
            "summary": booking['session']['training_category']['name'],
            "dtstart": utc_to_local(datetime.strptime(booking['session']['start_date'], r"%Y-%m-%d %H:%M:%S")),
            "dtend": utc_to_local(datetime.strptime(booking['session']['end_date'], r"%Y-%m-%d %H:%M:%S")),
            "comment": [comment],
            "location": address,
        }

        calendar.events.append(
            Event(**event_params)
        )
    
    print(f"Calendar now has {len(list(calendar.timeline))} bookings")
    
    print(f"Writing calendar file to {config['OUTPUT_ICS']}")

    os.makedirs(os.path.dirname(config['OUTPUT_ICS']), exist_ok=True)
    with open(config['OUTPUT_ICS'], "w+") as ics_file:
        ics_file.write(IcsCalendarStream.calendar_to_ics(calendar))

    print(f"Done. Exiting.")





if __name__ == "__main__":
    main()
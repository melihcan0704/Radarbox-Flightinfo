### Python class to scrape the latest flight information of a given tail id or flight number from Radarbox.com

## Examples & Output:

```python
import rbparser

acinfo=rbparser.aircraft_scrape()

```

When class is defined available functions are:

acinfo.report_status('Your input')

acinfo.current_status('Your input')

acinfo.isgrounded('Your input')

Input should either be an aircraft tail or a flight number. Otherwise it will raise an exception.

acinfo.current_status('Your input') :
tail_id (Registry),
aircraft type,
flight number,
airline,
flight status,
departure date utc,
estimated departure time utc,
actual departure time utc,
origin airport,
origin city,
origin country
arrival date utc,
estimated arrival time utc,
actual arrival time utc,
arrival airport,
arrival city,
arrival country,
is the output from an actual flight or from a future flight,
origin temperature,
origin sky,
arrival temperature,
arrival sky,
current altitude,
flight distance,

```python
acinfo.current_status('A7-BEW')

('A7-BEW', 'Boeing 777-300ER', 'QR701', 'Qatar Airways', 'live', 'Saturday, February 24 2024', '05:15', '05:33', 'DOH', 'Doha', 'Qatar', 'Saturday, February 24 2024', '20:00', None, 'JFK', 'New York, NY', 'United States', False, 21, 'day-cloudy-high', 5.6, 'cloud', 40625, 10772500)

```

acinfo.report_status('Your input') Output will vary depending on status of the aircraft (live, landed, grounded)
```python
acinfo.report_status('UA6066')

{'message': 'N943LR is airborne. Flight No: UA6066',
 'ac_type': 'Canadair CL-600-2D24 Regional Jet CRJ-900ER',
 'flight_origin': 'IAH Houston, TX/United States',
 'flight_destination': 'ELP El Paso, TX/United States',
 'status': 'live',
 'altitude': '1600 feet',
 'sitrep': 'LANDING IN 2h 39m',
 'estimated_takeoff': 'None UTC Saturday, February 24 2024',
 'actual_takeoff': '15:58 UTC Saturday, February 24 2024',
 'estimated_arrival': '18:14 UTC Saturday, February 24 2024',
 'distance_nm': 579.0,
 'report_distance': '185.3 miles flown. 393.7 miles remaining.',
 'org_report_sky': ('day-sunny ', '21.1°C'),
 'dst_report_sky': ('cloudy ', '11.1°C')}

```

## or

```python
acinfo.report_status('4X-EDF')

{'message': 'Aircraft is grounded. Last flight on: 22 Feb 2024 08:24 AM'}

```

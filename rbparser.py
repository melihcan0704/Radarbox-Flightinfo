from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import time
import requests
import json
import radarboxurl


class aircraft_scrape:
    
    def __init__(self):
        radarbox_site = radarboxurl.rbsite()
        self.baseurl = radarbox_site.baseurl
        self.flighturl = radarbox_site.flighturl
    
    def rbparse(self, tail_id):

        url = self.baseurl + tail_id
        r = requests.get(url)

        try:
            soup = BeautifulSoup(r.text, "html.parser")
            script_tag = soup.find_all('script', type='module')
            # Removing custom website function window.init() so it appears as a JSON body.
            script_tag2 = script_tag[2].text.replace('window.init(', '').replace(')', '')
        except IndexError:
            try:
                url = self.flighturl + tail_id #Check if input is flight number.
                r = requests.get(url)
                soup = BeautifulSoup(r.text, "html.parser")
                script_tag = soup.find_all('script', type='module')
                # Removing custom website function window.init() so it appears as a JSON body.
                script_tag2 = script_tag[2].text.replace('window.init(', '').replace(')', '')
            except Exception as e:
                print(f'Status Code: {r.status_code}')
                raise Exception('Request Failed: ', e)

        # JSON parsing for the flights table.
        json_parse = json.loads(script_tag2).get('current')  # json body of the last completed or live flight.
        return json_parse


    
    #return true if aircraft does not fly for more than 2 days.
    def is_grounded(self,tail_id):
        global output_datetime        
        flight_info=self.rbparse(tail_id)
        
        if flight_info.get('status') =='live':
            return False
        else:
            utc_year = flight_info.get('year_utc')
            utc_day = flight_info.get('day_utc')
            utc_time = flight_info.get('arre_utc') or flight_info.get('arrival_utc') or flight_info.get('arrs_utc')

            #parsing without time and year+day only if arrival time is missing. So script doesn't crash when formatting time.
            if utc_time is None: 
                #Only date (UTC).
                date_string = utc_year +" "+ utc_day
                input_datetime=datetime.strptime(date_string,"%Y %d %b")
                output_datetime=input_datetime.strftime("%d %b %Y")
            #Else date+time
            else:
                #Date & Time (UTC).
                date_string = utc_year +" "+ utc_day +" "+ utc_time
                input_datetime=datetime.strptime(date_string,"%Y %d %b %H:%M")
                output_datetime=input_datetime.strftime("%d %b %Y %I:%M %p")

            if input_datetime < datetime.utcnow() - timedelta(days=2): # Change threshold from here if 2 days is not enough.
                return True
            else:
                return False
        
        
    def current_status(self,ac_tail):
        flight_info=self.rbparse(ac_tail)
        self.reg=flight_info.get('acr')
        self.ac_type=flight_info.get('acd')
        self.flight_no=flight_info.get('fnia')
        self.airline=flight_info.get('alna')
        self.status=flight_info.get('status')
        self.dep_date=flight_info.get('depdate_utc')
        self.est_deptime=flight_info.get('depe_utc')
        self.act_deptime=flight_info.get('departure_utc')
        self.org_airport=flight_info.get('aporgia')
        self.org_city=flight_info.get('aporgci')
        self.org_country=flight_info.get('aporgco')
        self.arr_date=flight_info.get('arrdate_utc')
        self.est_arrtime=flight_info.get('arrs_utc')
        self.act_arrtime=flight_info.get('arrival_utc')
        self.arr_airport=flight_info.get('apdstia')
        self.arr_city=flight_info.get('apdstci')
        self.arr_country=flight_info.get('apdstco')
        self.future=flight_info.get('isFuture') # if true the flight_id is a future flight.
        self.org_temp=flight_info.get('org_temp_c')
        self.org_sky_cover=flight_info.get('org_sky_cover')
        self.dst_temp=flight_info.get('dst_temp_c')
        self.dst_sky_cover=flight_info.get('dst_sky_cover')
        self.altitude=flight_info.get('alt')
        self.sitrep=flight_info.get('statusLabel')['text']
        self.distance=flight_info.get('distance')
        self.progress=flight_info.get('progress')
        return (
        self.reg,self.ac_type,self.flight_no,self.airline,self.status,self.dep_date,self.est_deptime,self.act_deptime,self.org_airport,
self.org_city,self.org_country,self.arr_date,self.est_arrtime,self.act_arrtime,self.arr_airport,self.arr_city,self.arr_country,
self.future,self.org_temp,self.org_sky_cover,self.dst_temp,self.dst_sky_cover,self.altitude,self.distance)
        
    def report_status(self, tail):
        result = {}  # Initialize an empty dictionary

        if self.is_grounded(tail):
            self.current_status(tail)  # if you still want to access the current_status attributes
            result['message'] = 'Aircraft is grounded. Last flight on: ' + str(output_datetime)
        else:
            self.current_status(tail)

            if self.status == 'live':
                result['message'] = f'{self.reg} is airborne. Flight No: {self.flight_no}'
                result['ac_type'] = self.ac_type
                result['flight_origin'] = self.org_airport + " " + self.org_city + "/" + self.org_country
                result['flight_destination'] = self.arr_airport + " " + self.arr_city + "/" + self.arr_country
                result['status'] = self.status
                result['altitude'] = "-" if self.altitude is None else str(self.altitude) + ' feet'
                result['sitrep'] = self.sitrep
                result['estimated_takeoff'] = str(self.est_deptime) + " UTC " + str(self.dep_date)
                result['actual_takeoff'] = str(self.act_deptime) + " UTC " + str(self.dep_date)
                result['estimated_arrival'] = str(self.est_arrtime) + " UTC " + str(self.arr_date)
                result['distance_nm'] = round(self.distance * 0.000539957, 0) if self.distance is not None else None

                result['report_distance'] = (
                    str(round(result['distance_nm'] * self.progress / 100, 1)) + " miles flown. " +
                    str(round(result['distance_nm'] - (result['distance_nm'] * self.progress / 100), 1)) +
                    " miles remaining."
                )
                result['org_report_sky'] = self.org_sky_cover + " ", str(self.org_temp) + "°C"
                result['dst_report_sky'] = self.dst_sky_cover + " ", str(self.dst_temp) + "°C"

            elif self.status == 'landed':
                result['message'] = f'{self.reg} is on the ground. Last completed flight as follows: '
                result['ac_type'] = self.ac_type
                result['flight_origin'] = str(self.org_airport) + " " + str(self.org_city) + "/" + str(self.org_country)
                result['flight_destination'] = str(self.arr_airport) + " " + str(self.arr_city) + "/" + str(self.arr_country)
                result['estimated_takeoff'] = str(self.est_deptime) + " UTC " + str(self.dep_date)
                result['actual_takeoff'] = str(self.act_deptime) + " UTC " + str(self.dep_date)
                result['estimated_arrival'] = str(self.est_arrtime) + " UTC " + str(self.arr_date)
                result['actual_arrival'] = str(self.act_arrtime) + " UTC " + str(self.arr_date)
                result['distance_nm'] = round(self.distance * 0.000539957, 0) if self.distance is not None else None
                result['status'] = self.status
                result['sitrep'] = self.sitrep

            elif self.status == 'estimated':
                result['message'] = f'Flight number {self.flight_no} is scheduled for {self.reg}'
                result['ac_type'] = self.ac_type
                result['flight_origin'] = str(self.org_airport) + " " + str(self.org_city) + "/" + str(self.org_country)
                result['flight_destination'] = str(self.arr_airport) + " " + str(self.arr_city) + "/" + str(self.arr_country)
                result['estimated_takeoff'] = str(self.est_deptime) + " UTC " + str(self.dep_date)
                result['estimated_arrival'] = str(self.est_arrtime) + " UTC " + str(self.arr_date)
                result['distance_nm'] = round(self.distance * 0.000539957, 0) if self.distance is not None else None
                result['sitrep'] = self.sitrep

        return result

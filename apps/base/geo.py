import urllib,urllib2,time,json
"""
{
  "name": "1600 Amphitheatre Parkway, Mountain View, CA, USA",
  "Status": {
    "code": 200,
    "request": "geocode"
  },
  "Placemark": [
    {
      "address": "1600 Amphitheatre Pkwy, Mountain View, CA 94043, USA",
      "AddressDetails": {
        "Country": {
          "CountryNameCode": "US",
          "AdministrativeArea": {
            "AdministrativeAreaName": "CA",
            "SubAdministrativeArea": {
              "SubAdministrativeAreaName": "Santa Clara",
              "Locality": {
                "LocalityName": "Mountain View",
                "Thoroughfare": {
                  "ThoroughfareName": "1600 Amphitheatre Pkwy"
                },
                "PostalCode": {
                  "PostalCodeNumber": "94043"
                }
              }
            }
          }
        },
        "Accuracy": 8
      },
      "Point": {
        "coordinates": [-122.083739, 37.423021, 0]
      }
    }
  ]
}
"""
root_url = "http://maps.google.com/maps/geo?"
gkey = "ABQIAAAAw6ArS1eE_K0sprwtT178ZhSszzQBrvuXuJup0ZrfApALDIflmxRS66rHOHcb2Zrc61i3DyxE0gAbhA"
return_codes = {'200':'SUCCESS',
				'400':'BAD REQUEST',
				'500':'SERVER ERROR',
				'601':'MISSING QUERY',
				'602':'UNKOWN ADDRESS',
				'603':'UNAVAILABLE ADDRESS',
				'604':'UNKOWN DIRECTIONS',
				'610':'BAD KEY',
				'620':'TOO MANY QUERIES'
				}
#:Reverse//maps.google.com/maps/geo?q=40.714224,-73.961452&output=json&oe=utf8&sensor=false&key=your_api_key
def reverse_geocode(lng, lat):
    coords = "%f,%f" %(lat,lng)
    values = {'q' :coords, 'output':'json', 'key':gkey,'sensor':'false'}
    data = urllib.urlencode(values)
    url = root_url+data
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    geodat = json.load(response)
    return geodat

def geocode(addr):
    # Encode our dictionary of url parameters
    values = {'q' : addr, 'output':'json', 'key':gkey,'sensor':'false'}
    data = urllib.urlencode(values)
    # Set up our request
    url = root_url+data
    req = urllib2.Request(url)

    # Make request and read response
    response = urllib2.urlopen(req)

    # Get JSON data
    if response.code == 200:
        results = {}
        geodat = json.load(response)
        address_details = geodat["Placemark"][0]
        accuracy = address_details["AddressDetails"]["Accuracy"]
        results['address'] = address_details['address']

        # 0: Unknown address
        if accuracy > 0:
        	results['longitude'] = address_details["ExtendedData"]["LatLonBox"]["east"]
        	results['latitude']  = address_details["ExtendedData"]["LatLonBox"]["north"]

        # 1: Country level accuracy.
        if accuracy >= 1 and accuracy < 9:
            if 'Country' in address_details["AddressDetails"]:
                country  = address_details["AddressDetails"]["Country"]
                results['country'] = country

         # 2: Region (state, province, prefecture, etc.) level accuracy.
        if accuracy >= 2:
       	    results['state']= country["AdministrativeArea"]["AdministrativeAreaName"]

            # 3: Sub-region (county, municipality, etc.) level accuracy.
            if accuracy >=3:
              if "Locality" in country["AdministrativeArea"]:
                locality = country["AdministrativeArea"]["Locality"]
                results['county'] = locality

                    # 4: 	Town (city, village) level accuracy.
                if accuracy >= 4:
                    results['town'] = locality["LocalityName"]
                    if "PostalCode" in locality:
                	           results['zipcode']  = locality["PostalCode"]
                	# 5 Post code (zip code) level accuracy.
                	# 6 Street level accuracy.
                	# 7 Intersection level accuracy.
                	# 8 Address level accuracy.

        return results

    return None
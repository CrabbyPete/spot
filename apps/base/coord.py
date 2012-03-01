def getcords(d, m, s, ind):
    # Calculate the total number of seconds,
    # 43'41" = (43*60 + 41) = 2621 seconds.

    sec = float((m * 60) + s)
    # The fractional part is total number of
    # seconds divided by 3600. 2621 / 3600 = ~0.728056

    frac = float(sec / 3600)
    # Add fractional degrees to whole degrees
    # to produce the final result: 87 + 0.728056 = 87.728056

    deg = float(d + frac)
    # If it is a West or S longitude coordinate, negate the result.
    if ind == 'W':
        deg = deg * -1

    if ind == 'S':
        deg = deg * -1

    return float(deg)

def get_GPS(data):
    longitude = None
    latitude = None

    # See if GPS data is available and if so convert to decimal for Google Map
    if data.has_key('GPS GPSLatitude' ) and data.has_key('GPS GPSLatitudeRef') and \
                           data.has_key('GPS GPSLongitude') and data.has_key('GPS GPSLongitudeRef'):

        lat = data['GPS GPSLatitude'].values
        ns  = data['GPS GPSLatitudeRef'].values
        lng = data['GPS GPSLongitude'].values
        ew = data['GPS GPSLongitudeRef'].values

        if lat[0].den != 0 and lat[1].den != 0 and lat[2].den != 0 and\
           lng[0].den != 0 and lng[1].den != 0 and lng[2].den != 0:

            latitude  = getcords(float(lat[0].num)/float(lat[0].den),
                            float(lat[1].num)/float(lat[1].den),
                            float(lat[2].num)/float(lat[2].den), ns)

            longitude = getcords(float(lng[0].num)/float(lng[0].den),
                                                 float(lng[1].num)/float(lng[1].den),
                                                 float(lng[2].num)/float(lng[2].den), ew)

    return longitude,latitude

"""
def showmap():
    from pymaps import Map, PyMap # import the libraries

    # Create a map - pymaps allows multiple maps in an object
    tmap = Map()
    tmap.zoom = 3

    # Latitude and lognitude - see the getcords function
    # to see how we convert from traditional D/M/S to the DD type
    # used by Googel Maps

    lat = 0.0
    long = 0.0

    # These coordinates are for Hong Kong
    dlat = "22 15 0 N"
    dlong = "114 10 60 E"

    dlat = dcode.lat.split(" ")
    dlong = dcode.long.split(" ")

    # Convert the coordinates
    lat = getcords(float(dlat[0]), float(dlat[1]), float(dlat[2]), dlat[3])
    long = getcords(float(dlong[0]), float(dlong[1]), float(dlong[2]), dlong[3])

    # Inserts html into the hover effect
    pointhtml = "Hello!"

    # Add the point to the map
    point = (lat, long, pointhtml, icon.id)

    tmap.setpoint(point)
    tmap.center = (1.757537,144.492188)

    # Put your own googl ekey here
    gmap = PyMap(key=GOOGLE_KEY, maplist=[tmap])
    gmap.addicon(icon)

    # pymapjs exports all the javascript required to build the map!
    mapcode = gmap.pymapjs()

    # Do what you want with it - pass it to the template or print it!
    return mapcode

"""


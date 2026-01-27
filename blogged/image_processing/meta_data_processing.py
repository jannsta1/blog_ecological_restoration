from PIL import Image
from PIL.ExifTags import TAGS


def get_gps_coordinates_from_meta_data(image_path):
    # The path to the image
    image = Image.open(image_path)

    def decimal_coords(coords, ref):
        decimal_degrees = (
            float(coords[0]) + float(coords[1]) / 60 + float(coords[2]) / 3600
        )
        # the value is negative for South and West coordinates
        if ref == "S" or ref == "W":
            decimal_degrees = -1 * decimal_degrees
        return decimal_degrees

    GPSINFO_TAG = next(tag for tag, name in TAGS.items() if name == "GPSInfo")

    info = image.getexif()
    gpsinfo = info.get_ifd(GPSINFO_TAG)

    # print(f"GPS Info: {gpsinfo}")
    # GPS Info: {0: b'\x02\x02\x00\x00', 1: 'N', 2: (55.0, 34.0, 50.58), 3: 'W', 4: (3.0, 42.0, 51.45), 7: (11.0, 54.0, 44.0), 16: 'M', 17: 72.0, 29: '2024:02:04'}
    # GPS Info: {0: b'\x02\x02\x00\x00', 1: 'N', 2: (55.0, 38.0, 55.29), 3: 'W', 4: (3.0, 11.0, 49.29), 5: b'\x00', 6: 225.1, 7: (9.0, 16.0, 17.0), 16: 'M', 17: 190.0, 29: '2025:08:23'}

    # 1: Latitude Ref (N/S)
    # 2: Latitude (Degrees, Minutes, Seconds)
    # 3: Longitude Ref (E/W)
    # 4: Longitude (Degrees, Minutes, Seconds)
    # 5: Altitude Ref - byte 0 = above sea level, byte 1 = below sea level
    # 6: Altitude - Rational number (M)
    # 7: GPS Time Stamp (Hours, Minutes, Seconds)
    # 16: GPSImgDirectionRef - 'M' = Magnetic North, 'T' = True North
    # 17: GPSImgDirection - angle in degrees between 0 and 360
    # 29: Date Stamp

    if len(gpsinfo) < 6:
        raise LookupError("This image doesn't have the required GPS data")

    # TODO handle missing GPS data more gracefully
    lat = decimal_coords(gpsinfo[2], gpsinfo[1])
    lon = decimal_coords(gpsinfo[4], gpsinfo[3])
    # sometimes altitude is missing, in these cases set to 0 - perhaps we should set to None? And allow nullable field in DB?
    if 6 in gpsinfo:
        alt = gpsinfo[6]
        # alt = alt._numerator / alt._denominator
    else:
        alt = 0

    # print(f"Lat: {lat} Lon: {lon} Alt: {alt}")
    return (lat, lon, alt)

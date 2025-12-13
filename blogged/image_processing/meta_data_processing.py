from PIL import Image
from PIL.ExifTags import TAGS


def get_gps_coordinates_from_meta_data(image_path):
    # The path to the image
    image = Image.open(image_path)
    # image_path = "PXL_20250330_112845921.jpg"

    def decimal_coords(coords, ref):
        decimal_degrees = (
            float(coords[0]) + float(coords[1]) / 60 + float(coords[2]) / 3600
        )
        if ref == "S" or ref == "W":
            decimal_degrees = -1 * decimal_degrees
        return decimal_degrees

    GPSINFO_TAG = next(tag for tag, name in TAGS.items() if name == "GPSInfo")

    info = image.getexif()
    gpsinfo = info.get_ifd(GPSINFO_TAG)

    if len(gpsinfo) < 6:
        raise LookupError("This image doesn't have the required GPS data")

    lat = decimal_coords(gpsinfo[2], gpsinfo[1])
    lon = decimal_coords(gpsinfo[4], gpsinfo[3])
    alt = gpsinfo[6]

    # lat = lat._numerator / lat._denominator
    # lon = lon._numerator / lon._denominator
    alt = alt._numerator / alt._denominator

    print(f"Lat: {lat} Lon: {lon} Alt: {alt}")

    return (lat, lon, alt)

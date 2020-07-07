import PIL.Image
from PIL.ExifTags import TAGS, GPSTAGS
import sys
import json
import os

#36867 DateTimeOriginal = 2014:07:31 18:57:42
#274 Orientation = 1
#270 ImageDescription = {"MAPDeviceMake":"Samsung","MAPCameraMode":1,"MAPCaptureTime":"2014_07_31_18_57_43_182","MAPSettingsEmail":"fred.rodrigo@gmail.com","MAPLocalTimeZone":"+0200","MAPVersionString":"0.38","MAPCompassHeading":{"TrueHeading":290.1358337402344,"MagneticHeading":290.675048828125},"MAPDeviceModel":"Galaxy Nexus","MAPCameraRotation":"0","MAPPhotoUUID":"8a4a3e12-f8eb-43d3-b443-db77660fab2a","MAPLatitude":"44.83253728598356","MAPLightSensor":"2740.803","MAPGPSAccuracyMeters":"10.0","MAPSequenceUUID":"72f8be90-4721-4731-99fd-d2634ce3a6b7","MAPAltitude":"51.9000244140625","MAPSequenceCaptureUsed":"0","MAPSettingsUploadHash":"8b43ab95a9fb0da16a4637c69c57107a3b6a44bf374057bf358f88f08f83a5d1","MAPSettingsProject":"","MAPAccelerometerVector":{"z":0.34026679396629333,"y":0.17308391630649567,"x":9.746758460998535},"MAPLongitude":"-0.5600724834948778"}
#34853 GPSInfo = {1: 'N', 2: ((44, 1), (49, 1), (284757, 4984)), 3: 'W', 4: ((0, 1), (33, 1), (421751, 11631)), 17: (1190605, 4096)}


## https://gist.github.com/erans/983821/e30bd051e1b1ae3cb07650f24184aa15c0037ce8

def _get_if_exist(data, key):
    if key in data:
        return data[key]

    return None

def _convert_to_degress(value):
    """Helper function to convert the GPS coordinates stored in the EXIF to degress in float format"""
    d0 = value[0][0]
    d1 = value[0][1]
    d = float(d0) / float(d1)

    m0 = value[1][0]
    m1 = value[1][1]
    m = float(m0) / float(m1)

    s0 = value[2][0]
    s1 = value[2][1]
    s = float(s0) / float(s1)

    return d + (m / 60.0) + (s / 3600.0)

def get_lat_lon(exif_data):
    """Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)"""
    lat = None
    lon = None

    if "GPSInfo" in exif_data:
        gps_info = exif_data["GPSInfo"]

        gps_latitude = _get_if_exist(gps_info, "GPSLatitude")
        gps_latitude_ref = _get_if_exist(gps_info, 'GPSLatitudeRef')
        gps_longitude = _get_if_exist(gps_info, 'GPSLongitude')
        gps_longitude_ref = _get_if_exist(gps_info, 'GPSLongitudeRef')

        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = _convert_to_degress(gps_latitude)
            if gps_latitude_ref != "N":
                lat = 0 - lat

            lon = _convert_to_degress(gps_longitude)
            if gps_longitude_ref != "E":
                lon = 0 - lon

    return lat, lon

def parse_gps(gps):
    if gps:
        gps_data = {}
        for t, v in gps.items():
            sub_decoded = GPSTAGS.get(t, t)
            gps_data[sub_decoded] = v
        return (*get_lat_lon({"GPSInfo": gps_data}), None) # TODO parse GPSImgDirection
    return None, None, None


def parse_comment(comment):
    if comment:
        try:
            j = json.loads(comment)
        except:
            return None, None, None

        lat = lon = dir = None
        if "MAPCompassHeading" in j and "TrueHeading" in j["MAPCompassHeading"]:
            dir = j["MAPCompassHeading"]["TrueHeading"]
        else:
            dir = None

        lat = float(j.get("MAPLatitude"))
        lon = float(j.get("MAPLongitude"))

        sequence = j.get("MAPSequenceUUID")

        return lat, lon, dir, sequence

    return None, None, None, None

def parse_image(rep, user, seq, image):
    img = PIL.Image.open(rep + "/" + user + "/" + seq + "/" + image)

    exif = img._getexif()
    #for (k,v) in exif.items():
    #        print('%s %s = %s' % (k, TAGS.get(k), v))

    try:
        lat, lon, dir = parse_gps(exif[34853])
    except:
        pass
    m_lat, m_lon, m_dir, sequence = parse_comment(exif.get(270))

    if m_lat is None:
        m_lat = lat
    if m_lon is None:
        m_lon = lon
    if m_dir is None:
        m_dir = dir

    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [m_lon, m_lat],
        },
        "properties": {
            "user": user,
            "sequence": sequence or seq,
            "image": image,
            "DateTimeOriginal": exif.get(36867),
            "Orientation": exif.get(1),
            "heading": m_dir,
        }
    }


def parse_seq(rep, user, seq):
    list_of_files = os.listdir(rep + "/" + user + "/" + seq)
    seq = [parse_image(rep, user, seq, image) for image in list_of_files]
    seq = sorted(seq, key = lambda i: i["properties"]["DateTimeOriginal"])
    return {
        "type": "FeatureCollection",
        "features": seq,
        "properties": {
            "sequence": seq,
        }
    }

def parse_user(rep, user):
    list_of_files = os.listdir(rep + "/" + user)
    for seq in [s for s in list_of_files if os.path.isdir(rep + "/" + user + "/" + s)]:
        print(f"Extract meta data {seq}")
        s = parse_seq(rep, user, seq)
        f = open(rep + "/" + user + "/" + seq + "-point.geojson", "w")
        f.write(json.dumps(s))
        f.close()

if __name__ == "__main__":
    parse_user(sys.argv[1], sys.argv[2])

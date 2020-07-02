import json, os
import mapillary_takeout
import sys
import time
import gen_geojson
import traceback

stdout_orig = sys.stdout

def oldest_file():
    list_of_files = os.listdir('mapillary_user')
    full_path = ["mapillary_user/{0}".format(x) for x in list_of_files]
    return min(full_path, key=os.path.getctime)


def takeout():
    config = oldest_file()
    query = json.loads(open(config).read())
    email = query['email']
    password = query['password']
    username = query['username']

    sys.stdout = open('logs/' + username, 'w')

    try:
        mapillary_takeout.main(
            email,
            password,
            username,
            f'photo/{username}',
            None,
            None
        )

        gen_geojson.parse_user("photo/" + username)

        sys.stdout.close()
        sys.stdout = stdout_orig

        os.remove(config)
    except:
        sys.stdout.close()
        sys.stdout = stdout_orig

        print("Unexpected error:", traceback.format_exc())


while True:
    list_of_files = os.listdir('mapillary_user')
    print(list_of_files)
    if len(list_of_files) > 0:
        takeout()
    time.sleep(10)

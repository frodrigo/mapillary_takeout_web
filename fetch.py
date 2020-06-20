import json, os
import mapillary_takeout
import sys
import time

stdout_orig = sys.stdout

def oldest_file():
    list_of_files = os.listdir('mapillary_user')
    full_path = ["mapillary_user/{0}".format(x) for x in list_of_files]
    return min(full_path, key=os.path.getctime)


def takeout():
    query = json.loads(open(oldest_file()).read())
    email = query['email']
    password = query['password']
    username = query['username']

    sys.stdout = open('logs/' + username, 'w')

    mapillary_takeout.main(
        email,
        password,
        username,
        f'photo/{username}',
        None,
        None
    )

    sys.stdout.close()
    sys.stdout = stdout_orig


while True:
    list_of_files = os.listdir('mapillary_user')
    if len(list_of_files) > 0:
        takeout()
    else:
        time.sleep(10)

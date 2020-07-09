import sys
import json
import os
from blur_persons import blur_in_files


def parse_seq(user, seq):
    list_of_files = os.listdir(user + "/" + seq)
    l = [f"{user}/{seq}/{image}" for image in sorted(list_of_files) if image.endswith('.jpg')]

    blur_in_files(
        files = l,
        model="xception_coco_voctrainval",
        classes = ['person', 'bus', 'car', 'motorbike'],
        blur = 'white',
        dest = None,
        suffix = '-mask',
        dezoom = 6,
        quality = None,
        mask = True,
    ),


def parse_user(user):
    list_of_files = os.listdir(user)
    for seq in [s for s in sorted(list_of_files) if os.path.isdir(user + "/" + s)]:
        s = parse_seq(user, seq)

if __name__ == "__main__":
    parse_user(sys.argv[1])

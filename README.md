# Mapillary Takeout Web

Web frontend to [mapillary_takeout](https://github.com/gitouche-sur-osm/mapillary_takeout)

Download your "unprocessed original" images back from Mapillary.

## Install

```
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

```
mkdir -p logs mapillary_user photo
```

## Run

```
export FLASK_APP=web.py
export FLASK_ENV=development
python -m flask run
```

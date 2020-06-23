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

## Tools

``
npm install
``

## Dev

Run

```
export FLASK_APP=web.py
export FLASK_ENV=development
python -m flask run
```

## Production

### Web

Use WSGI. Apache configuration provied.

### Background download

```
python fetch.py
```

### Vector Tiles

```
`npm bin`/tileserver-gl-light -c map/config.json --public_url https://mapillary-takeout-web.openstreetmap.fr
```

## Update task

Merge sequences from users:
```
for user in photo/*/; do
    `npm bin`/geojson-merge $user/*.geojson > "${user::-1}.geojson"
done

`npm bin`/geojson-merge photo/*.geojson > map/photo.geojson
```

Convert to MBTiles, from photo directory:
```
tippecanoe -o images.mbtiles -l images -r1 --cluster-distance=1 photo.geojson
```

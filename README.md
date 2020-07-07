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

```
git clone https://github.com/tyndare/blur-persons.git
git clone https://github.com/gitouche-sur-osm/mapillary_takeout.git
```

## Tools

Install npm, tippecanoe.

Then:
``
npm install
``

Add mapillary_takeout:
```
wget https://raw.githubusercontent.com/gitouche-sur-osm/mapillary_takeout/master/mapillary_takeout.py
```

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

Prepare data from TMS, with GDAL >= 3.0.3
```
ogr2ogr -oo DATE_AS_STRING=YES photo.shp photo.geojson
shp2pgsql -d photo.shp > photo.sql
psql < photo.sql
```

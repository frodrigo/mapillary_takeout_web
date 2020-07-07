require 'rubygems'
require 'rack'
require 'sinatra'
require 'erb'
require 'pg'
require 'connection_pool'
enable :inline_template

con_pool = ConnectionPool.new(size: 5, timeout: 10) {
  PG.connect(dbname: 'fred')
}

get '/hi' do
  "Hello World!"
end

get '/' do
  erb :index
end

get '/:z/:x/:y.jpg' do
  row_params = request.query_string
  x = params[:x].to_i
  y = params[:y].to_i
  z = params[:z].to_i
  #for Google/OSM tile scheme we need to alter the y:
  y = ((2**z)-y-1)
  #calculate the bbox
  min = get_lat_lng_for_number(x, y, z)
  max = get_lat_lng_for_number(x+1, y+1, z)
  bbox = "#{min[:lat_deg]},#{min[:lng_deg]},#{max[:lat_deg]},#{max[:lng_deg]}"
  width = "256"
  height = "256"

  url = nil
  con_pool.with{ |conn|
    conn.exec("""
SELECT \"user\", sequence, image
FROM photo
WHERE geom && ST_MakeLine(ST_MakePoint(#{min[:lng_deg]}, #{min[:lat_deg]}, 4326), ST_MakePoint(#{max[:lng_deg]}, #{max[:lat_deg]}, 4326))
LIMIT 1""") do |result|
      result.each do |row|
        puts row.inspect
        url = "https://mapillary-takeout-web.openstreetmap.fr/#{row['user']}/#{row['sequence']}/#{row['image']}?#{row_params}"
        puts url
      end
    end
  }
  if url
    redirect url
  else
    halt 204
  end
end

def get_lat_lng_for_number(xtile, ytile, zoom)
  n = 2.0 ** zoom
  lon_deg = xtile / n * 360.0 - 180.0
  lat_rad = Math::atan(Math::sinh(Math::PI * (1 - 2 * ytile / n)))
  lat_deg = 180.0 * (lat_rad / Math::PI)
  {:lat_deg => -lat_deg, :lng_deg => lon_deg}
end


__END__

@@ layout
<%= yield %>

@@ index
<!DOCTYPE html>
<html>
<head>
    <title>Redirection HTTP de tuile TMS vers le WMS du Cadastre</title>
    <meta charset="utf-8" />

    <script src="https://unpkg.com/leaflet@0.7.3/dist/leaflet.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@0.7.3/dist/leaflet.css" />
</head>
<body>
    <div id="map" style="width: 100%; height: 600px"></div>

    <script>
        var osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 25,
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        });

        var photo = L.tileLayer('/tms/{z}/{x}/{y}.jpg?s=256', {
            maxZoom: 25,
            attribution: 'Photo',
        });

        var map = L.map('map', {layers: [osm, photo]}).setView([44.8265, -0.5692], 13);
    </script>
<% host = request.host %>
tms[22]:https://<%= host %>/tms/{z}/{x}/{y}.jpg?s=256
</body>
</html>

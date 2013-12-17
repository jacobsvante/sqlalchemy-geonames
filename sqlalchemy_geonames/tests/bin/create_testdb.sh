dropuser sqla_geonames
dropdb sqla_geonames
createuser sqla_geonames
createdb -O sqla_geonames sqla_geonames
for ext in postgis postgis_topology fuzzystrmatch postgis_tiger_geocoder
    do psql -d sqla_geonames -c "CREATE EXTENSION $ext;"
done

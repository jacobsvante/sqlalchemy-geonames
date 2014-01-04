# sqlalchemy-geonames

[![Build status](https://travis-ci.org/jmagnusson/sqlalchemy-geonames.png?branch=master)](http://travis-ci.org/#!/jmagnusson/sqlalchemy-geonames)
[![Code coverage](https://coveralls.io/repos/jmagnusson/sqlalchemy-geonames/badge.png?branch=master)](https://coveralls.io/r/jmagnusson/sqlalchemy-geonames)
[![PyPI version](https://pypip.in/v/sqlalchemy-geonames/badge.png)](https://pypi.python.org/pypi/sqlalchemy-geonames)
[![PyPI downloads](https://pypip.in/d/sqlalchemy-geonames/badge.png)](https://pypi.python.org/pypi/sqlalchemy-geonames)

Created by [Jacob Magnusson](https://twitter.com/pyjacob), 2013. List of contributors can be found in [CONTRIBUTORS.md](CONTRIBUTORS.md).


## About

Generates SQLAlchemy models and downloads and imports data from [geonames.org dumps](http://download.geonames.org/export/dump/). Currently only supports postgresql with postgis 2.0+ extension enabled.


## Installation

Install using `pip`

    $ pip install sqlalchemy-geonames

It's recommended to install `cdecimal` for optimal performance if you're on a python version lower than 3.3. With 3.3+ this is the default Decimal implementation.

    $ pip install --allow-external cdecimal


## Usage

After you've enabled the postgis extensions for your PostgreSQL database all you have to do is issue the following command to populate your database with city data (and data related to them) from geonames.org.

    $ sqlageonames -t postgresql -u <dbuser> -d <dbname> cities1000.txt

The tedious work of downloading `cities1000.txt` and related data dumps is handled for you so there's no need to get them manually.
For a full list of `sqlageonames` options, such as what data to download and database port etc:

    $ sqlageonames --help

After import you should be able to use the models in your application.

```python
from sqlalchemy_geonames import GeonameCountry, Geoname
...
session = Session()
countries = session.query(GeonameCountry).all()
swedish_cities = session.query(Geoname).join(GeonameCountry)\
                        .filter(GeonameCountry.country == 'Sweden').all()
```


## Import performance

* **cities15000.txt** (23k rows) ~ 10 seconds
* **cities5000.txt** (47k rows) ~ 19 seconds
* **cities1000.txt** (138k rows) ~ 49 seconds
* **allCountries.txt** (8.5M rows) ~ 14 minutes 16 seconds

Tested on my 2.7 GHz i7 + SSD Macbook Pro. The import process is very CPU bound, memory usage is about 20-40MB.


## Supported data

`sqlalchemy-geonames` imports the specified primary geonames file (i.e. `citiesXXXXX.txt` or `allCountries.txt`) and all other data that is related to it. The related data cannot be excluded from importing. The following data dumps are supported:

* allCountries.txt
* citiesXXXXX.txt
* countryInfo.txt
* timeZones.txt
* featureCodes_XX.txt


## Not yet supported data

These will be implemented in an upcoming release.

* admin1CodesASCII.txt
* admin2Codes.txt
* alternateNames.txt
* hieararchy.txt
* iso-languagecodes.txt
* no-country.txt (this is a list of geonames that don't have a country assigned to them)
* userTags.txt


## Documentation

TODO: Write!

Enabling postgis 2.0 extensions for your postgresql database:

    $ for ext in postgis postgis_topology fuzzystrmatch postgis_tiger_geocoder; do psql -d <dbname> -c "CREATE EXTENSION $ext;"; done


## Requirements

* Python 2.7+ / 3.3+
* A [PostGIS](http://postgis.net/) 2.0 enabled [PostgreSQL](http://www.postgresql.org/) database (support for other gis/databases is coming)


## Testing

From the project directory:

    $ pip install tox
    $ tox


## Attributions

[This project uses GeoNames data](http://www.geonames.org/). Extracts are used in the tests.

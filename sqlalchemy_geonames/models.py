from sqlalchemy import (Column, ForeignKey, Integer, String, Text, BigInteger,
                        DateTime, Numeric)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
from .utils import simple_repr


GeonameBase = declarative_base()


class GeonameMetadata(GeonameBase):
    __tablename__ = 'geonamemetadata'
    id = Column(Integer, primary_key=True)
    # TODO: Use this to keep track of data to download
    last_updated = Column(DateTime(timezone=True), nullable=False)


class GeonameCountry(GeonameBase):
    __tablename__ = 'geonamecountry'
    __repr__ = simple_repr('country')

    iso = Column(String(2), primary_key=True)
    iso3 = Column(String(3), nullable=False)
    iso_numeric = Column(Integer, nullable=False)
    fips = Column(String(2), nullable=False)
    country = Column(String(255), nullable=False)
    capital = Column(String(255), nullable=False)
    area_in_sq_km = Column(Integer)
    population = Column(Integer, nullable=False)
    continent = Column(String(255), nullable=False)
    tld = Column(String(3), nullable=False)
    currency_code = Column(String(3), nullable=False)
    currency_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    postal_code_format = Column(String(255), nullable=False)
    postal_code_regex = Column(String(255), nullable=False)
    languages = Column(String(255), nullable=False)
    geonameid = Column(Integer)
    neighbours = Column(String(255), nullable=False)
    equivalent_fips_code = Column(String(255), nullable=False)


class GeonameTimezone(GeonameBase):
    __tablename__ = 'geonametimezone'
    __repr__ = simple_repr('timezone_id')

    # the timezone id (see file timeZone.txt) varchar(40)
    # (Renamed from timezone)
    timezone_id = Column(String(40), primary_key=True)

    country_code = Column(String(2), nullable=False)
    gmt_offset = Column(Numeric(3, 1), nullable=False)
    dst_offset = Column(Numeric(3, 1), nullable=False)
    raw_offset = Column(Numeric(3, 1), nullable=False)


class GeonameFeature(GeonameBase):
    __tablename__ = 'geonamefeature'
    __repr__ = simple_repr('name')

    # see http://www.geonames.org/export/codes.html, varchar(10)
    feature_code = Column(String(10), primary_key=True)

    # see http://www.geonames.org/export/codes.html, char(1)
    feature_class = Column(String(1), nullable=False)

    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)


class Geoname(GeonameBase):
    __tablename__ = 'geoname'
    __repr__ = simple_repr('name')

    # integer id of record in geonames database
    geonameid = Column(Integer, primary_key=True)

    # name of geographical point (utf8) varchar(200)
    name = Column(String(200), nullable=False)

    # name of geographical point in plain ascii characters, varchar(200)
    asciiname = Column(String(200), nullable=False)

    # alternatenames, comma separated varchar(5000)
    alternatenames = Column(Text, nullable=False)

    # latitude in decimal degrees (wgs84)
    # latitude = Column(Numeric(10, 7), nullable=False)

    # longitude in decimal degrees (wgs84)
    # longitude = Column(Numeric(10, 7), nullable=False)

    # Custom. A point made from `latitude` and `longitude`.
    # SRID #4326 = WGS84
    point = Column(Geography(geometry_type='POINT', srid=4326), nullable=False)

    feature_code = Column(String(10), ForeignKey(GeonameFeature.feature_code))
    feature = relationship(GeonameFeature)

    # ISO-3166 2-letter country code, 2 characters
    country_code = Column(String(2), ForeignKey(GeonameCountry.iso))
    country = relationship(GeonameCountry)

    # alternate country codes, comma separated, ISO-3166 2-letter country
    # code, 60 characters
    cc2 = Column(String(60), nullable=False)

    # fipscode (subject to change to iso code), see exceptions below, see
    # file admin1Codes.txt for display names of this code; varchar(20)
    admin1_code = Column(String(20), nullable=False)

    # code for the second administrative division, a county in the US, see
    # file admin2Codes.txt; varchar(80)
    admin2_code = Column(String(80), nullable=False)

    # code for third level administrative division, varchar(20)
    admin3_code = Column(String(20), nullable=False)

    # code for fourth level administrative division, varchar(20)
    admin4_code = Column(String(20), nullable=False)

    # bigint (8 byte int)
    population = Column(BigInteger, nullable=False)

    # in meters, integer
    elevation = Column(Integer)

    # digital elevation model, srtm3 or gtopo30, average elevation
    # of 3''x3'' (ca 90mx90m) or 30''x30'' (ca 900mx900m) area in
    # meters, integer. srtm processed by cgiar/ciat.
    dem = Column(Integer, nullable=False)

    # (Renamed from timezone)
    timezone_id = Column(String(40), ForeignKey(GeonameTimezone.timezone_id))
    timezone = relationship(GeonameFeature)

"""sqlalchemy-geonames data downloader/importer

By default geonames data for cities with a population of 1000 or more will
be imported. To download different data one can pass in any of the following:

    cities1000.txt    All cities with a population of 1000 or more
    cities5000.txt    Only download cities with a population of 5000 or more
    cities15000.txt   Only download cities with a population of 15000 or more
    allCountries.txt  Downloads all data available for every country. Not
                      recommended unless you know for sure that you want
                      this. Import time is over 16 minutes on a Quad-Core
                      2.7GHz i7 and querying the geoname table takes over
                      a second no matter how small the result set is.

"""
from __future__ import print_function
import argparse
import os
import sys
from copy import deepcopy
from zipfile import ZipFile
import requests
from progressbar import ProgressBar, ETA, FileTransferSpeed, Percentage, Bar
from sqlalchemy import engine, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from .. import filename_config, get_importer_instances, GeonameBase
from ..utils import get_password, normalize_path, mkdir_p
from ..imports import _import_options_map


class RawArgumentDefaultsHelpFormatter(argparse.ArgumentDefaultsHelpFormatter,
                                       argparse.RawTextHelpFormatter):
    """Retain both raw text descriptions and argument defaults"""
    pass

NOT_SET = object()
DATABASE_CHOICES = ('postgresql', )
DEFAULT_DOWNLOAD_DIR = normalize_path('~/.sqlageonames')
DEFAULT_LANGUAGE_CODE = 'en'
PRIMARY_GEONAME_FILENAMES = [name for name, opts in filename_config.items()
                             if opts.get('is_primary') is True]
LANGUAGE_CHOICES = sorted(set(opts['language_code'] for name, opts
                              in filename_config.items()
                              if 'language_code' in opts))

supported_filenames = _import_options_map.keys()


def get_progress_bar(maxval):
    widgets = [Percentage(), ' ', Bar(), ' ', ETA(), ' ', FileTransferSpeed()]
    return ProgressBar(widgets=widgets, maxval=maxval)


def get_local_filepath(filename, download_dir=DEFAULT_DOWNLOAD_DIR):
    return os.path.join(download_dir, filename)


def get_download_config(primary_filename, language_code=DEFAULT_LANGUAGE_CODE):
    download_config = {k: v for k, v in deepcopy(filename_config).items()
                       if k in supported_filenames}
    for filename, opts in download_config.items():
        # Only download the selected primary primary_filename file
        if (filename in PRIMARY_GEONAME_FILENAMES
                and filename != primary_filename):
            del download_config[filename]
        # If a file is bound to a specific language code and is not the
        # specified one then remove it.
        if 'language_code' in opts and opts['language_code'] != language_code:
            del download_config[filename]
    return download_config


def download(url, download_dir=DEFAULT_DOWNLOAD_DIR, use_cache=True,
             chunk_size=1024):
    _, _, download_filename = url.rpartition('/')
    local_filepath = get_local_filepath(download_filename, download_dir)
    if use_cache and os.path.exists(local_filepath):
        print(u'Using cached file {}'.format(local_filepath))
        return local_filepath
    else:
        print(u'Downloading {} to {}...'.format(download_filename,
                                                local_filepath))
    req = requests.get(url, stream=True)
    req.raise_for_status()
    content_length = int(req.headers['content-length'])
    pbar = get_progress_bar(maxval=content_length)
    pbar.start()
    mkdir_p(download_dir)  # Make sure path exists
    with open(local_filepath, 'wb') as fh:
        for chunk in req.iter_content(chunk_size=chunk_size):
            if not chunk:
                import ipdb
                ipdb.set_trace()
            if chunk:  # Filter out keep-alive new chunks
                fh.write(chunk)
                fh.flush()
            new_pbar_val = pbar.currval + chunk_size
            if new_pbar_val <= pbar.maxval:
                pbar.update(new_pbar_val)
    pbar.finish()
    return local_filepath


def get_db_url(database_type, database, username,
               password=None, port=None, host=None):
    dburl_kwargs = {
        'database': database,
        'host': host,
        'port': port,
        'username': username,
    }
    if database_type == 'postgresql':
        dburl_kwargs['drivername'] = 'postgresql+psycopg2'
    else:
        sys.exit('Only postgresql is supported at the moment')

    dburl = engine.url.URL(**dburl_kwargs)

    if password is NOT_SET:
        pass  # No password
    elif password is None:
        dburl.password = get_password('Database password: ')
    else:
        dburl.password = password
    return dburl


def unzip(zip_filepath, filename_to_extract, extract_dir=DEFAULT_DOWNLOAD_DIR):
    """Unzip file from archive and return path to extracted file"""
    zipfile = ZipFile(zip_filepath)
    assert filename_to_extract in zipfile.namelist()
    print(u'Unzipping {}...'.format(zip_filepath))
    return zipfile.extract(member=filename_to_extract, path=extract_dir)


def create_geoname_tables(db_session, recreate_tables=False):
    if recreate_tables:
        GeonameBase.metadata.drop_all(bind=db_session.bind)
    GeonameBase.metadata.create_all(bind=db_session.bind)


def purge_geoname_tables(db_session):
    for table in reversed(GeonameBase.metadata.sorted_tables):
        print('Purging data from {}...'.format(table.name))
        db_session.bind.execute(table.delete())


def get_db_session(db_url):
    engine = create_engine(db_url)
    session_factory = sessionmaker(autocommit=False, autoflush=False)
    Session = scoped_session(session_factory)
    Session.configure(bind=engine)
    db_session = Session()

    # Test connection
    try:
        db_session.bind.table_names()
    except:
        raise
    else:
        return db_session


def run_importers(db_session, local_filepaths):
    for importer in get_importer_instances(db_session, *local_filepaths):
        print("Running importer for {}...".format(importer.filename))
        importer.run()


def download_and_import(filename, database_type, database, username,
                        password=None, port=None, host='localhost',
                        use_cache=False, download_dir=DEFAULT_DOWNLOAD_DIR,
                        language_code=DEFAULT_LANGUAGE_CODE,
                        keep_existing_data=False, recreate_tables=False):
    download_dir = normalize_path(download_dir)
    db_url = get_db_url(database_type, database, username,
                        password, port, host)
    db_session = get_db_session(db_url)
    download_config = get_download_config(filename, language_code)
    local_filepaths = []
    for filename, opts in download_config.items():
        local_filepath = download(opts['url'], download_dir, use_cache)
        if opts.get('unzip') is True:
            local_filepath = unzip(local_filepath,
                                   filename_to_extract=filename,
                                   extract_dir=download_dir)
        local_filepaths.append(local_filepath)

    create_geoname_tables(db_session, recreate_tables=recreate_tables)
    if not keep_existing_data:
        purge_geoname_tables(db_session)
    run_importers(db_session, local_filepaths)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=RawArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('filename', choices=PRIMARY_GEONAME_FILENAMES,
                        help='Main geoname file to download.')
    parser.add_argument('-t', '--database-type', choices=DATABASE_CHOICES,
                        help='Database type', required=True)
    parser.add_argument('-d', '--database', help='Database name')
    parser.add_argument('-u', '--username',
                        help='Database username')
    parser.add_argument('-p', '--password', default=None,
                        help='Database password. Defaults to asking for the '
                             'password.')
    parser.add_argument('-n', '--no-password', action='store_const',
                        default=False, const=True,
                        help='Password-less database connection')
    parser.add_argument('-P', '--port', type=int,
                        help='Database port.', default=None)
    parser.add_argument('-H', '--host',
                        help='Database host', default='localhost')
    parser.add_argument('-c', '--use-cache',
                        help="Use previously downloaded files if they exist "
                             "in the download directory",
                        action='store_const', const=True, default=False)
    parser.add_argument('-D', '--download-dir', default=DEFAULT_DOWNLOAD_DIR,
                        help='Where to download the data files')
    parser.add_argument('-l', '--language-code', default=DEFAULT_LANGUAGE_CODE,
                        choices=LANGUAGE_CHOICES, help='Feature data language')
    parser.add_argument('-k', '--keep-existing-data', action='store_const',
                        default=False, const=True,
                        help="Don't truncate geoname* tables before inserting."
                             " No use in specifying this as an integrity error"
                             " will be raised. This behavior will not be the"
                             " default once incremental updates is supported.")
    parser.add_argument('-r', '--recreate-tables', action='store_const',
                        default=False, const=True,
                        help="Recreate geoname* tables.")

    args = parser.parse_args()
    if args.no_password is True:
        args.password = NOT_SET
    del args.no_password

    download_and_import(**vars(args))


if __name__ == '__main__':
    main()

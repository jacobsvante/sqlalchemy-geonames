BASE_DOWNLOAD_URL = 'http://download.geonames.org/export/dump/'


def full_url(filename):
    return BASE_DOWNLOAD_URL + filename


filename_config = {
    'admin1CodesASCII.txt': {
        'url': full_url('admin1CodesASCII.txt'),
    },
    'admin2Codes.txt': {
        'url': full_url('admin2Codes.txt'),
    },
    'allCountries.txt': {
        'url': full_url('allCountries.zip'),
        'unzip': True,
        'is_primary': True,
    },
    'alternateNames.txt': {
        'url': full_url('alternateNames.zip'),
        'unzip': True,
    },
    'cities1000.txt': {
        'url': full_url('cities1000.zip'),
        'unzip': True,
        'is_primary': True,
    },
    'cities15000.txt': {
        'url': full_url('cities15000.zip'),
        'unzip': True,
        'is_primary': True,
    },
    'cities5000.txt': {
        'url': full_url('cities5000.zip'),
        'unzip': True,
        'is_primary': True,
    },
    'countryInfo.txt': {
        'url': full_url('countryInfo.txt'),
    },
    'featureCodes_bg.txt': {
        'url': full_url('featureCodes_bg.txt'),
        'language_code': 'bg',
    },
    'featureCodes_en.txt': {
        'url': full_url('featureCodes_en.txt'),
        'language_code': 'en',
    },
    'featureCodes_nb.txt': {
        'url': full_url('featureCodes_nb.txt'),
        'language_code': 'nb',
    },
    'featureCodes_nn.txt': {
        'url': full_url('featureCodes_nn.txt'),
        'language_code': 'nn',
    },
    'featureCodes_no.txt': {
        'url': full_url('featureCodes_no.txt'),
        'language_code': 'no',
    },
    'featureCodes_ru.txt': {
        'url': full_url('featureCodes_ru.txt'),
        'language_code': 'ru',
    },
    'featureCodes_sv.txt': {
        'url': full_url('featureCodes_sv.txt'),
        'language_code': 'sv',
    },
    'hierarchy.txt': {
        'url': full_url('hierarchy.zip'),
        'unzip': True,
    },
    'iso-languagecodes.txt': {
        'url': full_url('iso-languagecodes.txt'),
    },
    'timeZones.txt': {
        'url': full_url('timeZones.txt'),
    },
    'userTags.txt': {
        'url': full_url('userTags.zip'),
        'unzip': True,
    },
}

# TODO: Support modification files
# alternateNamesDeletes-2013-12-16.txt
# alternateNamesModifications-2013-12-16.txt
# deletes-2013-12-16.txt
# modifications-2013-12-16.txt

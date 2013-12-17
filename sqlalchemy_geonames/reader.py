"""Classes for reading geonames text data dumps"""
import codecs
from datetime import date
from . import log
from ._compat import text_type, Decimal
from .utils import cached_property, try_int

logger = log.get_logger()


def fastdate(val):
    """Fast parsing of date object from string values
    Requires format YYYY-MM-DD.
    From http://stackoverflow.com/a/13468161/109897
    """
    # Somewhat slower:
    # date(*map(int, val.split('-')))
    return date(int(val[:4]), int(val[5:7]), int(val[8:10]))


class GeonameReader(object):

    # The first row with data (0-indexed). Some files, like timeZones.txt
    # contains headers. The headers are explicitly defined in each class so
    # we have no use for them.
    start_row = 0

    # Character(s) to split each row at
    delimiter = '\t'

    # Hook to pre-process a row before it's split by `delimiter`
    def row_preprocess(self, row_str):
        return row_str

    # Some of Geonames' files don't have equal amounts of
    # delimiters. (Noticed this for featureCodes_en.txt). Pad
    # with empty strings if `append_on_missing` is enabled.
    append_on_missing = False

    # Skip row instead of raising an exception when row contains too few
    # cells when this is set to True.
    skip_on_missing = False

    # Some files (like countryInfo.txt) begin lines with #. These will
    # be ignored.
    comment_character = '#'

    # A tuple of definitions for each field in the source data.
    # Must have same length as cells in the source data
    # Element at index 0 should be the field name to give to the cell.
    # Element at index 1 should be something that can be passed the cell's
    # value and return it with its correct type (most often a type
    #                                            like `int` or `str`.)
    # Example::
    #
    #     field_definitions = (
    #         ('id', int),
    #         ('name', text_type),
    #         ('modified', lambda v: datetime.strptime(v, '%Y-%m-%d')),
    #     )
    field_definitions = None

    @cached_property
    def field_names(self):
        return tuple(fd[0] for fd in self.field_definitions)

    @cached_property
    def type_definitions(self):
        return tuple(fd[1] for fd in self.field_definitions)

    def __init__(self, filepath):
        self.filepath = filepath

    def __iter__(self):
        diffmsg = (u"Row #{0} in {1} contained {2} cell values instead"
                   u" of the expected {3}.")
        skipmsg = u"Row #{0} in {1} skipped as some values were missing"
        len_type_definitions = len(self.type_definitions)

        with codecs.open(self.filepath, encoding='utf-8') as fh:
            for rownum, row in enumerate(fh):
                if rownum < self.start_row:
                    continue
                if row.startswith(self.comment_character):
                    continue
                row = self.row_preprocess(row)
                cell_values = row.rstrip('\n').split(self.delimiter)

                # Warn on missing values. An index error will be raised later
                # on too many cell values. The same goes for too few cell
                # values, unless `append_on_missing` is enabled.
                cell_count_diff = len_type_definitions - len(cell_values)
                if cell_count_diff != 0:
                    logger.warning(diffmsg.format(rownum, self.filepath,
                                   len(cell_values),
                                   len_type_definitions))
                    if self.skip_on_missing and cell_count_diff > 0:
                        logger.warning(skipmsg.format(rownum, self.filepath))
                        continue
                    if self.append_on_missing and cell_count_diff > 0:
                        cell_values += [''] * cell_count_diff

                # NOTE 2: Using OrderedDict is about 280% slower so avoid at
                #         all costs. 280% is a lot when working with ~8.5M
                #         rows!
                dct = dict()
                for i, (key, type_def) in enumerate(self.field_definitions):
                    try:
                        dct[key] = type_def(cell_values[i])
                    except Exception as exc:
                        logger.error(u'Got {0} for key "{1}" with value '
                                     u'"{2}".'.format(exc.__class__.__name__,
                                                      key, cell_values[i]))
                        raise
                yield dct


class GeonameReader(GeonameReader):
    field_definitions = (
        ('geonameid', int),
        ('name', text_type),
        ('asciiname', text_type),
        ('alternatenames', text_type),
        ('latitude', Decimal),
        ('longitude', Decimal),
        ('feature_class', text_type),
        ('feature_code', text_type),
        ('country_code', text_type),
        ('cc2', text_type),
        ('admin1_code', text_type),
        ('admin2_code', text_type),
        ('admin3_code', text_type),
        ('admin4_code', text_type),
        ('population', int),
        ('elevation', try_int),
        ('dem', text_type),
        ('timezone_id', text_type),
        ('modification_date', fastdate),
    )


class GeonameFeatureReader(GeonameReader):
    skip_on_missing = True

    def row_preprocess(self, row_str):
        # feature_class and feature_code is joined with a dot in
        # these files. Replace the dot with a tab so they can be seen
        # as two different fields.
        return row_str.replace('.', '\t', 1)

    field_definitions = (
        ('feature_class', text_type),
        ('feature_code', text_type),
        ('name', text_type),
        ('description', text_type),
    )


class GeonameTimezoneReader(GeonameReader):
    # First row contains headers
    start_row = 1

    field_definitions = (
        ('country_code', text_type),
        ('timezone_id', text_type),
        ('gmt_offset', Decimal),
        ('dst_offset', Decimal),
        ('raw_offset', Decimal),
    )


class GeonameCountryInfoReader(GeonameReader):
    field_definitions = (
        ('iso', text_type),
        ('iso3', text_type),
        ('iso_numeric', text_type),
        ('fips', text_type),
        ('country', text_type),
        ('capital', text_type),
        ('area_in_sq_km', try_int),
        ('population', int),
        ('continent', text_type),
        ('tld', text_type),
        ('currency_code', text_type),
        ('currency_name', text_type),
        ('phone', text_type),
        ('postal_code_format', text_type),
        ('postal_code_regex', text_type),
        ('languages', text_type),
        ('geonameid', try_int),
        ('neighbours', text_type),
        ('equivalent_fips_code', text_type),
    )


class GeonameHierarchyReader(GeonameReader):
    pass  # TODO: Write


class GeonameAlternateNamesReader(GeonameReader):
    pass  # TODO: Write

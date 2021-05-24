""""
Interface for a simple budget database in Notion, uses Notion API (https://developers.notion.com/).
No external requirements are needed. The code is python 3.6.

The user of this script can either insert a record in the database or query the valid tag names from
a specified Notion's database.

The database in question is defined as follows:
    - Type (select)       -  The type of the record, can be "EXPENSE" or "INCOME".
                             This will make the script alter the sign of the number, in order to use
                              a sum to get the current balance of the budget.
    - Date (date)         -  The date of the record, by default is the day of creation.
    - Concept (title)     -  The concept of the record, used as title by the database.
    - Amount (number)     -  The amount of the record, formatted as dollars.
    - Tags (multi_select) -  User-defined Tags, used to sort and filter the database.

The name of these columns can be altered, but if one does so should also alter the corresponding
values on settings.json.

Usage:
    $ python nbudget.py -t
    -> Output the names of the tags defined in the notion db.
    $ python nbudget.py [-i] [-d 3/4/2021] CONCEPT AMOUNT [TAG1, [TAG2...]]
    -> Insert a record to the notion db.
        * The CONCEPT is the concept of the expense/income (a description of it)
        * The AMOUNT is the numerical amount for the record, it will be turned negative by default,
          and considered an "EXPENSE", unless -i is passed.
    -> -i is optional, sets the type as "INCOME" and turns AMOUNT to positive.
    -> -d D/M/Y is optional, if not passed the date of creation will be used. You can set the
    preferred format via the settings.json (D/M/Y, M/D/Y, Y/M/D, etc...)
    -> Tags are optional, and you can input as many as you want, but they should already exist in
    the notion db.

The first usage of this script via terminal will prompt the user for the API_KEY and the DATABASE_ID
and will create a settings.json with default values. The user can edit this file at any time, or can
create a new one by running the script with -w.

When using this script as an imported library, the user can get a default settings dict by using
.get_default_settings(database_id, api_key) and passing along the corresponding values
(This will not alter any existing settings.json file). Then he can pass the return dictionary of
this function to create an instance of NBudgetController, through which the following methods are
exposed:
    * clear_tags_cache() -> We need the tags names for validating insert_record(), but we don't want
    to get the tags every time if we are inserting records iteratively, so we instead save a cache
    of them the first time. This methods allows for emptying this cache so we get the tags again.
    * get_tags()
    * insert_record(concept: str, amount: float, tags: list = None, income: str = 'OUT',
                    date: str = None)

Which do exactly as the terminal commands explained in usage do.

The settings.json file is structured as follows:
        'database_id':                - database_id
        'api_key':                    - API key
        'date_input_format': 'D/M/Y', - Preferred input format for dates (can be D/M/Y, M/D/Y, etc)
        'tag_separator': '\n',        - Preferred tag separator for terminal output
        'type_name': 'Type',          - Name of the Type column in the Notion's database
        'date_name': 'Date',          - Name of the Date column in the Notion's database
        'concept_name': 'Concept',    - Name of the Concept column in the Notion's database
        'amount_name': 'Amount',      - Name of the Amount column in the Notion's database
        'tags_name': 'Tags'           - Name of the Tags column in the Notion's database

"""
import os
import sys
import argparse
import json
import datetime
import urllib.request
from copy import deepcopy
from urllib.error import HTTPError
from http.client import HTTPResponse
from typing import Dict, List, Type

_PATH = os.path.dirname(os.path.abspath(__file__))

_SETTINGS_KEY_VALIDATION = ['database_id', 'api_key', 'date_input_format', 'tag_separator',
                            'type_name', 'date_name', 'concept_name', 'amount_name', 'tags_name']


def _err(error_msg: str) -> None:
    """
    Avoid cluttering stdout with raises. Print error message and exit.
    :param error_msg: str, error message to print.
    :raises SystemExit -> code 1
    """
    print(f"[!] Error: {error_msg}")
    sys.exit(1)


def get_default_settings(database_id: str, api_key: str) -> Dict[str, str]:
    """
    :param database_id: str, A valid Notion's database id accessible via the api_key.
    :param api_key: str, A valid Notion's api_key that has access to the database under database_id.
    :returns: Dict[str, str], A default settings dictionary with the users information.
    :raises TypeError: if database_id or api_key are not string objects.
    """
    if not isinstance(database_id, str):
        raise TypeError('Expected str for database_id, got: %s' % database_id)
    if not isinstance(api_key, str):
        raise TypeError('Expected str for database_id, got: %s' % database_id)

    return {
        'database_id': database_id,
        'api_key': api_key,
        'date_input_format': 'D/M/Y',
        'tag_separator': '\n',
        'type_name': 'Type',
        'date_name': 'Date',
        'concept_name': 'Concept',
        'amount_name': 'Amount',
        'tags_name': 'Tags'
    }


class NBudgetController:
    """
    Controller class for budget databases on Notion
    """
    _DATABASE_QUERY = 'https://api.notion.com/v1/databases/%s'
    _PAGE_INSERTION_QUERY = 'https://api.notion.com/v1/pages'
    _HEADERS = {
        "User-Agent": "",  # Notion is using cloudflare to filter python-urllib's UA
        "Content-Type": "application/json",
        "Authorization": "Bearer %s",
        "Notion-Version": "2021-05-13"
    }

    def __init__(self, settings: Dict[str, str], raises: bool = True):
        """
        Controller class for budget databases on Notion.

        :param settings: Dict[str, str], settings file
        :param raises: bool, When we run the script via terminal we want the errors to be printed
        into the terminal, when the script is being ran as a module, we want to raise our errors
        instead. By default we raise.
        """
        self.settings: Dict[str, str] = settings
        self.raises: bool = raises
        # Don't constantly re-get tags when we are using this iteratively
        self.tags_cache: List[str] = []

        # Set up the API variables
        self.page_insertion_query = NBudgetController._PAGE_INSERTION_QUERY
        self.database_query_url = NBudgetController._DATABASE_QUERY % self.settings['database_id']
        self.headers = deepcopy(NBudgetController._HEADERS)
        self.headers['Authorization'] = self.headers['Authorization'] % self.settings['api_key']

    def clear_tags_cache(self) -> None:
        """ Empty self.tags_cache """
        self.tags_cache = []

    def _wrap_error(self, error_msg: str, exception: Type[Exception]):
        """
        Wraps an error to decide if raising or calling _err depending on self.raises
        :param error_msg: str, error message to print
        :param exception: Exception, exception to raise
        :raises e: if self.raises, else SystemExit
        """
        if self.raises:
            raise exception(error_msg)
        _err(error_msg)

    def _api_call(self, url, headers, data=None) -> dict:
        """
        Performs an HTTP call to the API.

        :param url: str, url to call
        :param headers: dict, headers to use
        :param data: bytes-encoded string, data for the request, if any.
        :return: dict, json response from the API
        :raises APIError, if the request went right but the API returned an error
        :raises HTTPError, if the request went wrong
        """
        request_object = urllib.request.Request(url, headers=headers, data=data)
        try:
            response: HTTPResponse = urllib.request.urlopen(request_object)
        except HTTPError as exception:
            try:
                # Check if the error is from the API or HTTP by attempting to JSON the response
                err_json = json.loads(exception.read())
                # TODO: self._parse_api_error() -> Give better feedback?
                return self._wrap_error('Api Error: %s -> %s'
                                        % (err_json['code'], err_json['message']), self.APIError)
            except json.decoder.JSONDecodeError:
                if exception.code == 403:  # This can happen if the UA is using python-urllib
                    return self._wrap_error('HTTP Error: %s -> Check your UA if you have modified '
                                            'the script' % exception.code, self.HTTPError)

                return self._wrap_error('HTTP Error: %s' % exception.code, self.HTTPError)
        else:
            return json.loads(response.read())

    def get_tags(self) -> List[str]:
        """
        Get the tags from the Notion's database.
        Fills self.tags_cache and returns them.

        :return: List[str], Tag names
        :raises APIParsingError: if there were errors when attempting to parse the API response
        """
        response = self._api_call(self.database_query_url, self.headers)
        tags_name = self.settings['tags_name']  # Get tags column name

        try:  # Get tag names out of the response
            options = [o['name'] for o in response[
                'properties'][tags_name]['multi_select']['options']]

        except KeyError as exception:  # Parsing error
            # Check what kind of key is missing
            if exception.args[0] == tags_name:  # Tags column name

                # Detect if there is another column with multi_select type, multiple, or none
                multi_selects = []
                for key in response['properties']:
                    if 'multi_select' in response['properties'][key].keys():
                        multi_selects.append(key)

                if len(multi_selects) == 1:
                    return self._wrap_error('APIParsingError: Column with name "%s" does not '
                                            'exist in the Notion database. Could it be "%s"? If '
                                            'it is then change "tag_name" in the settings file '
                                            'for it.' % (tags_name, multi_selects[0]),
                                            self.APIParsingError)
                elif len(multi_selects) > 1:
                    return self._wrap_error('APIParsingError: Column with name "%s" does not exist'
                                            'in the Notion database. Could it be one of these: '
                                            '%s? If one is then change "tag_name" in the settings '
                                            'file for it.' % (tags_name, ', '.join(multi_selects)),
                                            self.APIParsingError)
                else:
                    return self._wrap_error('APIParsingError: No multi_select type column found in'
                                            ' Notion database.',
                                            self.APIParsingError)

            elif exception.args[0] == 'multi_select':  # Wrong column type
                wrong_type = next(iter(response['properties'][tags_name]))
                return self._wrap_error('APIParsingError: Type of the %s column is: "%s". '
                                        'Must be "multi_select"' % (tags_name, wrong_type),
                                        self.APIParsingError)
            else:
                return self._wrap_error('APIParsingError: Did not understand the API response: '
                                        '%s' % response, self.APIParsingError)
        else:
            self.tags_cache = options
            return options

    def insert_record(self, concept: str, amount: float, tags: List[str] = None,
                      income: bool = False, date: str = '') -> None:
        """
        Transforms the arguments into valid page insertion data for the API and calls it.
        It calls self.get_tags() if self.tags_cache is empty in order to be able to validate the
        tags the user is attempting to pass into the database.

        :param concept: str, the record's concept
        :param amount: float, the record's amount
        :param tags: List[str], the record's tags. Empty by default.
        :param income: bool, if the record is an INCOME type. False by default.
        :param date: str, the record's date. None by default, which will use today's date.

        :return: None
        :raises InvalidTag: If the user attempted to use a tag that did not exist in Notion's db
        :raises APIError, if thr request went right but the API returned an error
        :raises HTTPError, if the request went wrong

        Lets the following exceptions escalate:

        From self._format_date()
        :raises InvalidDateFormat: If there is a missing key (D, M, Y) in date_input_format
        :raises InvalidDate: If there is a missing value in date
        :raises InvalidDateRange: If either day, month, or year is beyond range

        From self.get_tags()
        :raises APIError, if a request went right but the API returned an error
        :raises HTTPError, if a request went wrong
        :raises APIParsingError: if there were errors when attempting to parse the Tags API response
        """
        # Date parsing
        if date:
            date_object = self._format_date(date, self.settings['date_input_format'])
        else:
            today = datetime.datetime.today()
            # We don't want to clutter the database with time information
            date_object = datetime.date(today.year, today.month, today.day)

        iso_date = date_object.isoformat()  # Notion uses ISO 8601 Format

        # Income parsing
        record_type = 'EXPENSE' if not income else 'INCOME'
        amount = -amount if not income else amount

        # First build
        data: dict = {"parent": {"database_id": self.settings['database_id']},
                      "properties": {self.settings['type_name']: {"select": {"name": record_type}},
                                     self.settings['date_name']: {"date": {"start": iso_date}},
                                     self.settings['concept_name']: {
                                         "title": [{"text": {"content": concept}}]},
                                     self.settings['amount_name']: {"number": amount}
                                     }
                      }

        # Validate tags
        if tags:
            valid_options = self.tags_cache if self.tags_cache else self.get_tags()

            for tag in tags:
                if tag not in valid_options:
                    self._wrap_error('InvalidTag: Tag does not exist in Notion db: %s, use one of '
                                     'these: %s' % (tag, ", ".join(valid_options)), self.InvalidTag)

            tags_list = [{"name": t} for t in tags]
            data['properties'][self.settings['tags_name']] = {"multi_select": tags_list}

        encoded_data = str(data).replace("'", '"').encode()  # Encode data for urllib
        self._api_call(self.page_insertion_query, self.headers, encoded_data)

    def _format_date(self, date: str, date_input_format: str) -> datetime.date:
        """
        Transform a date string inputted by the user into a datetime.date using
        a date_input_format specified in the settings.

        We don't care if the user has done something like: D/M/Y/Y, we grab the first occurrence.

        :param date: str of date to be parsed by format specified on date_input_format
        :param date_input_format: str of format D/M/Y (D, M and Y separated by /)
        :return: datetime.date object
        :raises InvalidDateFormat: If there is a missing key (D, M, Y) in date_input_format
        :raises InvalidDate: If there is a missing value in date
        :raises InvalidDateRange: If either day, month, or year is beyond range
        """
        # Split by /
        split_date_input_format, split_date = date_input_format.split('/'), date.split('/')

        # Use format positions as indexes for date positions
        try:
            year, month, day = split_date[split_date_input_format.index('Y')], \
                               split_date[split_date_input_format.index('M')], \
                               split_date[split_date_input_format.index('D')]
        except ValueError:  # Missing key in date_input_format
            return self._wrap_error('Invalid date_input_format in settings file: %s'
                                    % date_input_format, self.InvalidDateFormat)
        except IndexError:  # Missing value in date
            return self._wrap_error('Invalid date: %s' % date, self.InvalidDate)
        else:
            try:
                return datetime.date(int(year), int(month), int(day))
            except ValueError:  # Either day, month, or year is beyond range
                return self._wrap_error('Invalid date range: %s' % date, self.InvalidDateRange)

    class InvalidDateRange(Exception):
        """ The date is beyond range """

    class InvalidDate(Exception):
        """ The date the user inputted is invalid """

    class InvalidDateFormat(Exception):
        """ The date format in the settings file is invalid """

    class APIError(Exception):
        """ The API has returned an error """

    class HTTPError(Exception):
        """ urllib has returned an HTTP error """

    class APIParsingError(Exception):
        """ get_tags() returned a structure the script can't work with """

    class InvalidTag(Exception):
        """ Attempted to insert a Tag that didn't exist in Notion's db as an option """


def _read_settings(*, filepath='settings.json') -> dict:
    """
    Reads and validates settings.json file on the scripts path using _SETTINGS_KEY_VALIDATION
    If the dictionary doesn't exist it calls _settings_wizard instead.

    :param filepath: str, just for the sake of not overwriting our own files when testing.
    :returns: dict, settings object
    """
    try:
        with open(_PATH + '/' + filepath, 'r', encoding='utf-8') as settings_file:
            settings = json.load(settings_file)
        settings_file.close()
    except FileNotFoundError:
        answer = _chose_option('Settings file does not exist. Create one?', ['Y', 'N'])
        if answer == 'Y':
            return _settings_wizard(filepath=filepath)

        _err(f'No {filepath} file.')

    except json.decoder.JSONDecodeError as exception:
        _err('settings.json is malformed: %s\nConsider running the '
             'settings_wizard by using -w option.' % exception)

    for key in _SETTINGS_KEY_VALIDATION:
        if key not in settings.keys():
            _err('settings.json file is missing key: %s\nConsider running the '
                 'settings_wizard by using -w option.' % key)

    return settings


def _settings_wizard(*, filepath='settings.json') -> dict:
    """
    Asks the user for its Notion's api_key and database_id and creates a new settings.json in the
    scripts path by using get_default_settings().

    :param filepath: str, just for the sake of not overwriting our own files when testing.
    :returns: dict, settings object
    """
    database_id = input('[>] Please enter the database_id of the Notion\'s budget database:')
    api_key = input('[>] Please enter the Notion\'s API key associated with this database_id:')
    settings = get_default_settings(database_id, api_key)
    with open(_PATH + '/' + filepath, 'w', encoding='utf-8') as settings_file:
        json.dump(settings, settings_file, indent=True)
    settings_file.close()
    return settings


def _chose_option(prompt: str, valid_options: List[str]) -> str:
    """
    Prompts the user via input() and forces it to chose an option from a list.
    All strings in valid_options will be treated without case distinction.

    :param prompt: str, message to print for the prompt
    :param valid_options: List[str], valid options the user can chose
    :return: str, option chosen
    """
    valid_options = [vo.upper() for vo in valid_options]
    valid_response = False
    response = ''
    while not valid_response:
        response = input(f'[>] {prompt} {valid_options}')
        if response.upper() in valid_options:
            valid_response = True
    return response


class GetTags(argparse.Action):
    """ Creates a class for NBudgetController and calls get_tags() """

    def __call__(self, parser, namespace, values, option_string=None):
        settings = _read_settings()
        options = NBudgetController(settings, raises=False).get_tags()
        print(settings['tag_separator'].join(options))
        parser.exit()


class RunWizard(argparse.Action):
    """ Calls _settings_wizard() """

    def __call__(self, parser, namespace, values, option_string=None):
        _settings_wizard()
        parser.exit()


if __name__ == '__main__':
    # Terminal entry points

    _DESC = 'Interface for a simple budget database in Notion using Notion\'s API. The database ' \
            'needs to be structured as follows: Type(select) -> with two options: "INCOME" and ' \
            '"EXPENSE", Date(date), Concept(title), Amount(number) -> formatted as Dollars, ' \
            'Tags(multi_select). The names of each column can be others (as long as the types are' \
            ' respected), but you will have to edit the settings.json file so the script knows ' \
            'their new names. '

    argument_parser = argparse.ArgumentParser(description=_DESC)

    W_HELP = 'Run the settings wizard and exit.'
    argument_parser.add_argument('-w', '--wizard', nargs=0, action=RunWizard, help=W_HELP)
    T_HELP = 'Output the current tag names in the database and exit.'
    argument_parser.add_argument('-t', '--tags', nargs=0, action=GetTags, help=T_HELP)

    I_HELP = 'Record is considered an INCOME instead of an EXPENSE.'
    argument_parser.add_argument('-i', '--income', action='store_true', help=I_HELP)
    D_HELP = 'The date to use for the expense record, if not used the current day will be used.'
    argument_parser.add_argument('-d', '--date', metavar='DATE', type=str, nargs=1, help=D_HELP)
    CONCEPT_HELP = 'The concept for the record.'
    argument_parser.add_argument('concept', metavar='CONCEPT', type=str, nargs=1, help=CONCEPT_HELP)
    AMOUNT_HELP = 'The amount value for the record.'
    argument_parser.add_argument('amount', metavar='AMOUNT', type=float, nargs=1, help=AMOUNT_HELP)
    TAG_HELP = 'A tag or tags for the record. Must be valid tags, if unsure, run "nbudget.py -t"'
    argument_parser.add_argument('tags', metavar='TAG', type=str, nargs='*', help=TAG_HELP)

    parsed_arguments = argument_parser.parse_args()
    NBC = NBudgetController(_read_settings(), raises=False)
    NBC.insert_record(parsed_arguments.concept[0], parsed_arguments.amount[0],
                      parsed_arguments.tags, parsed_arguments.income, parsed_arguments.date[0]
                      if parsed_arguments.date else None)

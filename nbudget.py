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
this function to create an instance of NBudgetController, through which he can access the
following methods:

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
import argparse
import json
import datetime
import urllib.request
from urllib.error import HTTPError
from http.client import HTTPResponse
from typing import List

_SETTINGS_KEY_VALIDATION = ['database_id', 'api_key', 'date_input_format', 'tag_separator',
                            'type_name', 'date_name', 'concept_name', 'amount_name', 'tags_name']


def get_default_settings(database_id: str, api_key: str):
    """
    TODO: Document

    :param database_id:
    :param api_key:
    :return:
    """
    default_settings = {
        'database_id': None,
        'api_key': None,
        'date_input_format': 'D/M/Y',
        'tag_separator': '\n',
        'type_name': 'Type',
        'date_name': 'Date',
        'concept_name': 'Concept',
        'amount_name': 'Amount',
        'tags_name': 'Tags'
    }
    return default_settings


class NBudgetController:
    """ Controller class for budget databases on Notion """

    def __init__(self, settings: dict = None):
        """
        :param settings:
        """
        self.settings = settings

    def _err(self, error_msg):
        """ TODO: Document """

    def _msg(self, msg):
        """ TODO: Document """

    def _api_call(self, data=None):
        """ TODO: Document """

    def _query_tags(self):
        """ TODO: Document """

    def get_tags(self):
        """ TODO: Document """

    def insert_record(self, concept: str, amount: float, tags: list = None, income: str = 'OUT',
                      date: str = None):
        """
        TODO: Document
        :param concept:
        :param amount:
        :param tags:
        :param income:
        :param date:
        :return:
        """

    def __format_date(self, date: str):
        """ TODO: Document """


if __name__ == '__main__':
    # Terminal entry point

    class ListTags(argparse.Action):
        """ TODO: Document """
        def __call__(self, parser, namespace, values, option_string):
            parser.exit()


    class RunWizard(argparse.Action):
        """ TODO: Document """
        def __call__(self, parser, namespace, values, option_string):
            parser.exit()

    def _read_settings(filepath: str = None) -> dict:
        """ TODO: Document """

    def __chose_option(prompt: str, options: List[str]) -> str:
        """ TODO: Document """

    def _settings_wizard():
        """ TODO: Document """


    _DESC = 'Interface for a simple budget database in Notion using Notion\'s API. The database ' \
            'needs to be structured as follows: Type(select), Date(date), Concept(title), ' \
            'Amount(number), Tags(multi_select). The names of each column can be others,' \
            'as long as the types are respected, you will have to edit the settings.json file so ' \
            'the script knows their new names. '

    argument_parser = argparse.ArgumentParser(description=_DESC)

    w_help = 'Run the settings wizard and exit.'
    argument_parser.add_argument('-w', '--wizard', nargs=0, action=RunWizard, help=w_help)
    t_help = 'Output the current tag names in the database and exit.'
    argument_parser.add_argument('-t', '--tags', nargs=0, action=ListTags, help=t_help)

    i_help = 'Record is considered an income instead of an expense.'
    argument_parser.add_argument('-i', '--income', action='store_true', help=i_help)
    d_help = 'The date to use for the expense record, if not used the current day will be used..'
    argument_parser.add_argument('-d', '--date', metavar='DATE', type=str, nargs=1, help=d_help)
    concept_help = 'The concept for the record.'
    argument_parser.add_argument('concept', metavar='CONCEPT', type=str, nargs=1, help=concept_help)
    amount_help = 'The amount value for the record.'
    argument_parser.add_argument('amount', metavar='AMOUNT', type=float, nargs=1, help=amount_help)
    tag_help = 'A tag or tags for the record. Must be valid tags, if unsure, run "nbudget.py -t"'
    argument_parser.add_argument('tags', metavar='TAG', type=str, nargs='*', help=tag_help)

    x = argument_parser.parse_args(['-h'])

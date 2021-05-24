""" Tests for nbudget.py """
import os
import json
import unittest
import datetime
from unittest import mock
from urllib.error import HTTPError

import nbudget


class Test(unittest.TestCase):
    """ Tests for the modules methods """

    def test_err(self):
        """ Test _err raises SystemExit """
        self.assertRaises(SystemExit, nbudget._err, 'Testing _err')

    def test_get_default_settings(self):
        """ Test the function returns a valid dictionary right."""
        expected = {
            'database_id': 'MY_DB_ID',
            'api_key': 'MY_API_KEY',
            'date_input_format': 'D/M/Y',
            'tag_separator': '\n',
            'type_name': 'Type',
            'date_name': 'Date',
            'concept_name': 'Concept',
            'amount_name': 'Amount',
            'tags_name': 'Tags'
        }
        self.assertEqual(expected, nbudget.get_default_settings('MY_DB_ID', 'MY_API_KEY'))

    def test_get_default_settings_type_error(self):
        """ Test the function raises a Type error when database_id or api_key are not strings """
        self.assertRaises(TypeError, nbudget.get_default_settings, None, None)
        self.assertRaises(TypeError, nbudget.get_default_settings, None, '')
        self.assertRaises(TypeError, nbudget.get_default_settings, '', None)

    def test__read_settings_right(self):
        """ Test that _read_settings reads and returns the dictionary file specified."""
        test_file_path = 'test_settings.json'  # We don't want to overwrite our own settings
        expected = {
            'database_id': 'MY_DB_ID',
            'api_key': 'MY_API_KEY',
            'date_input_format': 'D/M/Y',
            'tag_separator': '\n',
            'type_name': 'Type',
            'date_name': 'Date',
            'concept_name': 'Concept',
            'amount_name': 'Amount',
            'tags_name': 'Tags'
        }
        with open(f'{nbudget._PATH}/{test_file_path}', 'w', encoding='utf-8') as test_file:
            json.dump(expected, test_file, indent=True)
        test_file.close()
        self.assertEqual(expected, nbudget._read_settings(filepath=test_file_path))
        os.remove(test_file_path)  # Clean up

    def test__read_settings_exits_on_invalid_settings_keys(self):
        """ Test that _read_settings raises SystemExit if its lacking a KEY."""
        test_file_path = 'test_settings.json'  # We don't want to overwrite our own settings
        invalid_settings = {'database_id': 'MY_DATABASE_ID'}
        with open(f'{nbudget._PATH}/{test_file_path}', 'w', encoding='utf-8') as test_file:
            json.dump(invalid_settings, test_file, indent=True)
        test_file.close()
        self.assertRaises(SystemExit, nbudget._read_settings, filepath=test_file_path)
        os.remove(test_file_path)  # Clean up

    def test__read_settings_exits_on_malformed_json(self):
        """ Test that _read_settings exits if settings.json file is malformed."""
        test_file_path = 'test_settings.json'  # We don't want to overwrite our own settings
        malformed_settings = '{"database_id": "malformed'
        with open(f'{nbudget._PATH}/{test_file_path}', 'w', encoding='utf-8') as test_file:
            test_file.write(malformed_settings)
        test_file.close()
        self.assertRaises(SystemExit, nbudget._read_settings, filepath=test_file_path)
        os.remove(test_file_path)  # Clean up

    @mock.patch('nbudget.input', create=True)
    def test__read_settings_calls_wizard(self, mocked_input):
        """ Test that _read_settings prompts the user for the settings_wizard if the file does
        not exist and it returns the settings right if user says yes and goes through wizard."""
        test_file_path = 'test_settings.json'  # We don't want to overwrite our own settings
        expected = {
            'database_id': 'MY_DB_ID',
            'api_key': 'MY_API_KEY',
            'date_input_format': 'D/M/Y',
            'tag_separator': '\n',
            'type_name': 'Type',
            'date_name': 'Date',
            'concept_name': 'Concept',
            'amount_name': 'Amount',
            'tags_name': 'Tags'
        }
        mocked_input.side_effect = ['Y', 'MY_DB_ID', 'MY_API_KEY']
        self.assertEqual(expected, nbudget._read_settings(filepath=test_file_path))
        os.remove(test_file_path)  # Clean up

    @mock.patch('nbudget.input', create=True)
    def test__read_settings_does_not_call_wizard_exit(self, mocked_input):
        """ Test that _read_settings exits if settings.json file does not exist and user says no."""
        test_file_path = 'test_settings.json'  # We don't want to overwrite our own settings
        mocked_input.side_effect = ['N']
        self.assertRaises(SystemExit, nbudget._read_settings, filepath=test_file_path)

    @mock.patch('nbudget.input', create=True)
    def test__settings_wizard_creates_settings_right(self, mocked_input):
        """ Test that _settings_wizard() creates the settings dict right. """
        test_file_path = 'test_settings.json'  # We don't want to overwrite our own settings
        expected = {
            'database_id': 'MY_DB_ID',
            'api_key': 'MY_API_KEY',
            'date_input_format': 'D/M/Y',
            'tag_separator': '\n',
            'type_name': 'Type',
            'date_name': 'Date',
            'concept_name': 'Concept',
            'amount_name': 'Amount',
            'tags_name': 'Tags'
        }
        mocked_input.side_effect = ['MY_DB_ID', 'MY_API_KEY']
        self.assertEqual(expected, nbudget._settings_wizard(filepath=test_file_path))
        os.remove(test_file_path)  # Clean up

    @mock.patch('nbudget.input', create=True)
    def test__settings_wizard_creates_creates_file_right(self, mocked_input):
        """ Test that _settings_wizard() creates the settings.json file right. """
        test_file_path = 'test_settings.json'  # We don't want to overwrite our own settings
        expected = {
            'database_id': 'MY_DB_ID',
            'api_key': 'MY_API_KEY',
            'date_input_format': 'D/M/Y',
            'tag_separator': '\n',
            'type_name': 'Type',
            'date_name': 'Date',
            'concept_name': 'Concept',
            'amount_name': 'Amount',
            'tags_name': 'Tags'
        }
        mocked_input.side_effect = ['MY_DB_ID', 'MY_API_KEY']
        nbudget._settings_wizard(filepath=test_file_path)
        with open(f'{nbudget._PATH}/{test_file_path}', 'r', encoding='utf-8') as test_file:
            actual = json.load(test_file)
        test_file.close()
        self.assertEqual(expected, actual)
        os.remove(test_file_path)  # Clean up

    @mock.patch('nbudget.input', create=True)
    def test__chose_option(self, mocked_input):
        """ Test that chose_option only returns from input when a valid option is passed in
        to input, and that it doesn't care about case. """
        expected = 'NoCaSe'
        mocked_input.side_effect = ['Invalid', 'Invalid', expected]
        self.assertEqual(expected, nbudget._choose_option('', ['NOCASE', 'OTHER']))

    @mock.patch('nbudget.NBudgetController.get_tags', create=True)
    def test_GetTags(self, mocked_method):
        """ Test GetTags.__call__() calls NBudget"""
        mock__read_settings = mock.patch('nbudget._read_settings', create=True)
        mock__read_settings.return_value = nbudget.get_default_settings('abc', 'bcd')
        nbudget.GetTags.__call__(None, mock.Mock(), None, None, None)
        mocked_method.assert_called()

    @mock.patch('nbudget._settings_wizard')
    def test_RunWizard(self, mocked_method):
        """ Test RunWizard.__call__() calls NBudget"""
        nbudget.RunWizard.__call__(None, mock.Mock(), None, None, None)
        mocked_method.assert_called()


class TestNBudgetController(unittest.TestCase):
    """ Tests for the NBudgetController class """

    def setUp(self) -> None:
        """ Set up by creating an NBudgetController """
        settings = nbudget.get_default_settings('MY_DB_ID', 'MY_API_KEY')
        self.NBudgetController = nbudget.NBudgetController(settings)

    def test_clear_tags_cache(self):
        """ Test self.NBudgetController.tags_cache gets emptied. """
        self.NBudgetController.tags_cache = [1, 2, 3, 4, 5, 6]
        self.NBudgetController.clear_tags_cache()
        self.assertEqual([], self.NBudgetController.tags_cache)

    def test__wrap_error_raises_on(self):
        """ Tests that _wrap_error raises Exception passed in when self.raises is True """
        self.NBudgetController.raises = True
        self.assertRaises(TypeError, self.NBudgetController._wrap_error, '', TypeError)

    @mock.patch('nbudget._err', create=True)
    def test__wrap_error_raises_off(self, mocked__err):
        """ Tests that _wrap_error calls _err() instead when self.raises is False """
        self.NBudgetController.raises = False
        self.NBudgetController._wrap_error('', TypeError)
        mocked__err.assert_called()

    @mock.patch('urllib.request.urlopen', create=True)
    def test_api_call_right(self, mocked_urlopen):
        """ Test that _api_call calls urlopen() and returns parsed json """
        second_mock = mock.Mock()
        expected = {'a': 1}
        second_mock.read.return_value = str(expected).replace("'", '"')
        mocked_urlopen.return_value = second_mock
        self.assertEqual(expected, self.NBudgetController._api_call('http://example.org', {}, b''))

    @mock.patch('urllib.request.urlopen', create=True)
    def test_api_call_raises_APIError(self, mocked_urlopen):
        """ Test that _api_call raises APIError when an HTTPError returns a json string"""
        second_mock: mock.Mock = mock.Mock()
        expected = {'code': '', 'message': ''}
        second_mock.read.return_value = str(expected).replace("'", '"')
        mocked_urlopen.side_effect = HTTPError('', 0, '', {'': ''}, second_mock)
        self.assertRaises(self.NBudgetController.APIError, self.NBudgetController._api_call,
                          'http://google.com', {}, b'')

    @mock.patch('urllib.request.urlopen', create=True)
    def test_api_call_raises_HTTPError(self, mocked_urlopen):
        """ Test that _api_call raises HTTPError when an HTTPError does not return a json string """
        # First try 403, as we have separated it
        second_mock: mock.Mock = mock.Mock()
        second_mock.code.return_value = 403
        second_mock.read.return_value = 'error'
        mocked_urlopen.side_effect = HTTPError('', 0, '', {'': ''}, second_mock)
        self.assertRaises(self.NBudgetController.HTTPError, self.NBudgetController._api_call,
                          'http://google.com', {}, b'')

        # Then try not 403
        second_mock: mock.Mock = mock.Mock()
        second_mock.code.return_value = 503
        second_mock.read.return_value = 'error'
        mocked_urlopen.side_effect = HTTPError('', 0, '', {'': ''}, second_mock)
        self.assertRaises(self.NBudgetController.HTTPError, self.NBudgetController._api_call,
                          'http://google.com', {}, b'')

    @mock.patch('nbudget.NBudgetController._api_call', create=True)
    def test_get_tags_right(self, mocked_api_call):
        """ Tests get_tags calls _api_call with the right arguments, and returns the options."""
        expected = ['a', 'b']
        return_value = {'properties': {'Tags': {'multi_select': {'options': [{'name': 'a'},
                                                                             {'name': 'b'}]}}}}
        mocked_api_call.side_effect = [return_value]
        self.assertEqual(expected, self.NBudgetController.get_tags())

    @mock.patch('nbudget.NBudgetController._api_call', create=True)
    def test_get_tags_different_tags_name(self, mocked_api_call):
        """ Tests get_tags works right when tags_name has changed in settings """
        self.NBudgetController.settings['tags_name'] = 'Changed Tag Name'
        expected = ['a', 'b']
        return_value = {'properties': {
            'Changed Tag Name': {'multi_select': {'options': [{'name': 'a'}, {'name': 'b'}]}}}}
        mocked_api_call.side_effect = [return_value]
        self.assertEqual(expected, self.NBudgetController.get_tags())

    @mock.patch('nbudget.NBudgetController._api_call', create=True)
    def test_get_tags_unexpected_structure_raises_APIParsingError_wrong_tag_name_one_other_option(
            self, mocked_api_call):
        """ Test get_tags() return APIParsingError when it cannot parse the response due to wrong
        tag column name, one other option """
        return_value = {'properties': {
            'Other name': {'multi_select': {'options': [{'name': 'a'}, {'name': 'b'}]}}}}
        mocked_api_call.side_effect = [return_value]
        self.assertRaises(self.NBudgetController.APIParsingError, self.NBudgetController.get_tags)

    @mock.patch('nbudget.NBudgetController._api_call', create=True)
    def test_get_tags_unexpected_structure_raises_APIParsingError_wrong_tag_name_many_other_options(
            self, mocked_api_call):
        """ Test get_tags() return APIParsingError when it cannot parse the response due to wrong
        tag column name, several other options """
        return_value = {'properties': {
            'Other name': {'multi_select': {'options': [{'name': 'a'}, {'name': 'b'}]}},
            'Another name': {'multi_select': {'options': [{'name': 'a'}, {'name': 'b'}]}}}}
        mocked_api_call.side_effect = [return_value]
        self.assertRaises(self.NBudgetController.APIParsingError, self.NBudgetController.get_tags)

    @mock.patch('nbudget.NBudgetController._api_call', create=True)
    def test_get_tags_unexpected_structure_raises_APIParsingError_wrong_tag_name_no_other_options(
            self, mocked_api_call):
        """ Test get_tags() return APIParsingError when it cannot parse the response due to wrong
        tag column name, no other options """
        return_value = {'properties': {
            'Other name': {'select': {'options': [{'name': 'a'}, {'name': 'b'}]}}}}
        mocked_api_call.side_effect = [return_value]
        self.assertRaises(self.NBudgetController.APIParsingError, self.NBudgetController.get_tags)

    @mock.patch('nbudget.NBudgetController._api_call', create=True)
    def test_get_tags_unexpected_structure_raises_APIParsingError_wrong_tag_column_type(
            self, mocked_api_call):
        """ Test get_tags() return APIParsingError when it cannot parse the response due to wrong
        tag column type """
        return_value = {'properties': {'Tags': {'select': {'options': [{'name': 'a'},
                                                                       {'name': 'b'}]}}}}
        mocked_api_call.side_effect = [return_value]
        self.assertRaises(self.NBudgetController.APIParsingError, self.NBudgetController.get_tags)

    @mock.patch('nbudget.NBudgetController._api_call', create=True)
    def test_get_tags_unexpected_d_structure_raises_APIParsingError_wrong_structure(
            self, mocked_api_call):
        """ Test get_tags() return APIParsingError when it cannot parse the response due to extreme
        difference. """
        return_value = {'abd': {'ee': {'ff': {'ag32': [{'name': 'a'}, {'name': 'b'}]}}}}
        mocked_api_call.side_effect = [return_value]
        self.assertRaises(self.NBudgetController.APIParsingError, self.NBudgetController.get_tags)

    @mock.patch('nbudget.NBudgetController._api_call', create=True)
    def test_insert_record_right(self, mocked_api_call):
        """ Test inserts works right """
        self.NBudgetController.tags_cache = ['Tag1']

        expected = b'{"parent": {"database_id": "MY_DB_ID"}, ' \
                   b'"properties": {"Type": {"select": {"name": "EXPENSE"}}, "Date": {"date": ' \
                   b'{"start": "2019-01-12"}}, "Concept": {"title": [{"text": {"content": "My ' \
                   b'Concept"}}]}, "Amount": {"number": -1200.0}, "Tags": {"multi_select": [{' \
                   b'"name": "Tag1"}]}}}'

        self.NBudgetController.insert_record('My Concept', 1200.0, ["Tag1"], False, '12/1/2019')
        mocked_api_call.assert_called_with(self.NBudgetController.page_insertion_query,
                                           self.NBudgetController.headers, expected)

    @mock.patch('nbudget.NBudgetController._api_call', create=True)
    def test_insert_record_right_no_date(self, mocked_api_call):
        """ Test inserts works right without a date"""
        self.NBudgetController.tags_cache = ['Tag1']
        today = datetime.datetime.today()
        date = datetime.date(today.year, today.month, today.day).isoformat()

        expected = b'{"parent": {"database_id": "MY_DB_ID"}, ' \
                   b'"properties": {"Type": {"select": {"name": "EXPENSE"}}, "Date": {"date": ' \
                   b'{"start": "%s"}}, "Concept": {"title": [{"text": {"content": "My ' \
                   b'Concept"}}]}, "Amount": {"number": -1200.0}}}' % date.encode()

        self.NBudgetController.insert_record('My Concept', 1200.0, [], False)
        mocked_api_call.assert_called_with(self.NBudgetController.page_insertion_query,
                                           self.NBudgetController.headers, expected)

    @mock.patch('nbudget.NBudgetController._api_call', create=True)
    def test_insert_record_right_using_True_income_flag(self, mocked_api_call):
        """ Test inserts works right when using a True income flag. (Amount is positive and Type is
        "INCOME" """
        self.NBudgetController.tags_cache = ['Tag1']

        expected = b'{"parent": {"database_id": "MY_DB_ID"}, ' \
                   b'"properties": {"Type": {"select": {"name": "INCOME"}}, "Date": {"date": ' \
                   b'{"start": "2019-01-12"}}, "Concept": {"title": [{"text": {"content": "My ' \
                   b'Concept"}}]}, "Amount": {"number": 1200.0}}}'

        self.NBudgetController.insert_record('My Concept', 1200.0, [], True, '12/1/2019')
        mocked_api_call.assert_called_with(self.NBudgetController.page_insertion_query,
                                           self.NBudgetController.headers, expected)

    @mock.patch('nbudget.NBudgetController._api_call', create=True)
    def test_insert_record_right_using_different_name_settings(self, mocked_api_call):
        """ Test inserts work right when we use other name settings"""
        self.NBudgetController.tags_cache = ['Tag1']
        self.NBudgetController.settings['type_name'] = 'New Type Name'
        self.NBudgetController.settings['date_name'] = "New Date Name"
        self.NBudgetController.settings['concept_name'] = "New Concept Name"
        self.NBudgetController.settings['amount_name'] = "New Amount Name"
        self.NBudgetController.settings['tags_name'] = "New Tags Name"

        expected = b'{"parent": {"database_id": "MY_DB_ID"}, ' \
                   b'"properties": {"New Type Name": {"select": {"name": "INCOME"}}, ' \
                   b'"New Date Name": {"date": {"start": "2019-01-12"}}, ' \
                   b'"New Concept Name": {"title": [{"text": {"content": "My Concept"}}]}, ' \
                   b'"New Amount Name": {"number": 1200.0}, "New Tags Name": {"multi_select": [{' \
                   b'"name": "Tag1"}]}}}'

        self.NBudgetController.insert_record('My Concept', 1200.0, ["Tag1"], True, '12/1/2019')
        mocked_api_call.assert_called_with(self.NBudgetController.page_insertion_query,
                                           self.NBudgetController.headers, expected)

    def test_insert_record_raises_InvalidTag_when_using_invalid_tag_name(self):
        """ Test inserts works right when using an Invalid Tag name"""
        self.NBudgetController.tags_cache = ['Tag1']
        self.assertRaises(self.NBudgetController.InvalidTag, self.NBudgetController.insert_record,
                          'My Concept', 1200.0, ["Tag2"], False, '12/1/2019')

    def test__format_date_right(self):
        """ Test that _format_date works right. """
        values = [
            ['D/M/Y', [10, 2, 1996]],
            ['M/Y/D', [2, 1996, 10]],
            ['Y/D/M/M', [1996, 10, 2]],  # Extra-check that this one doesn't fail

            ['M/D/Y', [2, 10, 1996]],
            ['D/Y/M', [10, 1996, 2]],
            ['Y/M/D', [1996, 2, 10]],
        ]
        for value in values:
            fmt, values, expected = value[0], '/'.join([str(i) for i in value[1]]), [10, 2, 1996]
            response = self.NBudgetController._format_date(values, fmt)
            self.assertEqual(expected, [response.day, response.month, response.year])

    def test__format_date_raises_InvalidDateFormat(self):
        """ Test that _format_date raises InvalidDateFormat on invalid date_input_formats. """
        self.assertRaises(self.NBudgetController.InvalidDateFormat,
                          self.NBudgetController._format_date, '', '')
        self.assertRaises(self.NBudgetController.InvalidDateFormat,
                          self.NBudgetController._format_date, '', 'D/M')

    def test__format_date_raises_InvalidDate(self):
        """ Test that _format_date raises InvalidDate on invalid date. """
        self.assertRaises(self.NBudgetController.InvalidDate,
                          self.NBudgetController._format_date, '', 'D/M/Y')
        self.assertRaises(self.NBudgetController.InvalidDate,
                          self.NBudgetController._format_date, 'D/M', 'D/M/Y')

    def test__format_date_raises_InvalidDateRange(self):
        """ Test that _format_date raises InvalidDateRange on invalid date ranges. """
        self.assertRaises(self.NBudgetController.InvalidDateRange,
                          self.NBudgetController._format_date, '40/2/2020', 'D/M/Y')
        self.assertRaises(self.NBudgetController.InvalidDateRange,
                          self.NBudgetController._format_date, '30/20/2020', 'D/M/Y')
        self.assertRaises(self.NBudgetController.InvalidDateRange,
                          self.NBudgetController._format_date, '30/20/1000000000', 'D/M/Y')


if __name__ == '__main__':
    unittest.main()

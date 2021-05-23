import os
import json
import nbudget
import unittest
from unittest import mock
from urllib.error import HTTPError


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
        with open(test_file_path, 'w', encoding='utf-8') as test_file:
            json.dump(expected, test_file, indent=True)
        test_file.close()
        self.assertEqual(expected, nbudget._read_settings(filepath=test_file_path))
        os.remove(test_file_path)  # Clean up

    def test__read_settings_exits_on_invalid_settings_keys(self):
        """ Test that _read_settings raises SystemExit if its lacking a KEY."""
        test_file_path = 'test_settings.json'  # We don't want to overwrite our own settings
        invalid_settings = {'database_id': 'MY_DATABASE_ID'}
        with open(test_file_path, 'w', encoding='utf-8') as test_file:
            json.dump(invalid_settings, test_file, indent=True)
        test_file.close()
        self.assertRaises(SystemExit, nbudget._read_settings, filepath=test_file_path)
        os.remove(test_file_path)  # Clean up

    def test__read_settings_exits_on_malformed_json(self):
        """ Test that _read_settings exits if settings.json file is malformed."""
        test_file_path = 'test_settings.json'  # We don't want to overwrite our own settings
        malformed_settings = '{"database_id": "malformed'
        with open(test_file_path, 'w', encoding='utf-8') as test_file:
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
        with open(test_file_path, 'r', encoding='utf-8') as test_file:
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
        self.assertEqual(expected, nbudget._chose_option('', ['NOCASE', 'OTHER']))

    @mock.patch('nbudget.NBudgetController.get_tags', create=True)
    def test_GetTags(self, mocked_method):
        """ Test GetTags.__call__() calls NBudget"""
        temp_save = nbudget._read_settings  # Save the actual content for tear down
        nbudget._read_settings = lambda : nbudget.get_default_settings('abc%s', 'bcd')
        nbudget.GetTags.__call__(None, mock.Mock(), None, None, None)
        mocked_method.assert_called()
        nbudget._read_settings = temp_save  # Cleaning up

    @mock.patch('nbudget._settings_wizard')
    def test_RunWizard(self, mocked_method):
        """ Test RunWizard.__call__() calls NBudget"""
        nbudget.RunWizard.__call__(None, mock.Mock(), None, None, None)
        mocked_method.assert_called()


class TestNBudgetController(unittest.TestCase):
    """ Tests for the NBudgetController class """

    def setUp(self) -> None:
        """ Set up by creating an NBC """
        settings = nbudget.get_default_settings('MY_DB_ID', 'MY_API_KEY')
        self.NBC = nbudget.NBudgetController(settings)

    def test_clear_tags_cache(self):
        """ Test self.NBC.tags_cache gets emptied. """
        self.NBC.tags_cache = [1, 2, 3, 4, 5, 6]
        self.NBC.clear_tags_cache()
        self.assertEqual([], self.NBC.tags_cache)

    def test__wrap_error_raises_on(self):
        """ Tests that _wrap_error raises Exception passed in when self.raises is True """
        self.NBC.raises = True
        self.assertRaises(TypeError, self.NBC._wrap_error, '', TypeError)

    @mock.patch('nbudget._err', create=True)
    def test__wrap_error_raises_off(self, mocked__err):
        """ Tests that _wrap_error calls _err() instead when self.raises is False """
        self.NBC.raises = False
        self.NBC._wrap_error('', TypeError)
        mocked__err.assert_called()

    @mock.patch('urllib.request.urlopen', create=True)
    def test_api_call_right(self, mocked_urlopen):
        """ Test that _api_call calls urlopen() and returns parsed json """
        second_mock = mock.Mock()
        expected = {'a': 1}
        second_mock.read.return_value = str(expected).replace("'", '"')
        mocked_urlopen.return_value = second_mock
        self.assertEqual(expected, self.NBC._api_call('http://google.com', {}, b''))

    @mock.patch('urllib.request.urlopen', create=True)
    def test_api_call_raises_APIError(self, mocked_urlopen):
        """ Test that _api_call raises APIError when an HTTPError returns a json string"""
        second_mock: mock.Mock = mock.Mock()
        expected = {'code': '', 'message': ''}
        second_mock.read.return_value = str(expected).replace("'", '"')
        mocked_urlopen.side_effect = HTTPError('', 0, '', '', second_mock)
        self.assertRaises(self.NBC.APIError, self.NBC._api_call, 'http://google.com', {}, b'')

    @mock.patch('urllib.request.urlopen', create=True)
    def test_api_call_raises_HTTPError(self, mocked_urlopen):
        """ Test that _api_call raises HTTPError when an HTTPError does not return a json string """
        # First try 403, as we have separated it
        second_mock: mock.Mock = mock.Mock()
        second_mock.code.return_value = 403
        second_mock.read.return_value = 'error'
        mocked_urlopen.side_effect = HTTPError('', 0, '', '', second_mock)
        self.assertRaises(self.NBC.HTTPError, self.NBC._api_call, 'http://google.com', {}, b'')

        # Then try not 403
        second_mock: mock.Mock = mock.Mock()
        second_mock.code.return_value = 503
        second_mock.read.return_value = 'error'
        mocked_urlopen.side_effect = HTTPError('', '', '', '', second_mock)
        self.assertRaises(self.NBC.HTTPError, self.NBC._api_call, 'http://google.com', {}, b'')

    @mock.patch('nbudget.NBudgetController._api_call', create=True)
    def test_get_tags_right(self, mocked_api_call):
        """ Tests get_tags calls _api_call with the right arguments, and returns the options."""
        expected = ['a', 'b']
        return_value = {'properties': {'Tags': {'multi_select': {'options': [{'name': 'a'},
                                                                             {'name': 'b'}]}}}}
        mocked_api_call.side_effect = [return_value]
        self.assertEqual(expected, self.NBC.get_tags())

    @mock.patch('nbudget.NBudgetController._api_call', create=True)
    def test_get_tags_different_tags_name(self, mocked_api_call):
        """ Tests get_tags works right when tags_name has changed in settings """
        self.NBC.settings['tags_name'] = 'Changed Tag Name'
        expected = ['a', 'b']
        return_value = {'properties': {
            'Changed Tag Name': {'multi_select': {'options': [{'name': 'a'}, {'name': 'b'}]}}}}
        mocked_api_call.side_effect = [return_value]
        self.assertEqual(expected, self.NBC.get_tags())

    @mock.patch('nbudget.NBudgetController._api_call', create=True)
    def test_get_tags_not_expected_structure_raises_APIParsingError(self, mocked_api_call):
        """ Test get_tags() return APIParsingError when it cannot parse the response """
        # Wrong tag column name, one other option
        return_value = {'properties': {
            'Other name': {'multi_select': {'options': [{'name': 'a'}, {'name': 'b'}]}}}}
        mocked_api_call.side_effect = [return_value]
        self.assertRaises(self.NBC.APIParsingError, self.NBC.get_tags)

        # Wrong tag column name, several other options
        return_value = {'properties': {
            'Other name': {'multi_select': {'options': [{'name': 'a'}, {'name': 'b'}]}},
            'Another name': {'multi_select': {'options': [{'name': 'a'}, {'name': 'b'}]}}}}
        mocked_api_call.side_effect = [return_value]
        self.assertRaises(self.NBC.APIParsingError, self.NBC.get_tags)

        # Wrong tag column name, no options
        return_value = {'properties': {
            'Other name': {'select': {'options': [{'name': 'a'}, {'name': 'b'}]}}}}
        mocked_api_call.side_effect = [return_value]
        self.assertRaises(self.NBC.APIParsingError, self.NBC.get_tags)

        # Wrong tag column type
        return_value = {'properties': {'Tags': {'select': {'options': [{'name': 'a'},
                                                                       {'name': 'b'}]}}}}
        mocked_api_call.side_effect = [return_value]
        self.assertRaises(self.NBC.APIParsingError, self.NBC.get_tags)

        # Wrong structure all together
        return_value = {'abd': {'ee': {'ff': {'ag32': [{'name': 'a'}, {'name': 'b'}]}}}}
        mocked_api_call.side_effect = [return_value]
        self.assertRaises(self.NBC.APIParsingError, self.NBC.get_tags)

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
        for v in values:
            f, values, expected = v[0], '/'.join([str(i) for i in v[1]]), [10, 2, 1996]
            response = self.NBC._format_date(values, f)
            self.assertEqual(expected, [response.day, response.month, response.year])

    def test__format_date_raises_InvalidDateFormat(self):
        """ Test that _format_date raises InvalidDateFormat on invalid date_input_formats. """
        self.assertRaises(self.NBC.InvalidDateFormat, self.NBC._format_date, '', '')  # Empty
        self.assertRaises(self.NBC.InvalidDateFormat, self.NBC._format_date, '', 'D/M')  # Less

    def test__format_date_raises_InvalidDate(self):
        """ Test that _format_date raises InvalidDate on invalid date. """
        self.assertRaises(self.NBC.InvalidDate, self.NBC._format_date, '', 'D/M/Y')  # Empty
        self.assertRaises(self.NBC.InvalidDate, self.NBC._format_date, 'D/M', 'D/M/Y')  # Less

    def test__format_date_raises_InvalidDateRange(self):
        """ Test that _format_date raises InvalidDateRange on invalid date ranges. """
        self.assertRaises(self.NBC.InvalidDateRange, self.NBC._format_date, '40/2/2020', 'D/M/Y')
        self.assertRaises(self.NBC.InvalidDateRange, self.NBC._format_date, '30/20/2020', 'D/M/Y')
        self.assertRaises(self.NBC.InvalidDateRange, self.NBC._format_date, '30/20/1000000000',
                          'D/M/Y')


if __name__ == '__main__':
    unittest.main()

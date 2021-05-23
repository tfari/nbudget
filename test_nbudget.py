import os
import json
import nbudget
import unittest
from unittest import mock


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
        nbudget._read_settings = mock.Mock
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
        self.NBC = nbudget.NBudgetController(None)

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

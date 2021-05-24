# 💸 nbudget
CLI frontend for a budget database in Notion, via [Notion API]("https://developers.notion.com/").

Allows user to insert records into a simple budget database.

![](https://github.com/tfari/nbudget/blob/main/nbudget_animation.gif)

## Requirements:
* A shared Notion database formatted as shown in Setup
* A Notion API key to access said database
* At first run, the script will prompt the user to generate a settings file, asking for the database's ID
and the API key to access it, populating the rest of the options with default values.

## Usage:
```
usage: nbudget.py [-h] [-w] [-t] [-i] [-d DATE] CONCEPT AMOUNT [TAG [TAG ...]]

Interface for a simple budget database in Notion using Notion's API. The database needs to be structured as follows:
Type(select) -> with two options: "INCOME" and "EXPENSE", Date(date), Concept(title), Amount(number) -> formatted as
Dollars, Tags(multi_select). The names of each column can be others (as long as the types are respected), but you will
have to edit the settings.json file so the script knows their new names.

positional arguments:
  CONCEPT               The concept for the record.
  AMOUNT                The amount value for the record.
  TAG                   A tag or tags for the record. Must be valid tags, if unsure, run "nbudget.py -t"

optional arguments:
  -h, --help            show this help message and exit
  -w, --wizard          Run the settings wizard and exit.
  -t, --tags            Output the current tag names in the database and exit.
  -i, --income          Record is considered an INCOME instead of an EXPENSE.
  -d DATE, --date DATE  The date to use for the expense record, if not used the current day will be used.
```

## Setup:

![](https://github.com/tfari/nbudget/blob/main/budget_db.png)

The Notion database must contain the following columns:
* Type (select) -> with two options: "INCOME" and "EXPENSE"
* Date (date)
* Concept (title)
* Amount (number) -> formatted as Dollar
* Tags (multiselect) -> Can have any options the User choses

The names of these columns can be altered, but should be specified in the settings.json file. New
columns can be added without issues, but the script would need to be altered if the user wants to
fill them in through the utility.

The instructions to share the database and get an API key for it are specified [here](https://developers.notion.com/docs)

## Settings
The settings.json file specifies the following possible setting configurations:

* database_id: The database's id.
* api_key: The Notion API key to access said database.
* date_input_format: Any variation of `D/M/Y`. Default is `D/M/Y`
* tag_separator: The separator for tags when running `-t`. Default is `\n`
* type_name: The name of the Type column. Defaults is `Type`
* date_name: The name of the Date column. Defaults is `Date`
* concept_name: The name of the Concept column. Defaults is `Concept`
* amount_name: The name of the Amount column. Default is `Amount`
* tags_name: The name of the Tags column. Default is `Tags`

## Interface
The module provides the following public interfaces:

```
def get_default_settings(database_id: str, api_key: str) -> Dict[str, str]:
    """
    :param database_id: str, A valid Notion's database id accessible via the api_key.
    :param api_key: str, A valid Notion's api_key that has access to the database under database_id.
    :returns: Dict[str, str], A default settings dictionary with the users information.
    :raises TypeError: if database_id or api_key are not string objects.
    """
```
```
    class NBudgetController(self, settings: Dict[str, str], raises: bool = True):
        """
        Controller class for budget databases on Notion.

        :param settings: Dict[str, str], settings file
        :param raises: bool, When we run the script via terminal we want the errors to be printed
        into the terminal, when the script is being ran as a module, we want to raise our errors
        instead. By default we raise.
        """
        
        def clear_tags_cache(self) -> None:
            """ Empty self.tags_cache """
    
        def get_tags(self) -> List[str]:
            """
            Get the tags from the Notion's database. Fills self.tags_cache and returns them.
    
            :return: List[str], Tag names
            :raises APIParsingError: if there were errors when attempting to parse the API response
            """
            
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
            :raises APIError, if the request went right but the API returned an error
            :raises HTTPError, if the request went wrong
    
            Lets all self._format_date() and self.get_tags() exceptions escalate:
    
            From self._format_date():
            :raises InvalidDateFormat: If there is a missing key (D, M, Y) in date_input_format
            :raises InvalidDate: If there is a missing value in date
            :raises InvalidDateRange: If either day, month, or year is beyond range
    
            From self.get_tags():
            :raises APIError, if a request went right but the API returned an error
            :raises HTTPError, if a request went wrong
            :raises APIParsingError: if there were errors when attempting to parse the Tags API response
            """
```



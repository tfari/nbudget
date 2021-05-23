# nbudget
Terminal front-end for budget database via [Notion API]("https://developers.notion.com/"). 

Allows user to insert records into the database, and to query the current tag names in it.

## Usage:
```
[-h] [-w] [-t] [-i] [-d DATE] CONCEPT AMOUNT [TAG [TAG ...]]
```

* *OPTIONAL* **-h** : Show the help and exit.
* *OPTIONAL* **-w** : Run the settings wizard and exit.

* *OPTIONAL* **-t** : Output the current tag names in the database and exit.

* *OPTIONAL* **-i** : Record is considered an income instead of an expense.
* *OPTIONAL* **-d D/M/Y** : The date to use for the expense record, if not used the current day will be used.
* **CONCEPT** : The concept for the record.
* **AMOUNT** : The amount value for the record.
* *OPTIONAL* **TAG, TAG...**: A tag or tags for the record. Must be valid tags, if unsure, run "nbudget.py -t"

## Setup:



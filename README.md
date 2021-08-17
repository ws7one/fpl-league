# fpl-league

This is a script you can run that will give you the standings of a league with some extra info on each manager in the league which are used to sort standings more accurately

## How to run?

```sh
python gameweekstandings.py -l <league-id> -g <gameweek-number>
```

Make sure you enter the file path for the file name if you are runninng the script from some other location

**You will find the "league-id" in the url of fantasy.premierleague.com**

Make sure you enter both variables to get the script to run properly

## Installation

Few things to install

Make sure you have `python` installed in your system

Install `pip` and then `requests`

pip is you library manager and requests is the library you will need to run API calls**

### pip installation

You could run `python get-pip.py` to get pip installed on your system depending on the version of python you have installed. Included in this repo is a get-pip.py file which could be helpful, but make sure you have the right version of python installed to use this.

If you do end up using and installing using the above script, you can do the following to install any libraries using pip

```sh
python -m pip install requests
```

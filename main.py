import json
from time import sleep
import requests
from notifications import Notification
from datetime import datetime


def log(txt: str, output=True):
    """
    Since this program is intended to be run once a day in the background, its unlikely that the user will be able to
    see all the information outputted in the console. This function is a simple logger that will save any information
    entered in the arguement txt. Can also print the same information by altering the arg output.

    :param txt: String, whatever info you want to save to the log.txt file
    :param output: Bool, default is True. If True it will also print out the information in arg txt
    :return: N/A
    """
    try:
        with open('log.txt', 'a') as file:
            date = datetime.now().strftime('%Y-%m-%d')
            time = datetime.now().strftime('%H:%M:%S')
            file.write(f'{date} {time} | {txt}\n')
    except FileNotFoundError:
        with open('log.txt', 'w') as file:
            date = datetime.now().strftime('%Y-%m-%d')
            time = datetime.now().strftime('%H:%M:%S')
            file.write(f'{date} {time} | {txt}\n')
    else:
        if output:
            print(txt)


def filter_no_name(app: dict):
    """
    for use to filter out games without a name from the steam GetAppList

    :param app: dict containing the app's appid, and it's name
    :return: bool, filters out apps that dont have a proper name attached to them.
    """
    return False if app['name'] == '' else True


def get_gamelist() -> filter:
    """
    Gets the full list of games from steams api and returns a csv formatted string of their app ids

    :return: filter-obj (filter is used to remove apps without a proper name)
    """
    response = requests.get('https://api.steampowered.com/ISteamApps/GetAppList/v0001/').json()
    app_ids = [x for x in response['applist']['apps']['app']]
    return filter(filter_no_name, app_ids)


def to_csv_str(ids: list) -> str:
    """
    converts a list of numbers into a csv-formatted string, ie: 123,123,123

    :param ids: list of steam app ids
    :return: csv-formatted string of app ids
    """
    # we have to convert the app ids into csv format for the app details api call
    app_str = ''
    for i in ids:
        app_str += f"{i['appid']},"

    return app_str


def search_for_discounted_games(app_ids: list, app_str: str, discount_rate: int = 100):
    """
    calls the steam app details api with using a list of ids as a param, then pulls all games with a discount rate higher than arg given

    :param app_ids: list of dictionaries with an app id and a name
    :param app_str: csv-formatted str containing app ids
    :param discount_rate: default is 100 (aka free games only) lower to add games with n% off
    :return: Adds applications that fit the criteria to a txt file named discounted_games, if file does not exist it creates one
    """
    params = {'appids': app_str, 'filters': 'price_overview'}
    steam_response = requests.get('http://store.steampowered.com/api/appdetails/', params=params).json()
    for app in steam_response:
        if not steam_response[app]['success']:
            # not able to retrieve game data
            continue
        else:
            if len(steam_response[app]['data']) == 0:
                # some apps don't have data posted yet, we filter those out since we don't know if they are free/on sale
                continue
            elif steam_response[app]['data']['price_overview']['discount_percent'] >= discount_rate:
                for appid in app_ids:
                    if int(app) == appid['appid']:
                        # adding the name to the corresponding app information
                        # so the user can better understand which games are on sale
                        steam_response[app]['name'] = appid['name']
                        log(f'Discounted app found: {appid["name"]}')
                        try:
                            with open('discounted_games.txt', 'a') as file:
                                file.write('\n')
                                json.dump(steam_response[app], file)
                        except FileNotFoundError:
                            with open('discounted_games.txt', 'w') as file:
                                json.dump(steam_response[app], file)

                        break
            else:
                # app has all the data necessary but is not currently on sale / free to keep.
                continue


def main():
    """
    We check the games in increments of 750,
    trying to go over 750 per increment fails when getting the price from the app details request.
    we also sleep between each iteration, so we don't overload the servers getting the requests,
    and stay within steam's limits on API calls.
    """
    start = 0
    end = 750
    base_app_list = list(get_gamelist())
    log(f"Total amount of apps to search: {len(base_app_list)} apps")
    while end < len(base_app_list):
        log(f'Apps: {start} - {end}')
        app_ids = base_app_list[start:end]
        app_str = to_csv_str(app_ids)
        search_for_discounted_games(app_ids=app_ids, app_str=app_str, discount_rate=100)
        start += 750
        end += 750
        sleep(30)


if __name__ == '__main__':
    time1 = datetime.now()
    log(f"Starting search for discounted games...")
    main()
    time2 = datetime.now()
    log(f"Search finished, sending notifications now...")
    log(f"Runtime of search was {time2 - time1}")
    notif = Notification()
    notif.send_notif()

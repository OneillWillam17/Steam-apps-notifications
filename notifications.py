from pushbullet import Pushbullet
from dotenv import load_dotenv
import os
import json
from datetime import datetime


class Notification:
    def __init__(self):
        load_dotenv()
        KEY = os.getenv('PUSHBULLET_TOKEN')
        self.bullet = Pushbullet(KEY)
        self.phone = self.bullet.devices[1]
        print('Device found:', self.phone)

    def send_notif(self):
        """
        To be run after main file has finished, It sends a push notification to a phone containing information about
        what games are free/on sale on any given day aswell as saving the game's sale information
        to a separate text file and deleting discounted_games.txt

        :return: None
        """
        try:
            with open('discounted_games.txt', 'r') as file:
                for line in file.readlines():
                    game_information = json.loads(line)
                    game_name = game_information['name']
                    game_discount = game_information['data']['price_overview']['discount_percent']
                    game_finalcost = game_information['data']['price_overview']['final_formatted']
                    push = self.bullet.push_note(f"{game_name}", f"{game_name} is on sale for {game_discount}% off\nfinal price is {game_finalcost}", device=self.phone)
                    # print(push)  # gives information about the most recent notification sent, is useful for debugging
        except FileNotFoundError:
            print(f'There are no free games found for {datetime.today().strftime("%m/%d/%y")}')
        else:
            # games have been seen and sent to my phone, we add them to a new file that saves which games have been seen
            try:
                with open('previously_seen_games.txt', 'a') as file:
                    with open('discounted_games.txt', 'r') as old_games_file:
                        for line in old_games_file.readlines():
                            # to separate the games into their own lines, makes it easier to understand the data
                            line = json.loads(line)
                            line['date_of_sale'] = datetime.today().strftime("%m/%d/%Y")
                            file.write('\n')
                            json.dump(line, file)
            except FileNotFoundError:
                with open('previously_seen_games.txt', 'w') as file:
                    with open('discounted_games.txt', 'r') as old_games_file:
                        for line in old_games_file.readlines():
                            line = json.loads(line)
                            line['date_of_sale'] = datetime.today().strftime("%m/%d/%Y")
                            json.dump(line, file)

            # now that the games' information has been stored in a separate file, we can safely delete discounted_games
            # we do this because the function scans over any games in the discounted_games file,
            # and if a game was on sale for a short period of time, then became full price again,
            # we do not want it to send a message saying its on sale, when it really isnt.
            os.remove('discounted_games.txt')

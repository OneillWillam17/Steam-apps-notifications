# Steam-apps-notifications
Tells the user when any apps is on sale and/or free on the Steam app store. Can be configured to notify of any app below a certain % off

# How it works
The program runs by getting a list of all available applications from one of steam's API's (~150,000 apps), it then checks the price of each individual app using a differing
API. If the game is over the percent threshold for discount (which you can set in the main file) it will save the game's information to a textfile. Once all apps are searched
over. Any apps that fit the criteria are then passed into the notification.py file. In this file we load the data we stored in the text file and use it to send a push
notificaion to the user's phone (provided they have a pushbullet account, and api key). Once we send out the push notification we save the game's data to a different text file
and delete the original. 

# Push Notification example
https://cdn.discordapp.com/attachments/619691677329784832/1008839848511160351/Screenshot_20220815-164624_Nova7.jpg

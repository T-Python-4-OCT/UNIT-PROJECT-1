# Subscription Guardian

#### Overview : A CLI app that helps you keep track of all your subscriptions (Netflix, Shahid, Spotify, Gym, etc.). You enter when each subscription started, and the app calculates when it ends and renews, how many days are left, how much you spend every month and year, and how much you have paid so far. It also suggests which subscriptions you can cancel to save money. Most people forget their subscriptions and they keep renewing even when they don't need them, this app solves that problem.

### Features & User Stories
#### As a user I should be able to do the following :
- Add a subscription (name, price, cycle, category, how important it is, start date).
- Choose a monthly, yearly, or custom cycle (any number of months, for example 18 months).
- View all my subscriptions in a colored table, sorted by days left, monthly cost, or name.
- See the end (renewal) date of each subscription, calculated from its start date.
- See how many days are left until each subscription renews (red: 10 days or less, yellow: 30 days or less, green: more).
- See how much I have paid for each subscription since it started.
- Get a spending report (monthly total, yearly total, total paid so far, and spending by category with a share bar).
- Get suggestions on what to cancel inside the report (subscriptions that are not important to me, and more than one subscription in the same category) and how much I would save.
- Edit any detail of a subscription (name, price, cycle, category, importance, start date).
- Delete a subscription after confirming.
- Save my subscriptions automatically so they are still there the next time I open the app.
- Get a clear message and try again when I type something wrong (letters instead of a price, a wrong date, a name that already exists...).
- Go back at any step by typing `back` or picking Back from a list.



#### Usage :
 Install the requirements by typing `pip install -r requirements.txt`, then run the app by typing `python main.py`.

 Choose from the main menu with the arrow keys and Enter, or type the option number:
 - type in 1 to add a new subscription.
 - type in 2 to show all your subscriptions, their end dates, and the days left until each one renews.
 - type in 3 to show the spending report and the suggestions on what to cancel.
 - type in 4 to edit a subscription.
 - type in 5 to delete a subscription.
 - type in 6 to exit.
 - type in back (or pick Back) at any step to go back without saving.

# StockBot

Python program that retrieves stock data from [tradingview.com](https://tradingview.com), tracks them at every user-determined time interval, and send notifications to user when it has met their desired growth rates.

---

## Installation

1. Clone repository:

    ```sh
        git clone git@github.com:ultramolecular/StockBot.git
        cd StockBot
    ```

2. Install Python modules required:

    ```sh
        pip install -r requirements.txt
    ```

---

## How To Use

To use the program, you will need to make a [tradingview account](https://tradingview.com) using the email and password method.

You'll want to create a `.env` file locally and set your email and password to `EMAIL` and `PASS` environment variables there.
The same goes for your own time zone hours (`OPEN_HR`, `CLOSE_HR`), since the market opens and closes at 09:30ET and 16:00ET.

Run `python3 stockBot.py` in a terminal, and it will prompt you to enter:

- List/Site refresh rate: `t` minutes
- Percentage change desired: `y%`
- Percent change desired for when a stock has already met the first percent change: `y'%`

> [!IMPORTANT]
> Solve the reCAPTCHA if it pops up in the GUI browser, as there is no good way to get around this.

Once you entered your configuration, it will immediately begin working, and display the top 5 gainers with a current time stamp, their price, and absolute percent changes since the moment you initiated the bot.
In addition to the absolute percent changes, it will include the past 1 minute, 5 minute, 10 minute, and 20 minutes percent changes.
It will send you notifications when your criteria has been met (on the absolute scale), and once a stock has met your criteria and is in the top 5, it will provide an additional line describing the time and price it met criteria, along with the time, price, volume, and percent increase from the price at met criteria. This is useful additional information.

Aside sending a notification, one of the features of this tool is a parrot notification mechanism, e.g. if $GME grew the `y%` you wanted it to notify you, it will send a notification each `y'%` that it grows after.

> [!NOTE]
> - Start the program at 9:30 ET for the full range of coverage and best analytics.
> - A premium membership account with TradingView is preferred, as it makes the best of it having real-time data, but a free membership or no membership will work too.
> - You cannot initiate the bot multiple instances with the same account credentials, unless you have the premium account that allows you to do so.
> - This is a constant work in progress, bugs should be brought in up issues!

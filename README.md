# StockBot
Python program that retrieves stock data from [tradingview.com](https://tradingview.com), tracks them at every user-determined time interval, and send notifications to user when it has met their desired growth rates.

---

# Installation:
Clone repo using `git clone git@github.com:ultramolecular/StockBot.git`.

This program runs on Python3.8+, depends on `selenium` for traversing the web. 
- `pip install selenium`

---

# How To Use
To use the program, you can make a [tradingview account](https://tradingview.com), and preferrably a paid
membership account, since real-time data makes the best of this tool, but you don't *need* an account at all to use. This is because the delayed charts are public to view.

Simply run `python3 stockBot.py` in a terminal, or just `stockBot.py` if on Windows, and it will prompt you to enter:
- List/Site refresh rate: `t` minutes
- Percentage change desired: `y%`
- Percent change desired for when a stock has already met the first percent change: `y'%`

Once you entered your configuration, it will immediately begin working, display the top 5 gainers with a current time stamp, their price, and absolute percent changes since the moment you initiated the bot.
In addition to the absolute percent changes, it will include the past 1 minute, 5 minute, 10 minute, and 20 minutes percent changes.
It will send you notifications when your criteria has been met (on the absolute scale).

Aside sending a notification, one of the features of this tool is a parrot notification mechanism, e.g if $GME grew the `y%` you wanted it to notify you, it will send a notification each `y'%` that it grows after.

---

## Caveats
- *Sometimes* if your connection is spotty and gives out at anytime for whatever reason, the program will crash, nothing the program can do about that.
- It is good to note that you cannot initiate the bot multiple instances with the same account credentials, unless you have the premium account that allows you to do so.
- Sometimes the site's refresh rate does not align with your refresh rate and you will get unchanged values, I built a mechanism that detects that and refreshes in a few seconds to combat that, it will look funky in the log however.
---

### *Development*
*This is a constant work in progress, any bugs should be reported to me.*
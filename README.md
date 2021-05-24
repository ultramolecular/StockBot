# StockBot
Python program that retrieves stock data from [tradingview.com](https://tradingview.com), tracks them at every user-determined time interval, and send notifications to user when it has met their desired growth rates.

---

# Installation:
Clone repo using `git clone git@github.com:ultramolecular/StockBot.git`.

This program runs on Python3.8+, depends on `selenium` for traversing the web, and `pydub` for sound (and its dependencies as well) if you're on MacOS/Linux.
- `pip install selenium`
- **MacOS/Linux**:
    - `pip install pydub`
    - `sudo apt-get install ffmpeg libavcodec-extra`

---

# How To Use
To use the program, you need a [tradingview account](https://tradingview.com), and preferrably a paid
membership account, since real-time data makes the best of this tool, but you don't *need* an account at all to use.

Simply run `python3 stockBot.py` in a terminal, or just `stockBot.py` if on Windows, and it will prompt you to enter:
- List/Site refresh rate: `t` minutes
- Percentage change desired: `y%`
- Percent change desired for when a stock has already met the first percent change: `y'%`

Once you entered your configuration, it will immediately begin working, display the top 5 gainers with a current time stamp, and send you notifications when your criteria has been met.

Aside sending a notification, one of the features of this tool is a parrot notification mechanism, e.g if $GME grew the `y%` you wanted it to notify you, it will send a notification each `y'%` that it grows after.

---

## Caveats
*Sometimes* if your connection is spotty and gives out at anytime for whatever reason, the program will crash, nothing the program can do about that.

On Windows, the program might output junk to the terminal from time to time, but it does not affect the program any way.

---

### *Development*
*This is a constant work in progress, any bugs should be reported to me.*
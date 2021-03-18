# StockBot
Python program that retrieves data from tradingview.com, makes decisions based on the data, and outputs notifications/text as a result.

# How To Use
If you want to run the program locally, first you have to make sure the market is open (9:30am-4pm ET), simply run it in a terminal and it will prompt you to enter: 
- List/Site refresh rate: `t` minutes
- Percentage change desired: `y%`
- Percent change desired for when a stock has already met the first percent change: `y'%`

Once you entered your configuration for the bot, it will immediately begin working and send you notifications when your criteria has been met, post top 5 gainers in those `t` minutes, and it will keep working until 4pm ET.

# Caveats
This program depends on `selenium`, `pydub` (and its dependencies as well).
## Installation:
- `pip install selenium`
- `pip install pydub`
- `sudo apt-get install ffmpeg libavcodec-extra`

Also, sometimes if your connection is spotty and gives out at anytime for whatever reason, the program will crash, nothing the program can do about that.

### Development
This is a constant work in progress, any bugs should be reported to me.
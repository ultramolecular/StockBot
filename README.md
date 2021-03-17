# StockBot
Python program that retrieves data from tradingview.com, makes decisions based on the data, and outputs notifications/text as a result.

# How To Use
If you want to run the program locally, first you have to make sure the market is open (9:30am-4pm ET), simply run it in a terminal and it will prompt you to enter: 
- List/Site refresh rate: `t` minutes
- Percentage change desired: `y%`
Once you entered your configuration for the bot, it will immediately begin working and send you notifications when your criteria has been met, and it will keep working until 4pm ET.

## Caveats
As mentioned before, aside from you starting the program, the program will also check the time and assess if it will continue based on the market hours.

### Development
This is a constant work in progress, any bugs should be reported to me.
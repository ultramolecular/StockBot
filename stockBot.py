#----------------------------------------------------#
#   Author:             Josiah Valdez                #
#   Began Development:  February, 7, 2021            #
#----------------------------------------------------#

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep

# Holds chromedriver & google-chrome locations on your machine - OPTIONAL FOR SOME.
#DRIV_LOC = "/usr/bin/chromedriver"
#BIN_LOC = "/usr/share/google-chrome"

# Holds url that program will go to.
url = "https://www.tradingview.com/markets/stocks-usa/market-movers-gainers/"

# Options for the driver - OPTIONAL FOR SOME.
#options = webdriver.ChromeOptions()
#options.binary_location = BIN_LOC

# Opens the chrome browser and goes to url specified.
driv = webdriver.Chrome()
driv.get(url)

# Holds xpath value of the stock name.
STOCK = "//a[@class='tv-screener__symbol apply-common-tooltip']"
# Holds xpath value of the stock percent change.
STOCK_PCT_CHG = "//td[@class='tv-data-table__cell tv-screener-table__cell tv-screener-table__cell--up tv-screener-table__cell--big tv-screener-table__cell--with-marker']"
# Grab a list of the stock elements (stock names listed on tradingview).
stockElems, stockPctElems = driv.find_elements_by_xpath(STOCK), driv.find_elements_by_xpath(STOCK_PCT_CHG)
# List only the names of the stocks.
stockNames, stockPctChg = [s.text for s in stockElems], [pct.text for pct in stockPctElems]

# Print the names of the stocks to make sure things are working right.
print("Today's Top Gainer Stocks:")
print("\n".join("{} {}".format(s, pct) for s, pct in zip(stockNames, stockPctChg)))

sleep(5)
driv.close()
driv.quit()
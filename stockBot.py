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
from stock import Stock
import datetime

''' TODO: 
    - See if current state works for getting and updating stocks, sends noti
      when pctChg desired is met.
    - Implement the logic for getting top 5 growing stocks.
'''

# Holds chromedriver & google-chrome locations on your machine - OPTIONAL FOR SOME.
#DRIV_LOC = "/usr/bin/chromedriver"
#BIN_LOC = "/usr/share/google-chrome"

# Options for the driver - OPTIONAL FOR SOME (i.e. not doing headless).
options = webdriver.ChromeOptions()
options.headless = True
options.add_argument("window-size=1920x1080");
#options.binary_location = BIN_LOC

# Opens the chrome browser and goes to url specified.
driv = webdriver.Chrome(options = options)
# Uncomment if you are not doing headless.
#driv.set_window_size(1080, 1044)

# Holds xpath value of the stock name, stock price, and stock pct change.
STOCK = "//a[@class='tv-screener__symbol apply-common-tooltip']"
STOCK_PRICES = "//td[@class='tv-data-table__cell tv-screener-table__cell tv-screener-table__cell--big tv-screener-table__cell--with-marker']"

URL = "https://www.tradingview.com"
GAINS_URL = "https://www.tradingview.com/markets/stocks-usa/market-movers-gainers/"

MAIN_LOGIN_PATH = "/html/body/div[2]/div[3]/div/div[4]/span[2]/a"
LOGIN_PATH = "/html/body/div[11]/div/div[2]/div/div/div/div/div/div/form/div[5]/div[2]/button/span[2]"
EMAIL_PATH = "/html/body/div[11]/div/div[2]/div/div/div/div/div/div/div[1]/div[4]/div/span"
CRED_BOX = "//input[@class='tv-control-material-input tv-signin-dialog__input tv-control-material-input__control']"

# Enter your tradingview login info.
EMAIL = "Awesome835459@hotmail.com"
PASS = "Awesome90"

# Holds the current time, will be referencing it for other causes later.
time = datetime.datetime.now()
# Opening market hour and closing market hour.
MARKET_OPEN = time.replace(hour = 8, minute = 30)
MARKET_CLOSE = time.replace(hour = 15, minute = 0)

#-------------------------------------------------------------#
# Searches for a stock of interest in the list and gets it    #
# back to user if it exists.                                  #
#                                                             #
# Args:                                                       #
#     l (list): the container in which to search in.          #
#     filt (lambda): the filter which will be the ticker.     #
# Returns:                                                    #
#     stock (Stock): the stock of interest if it exists.      #
#     None (null): None/null if it does not exist.            #
#-------------------------------------------------------------#
def inGainers(l, filt):
    for stock in l:
       if filt(stock):
           return stock
    return None

#------------------------------------------------------#
#  ONLY CONTINUE PROGRAM IF IT IS DURING MARKET HOURS, #
#  OTHERWISE, YOU CAN BYPASS IT FOR DEVELOPMENT.       #
#------------------------------------------------------#
if time > MARKET_OPEN and time < MARKET_CLOSE:
    print("Market: OPEN\n")
    refRateDes = int(input("Enter refresh rate (minutes) desired: ")) * 60
    pctChgDes = float(input("Enter percent change desired: "))

    # Once we get info from user, go to tradingview home site.
    driv.get(URL)

    WebDriverWait(driv, 2).until(EC.presence_of_element_located((By.XPATH, MAIN_LOGIN_PATH))).click()
    WebDriverWait(driv, 2).until(EC.presence_of_element_located((By.XPATH, EMAIL_PATH))).click()
    creds = driv.find_elements_by_xpath(CRED_BOX)
    creds[0].send_keys(EMAIL)
    creds[1].send_keys(PASS)
    driv.find_element_by_xpath(LOGIN_PATH).click() 
    sleep(.5)
    # Once we're logged in, go to top gainer stock page.
    driv.get(GAINS_URL)
    # This will be the main list that will hold the stocks for the program.
    gainers = []
    # Begins our main loop, where we wait refresh rate and only continue if we still in market hours.
    while time < MARKET_CLOSE:
        # Grab a list of the stock elements (stock names listed on tradingview).
        stockElems, stockPriceElems = driv.find_elements_by_xpath(STOCK), driv.find_elements_by_xpath(STOCK_PRICES)
        # Create list of stocks and a list of their respective percent changes.
        stockNames, stockPrices = [s.text for s in stockElems], []
        i = 0
        while i < len(stockPriceElems):
            stockPrices.append(stockPriceElems[i].text)
            i += 6
        del i
        # Go through each newly fetched stocks and if they are in our gainers list, update, if not add them."
        for stock, price in zip(stockNames, stockPrices):
            stk = inGainers(gainers, lambda s: s.TICKER == stock)
            if stk is not None:
                stk.setPctChg((float(price) - stk.getOGPrice()) / stk.getOGPrice())
                stk.setPrice(float(price))
                print(f"{stock}'s price: {stk.getPrice()} and percent change: {stk.getPctChg()}\n")
                if stk.getPctChg() >= pctChgDes:
                    print(f"{stk.getTick()} grew by {stk.getPctChg()} in top gainers! Check it out!\n")
            else:
                gainers.append(Stock(stock, float(price), float(price), 0.0))
        sleep(refRateDes)
    print("Market closed now, come back next market day!")
else:
    print("Market: CLOSED, return tomorrow or when it opens.\n")

driv.close()
driv.quit()
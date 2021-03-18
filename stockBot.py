#----------------------------------------------------#
# Author:             Josiah Valdez                  #
# Began Development:  February, 7, 2021              #
#----------------------------------------------------#

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
from stock import Stock
from pydub import AudioSegment
from pydub.playback import play
import datetime

''' TODO: 
    - Implement checking if it is market day (Monday-Friday).
    - Try to figure out a way to either suppress the junk that pydub ouputs
      when playing a sound, or another way to play sound.
'''

# Holds chromedriver & google-chrome locations on your machine - OPTIONAL FOR SOME.
#DRIV_LOC = "/usr/bin/chromedriver"
#BIN_LOC = "/usr/share/google-chrome"

# Options for the driver - OPTIONAL FOR SOME (i.e. not doing headless).
options = webdriver.ChromeOptions()
options.headless = True
options.add_argument("window-size=1920x1080");
#options.binary_location = BIN_LOC

# Opens the chrome browser.
driv = webdriver.Chrome(options = options)
# Uncomment if you are not doing headless.
#driv.set_window_size(1080, 1044)

# Holds xpath value of the stock name, stock price, and stock pct change.
STOCK_PATH = "//a[@class='tv-screener__symbol apply-common-tooltip']"
STOCK_PRICES_PATH = "//td[@class='tv-data-table__cell tv-screener-table__cell tv-screener-table__cell--big tv-screener-table__cell--with-marker']"

URL = "https://www.tradingview.com"
GAINS_URL = "https://www.tradingview.com/markets/stocks-usa/market-movers-gainers/"

MAIN_LOGIN_PATH = "/html/body/div[2]/div[3]/div/div[4]/span[2]/a"
LOGIN_PATH = "/html/body/div[11]/div/div[2]/div/div/div/div/div/div/form/div[5]/div[2]/button/span[2]"
EMAIL_PATH = "/html/body/div[11]/div/div[2]/div/div/div/div/div/div/div[1]/div[4]/div/span"
CRED_BOX = "//input[@class='tv-control-material-input tv-signin-dialog__input tv-control-material-input__control']"

# Enter your tradingview login info and what sound you want as notification.
EMAIL = ""
PASS = ""
SOUND = AudioSegment.from_mp3("swiftly.mp3")

# Holds the current time, will be referencing it for other causes later.
time = datetime.datetime.now()
# Opening market hour and closing market hour.
MARKET_OPEN = time.replace(hour = 8, minute = 30)
MARKET_CLOSE = time.replace(hour = 15, minute = 0)

#-------------------------------------------------------------#
# Searches for a stock of interest in the list and gets it    #
# back to user if it exists.                                  #
# Args:                                                       #
#     gainers (list): the list that contains the gainers.     #
#     filt (lambda): the filter which will be the ticker.     #
# Returns:                                                    #
#     stock (Stock): the stock of interest if it exists.      #
#     None (null): None/null if it does not exist.            #
#-------------------------------------------------------------#
def inGainers(gainers, filt):
    for stock in gainers:
       if filt(stock):
           return stock
    return None

#---------------------------------------#
# Displays current top 5 gainers.       #
# Args:                                 #
#     gainers (list): list of gainers.  #
#---------------------------------------#
def showTop5(gainers):
    if len(gainers) > 0:
        print("-" * 100, "\nTOP 5 GAINERS:\n")
        for g in range(5):
            print(gainers[g])

# CONTINUE PROGRAM IF IT IS DURING MARKET HOURS, OR BYPASS FOR DEVELOPMENT.
if time > MARKET_OPEN and time < MARKET_CLOSE:
    print("Market: OPEN\n")
    refRateDes = float(input("Enter refresh rate (minutes) desired: ")) * 60
    pctChgDes = float(input(r"Enter percent change desired (y% format): "))
    pctChgAfter = float(input("Enter percent change desired after it has met initial desired change: "))

    # Once we get info from user, go to tradingview home site.
    driv.get(URL)

    # Wait for login button to click, then send credentials and log in.
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
        stockElems, stockPriceElems = driv.find_elements_by_xpath(STOCK_PATH), driv.find_elements_by_xpath(STOCK_PRICES_PATH)
        # Create list of stocks and a list of their respective percent changes.
        stockNames, stockPrices = [s.text for s in stockElems], []
        i = 0
        while i < len(stockPriceElems):
            stockPrices.append(float(stockPriceElems[i].text))
            i += 6
        # Flag to let program know whether to sort gainers list or not.
        changed = False
        showTop5(gainers)
        # Go through each newly fetched stocks and if they are in our gainers list, update, if not add them.
        for stock, price in zip(stockNames, stockPrices):
            stk = inGainers(gainers, lambda s: s.TICKER == stock)
            if stk is not None:
                #print(f"{stock}'s price: {stk.price}\tPct Chg: {stk.pctChg}%\tfrom base price: {stk.basePrice}\n")
                newPctChg = ((price - stk.basePrice) / stk.basePrice) * 100
                # Only update its pct chg and price if it changed...
                if newPctChg != stk.pctChg:
                    changed = True
                    stk.pctChg = newPctChg
                    stk.price = price
                # If current stock's percent change meets desired and it has already not met the desired...
                if stk.pctChg >= pctChgDes and not stk.metCrit:
                    # Send notification, flag it as met, and set base price as this price.
                    print(f"{stk.TICKER} grew by {stk.pctChg}% in top gainers! Check it out!\n")
                    stk.metCrit = True
                    stk.basePrice = price
                    play(SOUND)
                # If current stock has already met desired pct chg, then check if it met the desired chg for after.
                elif stk.metCrit and stk.pctChg >= pctChgAfter:
                    print(f"{stk.TICKER} grew by {stk.pctChg}% even after it grew by {pctChgDes}%! Check it out!\n")
                    stk.basePrice = price
                    play(SOUND)
            else:
                gainers.append(Stock(stock, price, price, 0.0, False))
                changed = True
        # If the list changed, sort list from highest gainers to lowest gainers.
        if changed:
            gainers.sort(key = lambda s: s.pctChg, reverse = True)
        sleep(refRateDes)
        driv.refresh()
    print("Market closed now, come back next market day!")
else:
    print("Market: CLOSED, return next market day!\n")

driv.close()
driv.quit()
#-----------------------------------------------------------------------------------------#
# Author:             Josiah Valdez                                                       #
# Began Development:  February, 7, 2021                                                   #
#                                                                                         #
# This is a program that uses selenium to extract data from tradingview.com top gainers,  #
# calculate and store their prices and percent changes, and send notifications given the  #
# desired change from the user. It is in constant development, and is sometimes unstable. #
#-----------------------------------------------------------------------------------------#
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
from stock import Stock
from datetime import datetime as dt
from platform import system

''' TODO: 

    LEGEND: [1] - highest priority [2] - next priority [3] - last priority

    - [1] Have different gainers list, absolute gainers (entire day), 1m gainers, 5m gainers, 10m gainers, etc

    - [3] Try to have the notifications be in a different color, also the percent changes whether they're
      positive (green) or negative (red)

    - [3] Figure out some way for the program to run on itself and know when to
      start processing data.

    - [3] Make an easy and visually appealing gui for users.
'''

#----------------------------------------------------------------------------#
# All things chromedriver - set your chromedriver and google chrome binary   #
# locations here, as well as the driver options, which if you don't want to  #
# do headless you can comment that out.                                      #
# NOTE: Setting driver and binary location is not necessary for some users.  #
#----------------------------------------------------------------------------#
#DRIV_LOC = "/usr/bin/chromedriver"
#BIN_LOC = "/usr/share/google-chrome"
options = webdriver.ChromeOptions()
# For Windows, this will disable the extraneous warnings displayed.
#options.add_experimental_option('excludeSwitches', ['enable-logging'])
# options.headless = True
# options.add_argument("window-size=1920x1080")
#options.binary_location = BIN_LOC
driv = webdriver.Chrome(options = options)
# Uncomment if you are not doing headless.
driv.set_window_size(1080, 1044)

#--------------------------------------------------------------------------#
# All program constants are declared here - stock ticker and price paths,  #
# login paths, tradingview.com urls and credentials, the sound file        #
# for notification, and the market open/close hours.                       #
# NOTE: Sometimes tradingview updates/moves/changes the way fields of the  #
# page are located, so updating the xpath is necessary in those instances. #
#--------------------------------------------------------------------------#
STOCK_PATH = "//a[@class='tv-screener__symbol apply-common-tooltip']"
STOCK_PRICES_PATH = "//td[@class='tv-data-table__cell tv-screener-table__cell tv-screener-table__cell--big tv-screener-table__cell--with-marker']"
MAIN_LOGIN_PATH = "/html/body/div[2]/div[3]/div/div[4]/span[2]/a"
LOGIN_PATH = "/html/body/div[9]/div/div[2]/div/div/div/div/div/div/form/div[5]/div[2]/button/span[2]"
EMAIL_PATH = "/html/body/div[9]/div/div[2]/div/div/div/div/div/div/div[1]/div[4]/div/span"
CRED_BOX = "//input[@class='tv-control-material-input tv-signin-dialog__input tv-control-material-input__control']"
URL = "https://www.tradingview.com"
GAINS_URL = "https://www.tradingview.com/markets/stocks-usa/market-movers-gainers/"
EMAIL = ""
PASS = ""
SOUND = "swiftly.wav"
OS = system()
MARKET_MONDAY = 0
MARKET_FRIDAY = 5
MARKET_OPEN = dt.now().replace(hour = 8, minute = 30)
MARKET_CLOSE = dt.now().replace(hour = 15, minute = 0)

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

#--------------------------------------#
# Displays current top 5 gainers.      #
# Args:                                #
#     gainers (list): list of gainers. #
#--------------------------------------#
def showTop5(gainers):
    if len(gainers) > 0:
        print("-" * 200, f"\nTOP 5 GAINERS @ {dt.now().strftime('%H:%M:%S')}:\n")
        for g in range(5):
            print(gainers[g])
    
#---------------------------------------------------------#
# Play sound based on OS and given sound file path.       #
# Uses winsound if on Windows, playsound if MacOS/Linux.  #
# Args:                                                   #
#     file (str): sound file path.                        #
#     osType (str): platform/os of the user.              #
#---------------------------------------------------------#
def play(file, osType):
    if osType == "Windows":
        import winsound
        winsound.PlaySound(file, winsound.SND_ASYNC)
    else:
        from playsound import playsound
        playsound(file)

# CONTINUE PROGRAM IF IT IS DURING MARKET DAY & HOURS, OR BYPASS FOR DEVELOPMENT.
if dt.now().weekday() >= MARKET_MONDAY and dt.now().weekday() <= MARKET_FRIDAY and dt.now() > MARKET_OPEN and dt.now() < MARKET_CLOSE:    
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
    while dt.now() < MARKET_CLOSE:
        # Grab a list of the stock elements (stock names & prices listed on tradingview).
        stockElems, stockPriceElems = driv.find_elements_by_xpath(STOCK_PATH), driv.find_elements_by_xpath(STOCK_PRICES_PATH)
        # Create list of stocks and a list of their respective prices.
        stockNames, stockPrices = [s.text for s in stockElems], []
        # For the prices, as of right now it is getting the other stats as well, so every other 6th is the correct element.
        i = 0
        while i < len(stockPriceElems):
            stockPrices.append(float(stockPriceElems[i].text))
            i += 6
        # Flag to let program know whether to sort gainers list or not.
        changed = False

        # Go through each newly fetched stocks and if they are in our gainers list, update, if not add them.
        for stock, price in zip(stockNames, stockPrices):
            stk = inGainers(gainers, lambda s: s.TICKER == stock)
            if stk is not None:
                # Calculate each stock's absolute percent change and it if has met criteria, it's relative percent change.
                newAbsPctChg = stk.getNewAbs(price)
                stk.setNewAfter(price)
                # Update the 1m, 5m, 10m, 20m intervals.
                stk.updateIntervals(price, dt.now())
                # Only update its pct chg and price if it changed...
                if newAbsPctChg != stk.getAbs():
                    changed = True
                    stk.setAbs(newAbsPctChg)
                    stk.setPrice(price)
                # If current stock's percent change meets desired and it has already not met the desired...
                if stk.getAbs() >= pctChgDes and not stk.hasMetCrit():
                    # Send notification, flag it as met, and set base price as this price.
                    print(f"\n{stk.TICKER} grew by {stk.getAbs():.2f}% in top gainers! Check it out!")
                    stk.didMeetCrit()
                    stk.setBasePrice(price)
                    play(SOUND, OS)
                # If current stock has already met desired pct chg, then check if it met the desired chg for after.
                elif stk.hasMetCrit() and stk.getAfter() >= pctChgAfter:
                    print(f"\n{stk.getTicker()} grew by {stk.getAfter():.2f}% even after it grew by {pctChgDes}%! Check it out!")
                    stk.setBasePrice(price)
                    play(SOUND, OS)
            else:
                gainers.append(Stock(stock, price, dt.now()))
                changed = True

        # If the list changed, sort list from highest gainers to lowest gainers.
        if changed:
            gainers.sort(key = lambda s: s.absPctChg, reverse = True)
        showTop5(gainers)
        # Wait the desired refresh rate if the list has changed, or refresh after 10 seconds if not.
        sleep(refRateDes if changed else 10)
        driv.refresh()
        # Wait for a second as a buffer to the data scraping.
        sleep(1)

    print("\nMarket closed now, come back next market day!\n")
else:
    print("\nMarket: CLOSED, return next market day!\n")

driv.close()
driv.quit()
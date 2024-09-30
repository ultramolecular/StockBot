#-----------------------------------------------------------------------------------------#
# Author:             Josiah Valdez                                                       #
# Began Development:  February, 7, 2021                                                   #
#                                                                                         #
# This is a program that uses selenium to extract data from tradingview.com top gainers,  #
# calculate and store their prices and percent changes, and send notifications given the  #
# desired change from the user. It is in constant development, and is sometimes unstable. #
#-----------------------------------------------------------------------------------------#
from dotenv import load_dotenv
from datetime import datetime as dt
import os
from pathlib import Path
from platform import system
from time import sleep
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from stock import Stock

''' TODO: 

    LEGEND: [1] - highest priority [2] - next priority [3] - last priority

    - [2] Have different gainers list, absolute gainers (entire day), 1m gainers, 5m gainers, 10m gainers, etc

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
env_path = Path('.') / '.env'
load_dotenv(dotenv_path= env_path)
options = webdriver.ChromeOptions()
# NOTE: For Windows, this will disable the extraneous warnings displayed.
# options.add_experimental_option('excludeSwitches', ['enable-logging'])
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
# page are located, so updating the css selectors and xpaths is necessary. #
#--------------------------------------------------------------------------#
URL = "https://www.tradingview.com"
GAINS_URL = "https://www.tradingview.com/markets/stocks-usa/market-movers-gainers/"
STOCK_LIST_CSS = "tr[class*='listRow']"
STOCK_CSS = "td:nth-child(1) a"
STOCK_PRICES_CSS = "td:nth-child(3)"
LOGIN_ICON_CSS = "button[aria-label='Open user menu']"
EMAIL_CSS = ".emailButton-nKAw8Hvt"
CREDS_IDS = ("id_username", "id_password")
LOGIN_BUTTON_CSS = ".submitButton-LQwxK8Bm"
EMAIL = os.getenv('EMAIL')
PASS = os.getenv('PASS')
SOUND = "swiftly.wav"
OS = system()
MARKET_MONDAY = 0
MARKET_FRIDAY = 5
MARKET_OPEN = dt.now().replace(hour = int(os.getenv('OPEN_HR')), minute = 30)
MARKET_CLOSE = dt.now().replace(hour = int(os.getenv('CLOSE_HR')), minute = 0)

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
def in_gainers(gainers, filt):
    for stock in gainers:
       if filt(stock):
           return stock
    return None

#--------------------------------------#
# Displays current top 5 gainers.      #
# Args:                                #
#     gainers (list): list of gainers. #
#--------------------------------------#
def show_top_5(gainers):
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

def is_recaptcha_visible(driver):
    return driver.execute_script("""
        var iframe = document.querySelector("iframe[title='reCAPTCHA']");
        if (iframe) {
            var style = window.getComputedStyle(iframe);
            var display = style && style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0';
            var rect = iframe.getBoundingClientRect();
            var inViewport = rect.width > 0 && rect.height > 0;
            return display && inViewport;
        } else {
            return false;
        }
    """)

# CONTINUE PROGRAM IF IT IS DURING MARKET DAY & HOURS, OR BYPASS FOR DEVELOPMENT.
if dt.now().weekday() >= MARKET_MONDAY and dt.now().weekday() <= MARKET_FRIDAY and dt.now() > MARKET_OPEN and dt.now() < MARKET_CLOSE:
    print("Market: OPEN\n")
    refRateDes = float(input("Enter refresh rate (minutes) desired: ")) * 60
    pctChgDes = float(input(r"Enter percent change desired (y% format): "))
    pctChgAfter = float(input("Enter percent change desired after it has met initial desired change: "))
    # Once we get info from user, go to tradingview home site.
    driv.get(URL)
    # Create instace of ActionChains to be able to perform keyboard actions
    actions = ActionChains(driv)
    # Wait for login button to click, then send credentials and log in.
    login_icon = WebDriverWait(driv, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, LOGIN_ICON_CSS)))
    login_icon.click()
    # Focus the action chains to the sign in icon and press down arrow and enter to go to sign in display
    actions.move_to_element(login_icon).perform()
    actions.send_keys(Keys.ARROW_DOWN).send_keys(Keys.RETURN).perform()
    WebDriverWait(driv, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, EMAIL_CSS))).click()
    WebDriverWait(driv, 2).until(EC.visibility_of_element_located((By.ID, CREDS_IDS[0]))).send_keys(EMAIL)
    sleep(.5)
    WebDriverWait(driv, 2).until(EC.visibility_of_element_located((By.ID, CREDS_IDS[1]))).send_keys(PASS)
    sleep(.5)    
    WebDriverWait(driv, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, LOGIN_BUTTON_CSS))).click()

    # Check if reCAPTCHA is visible
    try:
        WebDriverWait(driv, 5).until(lambda driver: is_recaptcha_visible(driver))
        print('-' * 200, "\nreCAPTCHA detected, please solve to continue!")
        # Wait until the 'g-recaptcha-response' element has a non-empty value
        try:
            WebDriverWait(driv, 40).until(
                lambda driver: driver.execute_script("return document.getElementsByName('g-recaptcha-response')[0].value !== '';")
            )
            print("reCAPTCHA solved! Continuing...")
        except TimeoutException:
            print("Timeout waiting for reCAPTCHA to be solved.")
            driv.quit()
        finally:
            # Attempt to click login button again
            WebDriverWait(driv, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, LOGIN_BUTTON_CSS))).click()
    except TimeoutException:
        print("No reCAPTCHA detected. Continuing...")

    # Once we're logged in, go to top gainer stock page.
    driv.get(GAINS_URL)
    # This will be the main list that will hold the stocks for the program.
    gainers = []

    # Begins our main loop, where we wait refresh rate and only continue if we still in market hours.
    while dt.now() < MARKET_CLOSE:
        # Wait for the table to load
        WebDriverWait(driv, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "table")))
        # Grab a list of the stock elements (stock names & prices listed on tradingview).
        stockElems = driv.find_elements(By.CSS_SELECTOR, STOCK_LIST_CSS)
        # Create list of stocks and a list of their respective prices.
        stockNames, stockPrices = [], []
        for stk in stockElems:
            try:
                tick = stk.find_element(By.CSS_SELECTOR, STOCK_CSS).text.strip()
                price = float(stk.find_element(By.CSS_SELECTOR, STOCK_PRICES_CSS).text.strip().split()[0])
                stockNames.append(tick)
                stockPrices.append(price)
            except ValueError as e:
                print(f'Something went wrong with stock extraction: {e}')

        # Flag to let program know whether to sort gainers list or not.
        changed = False

        # Go through each newly fetched stocks and if they are in our gainers list, update, if not add them.
        for stock, price in zip(stockNames, stockPrices):
            stk = in_gainers(gainers, lambda s: s.TICKER == stock)
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
        show_top_5(gainers)
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
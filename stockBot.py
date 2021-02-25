#----------------------------------------------------#
#   Author:             Josiah Valdez                #
#   Began Development:  February, 7, 2021            #
#----------------------------------------------------#

from selenium import webdriver
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep

''' TODO: 
    - Implement asking for time interval, cutoff, & % chg desired.
    - Implement checking if current time is between stock market open hours.
    - Implement the logic for getting potential on the rise stocks.
    - Implement the notification system that shows "X Stock grew by Y%" + ifZ =: (in less than Z minutes) + "in Top Gainers! From prePos to currPos,
      sitting at currPct!"
'''

# Holds chromedriver & google-chrome locations on your machine - OPTIONAL FOR SOME.
#DRIV_LOC = "/usr/bin/chromedriver"
#BIN_LOC = "/usr/share/google-chrome"

# Options for the driver - OPTIONAL FOR SOME (i.e. not doing headless).
options = webdriver.ChromeOptions()
options.headless = True
options.add_argument("window-size=1920x1080");
#options.binary_location = BIN_LOC

# Go to tradingview, then once logged in, top gainers.
url = "https://www.tradingview.com"
gainsUrl = "https://www.tradingview.com/markets/stocks-usa/market-movers-gainers/"

# Opens the chrome browser and goes to url specified.
driv = webdriver.Chrome(options = options)
# Uncomment if you are not doing headless.
#driv.set_window_size(1080, 1044)
driv.get(url)
WAIT = 2

# Goes to login page and enters info to log in.
MAIN_LOGIN_PATH = "/html/body/div[2]/div[3]/div/div[4]/span[2]/a"
LOGIN_PATH = "/html/body/div[11]/div/div[2]/div/div/div/div/div/div/form/div[5]/div[2]/button/span[2]"
EMAIL_PATH = "/html/body/div[11]/div/div[2]/div/div/div/div/div/div/div[1]/div[4]/div/span"
CRED_BOX = "//input[@class='tv-control-material-input tv-signin-dialog__input tv-control-material-input__control']"
# Enter your tradingview login info.
EMAIL = ""
PASS = ""
WebDriverWait(driv, WAIT).until(EC.presence_of_element_located((By.XPATH, MAIN_LOGIN_PATH))).click()
WebDriverWait(driv, WAIT).until(EC.presence_of_element_located((By.XPATH, EMAIL_PATH))).click()
creds = driv.find_elements_by_xpath(CRED_BOX)
creds[0].send_keys(EMAIL)
creds[1].send_keys(PASS)
driv.find_element_by_xpath(LOGIN_PATH).click() 
sleep(.5)

# Once we're logged in, go to top gainer stock page.
driv.get(gainsUrl)

# Holds xpath value of the stock name, and stock pct change.
STOCK = "//a[@class='tv-screener__symbol apply-common-tooltip']"
STOCK_PCT_CHG = "//td[@class='tv-data-table__cell tv-screener-table__cell tv-screener-table__cell--up tv-screener-table__cell--big tv-screener-table__cell--with-marker']"
# Grab a list of the stock elements (stock names listed on tradingview).
stockElems, stockPctElems = driv.find_elements_by_xpath(STOCK), driv.find_elements_by_xpath(STOCK_PCT_CHG)
# List only the names of the stocks.
stockNames, stockPctChg = [s.text for s in stockElems], [pct.text for pct in stockPctElems]

# Print the names of the stocks to make sure things are working right.
print("----------------------------------\nSTOCK \t % CHG \t\t |CHG|\n----------------------------------")
i = 0
for stock in stockNames:
    print(stock, '\t', stockPctChg[i], '\t', stockPctChg[i + 1])
    i += 2

driv.close()
driv.quit()
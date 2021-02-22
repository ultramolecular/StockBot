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

# Sets time for driver to wait for elements to show up, change as needed.
WAIT_ELEM = 2
XPATH_VAL = "/html/body/div[2]/div[5]/div/div/div/div[2]/div/div/div/div/div/div[1]/div/div/a[1]"
# Click on a trivial button just to test things out.
elem = WebDriverWait(driv, WAIT_ELEM).until(EC.presence_of_element_located((By.XPATH, XPATH_VAL)))
elem.click()

driv.close()
driv.quit()
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
from rich.console import Console
from rich.table import Table
from time import sleep
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from stock import Stock


# Configure Chrome and OS path variables
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
OS = system()

options = webdriver.ChromeOptions()
if OS == "Windows":
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
driv = webdriver.Chrome(options=options)
driv.set_window_size(1080, 1044)

# Program constants
URL = "https://www.tradingview.com"
GAINS_URL = "https://www.tradingview.com/markets/stocks-usa/market-movers-gainers/"
STOCK_LIST_CSS = "tr[class*='listRow']"
STOCK_CSS = "td:nth-child(1) a"
STOCK_PRICES_CSS = "td:nth-child(3)"
VOL_CSS = "td:nth-child(4)"
LOGIN_ICON_CSS = "button[aria-label='Open user menu']"
EMAIL_CSS = ".emailButton-nKAw8Hvt"
CREDS_IDS = ("id_username", "id_password")
LOGIN_BUTTON_CSS = ".submitButton-LQwxK8Bm"
EMAIL = os.getenv('EMAIL', '')
PASS = os.getenv('PASS', '')
SOUND = "swiftly.wav"
MARKET_MONDAY = 0
MARKET_FRIDAY = 5
OPEN_HR = int(os.getenv('OPEN_HR', ''))
CLOSE_HR = int(os.getenv('CLOSE_HR', ''))
MARKET_OPEN = dt.now().replace(hour=OPEN_HR, minute=30, second=0)
MARKET_CLOSE = dt.now().replace(hour=CLOSE_HR, minute=0, second=0)


def colorize_pct(val):
    """
    Colorizes given percentages using Rich markup e.g. [green]2.53%[/green].
    Positive = green, Negative = red, Zero = white.
    """
    if val > 0:
        color = "green"
    elif val < 0:
        color = "red"
    else:
        color = "white"
    return f"[{color}]{val:6.2f}%[/{color}]"

def safe_pct(stk_age, val, min_age):
    """
    Return either a colorized percent if stk.age >= min_age, or '--' otherwise.
    This avoids displaying intervals that the stock hasn't 'lived' for yet.
    """
    if stk_age >= min_age:
        return colorize_pct(val)
    else:
        return "--"

def show_top_5(gainers):
    """
    Prints a table for the top 5 gainers with columns:
    [Ticker | Price | Abs% | 1m % | 5m % | 10m % | 20m %].
    If a stock has met user criteria, prints a second row for the 'peak' info.
    """
    if not gainers:
        return

    console = Console()
    top5 = gainers[:5]
    now_str = dt.now().strftime("%H:%M:%S")

    table = Table(
        title=f"Top 5 Gainers @ {now_str}",
        show_header=True,
        header_style="bold cyan",
    )

    table.add_column("Ticker", style="bold white")
    table.add_column("Price", justify="right")
    table.add_column("Abs", justify="right")
    table.add_column("1m", justify="right")
    table.add_column("5m", justify="right")
    table.add_column("10m", justify="right")
    table.add_column("20m", justify="right")

    for stk in top5:
        # Primary row for the main data
        table.add_row(
            stk.getTicker(),
            f"${stk.price:.2f}",
            colorize_pct(stk.getAbs()),
            safe_pct(stk.getAge(), stk.get1mPct(), 1),
            safe_pct(stk.getAge(), stk.get5mPct(), 5),
            safe_pct(stk.getAge(), stk.get10mPct(), 10),
            safe_pct(stk.getAge(), stk.get20mPct(), 20)
        )
        # If it met criteria, add a second row with the “criteria/peak” info
        if stk.hasMetCrit():
            crit_time_str = stk.getCritTime().strftime("%H:%M:%S")
            time_max_str  = stk.getTimeMaxPrice().strftime("%H:%M:%S")
            peak_change   = stk.getPeakChange()  # absolute % from critPrice
            second_line = (
                f"[bold yellow]-> Crit:[/bold yellow] {crit_time_str}, "
                f"${stk.getCritPrice():.2f} | [bold yellow]Peak:[/bold yellow] {time_max_str}, "
                f"${stk.getMaxPrice():.2f}, Vol: {stk.getVolAtMaxPrice()} => {colorize_pct(peak_change)}"
            )
            # We'll put that entire info into the first column, leaving the others blank
            table.add_row(second_line, "", "", "", "", "", "")
    console.print(table)

def show_eod_stats(gainers, pctChgDes):
    """
    Prints the end-of-day summary table for all stocks that have met or surpassed pctChgDes.
    """
    winners = [s for s in gainers if s.hasMetCrit()]

    if not winners:
        print("\nNo stocks met or surpassed your desired growth today.")
        return

    console = Console()
    table = Table(
        title=f"SUMMARY OF STOCKS THAT SURPASSED {pctChgDes}% GROWTH TODAY",
        show_header=True,
        header_style="bold cyan"
    )

    table.add_column("CritTime", style="bold white")
    table.add_column("CritPrice", justify="right")
    table.add_column("Ticker", justify="left")
    table.add_column("PeakTime", justify="right")
    table.add_column("MaxPrice", justify="right")
    table.add_column("Volume", justify="right")
    table.add_column("Peak %", justify="right")

    for s in winners:
        crit_time_str = s.getCritTime().strftime("%H:%M:%S")
        time_max_str  = s.getTimeMaxPrice().strftime("%H:%M:%S")
        peak_change   = s.getPeakChange()
        
        volume_str = s.getVolAtMaxPrice()
        peak_str = colorize_pct(peak_change)
        crit_price_str = f"${s.getCritPrice():.2f}"
        max_price_str  = f"${s.getMaxPrice():.2f}"

        table.add_row(
            crit_time_str,
            crit_price_str,
            s.getTicker(),
            time_max_str,
            max_price_str,
            volume_str,
            peak_str
        )
    console.print(table)

def play(file, osType):
    """Play sound based on OS and given sound file path."""
    if osType == "Windows":
        import winsound
        winsound.PlaySound(file, winsound.SND_ASYNC)
    else:
        from playsound import playsound
        playsound(file)

def is_recaptcha_visible(driver):
    """Detects recaptcha iframe visibility and returns true if visible, false if not."""
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

def in_gainers(gainers, filt):
    """Searches for a stock of interest in the list and returns it if it exists."""
    for stock in gainers:
       if filt(stock):
           return stock
    return None


# Check if current day is within market week
if dt.now().weekday() >= MARKET_MONDAY and dt.now().weekday() <= MARKET_FRIDAY:
    # If user started program before market open time, wait until open
    if dt.now() < MARKET_OPEN:
        print(f"Market isn't open just yet, waiting until open @ {MARKET_OPEN.strftime('%H:%M:%S')}...")
        while dt.now() < MARKET_OPEN:
            pass
    # Once we're within market hours, begin program specification set up and navigation
    if dt.now() >= MARKET_OPEN and dt.now() <= MARKET_CLOSE:
        print("Market: OPEN\n")
        refRateDes = float(input("Enter refresh rate (minutes) desired: ")) * 60
        pctChgDes = float(input(r"Enter percent change desired (y% format): "))
        pctChgAfter = float(input("Enter percent change desired after it has met initial desired change: "))

        # Go to TradingView
        driv.get(URL)
        actions = ActionChains(driv)

        # Login
        login_icon = WebDriverWait(driv, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, LOGIN_ICON_CSS)))
        login_icon.click()
        actions.move_to_element(login_icon).perform()
        actions.send_keys(Keys.ARROW_DOWN).send_keys(Keys.RETURN).perform()
        WebDriverWait(driv, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, EMAIL_CSS))).click()
        WebDriverWait(driv, 2).until(EC.visibility_of_element_located((By.ID, CREDS_IDS[0]))).send_keys(EMAIL)
        sleep(.5)
        WebDriverWait(driv, 2).until(EC.visibility_of_element_located((By.ID, CREDS_IDS[1]))).send_keys(PASS)
        sleep(.5)
        WebDriverWait(driv, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, LOGIN_BUTTON_CSS))).click()

        # Check for reCAPTCHA
        try:
            WebDriverWait(driv, 4).until(lambda driver: is_recaptcha_visible(driver))
            print('-' * 200, "\nreCAPTCHA detected, please solve to continue!")
            try:
                WebDriverWait(driv, 40).until(
                    lambda driver: driver.execute_script("return document.getElementsByName('g-recaptcha-response')[0].value !== '';")
                )
                print("reCAPTCHA solved! Continuing...")
                WebDriverWait(driv, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, LOGIN_BUTTON_CSS))).click()
            except TimeoutException:
                print("Timeout waiting for reCAPTCHA to be solved.")
                driv.close()
                driv.quit()
                exit()
        except TimeoutException:
            print("No reCAPTCHA detected. Continuing...")

        # Go to Gainers page
        driv.get(GAINS_URL)

        # Main list holding the stocks
        gainers = []

        # Main program loop where we wait refresh rate and only continue if we are still in market hours
        while dt.now() < MARKET_CLOSE:
            # Wait for table
            WebDriverWait(driv, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "table")))
            # Grab rows
            stockElems = driv.find_elements(By.CSS_SELECTOR, STOCK_LIST_CSS)
            stockNames, stockPrices, volumes = [], [], []

            for row in stockElems:
                try:
                    tick = row.find_element(By.CSS_SELECTOR, STOCK_CSS).text.strip()
                    price_text = row.find_element(By.CSS_SELECTOR, STOCK_PRICES_CSS).text.strip().split()[0]
                    price = float(price_text)
                    vol_text = row.find_element(By.CSS_SELECTOR, VOL_CSS).text.strip()

                    stockNames.append(tick)
                    stockPrices.append(price)
                    volumes.append(vol_text)
                except ValueError as e:
                    print(f'Something went wrong with value extraction: {e}')

            changed = False

            # Update each stock or create new
            for (stockName, price, vol) in zip(stockNames, stockPrices, volumes):
                stk = in_gainers(gainers, lambda s: s.TICKER == stockName)
                if stk is not None:
                    # Calculate absolute % chg
                    newAbsPctChg = stk.getNewAbs(price)
                    stk.setNewAfter(price)
                    stk.updateIntervals(price, vol, dt.now())

                    # Only update its % chg and price if it changed...
                    if newAbsPctChg != stk.getAbs():
                        changed = True
                        stk.setAbs(newAbsPctChg)
                        stk.setPrice(price)

                    # If meets desired and wasn't met before
                    if stk.getAbs() >= pctChgDes and not stk.hasMetCrit():
                        print(f"\n{stk.getTicker()} grew by {stk.getAbs():.2f}% in top gainers! Check it out!")
                        stk.didMeetCrit()
                        stk.setBasePrice(price)
                        play(SOUND, OS)

                    # If already met criteria, check if after-criteria growth is reached
                    elif stk.hasMetCrit() and stk.getAfter() >= pctChgAfter:
                        print(f"\n{stk.getTicker()} grew by {stk.getAfter():.2f}% even after hitting your growth rate desired ({pctChgDes}%)!")
                        stk.setBasePrice(price)
                        play(SOUND, OS)
                else:
                    # Create new stock object
                    newStock = Stock(stockName, price, vol, dt.now())
                    gainers.append(newStock)
                    changed = True

            # Sort list from highest gainers to lowest and show top 5 if list is changed
            if changed:
                gainers.sort(key=lambda s: s.getAbs(), reverse=True)
                show_top_5(gainers)

            # Sleep
            sleep(refRateDes if changed else 10)
            driv.refresh()
            sleep(1)

        # End-of-day summary
        show_eod_stats(gainers, pctChgDes)
else:
    print("\nMarket: CLOSED, return next market day!\n")

driv.close()
driv.quit()

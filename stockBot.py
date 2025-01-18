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
from typing import Callable, Optional
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from rich.console import Console
from rich.table import Table
from stock import Stock

##############################################################################
#                           GLOBAL CONFIG                                    #
##############################################################################

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
OS = system()
LOGIN_ICON_CSS = "button[aria-label='Open user menu']"
EMAIL_CSS = ".emailButton-nKAw8Hvt"
CREDS_IDS = ("id_username", "id_password")
LOGIN_BUTTON_CSS = ".submitButton-LQwxK8Bm"
STOCK_LIST_CSS = "tr[class*='listRow']"
STOCK_CSS = "td:nth-child(1) a"
STOCK_PRICES_CSS = "td:nth-child(3)"
VOL_CSS = "td:nth-child(4)"
URL = "https://www.tradingview.com"
GAINS_URL = "https://www.tradingview.com/markets/stocks-usa/market-movers-gainers/"
EMAIL = os.getenv('EMAIL', '')
PASS = os.getenv('PASS', '')
SOUND = "swiftly.wav"
MARKET_MONDAY = 0
MARKET_FRIDAY = 4
OPEN_HR = int(os.getenv('OPEN_HR', ''))
CLOSE_HR = int(os.getenv('CLOSE_HR', ''))
MARKET_OPEN = dt.now().replace(hour=OPEN_HR, minute=31, second=0)
MARKET_CLOSE = dt.now().replace(hour=CLOSE_HR, minute=0, second=0)

##############################################################################
#                           HELPER FUNCTIONS                                 #
##############################################################################

def setup_webdriver() -> webdriver.Chrome:
    """
    Creates and configures the Selenium Chrome WebDriver instance.
    """
    options = webdriver.ChromeOptions()
    if OS == "Windows":
        # Suppress extraneous logging in Windows
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1080, 1044)
    return driver

def is_recaptcha_visible(driver: webdriver.Chrome) -> bool:
    """
    Detect recaptcha iframe visibility and returns True if visible, False otherwise.
    """
    return driver.execute_script(
        """
        var iframe = document.querySelector("iframe[title='reCAPTCHA']");
        if (iframe) {
            var style = window.getComputedStyle(iframe);
            var display = style && style.display !== 'none'
                              && style.visibility !== 'hidden'
                              && style.opacity !== '0';
            var rect = iframe.getBoundingClientRect();
            var inViewport = rect.width > 0 && rect.height > 0;
            return display && inViewport;
        } else {
            return false;
        }
        """
    )

def play_sound(file: str):
    """
    Play sound for user notifications. Different approach for Windows vs. other OS.
    """
    if OS == "Windows":
        import winsound
        winsound.PlaySound(file, winsound.SND_ASYNC)
    else:
        from playsound import playsound
        playsound(file)

def wait_for_market_open() -> tuple[float, float, float, bool]:
    """
    If it's before market open, block until we hit the open time.
    """
    if dt.now() < MARKET_OPEN:
        print(
            f"Market isn't open yet (will open at {MARKET_OPEN.strftime('%H:%M:%S')}).\n"
            "Input your parameters in the meantime! ...\n"
        )
        r, pd, pa = get_user_params()

        while dt.now() < MARKET_OPEN:
            pass

        return r, pd, pa, True

    return 0, 0, 0, False

def get_user_params() -> tuple[float, float, float]:
    """
    Prompt user for refresh rate, desired percent change, and secondary threshold.
    Returns (refRateDesSeconds, pctChgDes, pctChgAfter).
    """
    refRateDes = float(input("Enter refresh rate (minutes) desired: ")) * 60
    pctChgDes = float(input("Enter percent change desired (y% format): "))
    pctChgAfter = float(input("Enter percent change desired after it has met initial desired change: "))

    return refRateDes, pctChgDes, pctChgAfter

def login_to_tradingview(driver: webdriver.Chrome, email: str, password: str):
    """
    Logs in to TradingView by clicking the login icon, selecting email, entering credentials.
    """
    login_icon = WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, LOGIN_ICON_CSS))
    )
    login_icon.click()

    actions = ActionChains(driver)
    actions.move_to_element(login_icon).perform()
    actions.send_keys(Keys.ARROW_DOWN).send_keys(Keys.RETURN).perform()

    WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, EMAIL_CSS))
    ).click()

    WebDriverWait(driver, 2).until(
        EC.visibility_of_element_located((By.ID, CREDS_IDS[0]))
    ).send_keys(email)

    sleep(0.5)
    WebDriverWait(driver, 2).until(
        EC.visibility_of_element_located((By.ID, CREDS_IDS[1]))
    ).send_keys(password)

    sleep(0.5)
    WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, LOGIN_BUTTON_CSS))
    ).click()

def check_recaptcha(driver: webdriver.Chrome):
    """
    Detect reCAPTCHA and wait for it to be solved if present. Otherwise, proceed.
    """
    try:
        WebDriverWait(driver, 4).until(lambda drv: is_recaptcha_visible(drv))
        print('-' * 120, "\nreCAPTCHA detected, please solve to continue!")
        try:
            WebDriverWait(driver, 40).until(
                lambda drv: drv.execute_script(
                    "return document.getElementsByName('g-recaptcha-response')[0].value !== '';"
                )
            )
            print("reCAPTCHA solved! Continuing...")
            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, LOGIN_BUTTON_CSS))
            ).click()
        except TimeoutException:
            print("Timeout waiting for reCAPTCHA to be solved. Exiting.")
            driver.close()
            driver.quit()
            exit()
    except TimeoutException:
        print("No reCAPTCHA detected. Continuing...")

def scrape_stocks(driver: webdriver.Chrome) -> list[tuple[str, float, str]]:
    """
    Scrape the table of stocks from the Gainers page and return a list
    of (ticker, price, volume).
    """
    WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
    )
    rows = driver.find_elements(By.CSS_SELECTOR, STOCK_LIST_CSS)

    data = []
    for row in rows:
        try:
            tick = row.find_element(By.CSS_SELECTOR, STOCK_CSS).text.strip()
            price_text = row.find_element(By.CSS_SELECTOR, STOCK_PRICES_CSS).text.strip().split()[0]
            price_val = float(price_text)
            vol_text = row.find_element(By.CSS_SELECTOR, VOL_CSS).text.strip()
            data.append((tick, price_val, vol_text))
        except ValueError as e:
            print(f"Something went wrong with value extraction: {e}")
    return data

def in_gainers(gainers: list[Stock], filt: Callable[[Stock], bool]) -> Optional[Stock]:
    """
    Searches for a stock of interest in the list and returns it if it exists.
    """
    for stock in gainers:
        if filt(stock):
            return stock
    return None

def process_stocks(gainers: list[Stock], new_data: list[tuple[str, float, str]], refRateDes: float, pctChgDes: float, pctChgAfter: float) -> bool:
    """
    Update each Stock or create new ones based on the newly scraped data.
    Checks if user criteria is met, plays sounds, etc.
    Returns True if anything changed, otherwise False.
    """
    changed = False
    for (stockName, price, vol) in new_data:
        stk = in_gainers(gainers, lambda s: s.getTicker() == stockName)
        if stk:
            newAbsPctChg = stk.getNewAbs(price)
            stk.setNewAfter(price)

            # pass refRate (in minutes) to update intervals
            refRateMins = refRateDes / 60.0
            stk.updateIntervals(price, vol, dt.now(), refRateMins)

            if newAbsPctChg != stk.getAbs():
                changed = True
                stk.setAbs(newAbsPctChg)
                stk.setPrice(price)

            # check user criteria
            if stk.getAbs() >= pctChgDes and not stk.hasMetCrit():
                print(f"\n{stk.getTicker()} grew by {stk.getAbs():.2f}% in top gainers! Check it out!")
                stk.didMeetCrit()
                stk.setBasePrice(price)
                play_sound(SOUND)
            elif stk.hasMetCrit() and stk.getAfter() >= pctChgAfter:
                print(f"\n{stk.getTicker()} grew by {stk.getAfter():.2f}% even after hitting your threshold {pctChgDes}%!")
                stk.setBasePrice(price)
                play_sound(SOUND)

        else:
            # brand new stock
            newStock = Stock(stockName, price, vol, dt.now())
            gainers.append(newStock)
            changed = True

    return changed

def getIntervalLabels(refRateMins: float) -> tuple[str, str, str, str]:
    """
    Return a tuple of 4 strings representing column labels for intervals,
    e.g. '2m', '10m', etc., depending on the user’s refresh rate.
    This ensures the table column headers are more honest about the real intervals.
    """
    intervals = [1, 5, 10, 20]
    labels = []
    for minutes in intervals:
        steps_float = minutes / refRateMins
        steps = round(steps_float)
        steps = steps if steps > 0 else 1
        real_time = int(steps * refRateMins)
        label_str = f"{real_time}m"
        labels.append(label_str)
    return tuple(labels)

def colorize_pct(val: float) -> str:
    """
    Return a Rich color markup string for the percentage, e.g. [green]2.53%[/green].
    Positive => green, Negative => red, Zero => white.
    """
    if val > 0:
        color = "green"
    elif val < 0:
        color = "red"
    else:
        color = "white"
    return f"[{color}]{val:6.2f}%[/{color}]"

def safe_pct(stk_age: int, val: float, min_age: int) -> str:
    """
    Return a colorized percent if the stock's age >= min_age, else '--'.
    This avoids showing intervals not yet 'lived'.
    """
    if stk_age >= min_age:
        return colorize_pct(val)
    else:
        return "--"

def show_top_5(gainers: list[Stock], labels: tuple[str, str, str, str]):
    """
    Renders the top 5 gainers in a Rich table. If a stock met criteria,
    prints a second row showing the criteria/peak info.
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

    # 7 columns total: Ticker, Price, Abs, 1m, 5m, 10m, 20m
    table.add_column("Ticker")
    table.add_column("Price", justify="right")
    table.add_column("Abs", justify="right")
    table.add_column(labels[0], justify="right")
    table.add_column(labels[1], justify="right")
    table.add_column(labels[2], justify="right")
    table.add_column(labels[3], justify="right")

    for stk in top5:
        table.add_row(
            stk.getTicker(),
            f"${stk.price:.2f}",
            colorize_pct(stk.getAbs()),
            safe_pct(stk.getAge(), stk.get1mPct(), 1),
            safe_pct(stk.getAge(), stk.get5mPct(), 5),
            safe_pct(stk.getAge(), stk.get10mPct(), 10),
            safe_pct(stk.getAge(), stk.get20mPct(), 20),
        )

        if stk.hasMetCrit():
            crit_time = stk.getCritTime()
            time_max = stk.getTimeMaxPrice()
            assert crit_time is not None, "Logic error: we must have crit time here!"
            assert time_max is not None, "Logic error: we must have time max here!"
            crit_time_str = crit_time.strftime("%H:%M:%S")
            time_max_str  = time_max.strftime("%H:%M:%S")
            peak_change   = stk.getPeakChange()
            second_line = (
                f"[bold yellow]-> Crit:[/bold yellow] {crit_time_str}, "
                f"${stk.getCritPrice():.2f} | [bold yellow]Peak:[/bold yellow] {time_max_str}, "
                f"${stk.getMaxPrice():.2f}, Vol: {stk.getVolAtMaxPrice()} => {colorize_pct(peak_change)}"
            )
            # We'll put that entire info into the first column, leaving others blank
            table.add_row(second_line)

    console.print(table)

def show_eod_stats(gainers: list[Stock], pctChgDes: float):
    """
    End-of-day summary for all stocks that have met or surpassed pctChgDes, in a Rich table.
    """
    winners = [s for s in gainers if s.hasMetCrit()]
    if not winners:
        print("\nNo stocks met or surpassed your desired growth today.")
        return

    console = Console()
    table = Table(
        title=f"SUMMARY OF STOCKS THAT SURPASSED {pctChgDes}% GROWTH TODAY",
        show_header=True,
        header_style="bold cyan",
    )

    table.add_column("CritTime")
    table.add_column("CritPrice", justify="right")
    table.add_column("Ticker", justify="left")
    table.add_column("PeakTime", justify="right")
    table.add_column("MaxPrice", justify="right")
    table.add_column("Volume", justify="right")
    table.add_column("Peak %", justify="right")

    for s in winners:
        crit_time = s.getCritTime()
        time_max = s.getTimeMaxPrice()
        assert crit_time is not None, "Logic error: we must have crit time here!"
        assert time_max is not None, "Logic error: we must have time max here!"
        crit_time_str = crit_time.strftime("%H:%M:%S")
        time_max_str  = time_max.strftime("%H:%M:%S")
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
            peak_str,
        )

    console.print(table)

def run_main_loop(driver: webdriver.Chrome, gainers: list[Stock], refRateDes: float, pctChgDes: float, pctChgAfter: float):
    """
    The main loop that repeatedly scrapes the gainers table, updates stocks,
    checks user criteria, displays top 5 if changed, etc.
    """
    while dt.now() < MARKET_CLOSE:
        # 1) Scrape
        new_data = scrape_stocks(driver)
        # 2) Process
        changed = process_stocks(gainers, new_data, refRateDes, pctChgDes, pctChgAfter)
        # 3) If changed, sort and show top 5
        if changed:
            gainers.sort(key=lambda s: s.getAbs(), reverse=True)
            labels = getIntervalLabels(refRateDes / 60)
            show_top_5(gainers, labels)
        # 4) Sleep
        sleep(refRateDes if changed else 10)
        driver.refresh()
        sleep(1)

def main():
    """
    Main entry point for the StockBot application.
    Checks market day, waits if before open, obtains user params, logs in, and runs main loop.
    """
    # 1) Check if it's a weekday in [MON..FRI]
    dow = dt.now().weekday()
    if dow >= MARKET_MONDAY and dow <= MARKET_FRIDAY:
        # 2) Check if user started program before market open, if so get their input too
        refRateDes, pctChgDes, pctChgAfter, got_params = wait_for_market_open()
        # 3) Check if we are within open/close window
        now = dt.now()

        if now >= MARKET_OPEN and now <= MARKET_CLOSE:
            print("Market: OPEN\n")
            # 4) Gather user parameters if we haven't already
            if not got_params:
                refRateDes, pctChgDes, pctChgAfter = get_user_params()
            # 5) Setup driver & login
            driver = setup_webdriver()
            driver.get(URL)
            login_to_tradingview(driver, EMAIL, PASS)
            # 6) Check recaptcha
            check_recaptcha(driver)
            # 7) Go to Gainers page
            driver.get(GAINS_URL)
            # 8) Create main list
            gainers = []
            # 9) Run main loop
            run_main_loop(driver, gainers, refRateDes, pctChgDes, pctChgAfter)
            # 10) End-of-day summary
            show_eod_stats(gainers, pctChgDes)
            print("\nMarket CLOSED now, come back next market day!\n")

            driver.close()
            driver.quit()
    else:
        print("\nMarket: CLOSED, return next market day!\n")


if __name__ == "__main__":
    main()

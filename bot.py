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
from datetime import timedelta
import openpyxl
import os
from pathlib import Path
from platform import system
from time import sleep
from typing import Callable, Optional
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from rich.console import Console
from rich.table import Table
from stock import Stock
from webdriver_manager.chrome import ChromeDriverManager

##############################################################################
#                           GLOBAL CONFIG                                    #
##############################################################################

env_path = Path(".") / ".env"
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
EMAIL = os.getenv("EMAIL", "")
PASS = os.getenv("PASS", "")
SOUND = "swiftly.wav"
MARKET_MONDAY = 0
MARKET_FRIDAY = 4
OPEN_HR = int(os.getenv("OPEN_HR", ""))
CLOSE_HR = int(os.getenv("CLOSE_HR", ""))
EOD_EXPORT_DIR = os.getenv("EOD_EXPORT_PATH", "")
EXPORT_PATH = Path(EOD_EXPORT_DIR) if EOD_EXPORT_DIR else None

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
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(options=options, service=service)
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


def get_next_day(now=None) -> tuple[dt, dt]:
    if now is None:
        now = dt.now()

    wday = now.weekday()
    start_date = now.replace(hour=OPEN_HR, minute=31)
    end_date = now.replace(hour=CLOSE_HR, minute=0)

    # If it's a weekend go to next Monday market open
    if wday >= 5:
        # Calc days until Monday
        days_ahead = (7 - wday) % 7
        next_mon = (now + timedelta(days=days_ahead)).replace(
                hour=OPEN_HR, minute=31
        )
        # Update MARKET_CLOSE to account for the new date
        return next_mon, next_mon.replace(hour=CLOSE_HR)
    
    # If a weekday and it's before market open and close, run then
    if now < start_date or now < end_date:
        return start_date, end_date
    else:
        # After market close (still a weekday), schedule next day
        next_day = now + timedelta(days=1)
        # Check if the next day is Saturday to skip to Monday
        if next_day.weekday() == 5:
            next_day += timedelta(days=2) 

        return next_day.replace(hour=OPEN_HR, minute=31), \
                next_day.replace(hour=CLOSE_HR, minute=0)


def get_user_params() -> tuple[float, float, float]:
    """
    Prompt user for refresh rate, desired percent change, and secondary threshold.
    Returns (ref_rate_desSeconds, pct_chg_des, pct_chg_after).
    """
    ref_rate_des = float(input("Enter refresh rate (minutes) desired: ")) * 60
    pct_chg_des = float(input("Enter percent change desired (y% format): "))
    pct_chg_after = float(
        input("Enter percent change desired after it has met initial desired change: ")
    )

    return ref_rate_des, pct_chg_des, pct_chg_after


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
        print("-" * 120, "\nreCAPTCHA detected, please solve to continue!")
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
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
    )
    rows = driver.execute_script(
        """
        const rowCss = arguments[0];
        return Array.from(document.querySelectorAll(rowCss))
            .slice(0, 100)
            .map(r => {
                const c = r.querySelectorAll("td");
                if (c.length < 4) return null;

                const ticker =
                    (c[0].querySelector("a")?.innerText || c[0].innerText)
                        .trim();

                const priceText = c[2].innerText.trim().replace(/[^0-9.]/g, '');
                const price = parseFloat(priceText);
                const vol = c[3].innerText.trim();

                if (!ticker || Number.isNaN(price)) return null;
                return { ticker, price, vol };
            })
            .filter(r => r !== null);
        """,
        STOCK_LIST_CSS,
    )
    return [(r["ticker"], r["price"], r["vol"]) for r in rows]

def in_gainers(gainers: list[Stock], filt: Callable[[Stock], bool]) -> Optional[Stock]:
    """
    Searches for a stock of interest in the list and returns it if it exists.
    """
    for stock in gainers:
        if filt(stock):
            return stock
    return None


def process_stocks(
    gainers: list[Stock],
    new_data: list[tuple[str, float, str]],
    ref_rate_des: float,
    pct_chg_des: float,
    pct_chg_after: float,
) -> bool:
    """
    Update each Stock or create new ones based on the newly scraped data.
    Checks if user criteria is met, plays sounds, etc.
    Returns True if anything changed, otherwise False.
    """
    changed = False
    for stk_name, price, vol in new_data:
        stk = in_gainers(gainers, lambda s: s.get_ticker() == stk_name)
        if stk:
            new_abs_pct_chg = stk.get_new_abs(price)
            stk.set_new_after(price)

            # pass ref_rate (in minutes) to update intervals
            ref_rate_mins = ref_rate_des / 60.0
            stk.update_intervals(price, vol, dt.now(), ref_rate_mins)

            if new_abs_pct_chg != stk.get_abs():
                changed = True
                stk.set_abs(new_abs_pct_chg)
                stk.set_price(price)

            # check user criteria
            if stk.get_abs() >= pct_chg_des and not stk.has_met_crit():
                print(
                    f"\n{stk.get_ticker()} grew by {stk.get_abs():.2f}% in top gainers! Check it out!"
                )
                stk.did_meet_crit()
                stk.set_base_price(price)
                play_sound(SOUND)
            elif stk.has_met_crit() and stk.get_after() >= pct_chg_after:
                print(
                    f"\n{stk.get_ticker()} grew by {stk.get_after():.2f}% even after hitting your threshold {pct_chg_des}%!"
                )
                stk.set_base_price(price)
                play_sound(SOUND)

        else:
            # brand new stock
            new_stock = Stock(stk_name, price, vol, dt.now())
            gainers.append(new_stock)
            changed = True

    return changed


def get_interval_labels(ref_rate_mins: float) -> tuple[str, str, str, str]:
    """
    Return a tuple of 4 strings representing column labels for intervals,
    e.g. '2m', '10m', etc., depending on the user’s refresh rate.
    This ensures the table column headers are more honest about the real intervals.
    """
    intervals = [1, 5, 10, 20]
    labels = []
    for minutes in intervals:
        steps_float = minutes / ref_rate_mins
        steps = round(steps_float)
        steps = steps if steps > 0 else 1
        real_time = int(steps * ref_rate_mins)
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
            stk.get_ticker(),
            f"${stk.price:.2f}",
            colorize_pct(stk.get_abs()),
            safe_pct(stk.get_age(), stk.get_1m_pct(), 1),
            safe_pct(stk.get_age(), stk.get_5m_pct(), 5),
            safe_pct(stk.get_age(), stk.get_10m_pct(), 10),
            safe_pct(stk.get_age(), stk.get_20m_pct(), 20),
        )

        if stk.has_met_crit():
            crit_time = stk.get_crit_time()
            time_max = stk.get_time_max_price()
            assert crit_time is not None, "Logic error: we must have crit time here!"
            assert time_max is not None, "Logic error: we must have time max here!"
            crit_time_str = crit_time.strftime("%H:%M:%S")
            time_max_str = time_max.strftime("%H:%M:%S")
            peak_change = stk.get_peak_change()
            second_line = (
                f"[bold yellow]-> Crit:[/bold yellow] {crit_time_str}, "
                f"${stk.get_crit_price():.2f} | [bold yellow]Peak:[/bold yellow] {time_max_str}, "
                f"${stk.get_max_price():.2f}, Vol: {stk.get_vol_at_max_price()} => {colorize_pct(peak_change)}"
            )
            table.add_row(second_line)

    console.print(table)


def export_eod_stats_to_excel(
    winners: list[Stock], export_dir: Path
):
    """
    Create/write to an Excel file with the summary of stocks that met criteria.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    assert ws is not None, "Logic error: openpyxl's wb.active is unexpectedly None!"
    ws.title = f"EOD Crit Stock Growth Summary"

    headers = [
        "CritTime",
        "CritPrice",
        "Ticker",
        "PeakTime",
        "MaxPrice",
        "Volume",
        "Peak%",
    ]
    ws.append(headers)

    # Format for date/time we want
    date_format = "HH:MM:SS"
    pct_format = "0.00%"
    currency_format = '"$"#,##0.00'

    # Store today's date/time for naming
    date_str = dt.now().strftime("%Y_%m_%d")

    # Append a row for each winner
    for s in winners:
        crit_time = s.get_crit_time()
        peak_time = s.get_time_max_price()
        # e.g. 20.0 => 0.2 in excel
        peak_change = s.get_peak_change() / 100.0

        row = [
            crit_time,  # datetime
            s.get_crit_price(),  # float
            s.get_ticker(),  # string
            peak_time,  # datetime
            s.get_max_price(),  # float
            s.get_vol_at_max_price(),  # string
            peak_change,  # float for actual %  e.g. 0.2 => 20%
        ]
        ws.append(row)

    # Data starts at row 2
    for i in range(2, len(winners) + 2):
        # CritTime
        ws.cell(row=i, column=1).number_format = date_format
        # PeakTime
        ws.cell(row=i, column=4).number_format = date_format
        # CritPrice
        ws.cell(row=i, column=2).number_format = currency_format
        # MaxPrice
        ws.cell(row=i, column=5).number_format = currency_format
        # Peak%
        ws.cell(row=i, column=7).number_format = pct_format

    fname = f"eod_summary_{date_str}.xlsx"
    export_dir.mkdir(parents=True, exist_ok=True)
    fpath = export_dir / fname

    wb.save(str(fpath))
    print(f"End-of-day summary exported to: {fpath}")


def show_eod_stats(gainers: list[Stock], pct_chg_des: float):
    """
    End-of-day summary for all stocks that have met or surpassed pct_chg_des, in a Rich table.
    Saves to excel file if possible for record keeping.
    """
    winners = [s for s in gainers if s.has_met_crit()]
    if not winners:
        print("\nNo stocks met or surpassed your desired growth today.")
        return

    console = Console()
    table = Table(
        title=f"SUMMARY OF STOCKS THAT SURPASSED {pct_chg_des}% GROWTH TODAY",
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
        crit_time = s.get_crit_time()
        time_max = s.get_time_max_price()
        assert crit_time is not None, "Logic error: we must have crit time here!"
        assert time_max is not None, "Logic error: we must have time max here!"
        crit_time_str = crit_time.strftime("%H:%M:%S")
        time_max_str = time_max.strftime("%H:%M:%S")
        peak_change = s.get_peak_change()

        volume_str = s.get_vol_at_max_price()
        peak_str = colorize_pct(peak_change)
        crit_price_str = f"${s.get_crit_price():.2f}"
        max_price_str = f"${s.get_max_price():.2f}"

        table.add_row(
            crit_time_str,
            crit_price_str,
            s.get_ticker(),
            time_max_str,
            max_price_str,
            volume_str,
            peak_str,
        )

    console.print(table)
    if EXPORT_PATH is not None:
        export_eod_stats_to_excel(winners, EXPORT_PATH)
    else:
        print("No EOD_EXPORT_PATH environment variable found; skipping Excel export.")


def run_main_loop(
    MARKET_CLOSE: dt,
    driver: webdriver.Chrome,
    gainers: list[Stock],
    ref_rate_des: float,
    pct_chg_des: float,
    pct_chg_after: float,
    labels: tuple[str, str, str, str],
):
    """
    The main loop that repeatedly scrapes the gainers table, updates stocks,
    checks user criteria, displays top 5 if changed, etc.
    """
    while dt.now() < MARKET_CLOSE:
        # 1) Scrape
        new_data = scrape_stocks(driver)
        # 2) Process
        changed = process_stocks(
            gainers, new_data, ref_rate_des, pct_chg_des, pct_chg_after
        )
        # 3) If changed, sort and show top 5
        if changed:
            gainers.sort(key=lambda s: s.get_abs(), reverse=True)
            show_top_5(gainers, labels)
        # 4) Sleep
        sleep(ref_rate_des if changed else 10)
        driver.refresh()
        sleep(1)


def main():
    """
    Main entry point for the StockBot application.
    Checks market day, waits if before open, obtains user params, logs in, and runs main loop.
    """
    ref_rate_des, pct_chg_des, pct_chg_after = get_user_params()
    # Setup driver & login
    driver = setup_webdriver()
    driver.get(URL)
    login_to_tradingview(driver, EMAIL, PASS)
    # Check recaptcha
    check_recaptcha(driver)
    # Go to Gainers page
    driver.get(GAINS_URL)

    while True:
        # Get next market day
        now = dt.now()
        next_open, next_close = get_next_day(now)
        sec_until_open = (next_open - now).total_seconds() 
        labels = get_interval_labels(ref_rate_des / 60)
        # Create main list
        gainers = []
        # Wait until market open of next available day
        if sec_until_open > 0:
            print(f"\nWaiting until market open on {next_open.strftime('%a')}" \
                    f" @ {next_open.hour}:{next_open.minute} ...")
            sleep(sec_until_open)
        # Run main loop
        run_main_loop(
            next_close, driver, gainers, ref_rate_des, pct_chg_des,
                                            pct_chg_after, labels
        )
        # End-of-day summary
        show_eod_stats(gainers, pct_chg_des)
        print("\nMarket CLOSED now!\n")


if __name__ == "__main__":
    main()

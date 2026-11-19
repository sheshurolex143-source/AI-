"""Automated browser screenshot capture for FinSight AI.
Captures high-resolution screenshots of all frontend views into docs/screenshots/.
"""

import os
import sys

# Ensure UTF-8 output encoding on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import time
from playwright.sync_api import sync_playwright

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "docs", "screenshots"))
os.makedirs(OUTPUT_DIR, exist_ok=True)


def capture_all():
    print(f"Saving screenshots to: {OUTPUT_DIR}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        # 1. Login Page
        print("Capturing 1. Login Page...")
        page.goto("http://localhost:5173/login")
        page.wait_for_selector("text=Welcome to FinSight AI", timeout=10000)
        time.sleep(1)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "01_login.png"))

        # 2. Perform Login
        print("Authenticating as demo user...")
        page.click("button:has-text('Sign In')")
        page.wait_for_url("http://localhost:5173/", timeout=10000)
        page.wait_for_selector("text=Income vs Expense Trends", timeout=10000)
        time.sleep(2)  # allow charts to animate

        # 3. Dashboard Page
        print("Capturing 2. Dashboard Page...")
        page.screenshot(path=os.path.join(OUTPUT_DIR, "02_dashboard.png"), full_page=True)

        # 4. Transactions Ledger
        print("Capturing 3. Transactions Page...")
        page.goto("http://localhost:5173/transactions")
        page.wait_for_selector("text=Transaction Ledger", timeout=10000)
        time.sleep(1.5)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "03_transactions.png"), full_page=True)

        # 5. AI Insights & What-If Simulator
        print("Capturing 4. Insights & What-If Simulator...")
        page.goto("http://localhost:5173/insights")
        page.wait_for_selector("text=AI What-If Budget Simulator", timeout=10000)
        time.sleep(2)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "04_insights.png"), full_page=True)

        # 6. Budgets & Goals
        print("Capturing 5. Budgets & Goals...")
        page.goto("http://localhost:5173/budgets")
        page.wait_for_selector("text=Monthly Category Budgets", timeout=10000)
        time.sleep(1.5)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "05_budgets.png"), full_page=True)

        # 7. How the AI Works (Viva Lab)
        print("Capturing 6. How the AI Works...")
        page.goto("http://localhost:5173/how-it-works")
        page.wait_for_selector("text=Machine Learning Architecture", timeout=10000)
        time.sleep(2)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "06_how_it_works.png"), full_page=True)

        # 8. Settings & Retraining
        print("Capturing 7. Settings Page...")
        page.goto("http://localhost:5173/settings")
        page.wait_for_selector("text=System Settings & AI Ops", timeout=10000)
        time.sleep(1.5)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "07_settings.png"), full_page=True)

        browser.close()
        print("[SUCCESS] All 7 page screenshots captured successfully!")


if __name__ == "__main__":
    capture_all()


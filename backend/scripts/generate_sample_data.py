"""Synthetic dataset generator for FinSight AI.
Generates:
1. ml_artifacts/training_data.csv (3,500+ realistic noisy bank descriptions across 13 categories)
2. sample_data/transactions_sample.csv (6 months of realistic Indian demo user transactions with planted anomalies)
"""

import os
import sys

# Ensure UTF-8 output encoding on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import random
from datetime import date, timedelta
import pandas as pd

# Categories matching CATEGORIES in categorizer.py
CATEGORIES = [
    "Food & Dining",
    "Groceries",
    "Transport",
    "Shopping",
    "Bills & Utilities",
    "Rent & Housing",
    "Entertainment & Subscriptions",
    "Health",
    "Education",
    "Travel",
    "Investments & Savings",
    "Income",
    "Other",
]

# Prefixes and noise patterns typical of Indian bank statements / UPI / POS
PREFIXES = [
    "UPI/", "POS ", "NEFT-", "IMPS-", "ACH/", "NACH DEBIT ", "CMS/", "BILLDESK/",
    "PAYTM*", "RAZORPAY*", "CASHFREE*", "BHIM/", "INB/TXN/", "ATM WDL ", ""
]
CITIES = ["BLR", "MUM", "DEL", "HYD", "PUN", "CHE", "KOL", "NOI", "GGN", "IND"]
BANKS = ["HDFC", "ICICI", "SBI", "AXIS", "KOTAK", "CITI", "YESB"]

CATEGORY_KEYWORDS = {
    "Food & Dining": [
        "SWIGGY ORDER", "ZOMATO RESTAURANT", "DOMINOS PIZZA", "MCDONALDS INDIA", "BURGER KING",
        "STARBUCKS COFFEE", "CHAI POINT", "CHAAYOS", "HALDIRAMS", "BARBEQUE NATION", "PIZZA HUT",
        "CAFE COFFEE DAY", "SUBWAY SANDWICHES", "KFC FRIED CHICKEN", "WOW MOMO", "BIRYANI BLUES",
        "BEHROUZ BIRYANI", "FAASOS EATS", "SWEET TRUTH", "OVEN STORY PIZZA", "MAINLAND CHINA",
        "THE BEER CAFE", "PUNJAB GRILL", "SOCIAL BAR & DINING", "IRANI CHAI & CAFE", "UDUPI RESTAURANT",
        "SAGAR RATNA", "SARAVANA BHAVAN", "PARADISE BIRYANI", "NATRAJ CHOLE BHATURE", "BENGAL SWEETS"
    ],
    "Groceries": [
        "BIGBASKET RETAIL", "DMART HYPERMARKET", "RELIANCE FRESH", "MORE RETAIL SUPERMARKET",
        "BLINKIT QUICK COMMERCE", "ZEPTO INSTANT GROCERY", "INSTAMART SWIGGY", "NATURES BASKET",
        "SPENCERS RETAIL", "LULU HYPERMARKET", "STAR BAZAAR", "APOLLO SUPERSTORE", "VEG & FRUITS VENDOR",
        "LOCAL KIRANA STORE", "ORGANIC INDIA STORE", "MOTHER DAIRY MILK", "AMUL PARLOUR DAIRY",
        "COUNTRY DELIGHT MILK", "MILK BASKET GROCERY", "HERITAGE FOODS", "RATNADEEP SUPERMARKET",
        "BB DAILY MILK", "FRESH TO HOME FISH MEAT", "LICIOUS MEAT DELIVERY", "MEATIGO FOODS"
    ],
    "Transport": [
        "UBER INDIA RIDES", "OLA CABS BANGALORE", "RAPIDO BIKE TAXI", "NANDI INFRA TOLL PLAZA",
        "FASTAG NHAI TOLL", "DELHI METRO RECHARGE DMRC", "BANGALORE METRO BMRCL", "INDIAN OIL PETROL PUMP",
        "BHARAT PETROLEUM HPCL", "SHELL PETROL STATION", "HP FUEL STATION", "AUTO RICKSHAW FARE",
        "BLUSMART MOBILITY EV", "YULU BIKES ELECTRIC", "MAHARASHTRA STATE TOLL", "FASTAG RECHARGE ICICI",
        "KSRTC BUS TICKET", "MSRTC TICKET", "CAR PARKING MALL", "METRO SMART CARD AUTO TOPUP"
    ],
    "Shopping": [
        "AMAZON SELLER SERVICES", "FLIPKART INTERNET PVT", "MYNTRA DESIGNS", "AJIO DIGITAL RELIANCE",
        "NYKAA E-RETAIL", "TATA CLiQ FASHION", "ZARA RETAIL INDIA", "H&M CLOTHING STORE",
        "UNIQLO CLOTHING", "DECATHLON SPORTS", "CROMA ELECTRONICS", "RELIANCE DIGITAL STORE",
        "VIJAY SALES", "MEESHO ONLINE SHOPPING", "LENSKART EYEWEAR", "TITAN WATCHES EYEWEAR",
        "WESTSIDE TRENT", "PANTALOONS FASHION", "MAX FASHION INDIA", "SHOPPERS STOP", "FABINDIA HANDICRAFTS"
    ],
    "Bills & Utilities": [
        "BESCOM ELECTRICITY BILL", "TATA POWER MUMBAI", "ADANI ELECTRICITY", "BWSSB WATER SUPPLY",
        "INDANE GAS CYLINDER", "BHARAT GAS REFILL", "JIO PREPAID RECHARGE", "AIRTEL BROADBAND FIBER",
        "VI CELLULAR RECHARGE", "ACT FIBERNET INTERNET", "HATHWAY CABLE BROADBAND", "TATA PLAY DTH",
        "AIRTEL DTH RECHARGE", "MUNICIPAL PROPERTY TAX", "MAHANAGAR GAS LIMITED", "IGL INDRAPRASTHA GAS"
    ],
    "Rent & Housing": [
        "HOUSE RENT TO LANDLORD", "SOCIETY MAINTENANCE CHARGES", "APARTMENT OWNERS ASSOC",
        "PG MONTHLY RENT", "NESTAWAY RENT PAYMENT", "NOBROKER HOUSING RENT", "FLAT RENT SHARING",
        "BUILDING WATER TANKER CHARGE", "HOUSE CLEANING SERVICES URBAN COMPANY", "SECURITY GUARD SOCIETY SALARY",
        "MAID SALARY MONTHLY", "COOK SALARY HOME", "GATED COMMUNITY MAINTENANCE", "GUEST HOUSE RENT"
    ],
    "Entertainment & Subscriptions": [
        "NETFLIX ENTERTAINMENT SUBSCRIPTION", "SPOTIFY PREMIUM STREAMING", "AMAZON PRIME MEMBERSHIP",
        "DISNEY+ HOTSTAR VIP", "YOUTUBE PREMIUM SUBSCRIPTION", "BOOKMYSHOW MOVIE TICKETS",
        "PVR CINEMAS MULTIPLEX", "INOX LEISURE MOVIES", "SONYLIV ANNUAL PLAN", "ZEE5 SUBSCRIPTION",
        "APPLE SERVICES ICLOUD ITUNES", "GOOGLE PLAY SERVICES APPS", "AUDIBLE AUDIOBOOKS", "TIMES PRIME MEMBERSHIP"
    ],
    "Health": [
        "APOLLO PHARMACY MEDICALS", "MEDPLUS PHARMACY", "TATA 1MG HEALTHCARE", "PHARMEASY ONLINE MEDICINE",
        "PRACTO CONSULTATION CLINIC", "DR LAL PATHLABS TEST", "METROPOLIS HEALTHCARE LAB", "MAX HEALTHCARE HOSPITAL",
        "FORTIS HOSPITAL CLINIC", "DENTAL CLINIC ROOT CANAL", "EYE CLINIC EYEWEAR", "HEALTH CHECKUP DIAGNOSTICS",
        "CULT.FIT GYM SUBSCRIPTION", "GOLD GYM FITNESS MEMBERSHIP", "AYURVEDIC CLINIC MEDICINE", "PHYSIOTHERAPY SESSION"
    ],
    "Education": [
        "COURSERA INC ONLINE COURSE", "UDEMY ONLINE LEARNING", "BYJUS LEARNING PROGRAM",
        "UNACADEMY PLUS SUBSCRIPTION", "UPGRAD EDUCATION PVT", "COLLEGE TUITION SEMESTER FEE",
        "SCHOOL TERM FEES", "EXAM APPLICATION REGISTRATION", "OXFORD BOOK STORE", "CROSSWORD BOOKSTORE",
        "ACADEMIC TEXTBOOKS PURCHASE", "EDX ONLINE CERTIFICATION", "CODING BOOTCAMP FEE", "GRE TOEFL EXAM FEE"
    ],
    "Travel": [
        "MAKEMYTRIP INDIA FLIGHTS", "GOIBIBO HOTEL BOOKING", "IRCTC TRAIN TICKET BOOKING",
        "INDIGO AIRLINES TICKET", "AIR INDIA FLIGHT RESERVATION", "OYO ROOMS HOTEL", "CLEARTRIP TRAVEL PVT",
        "EASEMYTRIP TRAVEL", "EXPEDIA HOTEL & FLIGHT", "ZOSTEL HOSTEL BOOKING", "CAB TO AIRPORT OUTSTATION",
        "VISA PROCESSING FEES", "RESORT WEEKEND STAY", "TRAVEL INSURANCE POLICY", "SPICEJET FLIGHT"
    ],
    "Investments & Savings": [
        "ZERODHA BROKING LTD", "GROWW INVESTMENTS TECH", "ICICI PRUDENTIAL MUTUAL FUND",
        "SBI MUTUAL FUND SYSTEMATIC SIP", "HDFC BALANCED ADVANTAGE FUND", "NIPPON INDIA MUTUAL FUND",
        "UTI NIFTY INDEX FUND SIP", "PARAG PARIKH FLEXI CAP SIP", "AXIS BLUECHIP FUND SIP",
        "KOTAK SECURITIES SHARE PURCHASE", "GOLD SOVEREIGN BOND PURCHASE", "PPF ACCOUNT DEPOSIT POST OFFICE",
        "NATIONAL PENSION SCHEME NPS", "FIXED DEPOSIT SBI BANK", "RECURRING DEPOSIT POST OFFICE"
    ],
    "Income": [
        "SALARY CREDIT FROM INFOSYS", "SALARY DIRECT DEPOSIT TCS", "MONTHLY SALARY WIPRO LTD",
        "PAYROLL CREDIT ACCENTURE", "SALARY DEPOSIT GOOGLE INDIA", "FREELANCE DESIGN CONSULTING PAYMENT",
        "CLIENT CONSULTING FEES NEFT", "UPWORK FREELANCE PAYOUT", "DIVIDEND CREDIT TCS EQUITY",
        "INTEREST CREDIT SAVINGS ACCOUNT", "REFUND FROM AMAZON PAY", "CASHBACK REWARD CREDITED",
        "TAX REFUND INCOME TAX DEPT", "ANNUAL PERFORMANCE BONUS CREDIT", "REIMBURSEMENT EXPENSE CLAIM"
    ],
    "Other": [
        "ATM CASH WITHDRAWAL", "MISCELLANEOUS DEBIT", "BANK CHARGES & SMS ALERT FEE",
        "ANNUAL DEBIT CARD MAINTENANCE CHARGE", "CHEQUE RETURN CHARGES", "DONATION PM CARES FUND",
        "GIFT FOR FRIEND BIRTHDAY", "STATIONERY AND COURIER BLUEDART", "DOCUMENT NOTARY & STAMP DUTY",
        "KEY MAKER REPAIR SERVICE", "LAUNDRY DRY CLEANING SHOP", "PET CLINIC AND PET FOOD"
    ]
}


def generate_training_data(output_path: str, samples_per_category: int = 280) -> int:
    """Generate 3,500+ diverse, realistic noisy bank statement strings."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    rows = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        count = 0
        while count < samples_per_category:
            kw = random.choice(keywords)
            pfx = random.choice(PREFIXES)
            city = random.choice(CITIES) if random.random() > 0.4 else ""
            ref_num = str(random.randint(1000, 999999))
            bank = random.choice(BANKS) if random.random() > 0.5 else ""

            # Pattern formats
            patterns = [
                f"{pfx}{kw} {ref_num} {city}".strip(),
                f"{pfx}{kw}*{ref_num}".strip(),
                f"{pfx}{bank}/{kw}/{ref_num}".strip(),
                f"{kw} {city} REF:{ref_num}".strip(),
                f"{pfx}{kw}".strip(),
                f"TXN#{ref_num} {kw}".strip(),
                f"{pfx}{kw} - {bank} TXN".strip(),
                f"{kw.lower()} ord {ref_num}".strip(),
                f"{kw.upper()} / {ref_num}".strip(),
            ]
            desc = random.choice(patterns)
            rows.append({"description": desc, "category": category})
            count += 1

    df = pd.DataFrame(rows)
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    df.to_csv(output_path, index=False)
    return len(df)


def generate_demo_transactions(output_path: str) -> int:
    """Generate 6 months of demo transactions (approx 350-400 rows) with 6 planted anomalies."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    today = date.today()
    start_date = today - timedelta(days=180)

    txns = []

    # Monthly regular events (Salary, Rent, EMI, SIP, Utilities, Subscriptions)
    curr_month = date(start_date.year, start_date.month, 1)
    while curr_month <= today:
        y, m = curr_month.year, curr_month.month

        # 1. Salary (1st of month)
        sal_date = date(y, m, 1)
        if sal_date <= today:
            txns.append({
                "date": sal_date.isoformat(),
                "description": "SALARY CREDIT FROM ACME TECH LTD",
                "amount": 75000.0,
                "type": "income",
                "category": "Income",
            })

        # Occasional freelance income (mid month)
        if random.random() > 0.4:
            f_date = date(y, m, min(15, 28))
            if f_date <= today:
                txns.append({
                    "date": f_date.isoformat(),
                    "description": "NEFT FREELANCE UI CONSULTING",
                    "amount": float(random.choice([8000, 12000, 15000])),
                    "type": "income",
                    "category": "Income",
                })

        # 2. Rent (2nd of month)
        rent_date = date(y, m, 2)
        if rent_date <= today:
            txns.append({
                "date": rent_date.isoformat(),
                "description": "HOUSE RENT TRANSFER TO LANDLORD",
                "amount": 16000.0,
                "type": "expense",
                "category": "Rent & Housing",
            })

        # 3. EMI (5th of month)
        emi_date = date(y, m, 5)
        if emi_date <= today:
            txns.append({
                "date": emi_date.isoformat(),
                "description": "NACH DEBIT HDFC PERSONAL LOAN EMI",
                "amount": 8500.0,
                "type": "expense",
                "category": "Bills & Utilities",
            })

        # 4. SIP Mutual Fund (8th of month)
        sip_date = date(y, m, 8)
        if sip_date <= today:
            txns.append({
                "date": sip_date.isoformat(),
                "description": "ACH DEBIT SBI MUTUAL FUND SIP",
                "amount": 5000.0,
                "type": "expense",
                "category": "Investments & Savings",
            })

        # 5. Utilities
        u_date = date(y, m, 10)
        if u_date <= today:
            txns.append({
                "date": u_date.isoformat(),
                "description": "BESCOM ELECTRICITY BILL ONLINE",
                "amount": float(random.randint(900, 1400)),
                "type": "expense",
                "category": "Bills & Utilities",
            })
            txns.append({
                "date": (u_date + timedelta(days=2)).isoformat(),
                "description": "AIRTEL BROADBAND FIBER BILL",
                "amount": 999.0,
                "type": "expense",
                "category": "Bills & Utilities",
            })
            txns.append({
                "date": (u_date + timedelta(days=3)).isoformat(),
                "description": "JIO POSTPAID MOBILE RECHARGE",
                "amount": 499.0,
                "type": "expense",
                "category": "Bills & Utilities",
            })

        # 6. Subscriptions
        sub_date = date(y, m, 18)
        if sub_date <= today:
            txns.append({
                "date": sub_date.isoformat(),
                "description": "NETFLIX ENTERTAINMENT SUBSCRIPTION",
                "amount": 649.0,
                "type": "expense",
                "category": "Entertainment & Subscriptions",
            })
            txns.append({
                "date": (sub_date + timedelta(days=1)).isoformat(),
                "description": "SPOTIFY PREMIUM RECURRING",
                "amount": 119.0,
                "type": "expense",
                "category": "Entertainment & Subscriptions",
            })

        # Next month calculation
        if m == 12:
            curr_month = date(y + 1, 1, 1)
        else:
            curr_month = date(y, m + 1, 1)

    # Daily variable transactions across 180 days
    current_day = start_date
    while current_day <= today:
        # Food & dining (2-3 times a week)
        if random.random() < 0.35:
            merchant = random.choice(["SWIGGY*ORDER", "ZOMATO RESTAURANT", "CHAI POINT", "STARBUCKS INDIA", "DOMINOS PIZZA"])
            amt = random.randint(180, 650)
            txns.append({
                "date": current_day.isoformat(),
                "description": f"UPI/{merchant} #{random.randint(100, 999)}",
                "amount": float(amt),
                "type": "expense",
                "category": "Food & Dining",
            })

        # Groceries (1-2 times a week)
        if random.random() < 0.22:
            merchant = random.choice(["BIGBASKET RETAIL", "BLINKIT QUICK GROCERY", "DMART HYPERMARKET", "ZEPTO INSTANT"])
            amt = random.randint(450, 2400)
            txns.append({
                "date": current_day.isoformat(),
                "description": f"POS {merchant} BLR",
                "amount": float(amt),
                "type": "expense",
                "category": "Groceries",
            })

        # Transport (rides / fuel)
        if random.random() < 0.30:
            merchant = random.choice(["UBER INDIA RIDES", "OLA CABS BANGALORE", "SHELL PETROL STATION", "FASTAG TOLL"])
            amt = random.randint(80, 550) if "PETROL" not in merchant else random.randint(1000, 2000)
            txns.append({
                "date": current_day.isoformat(),
                "description": f"{merchant} TXN",
                "amount": float(amt),
                "type": "expense",
                "category": "Transport",
            })

        # Shopping
        if random.random() < 0.10:
            merchant = random.choice(["AMAZON SELLER SERVICES", "FLIPKART INTERNET", "MYNTRA DESIGNS", "DECATHLON INDIA"])
            amt = random.randint(600, 3500)
            txns.append({
                "date": current_day.isoformat(),
                "description": f"BILLDESK/{merchant} IND",
                "amount": float(amt),
                "type": "expense",
                "category": "Shopping",
            })

        # Health
        if random.random() < 0.05:
            merchant = random.choice(["APOLLO PHARMACY MEDICALS", "TATA 1MG HEALTH", "DR LAL PATHLABS"])
            amt = random.randint(250, 1500)
            txns.append({
                "date": current_day.isoformat(),
                "description": f"POS {merchant}",
                "amount": float(amt),
                "type": "expense",
                "category": "Health",
            })

        current_day += timedelta(days=1)

    # ── PLANT 6 REALISTIC ANOMALIES ──
    # 1. Unusually huge food delivery
    txns.append({
        "date": (today - timedelta(days=22)).isoformat(),
        "description": "UPI/SWIGGY*ORDER PARTY CATERING 9928",
        "amount": 5400.0,  # Usual is ₹180 - ₹650
        "type": "expense",
        "category": "Food & Dining",
    })

    # 2. Large shopping spree
    txns.append({
        "date": (today - timedelta(days=45)).isoformat(),
        "description": "POS CROMA ELECTRONICS APPLE IPAD",
        "amount": 42000.0,  # Usual shopping is ₹600 - ₹3500
        "type": "expense",
        "category": "Shopping",
    })

    # 3. Abnormal electricity bill surge
    txns.append({
        "date": (today - timedelta(days=70)).isoformat(),
        "description": "BESCOM ELECTRICITY BILL ABNORMAL SURCHARGE",
        "amount": 7800.0,  # Usual is ~₹1000
        "type": "expense",
        "category": "Bills & Utilities",
    })

    # 4. Rare huge ATM cash withdrawal
    txns.append({
        "date": (today - timedelta(days=95)).isoformat(),
        "description": "ATM CASH WITHDRAWAL HDFC MAIN BRANCH",
        "amount": 25000.0,
        "type": "expense",
        "category": "Other",
    })

    # 5. Duplicate subscription charge
    txns.append({
        "date": (today - timedelta(days=15)).isoformat(),
        "description": "NETFLIX ENTERTAINMENT DUPLICATE RETRY",
        "amount": 649.0,
        "type": "expense",
        "category": "Entertainment & Subscriptions",
    })

    # 6. Rare luxury weekend resort travel charge
    txns.append({
        "date": (today - timedelta(days=35)).isoformat(),
        "description": "RAZORPAY*TAJ RESORTS LUXURY GETAWAY GOA",
        "amount": 28500.0,
        "type": "expense",
        "category": "Travel",
    })

    df = pd.DataFrame(txns)
    df = df.sort_values(by="date", ascending=True).reset_index(drop=True)
    df.to_csv(output_path, index=False)
    return len(df)


if __name__ == "__main__":
    train_path = os.path.join("ml_artifacts", "training_data.csv")
    sample_path = os.path.join("..", "sample_data", "transactions_sample.csv")
    if not os.path.exists("../sample_data"):
        os.makedirs("../sample_data", exist_ok=True)

    print(f"Generating synthetic training dataset at {train_path}...")
    n_train = generate_training_data(train_path, samples_per_category=280)
    print(f"✅ Generated {n_train} training samples.")

    print(f"Generating realistic demo user transactions at {sample_path}...")
    n_sample = generate_demo_transactions(sample_path)
    print(f"✅ Generated {n_sample} demo transactions with 6 planted anomalies.")

"""Symbol universe: EGX (.CA suffix on Yahoo Finance), US mega-caps, popular ETFs.

EGX tickers use the Yahoo Finance convention <TICKER>.CA (Cairo exchange).
"""

from __future__ import annotations

# --- EGX: actively traded names (EGX30 core + liquid mid-caps) ----------------
EGX_SYMBOLS: dict[str, dict] = {
    "COMI.CA": {"name": "Commercial International Bank", "sector": "Banks"},
    "ETEL.CA": {"name": "Telecom Egypt", "sector": "Telecom"},
    "SWDY.CA": {"name": "Elsewedy Electric", "sector": "Industrials"},
    "HRHO.CA": {"name": "EFG Hermes Holding", "sector": "Financial Services"},
    "ESRS.CA": {"name": "Ezz Steel", "sector": "Basic Resources"},
    "EAST.CA": {"name": "Eastern Company", "sector": "Personal Goods"},
    "TMGH.CA": {"name": "Talaat Moustafa Group", "sector": "Real Estate"},
    "ABUK.CA": {"name": "Abu Qir Fertilizers", "sector": "Chemicals"},
    "MFPC.CA": {"name": "Misr Fertilizers (MOPCO)", "sector": "Chemicals"},
    "ORWE.CA": {"name": "Oriental Weavers", "sector": "Industrials"},
    "JUFO.CA": {"name": "Juhayna Food Industries", "sector": "Food & Beverage"},
    "CLHO.CA": {"name": "Cleopatra Hospital", "sector": "Healthcare"},
    "ISPH.CA": {"name": "Ibnsina Pharma", "sector": "Healthcare"},
    "FWRY.CA": {"name": "Fawry", "sector": "Technology / Fintech"},
    "AMOC.CA": {"name": "Alexandria Mineral Oils", "sector": "Energy"},
    "SKPC.CA": {"name": "Sidi Kerir Petrochemicals", "sector": "Chemicals"},
    "PHDC.CA": {"name": "Palm Hills Developments", "sector": "Real Estate"},
    "ORHD.CA": {"name": "Orascom Development Egypt", "sector": "Real Estate"},
    "AUTO.CA": {"name": "GB Corp (GB Auto)", "sector": "Automobiles"},
    "CCAP.CA": {"name": "Citadel Capital (Qalaa Holdings)", "sector": "Financial Services"},
    "ADIB.CA": {"name": "Abu Dhabi Islamic Bank Egypt", "sector": "Banks"},
    "BTFH.CA": {"name": "Beltone Financial Holding", "sector": "Financial Services"},
    "RMDA.CA": {"name": "Rameda Pharma", "sector": "Healthcare"},
    "EFID.CA": {"name": "Edita Food Industries", "sector": "Food & Beverage"},
    "HELI.CA": {"name": "Heliopolis Housing", "sector": "Real Estate"},
    "MICH.CA": {"name": "Misr Chemical Industries", "sector": "Chemicals"},
    "CIRA.CA": {"name": "CIRA Education", "sector": "Education"},
    "MOED.CA": {"name": "Modern Education", "sector": "Education"},
    "EGCH.CA": {"name": "Egyptian Chemical Industries (KIMA)", "sector": "Chemicals"},
    "DAPH.CA": {"name": "Development & Engineering Consultants", "sector": "Industrials"},
}


# --- US: liquid mega/large caps ------------------------------------------------
US_SYMBOLS: dict[str, dict] = {
    "AAPL": {"name": "Apple Inc.", "sector": "Technology"},
    "MSFT": {"name": "Microsoft Corp.", "sector": "Technology"},
    "NVDA": {"name": "NVIDIA Corp.", "sector": "Semiconductors"},
    "GOOGL": {"name": "Alphabet Inc. (A)", "sector": "Communication"},
    "AMZN": {"name": "Amazon.com Inc.", "sector": "Consumer Discretionary"},
    "META": {"name": "Meta Platforms", "sector": "Communication"},
    "TSLA": {"name": "Tesla Inc.", "sector": "Consumer Discretionary"},
    "AVGO": {"name": "Broadcom Inc.", "sector": "Semiconductors"},
    "AMD": {"name": "Advanced Micro Devices", "sector": "Semiconductors"},
    "NFLX": {"name": "Netflix Inc.", "sector": "Communication"},
    "JPM": {"name": "JPMorgan Chase", "sector": "Financials"},
    "V": {"name": "Visa Inc.", "sector": "Financials"},
    "MA": {"name": "Mastercard Inc.", "sector": "Financials"},
    "BAC": {"name": "Bank of America", "sector": "Financials"},
    "WMT": {"name": "Walmart Inc.", "sector": "Consumer Staples"},
    "COST": {"name": "Costco Wholesale", "sector": "Consumer Staples"},
    "PG": {"name": "Procter & Gamble", "sector": "Consumer Staples"},
    "KO": {"name": "Coca-Cola Co.", "sector": "Consumer Staples"},
    "PEP": {"name": "PepsiCo Inc.", "sector": "Consumer Staples"},
    "JNJ": {"name": "Johnson & Johnson", "sector": "Healthcare"},
    "LLY": {"name": "Eli Lilly & Co.", "sector": "Healthcare"},
    "UNH": {"name": "UnitedHealth Group", "sector": "Healthcare"},
    "PFE": {"name": "Pfizer Inc.", "sector": "Healthcare"},
    "ABBV": {"name": "AbbVie Inc.", "sector": "Healthcare"},
    "XOM": {"name": "Exxon Mobil", "sector": "Energy"},
    "CVX": {"name": "Chevron Corp.", "sector": "Energy"},
    "HD": {"name": "Home Depot", "sector": "Consumer Discretionary"},
    "MCD": {"name": "McDonald's Corp.", "sector": "Consumer Discretionary"},
    "DIS": {"name": "Walt Disney Co.", "sector": "Communication"},
    "INTC": {"name": "Intel Corp.", "sector": "Semiconductors"},
    "QCOM": {"name": "Qualcomm Inc.", "sector": "Semiconductors"},
    "TXN": {"name": "Texas Instruments", "sector": "Semiconductors"},
    "ORCL": {"name": "Oracle Corp.", "sector": "Technology"},
    "CRM": {"name": "Salesforce Inc.", "sector": "Technology"},
    "ADBE": {"name": "Adobe Inc.", "sector": "Technology"},
    "CSCO": {"name": "Cisco Systems", "sector": "Technology"},
    "IBM": {"name": "IBM Corp.", "sector": "Technology"},
    "PLTR": {"name": "Palantir Technologies", "sector": "Technology"},
    "UBER": {"name": "Uber Technologies", "sector": "Industrials"},
    "CAT": {"name": "Caterpillar Inc.", "sector": "Industrials"},
    "BA": {"name": "Boeing Co.", "sector": "Industrials"},
    "GE": {"name": "GE Aerospace", "sector": "Industrials"},
    "UPS": {"name": "United Parcel Service", "sector": "Industrials"},
    "T": {"name": "AT&T Inc.", "sector": "Communication"},
    "VZ": {"name": "Verizon Communications", "sector": "Communication"},
    "NKE": {"name": "Nike Inc.", "sector": "Consumer Discretionary"},
    "SBUX": {"name": "Starbucks Corp.", "sector": "Consumer Discretionary"},
    "SOFI": {"name": "SoFi Technologies", "sector": "Financials"},
    "NEE": {"name": "NextEra Energy", "sector": "Utilities"},
    "PLD": {"name": "Prologis Inc.", "sector": "Real Estate"},
}

# --- ETFs ----------------------------------------------------------------------
ETF_SYMBOLS: dict[str, dict] = {
    "SPY": {"name": "SPDR S&P 500 ETF", "category": "US Broad Market"},
    "VOO": {"name": "Vanguard S&P 500 ETF", "category": "US Broad Market"},
    "VTI": {"name": "Vanguard Total Stock Market", "category": "US Broad Market"},
    "IVV": {"name": "iShares Core S&P 500", "category": "US Broad Market"},
    "QQQ": {"name": "Invesco QQQ (Nasdaq-100)", "category": "US Growth"},
    "SCHD": {"name": "Schwab US Dividend Equity", "category": "Dividend"},
    "VYM": {"name": "Vanguard High Dividend Yield", "category": "Dividend"},
    "JEPI": {"name": "JPMorgan Equity Premium Income", "category": "Dividend / Income"},
    "JEPQ": {"name": "JPMorgan Nasdaq Equity Premium", "category": "Dividend / Income"},
    "DGRO": {"name": "iShares Core Dividend Growth", "category": "Dividend"},
    "SOXX": {"name": "iShares Semiconductor ETF", "category": "Sector: Tech"},
    "XLK": {"name": "Technology Select SPDR", "category": "Sector: Tech"},
    "XLF": {"name": "Financial Select SPDR", "category": "Sector: Financials"},
    "XLE": {"name": "Energy Select SPDR", "category": "Sector: Energy"},
    "XLV": {"name": "Health Care Select SPDR", "category": "Sector: Healthcare"},
    "XLI": {"name": "Industrial Select SPDR", "category": "Sector: Industrials"},
    "XLP": {"name": "Consumer Staples Select SPDR", "category": "Sector: Staples"},
    "XLU": {"name": "Utilities Select SPDR", "category": "Sector: Utilities"},
    "EEM": {"name": "iShares MSCI Emerging Markets", "category": "International"},
    "VEA": {"name": "Vanguard FTSE Developed Markets", "category": "International"},
    "VWO": {"name": "Vanguard FTSE Emerging Markets", "category": "International"},
    "EFA": {"name": "iShares MSCI EAFE", "category": "International"},
    "GLD": {"name": "SPDR Gold Shares", "category": "Commodities"},
    "SLV": {"name": "iShares Silver Trust", "category": "Commodities"},
    "USO": {"name": "United States Oil Fund", "category": "Commodities"},
    "TLT": {"name": "iShares 20+ Year Treasury Bond", "category": "Bonds"},
    "AGG": {"name": "iShares Core US Aggregate Bond", "category": "Bonds"},
    "BND": {"name": "Vanguard Total Bond Market", "category": "Bonds"},
    "HYG": {"name": "iShares High Yield Corporate Bond", "category": "Bonds"},
    "ARKK": {"name": "ARK Innovation ETF", "category": "Thematic"},
    "VNQ": {"name": "Vanguard Real Estate ETF", "category": "Real Estate"},
    "IWM": {"name": "iShares Russell 2000", "category": "US Small Cap"},
    # --- Sharia-compliant ETFs (also recognized by analysis/sharia.py) ---
    "HLAL": {"name": "Wahed FTSE USA Shariah ETF", "category": "Sharia: US Equities"},
    "SPUS": {"name": "SP Funds S&P 500 Sharia Industry Exclusions", "category": "Sharia: US Equities"},
    "UMMA": {"name": "Wahed Dow Jones Islamic World ETF", "category": "Sharia: Global"},
    "SPSK": {"name": "SP Funds Dow Jones Global Sukuk ETF", "category": "Sharia: Sukuk"},
    "ISDU": {"name": "iShares MSCI USA Islamic", "category": "Sharia: US Equities"},
    "ISDE": {"name": "iShares MSCI Emerging Markets Islamic", "category": "Sharia: EM"},
    "ISWD": {"name": "iShares MSCI World Islamic", "category": "Sharia: Developed"},
}


def detect_market(symbol: str) -> str:
    """Classify a symbol as 'egx', 'us', or 'etf'.

    Rules: .CA suffix or known EGX list -> 'egx'; known ETF list -> 'etf';
    otherwise -> 'us'.
    """
    sym = symbol.strip().upper()
    if sym.endswith(".CA") or sym in EGX_SYMBOLS:
        return "egx"
    if f"{sym}.CA" in EGX_SYMBOLS:  # bare EGX ticker, e.g. "COMI"
        return "egx"
    if sym in ETF_SYMBOLS:
        return "etf"
    return "us"


def normalize_symbol(symbol: str, market: str | None = None) -> str:
    """Normalize user input to a fetchable ticker.

    'COMI' -> 'COMI.CA' (egx); 'comi.ca' -> 'COMI.CA'; 'aapl' -> 'AAPL'.
    """
    sym = symbol.strip().upper()
    m = market or detect_market(sym)
    if m == "egx" and not sym.endswith(".CA"):
        sym = f"{sym}.CA"
    return sym


def symbol_meta(symbol: str) -> dict:
    """Return metadata (name/sector) if known, else empty dict."""
    sym = symbol.strip().upper()
    return EGX_SYMBOLS.get(sym) or US_SYMBOLS.get(sym) or ETF_SYMBOLS.get(sym) or {}

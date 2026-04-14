# ruff: noqa: E501
"""
FinanceLab Wiki — reference articles for every asset class, instrument type,
market concept, and trading term covered by the platform.

Each article has:
  slug    — URL-safe id
  title   — display heading
  category — grouping for the wiki hub
  tags    — search tokens
  body    — multi-paragraph markdown-safe plain text
"""

from __future__ import annotations

from typing import Any

ARTICLES: list[dict[str, Any]] = [
    # =========================================================================
    # INDIA — EQUITY
    # =========================================================================
    {
        "slug": "india-equity-overview",
        "title": "Indian Equity Markets — Overview",
        "category": "India Equity",
        "tags": ["nse", "bse", "nifty", "sensex", "india", "stocks"],
        "body": (
            "India has two major stock exchanges: the National Stock Exchange (NSE) "
            "and the Bombay Stock Exchange (BSE). The flagship indices are NIFTY 50 "
            "(NSE) and SENSEX (BSE), tracking the top 50 and 30 companies respectively.\n\n"
            "Trading hours are 9:15 AM to 3:30 PM IST, Monday through Friday excluding "
            "market holidays. Settlement follows a T+1 cycle for equities since January 2023.\n\n"
            "Key regulators: SEBI (Securities and Exchange Board of India) oversees all "
            "market participants, exchanges, and mutual funds. Depositories NSDL and CDSL "
            "hold shares in dematerialised form."
        ),
    },
    {
        "slug": "india-equity-large-cap",
        "title": "Large Cap Stocks (India)",
        "category": "India Equity",
        "tags": ["large cap", "nifty 50", "blue chip", "india"],
        "body": (
            "Large cap stocks in India are typically the top 100 companies by full market "
            "capitalisation as defined by SEBI. They include NIFTY 50 constituents such as "
            "Reliance Industries, TCS, HDFC Bank, Infosys, and ICICI Bank.\n\n"
            "Large caps tend to have higher liquidity, lower volatility, and more analyst "
            "coverage. They form the core of most Indian equity portfolios and index funds.\n\n"
            "Tax treatment: Equity held >12 months qualifies for LTCG at 12.5% above "
            "Rs 1.25 lakh exemption (FY 2024-25). Below 12 months, STCG at 20%."
        ),
    },
    {
        "slug": "india-equity-intraday",
        "title": "Intraday Trading (India)",
        "category": "India Equity",
        "tags": ["intraday", "day trading", "speculation", "leverage"],
        "body": (
            "Intraday trading means buying and selling the same stock on the same day — "
            "positions are squared off before market close. Brokers offer leverage (margins) "
            "for intraday, typically 5x-20x depending on the stock.\n\n"
            "STT on intraday is 0.025% on the sell side only (lower than delivery). "
            "Profits are classified as speculative business income and taxed at your slab "
            "rate. Speculative losses can only offset speculative income and carry forward "
            "for 4 years.\n\n"
            "Key risk: Margin calls can force liquidation. Auto square-off happens at 3:15-3:20 PM."
        ),
    },
    {
        "slug": "india-equity-stt",
        "title": "Securities Transaction Tax (STT)",
        "category": "India Equity",
        "tags": ["stt", "tax", "transaction cost", "india"],
        "body": (
            "STT is levied on every transaction on recognised Indian exchanges. Rates vary "
            "by segment:\n\n"
            "- Equity Delivery: 0.1% on both buy and sell (effectively on sell in practice)\n"
            "- Equity Intraday: 0.025% on sell side only\n"
            "- Futures: 0.0125% on sell side\n"
            "- Options: 0.0625% on sell premium (per current Budget rates)\n"
            "- ITM option expiry: STT is charged on the settlement price, which can be "
            "significantly higher than the premium — the so-called 'ITM expiry trap'.\n\n"
            "STT paid on equity delivery is allowed as a deduction from business income "
            "under certain conditions."
        ),
    },
    # =========================================================================
    # INDIA — MUTUAL FUNDS
    # =========================================================================
    {
        "slug": "india-mutual-funds",
        "title": "Indian Mutual Funds — Overview",
        "category": "India Mutual Funds",
        "tags": ["mutual fund", "sip", "nav", "amfi", "india"],
        "body": (
            "Indian mutual funds are regulated by SEBI and distributed through AMFI-registered "
            "intermediaries. Over 40 AMCs (Asset Management Companies) offer thousands of schemes "
            "across equity, debt, hybrid, and thematic categories.\n\n"
            "Key concepts:\n"
            "- NAV (Net Asset Value): the per-unit price, calculated daily after market close.\n"
            "- SIP (Systematic Investment Plan): fixed monthly investment automating rupee-cost averaging.\n"
            "- Exit Load: typically 1% if redeemed within 1 year for equity funds.\n"
            "- Direct vs Regular: Direct plans have lower expense ratios (no distributor commission).\n\n"
            "Popular categories: Flexi Cap, Large Cap, Mid Cap, Small Cap, ELSS (tax-saving), "
            "Index Funds, Liquid Funds, and Debt Funds."
        ),
    },
    {
        "slug": "india-mf-elss",
        "title": "ELSS — Equity Linked Savings Scheme",
        "category": "India Mutual Funds",
        "tags": ["elss", "tax saving", "80c", "lock-in"],
        "body": (
            "ELSS funds qualify for tax deduction under Section 80C up to Rs 1.5 lakh per year. "
            "They have a mandatory 3-year lock-in — the shortest among 80C instruments.\n\n"
            "ELSS invests primarily in equities, so returns are market-linked. Historical CAGR "
            "for top ELSS funds has been 12-15% over 10+ year periods.\n\n"
            "After the lock-in, gains are taxed as LTCG (12.5% above Rs 1.25L exemption). "
            "SIPs in ELSS create a rolling lock-in: each SIP instalment has its own 3-year lock."
        ),
    },
    {
        "slug": "india-mf-index-funds",
        "title": "Index Funds & ETFs (India)",
        "category": "India Mutual Funds",
        "tags": ["index fund", "etf", "passive", "nifty 50", "tracking error"],
        "body": (
            "Index funds and ETFs passively replicate an index like NIFTY 50, NIFTY Next 50, "
            "or SENSEX. They have lower expense ratios (0.05%-0.20%) compared to actively "
            "managed funds (0.5%-2.0%).\n\n"
            "ETFs trade on the exchange like stocks and can have a bid-ask spread. Index mutual "
            "funds are bought/sold at NAV and are easier for SIP investing.\n\n"
            "Tracking error measures how closely the fund follows the index. Lower is better. "
            "Top index funds in India have tracking errors below 0.10%."
        ),
    },
    # =========================================================================
    # INDIA — BONDS & DEBT
    # =========================================================================
    {
        "slug": "india-bonds-overview",
        "title": "Indian Bond Market — Overview",
        "category": "India Bonds",
        "tags": ["bonds", "g-sec", "corporate bonds", "rbi", "debt"],
        "body": (
            "The Indian bond market comprises Government Securities (G-Secs), State Development "
            "Loans (SDLs), corporate bonds, and money market instruments.\n\n"
            "G-Secs are issued by RBI on behalf of the Government of India. They are considered "
            "risk-free and serve as the benchmark yield curve. The 10-year G-Sec yield is the "
            "most watched indicator.\n\n"
            "Corporate bonds are rated by agencies like CRISIL, ICRA, CARE, and India Ratings. "
            "AAA-rated bonds offer a spread of 50-100bps over G-Secs. Retail investors can access "
            "bonds via RBI Retail Direct, debt mutual funds, or bond platforms."
        ),
    },
    {
        "slug": "india-bonds-taxation",
        "title": "Bond Taxation (India)",
        "category": "India Bonds",
        "tags": ["bond tax", "debt fund tax", "indexation", "interest income"],
        "body": (
            "Interest income from bonds is taxed at your income tax slab rate. For listed bonds, "
            "capital gains on sale are STCG (slab rate) if held <12 months, LTCG (12.5%) if held >12 months.\n\n"
            "Debt mutual fund taxation changed from April 2023: all gains are now taxed at slab "
            "rate regardless of holding period (indexation benefit removed).\n\n"
            "Tax-free bonds (issued by NHAI, REC, PFC, etc.) pay interest exempt from income tax — "
            "they trade at a premium because of this benefit."
        ),
    },
    # =========================================================================
    # INDIA — FUTURES & OPTIONS
    # =========================================================================
    {
        "slug": "india-futures",
        "title": "Equity & Index Futures (India)",
        "category": "India F&O",
        "tags": ["futures", "nifty futures", "margin", "lot size", "expiry"],
        "body": (
            "Futures contracts on NSE are available for NIFTY 50, Bank NIFTY, Fin NIFTY, "
            "and ~190 individual stocks. Contracts are monthly with 3 active expiries.\n\n"
            "Key concepts:\n"
            "- Lot Size: minimum tradeable quantity (e.g., NIFTY lot = 25 units).\n"
            "- Margin: SPAN + Exposure margin, typically 10-15% of contract value.\n"
            "- Mark-to-Market (MTM): daily profit/loss settlement.\n"
            "- Rollover: closing the current month contract and opening the next month.\n\n"
            "F&O income is classified as non-speculative business income. Turnover for "
            "audit purposes is calculated as: absolute profit + absolute loss on all trades. "
            "If turnover exceeds Rs 10 crore, tax audit under Section 44AB may apply."
        ),
    },
    {
        "slug": "india-options",
        "title": "Options Trading (India)",
        "category": "India F&O",
        "tags": ["options", "call", "put", "premium", "greeks", "expiry"],
        "body": (
            "Options on NSE include index options (NIFTY, Bank NIFTY — European style, cash-settled) "
            "and stock options (American style for some, mostly European now).\n\n"
            "Weekly expiries are available for NIFTY (Thursday), Bank NIFTY (Wednesday), "
            "and Fin NIFTY (Tuesday). Monthly expiry is the last Thursday.\n\n"
            "The Greeks:\n"
            "- Delta: sensitivity to underlying price change.\n"
            "- Theta: time decay per day.\n"
            "- Vega: sensitivity to implied volatility.\n"
            "- Gamma: rate of change of delta.\n\n"
            "ITM Expiry Trap: If your option expires ITM, STT is charged on the full settlement "
            "value — not the premium. This can be 10-50x the normal STT. Always close ITM options "
            "before 3:00 PM on expiry day."
        ),
    },
    {
        "slug": "india-option-chain",
        "title": "Reading an Option Chain",
        "category": "India F&O",
        "tags": ["option chain", "oi", "max pain", "pcr", "iv"],
        "body": (
            "An option chain shows all available strike prices for calls and puts at a given expiry.\n\n"
            "Key columns:\n"
            "- OI (Open Interest): total outstanding contracts at a strike. High OI = strong support/resistance.\n"
            "- Change in OI: positive = new positions being built; negative = unwinding.\n"
            "- IV (Implied Volatility): market's expectation of future volatility priced into the option.\n"
            "- LTP/Premium: current trading price of the option.\n\n"
            "Derived analytics:\n"
            "- Max Pain: strike where option writers have minimum payout. Market often gravitates here at expiry.\n"
            "- PCR (Put-Call Ratio): PCR > 1.2 = more puts (potentially bullish contrarian); PCR < 0.8 = more calls.\n"
            "- IV Percentile: current IV vs. historical range. High IV = options are expensive."
        ),
    },
    # =========================================================================
    # ENERGY
    # =========================================================================
    {
        "slug": "energy-crude-oil",
        "title": "Crude Oil — WTI & Brent",
        "category": "Energy",
        "tags": ["crude oil", "wti", "brent", "petroleum", "opec"],
        "body": (
            "Crude oil is the world's most actively traded commodity. Two major benchmarks:\n\n"
            "WTI (West Texas Intermediate): Traded on NYMEX (CME Group). Light, sweet crude. "
            "Delivery point is Cushing, Oklahoma. Symbol: CL=F.\n\n"
            "Brent Crude: Traded on ICE. Benchmark for ~80% of global oil pricing. "
            "Sourced from the North Sea. Symbol: BZ=F.\n\n"
            "Price drivers: OPEC+ production decisions, US shale output, global demand "
            "(China, India), geopolitical tensions, US Strategic Petroleum Reserve, and "
            "USD strength (oil is dollar-denominated).\n\n"
            "Contract specs: CL=F is 1,000 barrels per contract. Micro crude (MCL=F) is 100 barrels."
        ),
    },
    {
        "slug": "energy-natural-gas",
        "title": "Natural Gas & LNG",
        "category": "Energy",
        "tags": ["natural gas", "henry hub", "lng", "lpg", "heating"],
        "body": (
            "Natural gas trades on NYMEX with the Henry Hub benchmark (NG=F). Prices are in "
            "USD per MMBtu (million British thermal units).\n\n"
            "LNG (Liquefied Natural Gas) is natural gas cooled to -162°C for shipping. "
            "Key exporters: Qatar, Australia, US. Key importers: Japan, South Korea, China, India.\n\n"
            "LPG (Liquefied Petroleum Gas) is a byproduct of oil refining — propane and butane. "
            "Used for cooking (India's Ujjwala scheme), heating, and petrochemical feedstock.\n\n"
            "Seasonality: gas prices spike in winter (heating demand) and summer (cooling/power). "
            "Storage reports from EIA (US) and weather forecasts are major catalysts."
        ),
    },
    {
        "slug": "energy-refined-products",
        "title": "Refined Products — Gasoline, Heating Oil",
        "category": "Energy",
        "tags": ["gasoline", "rbob", "heating oil", "diesel", "refining"],
        "body": (
            "Key refined petroleum products traded as futures:\n\n"
            "RBOB Gasoline (RB=F): 'Reformulated Blendstock for Oxygenate Blending' — "
            "the benchmark for US gasoline. Trades on NYMEX. Seasonal peak in summer driving season.\n\n"
            "Heating Oil (HO=F): Proxy for diesel and jet fuel. Trades on NYMEX. "
            "Winter demand spike. Closely correlated with Brent crude.\n\n"
            "Crack Spread: The margin between crude oil and refined products. "
            "3-2-1 crack = 3 barrels crude → 2 gasoline + 1 heating oil. "
            "Refiners hedge with crack spread trades."
        ),
    },
    {
        "slug": "energy-etfs",
        "title": "Energy ETFs & Funds",
        "category": "Energy",
        "tags": ["xle", "uso", "ung", "energy sector", "etf"],
        "body": (
            "Popular energy ETFs for investment exposure without futures:\n\n"
            "- XLE (Energy Select Sector SPDR): Top US energy stocks (Exxon, Chevron, etc.).\n"
            "- XOP (S&P Oil & Gas Exploration ETF): Upstream companies.\n"
            "- USO (US Oil Fund): Tracks WTI via futures — subject to contango drag.\n"
            "- UNG (US Natural Gas Fund): Tracks Henry Hub futures.\n"
            "- BOIL (ProShares Ultra Bloomberg Natural Gas): 2x leveraged daily — for short-term trading only.\n\n"
            "Contango warning: Commodity ETFs that hold futures (USO, UNG) lose value when rolling "
            "from expiring contracts into more expensive next-month contracts. Long-term holding "
            "of these products underperforms spot prices."
        ),
    },
    # =========================================================================
    # COMMODITIES
    # =========================================================================
    {
        "slug": "commodities-precious-metals",
        "title": "Precious Metals — Gold, Silver, Platinum, Palladium",
        "category": "Commodities",
        "tags": ["gold", "silver", "platinum", "palladium", "precious metal", "safe haven"],
        "body": (
            "Precious metals serve as stores of value, industrial inputs, and portfolio diversifiers.\n\n"
            "Gold (GC=F): The ultimate safe haven. Priced in USD/troy ounce. Driven by real interest "
            "rates, USD strength, central bank buying, and geopolitical fear. India is the world's "
            "second-largest consumer (jewellery + investment).\n\n"
            "Silver (SI=F): Dual role — monetary metal and industrial input (solar panels, electronics). "
            "More volatile than gold. Gold-to-silver ratio is a mean-reverting indicator (long-term avg ~65).\n\n"
            "Platinum (PL=F): Used in auto catalytic converters (diesel), jewellery, and hydrogen fuel cells.\n\n"
            "Palladium (PA=F): Critical for gasoline catalytic converters. Russia and South Africa produce ~80%."
        ),
    },
    {
        "slug": "commodities-base-metals",
        "title": "Base Metals — Copper, Aluminium, Zinc, Nickel",
        "category": "Commodities",
        "tags": ["copper", "aluminium", "zinc", "nickel", "base metal", "industrial"],
        "body": (
            "Base metals are industrial inputs traded primarily on the London Metal Exchange (LME) "
            "and COMEX.\n\n"
            "Copper (HG=F): 'Dr. Copper' — a leading economic indicator. Used in construction, "
            "electronics, and EVs. A single EV uses 4x more copper than an ICE vehicle.\n\n"
            "Aluminium (ALI=F): Lightest structural metal. Used in packaging, aerospace, and EVs. "
            "Energy-intensive smelting makes it sensitive to power costs.\n\n"
            "Zinc (ZN=F): Primarily for galvanising steel. China produces ~35% of global supply.\n\n"
            "Nickel (NI=F): Critical for EV battery cathodes (NMC chemistry). Indonesian supply "
            "surge has reshaped the market. Stainless steel is still the largest end-use."
        ),
    },
    {
        "slug": "commodities-agriculture",
        "title": "Agricultural Commodities",
        "category": "Commodities",
        "tags": ["wheat", "corn", "soybeans", "coffee", "sugar", "cotton", "agriculture"],
        "body": (
            "Agricultural futures trade on CME Group (CBOT) and ICE.\n\n"
            "Grains: Wheat (ZW=F), Corn (ZC=F), Soybeans (ZS=F). Driven by weather, "
            "USDA crop reports, and global trade flows. US Midwest is the breadbasket.\n\n"
            "Softs: Coffee (KC=F — Arabica), Sugar (SB=F — raw #11), Cocoa (CC=F), "
            "Cotton (CT=F). Brazil is the largest coffee and sugar producer.\n\n"
            "Livestock: Live Cattle (LE=F), Lean Hogs (HE=F). Driven by feed costs, "
            "herd cycles, and export demand (China is a major pork importer).\n\n"
            "India context: India is a major producer and consumer of wheat, rice, sugar, "
            "and cotton. MCX (Multi Commodity Exchange) offers domestic commodity futures."
        ),
    },
    # =========================================================================
    # METALS BY CITY (India)
    # =========================================================================
    {
        "slug": "india-gold-silver-prices",
        "title": "Gold & Silver Prices in India by City",
        "category": "India Metals",
        "tags": ["gold price", "silver price", "india", "city wise", "22k", "24k", "jewellery"],
        "body": (
            "Gold and silver prices in India vary by city due to local taxes, transportation costs, "
            "jeweller association markups, and demand patterns.\n\n"
            "How prices are formed:\n"
            "1. International gold/silver price in USD per troy ounce (31.1035 grams).\n"
            "2. Convert to INR using the prevailing USD/INR exchange rate.\n"
            "3. Add import duty (currently 6% basic + 2.5% agri cess = ~9% effective).\n"
            "4. Add GST at 3% on (price + duty).\n"
            "5. Add city-specific premium (transport, jeweller margin, local demand).\n\n"
            "Purity: 24K (99.9% pure, investment bars), 22K (91.6% pure, jewellery standard in India), "
            "18K (75% pure, fashion jewellery).\n\n"
            "Cities like Chennai and Kochi tend to have higher premiums due to strong jewellery "
            "demand. Delhi and Mumbai are closer to import hubs and may have lower premiums."
        ),
    },
    # =========================================================================
    # FOREX
    # =========================================================================
    {
        "slug": "forex-overview",
        "title": "Forex Markets — Overview",
        "category": "Forex",
        "tags": ["forex", "currency", "fx", "exchange rate", "pip"],
        "body": (
            "The foreign exchange market is the largest financial market, with ~$7.5 trillion "
            "daily volume. It operates 24 hours across Sydney, Tokyo, London, and New York sessions.\n\n"
            "Key concepts:\n"
            "- Pip: smallest price move, typically 0.0001 for most pairs (0.01 for JPY pairs).\n"
            "- Lot: standard lot = 100,000 units, mini = 10,000, micro = 1,000.\n"
            "- Spread: difference between bid and ask. Major pairs have tightest spreads.\n"
            "- Leverage: retail forex offers 20:1 to 50:1 (varies by jurisdiction).\n\n"
            "Major pairs: EUR/USD, GBP/USD, USD/JPY, USD/CHF, AUD/USD, USD/CAD, NZD/USD.\n"
            "INR crosses: USD/INR, EUR/INR, GBP/INR, JPY/INR — traded on NSE and BSE."
        ),
    },
    {
        "slug": "forex-usdinr",
        "title": "USD/INR — The Rupee Dollar Pair",
        "category": "Forex",
        "tags": ["usdinr", "rupee", "rbi", "forex reserves", "india"],
        "body": (
            "USD/INR is the most traded INR pair. RBI actively manages the exchange rate through "
            "intervention in spot and forward markets.\n\n"
            "Drivers: Current account deficit, FII equity/debt flows, oil import bill "
            "(India imports ~85% of its crude), US Federal Reserve policy, and RBI forex reserves "
            "(~$600B+).\n\n"
            "Trading: NSE offers USD/INR futures and options with monthly and weekly expiries. "
            "Lot size is $1,000. Margins are low (~2-3% of contract value).\n\n"
            "For investors in US stocks, USD/INR movement directly impacts returns. "
            "A depreciating rupee adds to US equity returns for Indian investors and vice versa."
        ),
    },
    {
        "slug": "forex-dxy",
        "title": "US Dollar Index (DXY)",
        "category": "Forex",
        "tags": ["dxy", "dollar index", "reserve currency", "fed"],
        "body": (
            "The DXY (US Dollar Index) measures the USD against a basket of 6 currencies: "
            "EUR (57.6%), JPY (13.6%), GBP (11.9%), CAD (9.1%), SEK (4.2%), CHF (3.6%).\n\n"
            "DXY rising = USD strengthening = typically bearish for commodities (priced in USD), "
            "emerging market equities, and currencies like INR.\n\n"
            "DXY > 100 is considered strong dollar territory. "
            "Key driver: US interest rate differential vs other developed economies."
        ),
    },
    # =========================================================================
    # US EQUITY
    # =========================================================================
    {
        "slug": "us-equity-overview",
        "title": "US Stock Market — Overview",
        "category": "US Equity",
        "tags": ["us stocks", "nyse", "nasdaq", "sp500", "dow"],
        "body": (
            "The US has the world's largest stock market (~$50 trillion+ market cap). "
            "Major exchanges: NYSE and NASDAQ.\n\n"
            "Key indices:\n"
            "- S&P 500 (^GSPC): 500 largest US companies, market-cap weighted. The global benchmark.\n"
            "- NASDAQ Composite (^IXIC): Tech-heavy, ~3,000 stocks.\n"
            "- Dow Jones (^DJI): 30 blue-chip stocks, price-weighted.\n"
            "- Russell 2000: Small-cap benchmark.\n\n"
            "Trading hours: 9:30 AM - 4:00 PM ET. Pre-market: 4:00 AM - 9:30 AM. "
            "After-hours: 4:00 PM - 8:00 PM.\n\n"
            "Settlement: T+1 since May 2024."
        ),
    },
    {
        "slug": "us-equity-for-indians",
        "title": "Investing in US Stocks from India",
        "category": "US Equity",
        "tags": ["us stocks from india", "lrs", "dtaa", "withholding tax"],
        "body": (
            "Indian residents can invest in US equities under the Liberalised Remittance Scheme "
            "(LRS) — up to $250,000 per financial year per person.\n\n"
            "Platforms: Vested, INDmoney, Groww (US), Interactive Brokers (IBKR), Charles Schwab.\n\n"
            "Tax implications:\n"
            "- Dividends: US withholds 25% (with W-8BEN). India taxes the gross dividend at slab rate. "
            "Claim Foreign Tax Credit (FTC) via Form 67 filed BEFORE your ITR.\n"
            "- Capital gains: No US tax for Indian residents (DTAA benefit). India taxes: "
            "STCG at 20% (<24 months), LTCG at 12.5% (>24 months) for listed foreign equity.\n"
            "- Currency: INR depreciation adds to returns and vice versa."
        ),
    },
    # =========================================================================
    # US OPTIONS
    # =========================================================================
    {
        "slug": "us-options-overview",
        "title": "US Options Market — Overview",
        "category": "US Options",
        "tags": ["us options", "spy", "qqq", "calls", "puts", "cboe"],
        "body": (
            "The US options market is the most liquid in the world. Most equity options are "
            "American style (can exercise anytime). Index options (SPX) are European and cash-settled.\n\n"
            "Standard contract = 100 shares of underlying.\n\n"
            "Popular underlyings: SPY (S&P 500 ETF), QQQ (NASDAQ 100), IWM (Russell 2000), "
            "and mega-cap singles (AAPL, TSLA, NVDA, AMZN, META).\n\n"
            "0DTE (zero days to expiry) options have exploded in popularity — SPX/SPY now have "
            "daily expirations every trading day.\n\n"
            "VIX: The CBOE Volatility Index measures implied volatility of S&P 500 options. "
            "VIX > 20 = elevated fear. VIX > 30 = market stress. VIX > 40 = crisis."
        ),
    },
    # =========================================================================
    # CRYPTO
    # =========================================================================
    {
        "slug": "crypto-overview",
        "title": "Cryptocurrency — Overview",
        "category": "Crypto",
        "tags": ["crypto", "bitcoin", "ethereum", "blockchain", "defi"],
        "body": (
            "Cryptocurrencies are digital assets on blockchain networks. The market trades 24/7/365.\n\n"
            "Major categories:\n"
            "- Layer 1: Bitcoin (BTC), Ethereum (ETH), Solana (SOL), Cardano (ADA).\n"
            "- Layer 2: Polygon (MATIC), Arbitrum, Optimism — scale Layer 1 chains.\n"
            "- DeFi: Uniswap (UNI), Aave, Compound — decentralised finance protocols.\n"
            "- Meme: Dogecoin (DOGE), Shiba Inu (SHIB) — community-driven tokens.\n"
            "- Stablecoins: USDT, USDC, DAI — pegged to USD.\n\n"
            "India taxation: 30% flat tax on crypto gains (no exemption, no loss offset, "
            "no deduction except cost of acquisition). 1% TDS on transfers above Rs 10,000."
        ),
    },
    {
        "slug": "crypto-bitcoin",
        "title": "Bitcoin (BTC)",
        "category": "Crypto",
        "tags": ["bitcoin", "btc", "satoshi", "halving", "digital gold"],
        "body": (
            "Bitcoin is the first and largest cryptocurrency by market cap. Created in 2009 by "
            "the pseudonymous Satoshi Nakamoto.\n\n"
            "Key properties:\n"
            "- Fixed supply: 21 million BTC maximum. ~19.7 million already mined.\n"
            "- Halving: Mining reward halves every ~4 years. Next halving ~2028. "
            "Historically a bullish catalyst.\n"
            "- Proof of Work: Energy-intensive mining secures the network.\n\n"
            "Bitcoin ETFs (US): Spot Bitcoin ETFs were approved in January 2024. "
            "IBIT (BlackRock), FBTC (Fidelity) are the largest.\n\n"
            "Correlation: Bitcoin has shifted from 'risk-on tech proxy' to partial 'digital gold' "
            "narrative, though correlations remain unstable."
        ),
    },
    # =========================================================================
    # US BONDS / TREASURIES
    # =========================================================================
    {
        "slug": "us-bonds-overview",
        "title": "US Treasury & Bond Market — Overview",
        "category": "US Bonds",
        "tags": ["treasury", "yield", "bonds", "fed", "interest rate"],
        "body": (
            "US Treasuries are considered the global risk-free benchmark. "
            "The US bond market is ~$50 trillion.\n\n"
            "Maturity spectrum:\n"
            "- T-Bills: 4, 8, 13, 17, 26, 52 weeks. Zero-coupon, sold at discount.\n"
            "- T-Notes: 2, 3, 5, 7, 10 years. Semi-annual coupon.\n"
            "- T-Bonds: 20, 30 years. Semi-annual coupon.\n"
            "- TIPS: Inflation-protected, principal adjusts with CPI.\n\n"
            "Yield curve: Normal (upward sloping) = healthy economy. "
            "Inverted (short yields > long yields) = recession signal. "
            "The 10Y-2Y spread is the most watched inversion indicator.\n\n"
            "Bond prices move inversely to yields. Duration measures price sensitivity to rate changes."
        ),
    },
    {
        "slug": "us-bonds-etfs",
        "title": "Bond ETFs — TLT, BND, AGG, HYG",
        "category": "US Bonds",
        "tags": ["tlt", "bnd", "agg", "hyg", "bond etf", "fixed income"],
        "body": (
            "Bond ETFs provide instant diversified access to fixed income:\n\n"
            "- TLT (iShares 20+ Year Treasury): Long duration, high rate sensitivity. "
            "Moves ~15-18% for every 1% change in long-term yields.\n"
            "- IEF (7-10 Year Treasury): Moderate duration.\n"
            "- SHY (1-3 Year Treasury): Short duration, low volatility.\n"
            "- BND / AGG: Total US bond market — investment grade govt + corporate.\n"
            "- HYG: High yield ('junk') corporate bonds. Higher yield, higher credit risk.\n"
            "- LQD: Investment grade corporate bonds.\n"
            "- EMB: Emerging market USD-denominated sovereign bonds.\n\n"
            "For Indian investors, US bond ETF dividends face 25% US withholding + India slab tax."
        ),
    },
    # =========================================================================
    # US FUTURES
    # =========================================================================
    {
        "slug": "us-futures-overview",
        "title": "US Futures Market — Overview",
        "category": "US Futures",
        "tags": ["futures", "es", "nq", "ym", "cme", "margin"],
        "body": (
            "US futures trade on CME Group (CME, CBOT, NYMEX, COMEX). They trade nearly 24 hours "
            "(Sunday 6 PM - Friday 5 PM ET with a 1-hour daily break).\n\n"
            "Equity index futures:\n"
            "- ES (E-mini S&P 500): $50 × index, the most liquid futures contract globally.\n"
            "- NQ (E-mini NASDAQ 100): $20 × index, tech-heavy.\n"
            "- YM (E-mini Dow): $5 × index.\n"
            "- RTY (E-mini Russell 2000): $50 × index, small cap.\n"
            "- Micro contracts: MES, MNQ, MYM, M2K — 1/10th the size.\n\n"
            "Futures are used for hedging, speculation, and as pre-market indicators for cash equities. "
            "They are margined products — you only need 3-10% of contract value as initial margin."
        ),
    },
    # =========================================================================
    # REAL ESTATE
    # =========================================================================
    {
        "slug": "real-estate-reits",
        "title": "REITs — Real Estate Investment Trusts",
        "category": "Real Estate",
        "tags": ["reit", "real estate", "vnq", "dividend", "property"],
        "body": (
            "REITs own and operate income-producing real estate. By law, they must distribute "
            "90%+ of taxable income as dividends, resulting in higher yields than most equities.\n\n"
            "US REIT categories:\n"
            "- Data Centers: Equinix (EQIX), Digital Realty (DLR).\n"
            "- Cell Towers: American Tower (AMT), Crown Castle (CCI).\n"
            "- Logistics: Prologis (PLD) — e-commerce warehouse boom.\n"
            "- Retail: Simon Property Group (SPG) — malls.\n"
            "- Storage: Public Storage (PSA).\n"
            "- Healthcare: Welltower (WELL).\n"
            "- Net Lease: Realty Income (O) — monthly dividends.\n\n"
            "VNQ (Vanguard Real Estate ETF) is the broadest US REIT ETF."
        ),
    },
    {
        "slug": "india-reits",
        "title": "Indian REITs — Embassy, Mindspace, Brookfield",
        "category": "Real Estate",
        "tags": ["india reit", "embassy", "mindspace", "brookfield", "commercial real estate"],
        "body": (
            "India has three listed REITs, all focused on office/commercial real estate:\n\n"
            "- Embassy Office Parks REIT (EMBASSY.NS): India's first and largest REIT. "
            "~45 million sq ft across Bangalore, Mumbai, Pune, Chennai. Anchor: Embassy + Blackstone.\n\n"
            "- Mindspace Business Parks REIT (MINDSPACE.NS): ~33 million sq ft. "
            "Strong Hyderabad presence. K Raheja Corp + Blackstone.\n\n"
            "- Brookfield India REIT (BROOKFIELD.NS): ~19 million sq ft. "
            "Mumbai, Gurugram, Noida, Kolkata.\n\n"
            "India REIT taxation: Rental income distributed by REIT is taxable at slab rate. "
            "Interest income component is also at slab rate. "
            "Capital gains on REIT units: STCG 15% (<36 months), LTCG 10% (>36 months, above Rs 1 lakh)."
        ),
    },
    # =========================================================================
    # BROKER COSTS & TRADING CONCEPTS
    # =========================================================================
    {
        "slug": "broker-costs-india",
        "title": "Brokerage & Trading Costs in India",
        "category": "Trading Concepts",
        "tags": ["brokerage", "zerodha", "upstox", "charges", "dp charges"],
        "body": (
            "A trade in India incurs multiple charges beyond brokerage:\n\n"
            "1. Brokerage: Discount brokers (Zerodha, Upstox, Angel One) charge Rs 0 for delivery, "
            "Rs 20/order for intraday/F&O. Full-service brokers charge 0.1-0.5% of turnover.\n\n"
            "2. STT (Securities Transaction Tax): Varies by segment.\n"
            "3. Exchange Transaction Charges: ~0.00297% of turnover.\n"
            "4. GST: 18% on (brokerage + exchange charges + SEBI charges).\n"
            "5. SEBI Turnover Fee: Rs 10 per crore.\n"
            "6. Stamp Duty: 0.015% on buy (delivery), varies by state for others.\n"
            "7. DP Charges: Rs 13-20 per scrip per sell (delivery only).\n\n"
            "FinanceLab's cost calculator computes all of these across Zerodha, Upstox, "
            "HDFC Sky, Angel One, and IBKR."
        ),
    },
    {
        "slug": "tax-stcg-ltcg-india",
        "title": "Capital Gains Tax — STCG vs LTCG (India)",
        "category": "Trading Concepts",
        "tags": ["stcg", "ltcg", "capital gains", "tax", "india"],
        "body": (
            "India differentiates between Short Term Capital Gains (STCG) and Long Term "
            "Capital Gains (LTCG) based on holding period.\n\n"
            "Listed Equity & Equity MF (FY 2024-25):\n"
            "- STCG (<12 months): 20%\n"
            "- LTCG (>12 months): 12.5% above Rs 1.25 lakh annual exemption\n"
            "- Grandfathering: For shares held before Jan 31, 2018, cost is the higher of "
            "actual cost or Jan 31, 2018 FMV.\n\n"
            "F&O: Not capital gains — classified as business income at slab rate.\n"
            "Debt MF (post April 2023): All gains at slab rate regardless of holding period.\n"
            "Crypto: 30% flat, no exemption, no loss offset against other income.\n\n"
            "FinanceLab's 'when to sell' tool helps you time the STCG-to-LTCG transition."
        ),
    },
    {
        "slug": "fii-dii-flows",
        "title": "FII/DII Flows — Why They Matter",
        "category": "Trading Concepts",
        "tags": ["fii", "dii", "foreign institutional", "domestic institutional", "flows"],
        "body": (
            "FII (Foreign Institutional Investor) and DII (Domestic Institutional Investor) "
            "flows are the biggest directional drivers of Indian markets.\n\n"
            "FIIs include hedge funds, sovereign wealth funds, pension funds, and foreign mutual "
            "funds. Their daily net buy/sell in equity and debt is published by NSDL and NSE.\n\n"
            "DIIs include Indian mutual funds, insurance companies (LIC, HDFC Life), and pension "
            "funds (EPFO, NPS). DIIs often act as counterweight to FII selling.\n\n"
            "Why it matters:\n"
            "- FII net selling > Rs 2,000 Cr/day for sustained periods = significant market pressure.\n"
            "- DII buying during FII selloffs provides support but may not fully offset.\n"
            "- FII flows are correlated with USD strength, US yields, and EM risk appetite.\n\n"
            "FinanceLab weights FII/DII flow as the strongest sentiment signal."
        ),
    },
    {
        "slug": "sentiment-analysis",
        "title": "Sentiment Analysis for Markets",
        "category": "Trading Concepts",
        "tags": ["sentiment", "finbert", "news", "fear greed", "vix"],
        "body": (
            "Market sentiment combines quantitative flow data with qualitative news analysis.\n\n"
            "FinanceLab's composite sentiment score uses:\n"
            "1. FII/DII flow (55% weight): Actual money moving in/out of Indian markets.\n"
            "2. News keyword analysis (35%): Positive/negative keywords from Finnhub headlines.\n"
            "3. FinBERT (10%, optional): NLP model fine-tuned for financial sentiment.\n\n"
            "Other sentiment indicators:\n"
            "- VIX (^VIX): Market fear gauge. VIX > 20 = caution.\n"
            "- India VIX: Similar concept for NIFTY options. India VIX > 15 = elevated.\n"
            "- Fear & Greed Index: CNN's composite sentiment indicator.\n"
            "- Put/Call Ratio: PCR > 1 = more puts = contrarian bullish."
        ),
    },
]

# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------


def all_articles() -> list[dict[str, Any]]:
    return ARTICLES


def all_categories() -> list[str]:
    seen: dict[str, None] = {}
    for a in ARTICLES:
        seen.setdefault(a["category"], None)
    return list(seen.keys())


def articles_by_category(category: str) -> list[dict[str, Any]]:
    return [a for a in ARTICLES if a["category"] == category]


def article_by_slug(slug: str) -> dict[str, Any] | None:
    for a in ARTICLES:
        if a["slug"] == slug:
            return a
    return None


def search_articles(query: str) -> list[dict[str, Any]]:
    q = query.lower()
    results: list[dict[str, Any]] = []
    for a in ARTICLES:
        if (
            q in a["title"].lower()
            or q in a["body"].lower()
            or any(q in t for t in a["tags"])
        ):
            results.append(a)
    return results[:30]

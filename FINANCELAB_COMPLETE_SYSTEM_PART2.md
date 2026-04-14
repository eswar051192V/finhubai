# FinanceLab — Complete System Reference · Part 2
## Sections 31–55 · Advanced Intelligence · Alternative Data · ML · Apple Integration

> **Inject alongside Part 1** into Ollama RAG pipeline
> **Depends on:** FINANCELAB_COMPLETE_SYSTEM.md (Part 1)
> **Covers:** Alternative data · Factor models · ML layer · Apple ecosystem · Corporate actions · Credit analysis · Geopolitical risk · Short squeeze · Arbitrage · Natural language queries · Content tools · Tax form generation · Family office · Performance attribution · Edge CDN

---

# TABLE OF CONTENTS — PART 2

| Section | Title |
|---------|-------|
| 31 | Alternative Data Engine |
| 32 | Volatility Surface and Term Structure |
| 33 | Market Microstructure — Order Book Intelligence |
| 34 | Factor Model — Systematic Alpha |
| 35 | Corporate Action Intelligence |
| 36 | Credit Analysis Engine |
| 37 | Geopolitical Risk Engine |
| 38 | Natural Language Query Interface |
| 39 | Sector Rotation Model |
| 40 | Dividend Intelligence and Income Tracking |
| 41 | Insider Cluster Analysis |
| 42 | Short Squeeze Detector |
| 43 | Arbitrage Scanner |
| 44 | Machine Learning Layer |
| 45 | Apple Ecosystem Integration |
| 46 | Tax Form Generation |
| 47 | Insurance and Liability Integration |
| 48 | Competitive Intelligence — Company Level |
| 49 | Family Office and Portfolio Consolidation |
| 50 | Trade Journaling With Emotion |
| 51 | Network of Early Signals — Leading Indicators |
| 52 | Risk-Adjusted Performance Attribution |
| 53 | Content Creation Tools — Go To Market |
| 54 | Regulatory Filing Tracker |
| 55 | Edge CDN and Infrastructure Optimization |

---

# SECTION 31 — ALTERNATIVE DATA ENGINE

## 31.1 Why Alternative Data Matters

```
Traditional data (price, volume, fundamentals)
is available to everyone. The edge comes from
data that predicts fundamentals BEFORE they
are officially reported.

Alternative data leads official data by:
  → Satellite imagery:   1-4 weeks
  → Web traffic:         2-4 weeks
  → Job postings:        4-8 weeks
  → Google Trends:       2-6 weeks
  → Import/export:       1-2 months
  → Credit card spend:   1-2 months
  → App store ratings:   2-4 weeks
  → Power consumption:   2-4 weeks

All of the above: FREE or very low cost.
```

## 31.2 Google Trends Integration

```python
pip install pytrends

from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime, timedelta

class GoogleTrendsEngine:

    def __init__(self):
        self.pytrends = TrendReq(
            hl='en-US',
            tz=330,          # IST offset
            timeout=(10, 25)
        )

    def get_brand_interest(self, company_name, ticker, period='today 3-m'):
        """
        Track search interest for a brand.
        Rising interest = rising consumer demand.
        Works best for B2C companies.
        """
        self.pytrends.build_payload(
            [company_name],
            cat=0,
            timeframe=period,
            geo='IN'         # India
        )
        data = self.pytrends.interest_over_time()

        if data.empty:
            return None

        # Calculate trend
        recent = data[company_name].tail(4).mean()   # Last 4 weeks
        prior  = data[company_name].head(4).mean()   # First 4 weeks
        trend  = (recent - prior) / prior * 100

        # Compare to revenue trend
        revenue_growth = get_revenue_growth(ticker)

        return {
            'ticker':           ticker,
            'brand':            company_name,
            'current_interest': recent,
            'trend_pct':        round(trend, 1),
            'revenue_growth':   revenue_growth,
            'lead_signal':      'POSITIVE' if trend > 10 else 'NEGATIVE' if trend < -10 else 'NEUTRAL',
            'divergence':       'BULLISH' if trend > 10 and revenue_growth < 5 else
                                'BEARISH' if trend < -10 and revenue_growth > 15 else 'ALIGNED'
        }

    def compare_competitors(self, companies, geo='IN'):
        """
        Compare brand interest between competitors.
        Who is gaining share before revenue data shows it.
        """
        self.pytrends.build_payload(
            companies[:5],  # Max 5 keywords
            timeframe='today 12-m',
            geo=geo
        )
        data = self.pytrends.interest_over_time()

        # Recent 30-day average vs prior 90-day average
        results = {}
        for company in companies[:5]:
            if company in data.columns:
                recent = data[company].tail(4).mean()
                prior  = data[company].iloc[:-4].mean()
                results[company] = {
                    'current':    round(recent, 1),
                    'trend':      round((recent - prior) / prior * 100, 1),
                    'data':       data[company].tolist()
                }

        # Identify rising and falling competitors
        ranked = sorted(results.items(), key=lambda x: x[1]['trend'], reverse=True)

        return {
            'winner':   ranked[0][0] if ranked else None,
            'loser':    ranked[-1][0] if ranked else None,
            'details':  results
        }

    def macro_consumer_signal(self):
        """
        Aggregate consumer demand signal for India.
        """
        consumer_keywords = [
            'buy mobile phone',
            'car loan',
            'home loan apply',
            'credit card apply',
            'air ticket booking'
        ]

        self.pytrends.build_payload(
            consumer_keywords,
            timeframe='today 3-m',
            geo='IN'
        )
        data = self.pytrends.interest_over_time()

        # Composite consumer demand index
        composite = data[consumer_keywords].mean(axis=1)
        recent    = composite.tail(4).mean()
        prior     = composite.head(4).mean()
        change    = (recent - prior) / prior * 100

        return {
            'composite_index':  round(recent, 1),
            'trend_pct':        round(change, 1),
            'signal':           'STRONG_DEMAND'  if change > 15 else
                                'RISING_DEMAND'  if change > 5  else
                                'FALLING_DEMAND' if change < -5 else
                                'STABLE_DEMAND',
            'implication':      'Positive for FMCG, retail, banking, auto'
                                if change > 5 else
                                'Negative for consumer-facing sectors'
        }

# Tickers that work well with Google Trends
TRENDS_WATCHLIST = {
    'ZOMATO.NS':        'Zomato food delivery',
    'NAUKRI.NS':        'Naukri job search',
    'IRCTC.NS':         'IRCTC train booking',
    'INDIGO.NS':        'IndiGo flight',
    'MARICO.NS':        'Marico hair oil',
    'TITAN.NS':         'Titan watches',
    'TATACONSUM.NS':    'Tata Tea',
    'JUBLFOOD.NS':      'Dominos pizza',
    'DMART.NS':         'DMart supermarket',
    'AAPL':             'Apple iPhone',
    'AMZN':             'Amazon shopping',
    'NFLX':             'Netflix',
    'UBER':             'Uber ride',
}
```

## 31.3 Job Postings Intelligence

```python
import requests
from bs4 import BeautifulSoup
import time

class JobPostingsEngine:
    """
    Rising job postings = company growing
    Falling job postings = slowdown before revenue shows it
    """

    def get_linkedin_jobs_count(self, company_name, ticker):
        """
        Scrape LinkedIn job count for a company.
        Proxy for growth and strategic direction.
        """
        # Use LinkedIn job search (no login for count)
        url = f"https://www.linkedin.com/jobs/search/?keywords={company_name.replace(' ', '+')}&f_C="
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find job count
            count_elem = soup.find('span', {'class': 'results-context-header__job-count'})
            if count_elem:
                count_text = count_elem.text.strip().replace(',', '')
                count = int(''.join(filter(str.isdigit, count_text)))
            else:
                count = 0

            return {
                'ticker':       ticker,
                'company':      company_name,
                'job_count':    count,
                'scraped_at':   datetime.now().isoformat()
            }

        except Exception as e:
            return {'ticker': ticker, 'error': str(e)}

    def track_hiring_skills(self, company_name):
        """
        What skills is the company hiring for?
        This reveals strategic direction before announcements.
        """
        # Naukri.com scraping (India)
        url = f"https://www.naukri.com/{company_name.lower().replace(' ', '-')}-jobs"
        headers = {'User-Agent': 'Mozilla/5.0'}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract skills from job descriptions
            skills = []
            for tag in soup.find_all('li', {'class': 'tag'}):
                skills.append(tag.text.strip().lower())

            # Cluster by type
            ai_ml_skills = [s for s in skills if any(
                k in s for k in ['machine learning', 'ai', 'deep learning', 'llm', 'genai']
            )]
            cloud_skills = [s for s in skills if any(
                k in s for k in ['aws', 'azure', 'gcp', 'cloud']
            )]
            data_skills = [s for s in skills if any(
                k in s for k in ['data', 'analytics', 'python', 'sql']
            )]

            return {
                'company':          company_name,
                'total_skills':     len(skills),
                'ai_ml_focus':      len(ai_ml_skills),
                'cloud_focus':      len(cloud_skills),
                'data_focus':       len(data_skills),
                'strategic_signal': 'HEAVY AI INVESTMENT' if len(ai_ml_skills) > 20
                                    else 'CLOUD MIGRATION' if len(cloud_skills) > 15
                                    else 'DATA-DRIVEN' if len(data_skills) > 25
                                    else 'TRADITIONAL'
            }

        except Exception as e:
            return {'error': str(e)}

    def layoff_detector(self, company_name):
        """
        Detect layoff signals before announcement.
        Sources: layoffs.fyi, LinkedIn activity
        """
        # Check layoffs.fyi (free API)
        url = f"https://layoffs.fyi/search/?q={company_name}"
        # Parse and return recent layoff activity
        pass

    def compare_hiring_trend(self, ticker, months_back=6):
        """
        Compare current hiring to 6 months ago.
        Hiring more = bullish signal
        Hiring less = bearish signal
        """
        current = self.get_current_job_count(ticker)
        historical = self.get_historical_job_count(ticker, months_back)

        if historical and current:
            change = (current - historical) / historical * 100
            return {
                'ticker':           ticker,
                'current_jobs':     current,
                'jobs_6mo_ago':     historical,
                'change_pct':       round(change, 1),
                'signal':           'GROWTH' if change > 20
                                    else 'SHRINKING' if change < -20
                                    else 'STABLE'
            }
```

## 31.4 Import/Export Intelligence (India)

```python
class ZaubaDataEngine:
    """
    Zauba.com tracks India's actual import/export shipments.
    Real trade data before official government statistics.
    """

    BASE_URL = "https://www.zauba.com"

    def get_company_imports(self, company_name):
        """
        Track what a company is importing.
        Auto company importing steel = production signal
        Pharma importing APIs = manufacturing ramp-up
        """
        url = f"{self.BASE_URL}/import-{company_name.lower().replace(' ', '-')}.html"
        headers = {'User-Agent': 'Mozilla/5.0'}

        try:
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Parse shipment data
            shipments = []
            for row in soup.find_all('tr', {'class': 'shipment'}):
                cols = row.find_all('td')
                if len(cols) >= 5:
                    shipments.append({
                        'date':         cols[0].text.strip(),
                        'item':         cols[1].text.strip(),
                        'quantity':     cols[2].text.strip(),
                        'value_usd':    cols[3].text.strip(),
                        'country':      cols[4].text.strip(),
                    })

            return {
                'company':      company_name,
                'shipments':    shipments[:50],   # Last 50 shipments
                'total_value':  sum_shipment_values(shipments),
                'trend':        calculate_import_trend(shipments)
            }

        except Exception as e:
            return {'error': str(e)}

    def sector_trade_flow(self, product_category, direction='import'):
        """
        Track industry-wide trade flows.
        Rising semiconductor imports = tech expansion
        Falling crude imports = economic slowdown
        """
        pass
```

## 31.5 App Store Intelligence

```python
class AppStoreEngine:
    """
    App ratings and download trends predict
    consumer product quality and growth.
    """

    def get_google_play_rating(self, package_name):
        """
        package_name: e.g., 'com.zomato.ordering'
        """
        url = f"https://play.google.com/store/apps/details?id={package_name}"
        headers = {'User-Agent': 'Mozilla/5.0'}

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract rating
        rating_elem = soup.find('div', {'itemprop': 'starRating'})
        rating = float(rating_elem.find('meta')['content']) if rating_elem else None

        # Extract review count
        count_elem = soup.find('span', {'class': 'AYi5wd'})
        count = count_elem.text if count_elem else None

        return {
            'package':      package_name,
            'rating':       rating,
            'review_count': count,
            'scraped_at':   datetime.now().isoformat()
        }

    def track_rating_trend(self, ticker, package_name, historical_rating):
        """
        Compare current rating to 3 months ago.
        Declining rating = product quality issue ahead of earnings.
        """
        current = self.get_google_play_rating(package_name)

        if current['rating'] and historical_rating:
            change  = current['rating'] - historical_rating
            signal  = 'IMPROVING' if change > 0.2 else 'DECLINING' if change < -0.2 else 'STABLE'

            return {
                'ticker':           ticker,
                'current_rating':   current['rating'],
                'historical_rating': historical_rating,
                'change':           round(change, 2),
                'signal':           signal,
                'trading_implication': 'Revenue and user metrics may improve'
                                       if signal == 'IMPROVING' else
                                       'User churn risk — watch next earnings'
            }

# Key apps to track
APP_WATCHLIST = {
    'ZOMATO.NS':    'com.zomato.ordering',
    'JUBLFOOD.NS':  'com.dominos.app',
    'IRCTC.NS':     'cris.org.in.prs.ima',
    'INDIGO.NS':    'com.goindigo.app',
    'HDFC':         'com.snapwork.HDFC',
    'PAYTM':        'net.one97.paytm',
}
```

## 31.6 Alternative Data Aggregator

```python
def run_alternative_data_scan(watchlist):
    """
    Run all alternative data sources daily.
    Aggregate into alt_data score per ticker.
    """
    results = {}

    trends_engine   = GoogleTrendsEngine()
    jobs_engine     = JobPostingsEngine()
    app_engine      = AppStoreEngine()

    for ticker, company_name in watchlist.items():
        alt_signals = []

        # Google Trends
        try:
            trends = trends_engine.get_brand_interest(company_name, ticker)
            if trends:
                alt_signals.append({
                    'source':   'google_trends',
                    'signal':   trends['lead_signal'],
                    'value':    trends['trend_pct'],
                    'weight':   0.30
                })
        except Exception:
            pass

        # Job postings
        try:
            jobs = jobs_engine.compare_hiring_trend(ticker)
            if jobs:
                alt_signals.append({
                    'source':   'job_postings',
                    'signal':   jobs['signal'],
                    'value':    jobs['change_pct'],
                    'weight':   0.25
                })
        except Exception:
            pass

        # App ratings (if applicable)
        if ticker in APP_WATCHLIST:
            try:
                rating = app_engine.track_rating_trend(
                    ticker,
                    APP_WATCHLIST[ticker],
                    get_historical_rating(ticker)
                )
                if rating:
                    alt_signals.append({
                        'source':   'app_rating',
                        'signal':   rating['signal'],
                        'value':    rating['change'],
                        'weight':   0.20
                    })
            except Exception:
                pass

        # Calculate composite alt data score
        if alt_signals:
            score = calculate_alt_data_score(alt_signals)
            results[ticker] = {
                'score':    score,
                'signals':  alt_signals,
                'summary':  interpret_alt_score(score)
            }

    return results
```

---

# SECTION 32 — VOLATILITY SURFACE AND TERM STRUCTURE

## 32.1 Volatility Surface Construction

```python
import numpy as np
from scipy.interpolate import griddata
import plotly.graph_objects as go

class VolatilitySurface:
    """
    3D visualization of IV across strikes and expiries.
    Shows where market prices risk concentration.
    """

    def build_surface(self, option_chain_data):
        """
        option_chain_data: list of {strike, expiry, iv, option_type}
        """
        # Separate calls and puts
        calls = [d for d in option_chain_data if d['type'] == 'CE']

        # Extract coordinates
        strikes  = np.array([d['strike']  for d in calls])
        expiries = np.array([d['days_to_expiry'] for d in calls])
        ivs      = np.array([d['iv']      for d in calls])

        # Moneyness (strike / spot)
        spot       = get_current_spot()
        moneyness  = strikes / spot

        # Create grid for surface
        m_grid = np.linspace(moneyness.min(), moneyness.max(), 50)
        e_grid = np.linspace(expiries.min(),  expiries.max(),  20)
        mm, ee = np.meshgrid(m_grid, e_grid)

        # Interpolate IV surface
        iv_grid = griddata(
            (moneyness, expiries),
            ivs,
            (mm, ee),
            method='cubic'
        )

        return {
            'moneyness_grid':   mm,
            'expiry_grid':      ee,
            'iv_grid':          iv_grid,
            'atm_term_structure': self.atm_term_structure(option_chain_data),
            'skew':             self.calculate_skew(option_chain_data),
            'smile':            self.smile_analysis(option_chain_data)
        }

    def atm_term_structure(self, chain_data):
        """
        IV at ATM across different expiries.
        Contango: near < far (normal)
        Backwardation: near > far (stress signal)
        """
        spot        = get_current_spot()
        atm_ivs     = {}

        expiries = list(set(d['days_to_expiry'] for d in chain_data))
        expiries.sort()

        for exp in expiries:
            exp_data = [d for d in chain_data if d['days_to_expiry'] == exp]
            # Find ATM strike (closest to spot)
            atm = min(exp_data, key=lambda x: abs(x['strike'] - spot))
            atm_ivs[exp] = atm['iv']

        # Detect contango/backwardation
        ivs_sorted = [atm_ivs[e] for e in expiries]
        is_contango = ivs_sorted[0] < ivs_sorted[-1] if len(ivs_sorted) >= 2 else True

        return {
            'term_structure':   atm_ivs,
            'shape':            'CONTANGO' if is_contango else 'BACKWARDATION',
            'signal':           'NORMAL' if is_contango else 'STRESS — near-term fear elevated'
        }

    def calculate_skew(self, chain_data, dte_target=30):
        """
        Volatility skew = IV difference between
        25-delta put and 25-delta call.
        High skew = market fears downside
        """
        target_exp = min(chain_data, key=lambda x: abs(x['days_to_expiry'] - dte_target))
        exp_dte    = target_exp['days_to_expiry']
        exp_data   = [d for d in chain_data if d['days_to_expiry'] == exp_dte]

        spot       = get_current_spot()
        puts       = [d for d in exp_data if d['type'] == 'PE']
        calls      = [d for d in exp_data if d['type'] == 'CE']

        # 25-delta put (approx 90% moneyness strike)
        otm_put    = min(puts,  key=lambda x: abs(x['strike'] - spot * 0.92))
        otm_call   = min(calls, key=lambda x: abs(x['strike'] - spot * 1.08))

        skew = otm_put['iv'] - otm_call['iv']

        return {
            'skew_value':   round(skew, 2),
            'put_iv':       otm_put['iv'],
            'call_iv':      otm_call['iv'],
            'interpretation': 'EXTREME FEAR' if skew > 10
                              else 'ELEVATED FEAR' if skew > 5
                              else 'NORMAL' if skew > 0
                              else 'COMPLACENCY — puts cheaper than calls'
        }

    def vol_risk_premium(self, ticker, lookback_days=30):
        """
        VRP = Implied Volatility - Realized Volatility
        High VRP = good time to sell premium
        Low or negative VRP = good time to buy premium
        """
        # Get ATM IV
        chain    = get_option_chain(ticker)
        atm_iv   = get_atm_iv(chain)

        # Get realized volatility (historical)
        prices   = get_price_history(ticker, lookback_days)
        returns  = prices['close'].pct_change().dropna()
        realized = returns.std() * np.sqrt(252) * 100  # Annualized %

        vrp = atm_iv - realized

        return {
            'implied_vol':      round(atm_iv, 2),
            'realized_vol':     round(realized, 2),
            'vol_risk_premium': round(vrp, 2),
            'strategy':         'SELL PREMIUM — IV rich vs realized'    if vrp > 5
                                else 'BUY PREMIUM — IV cheap vs realized' if vrp < -2
                                else 'NEUTRAL — IV fairly priced'
        }
```

## 32.2 NIFTY VIX Analysis

```python
def nifty_vix_analysis():
    """
    India VIX = 30-day forward volatility of NIFTY.
    Most important single volatility indicator for India.
    """
    vix_current = get_india_vix()
    vix_history = get_india_vix_history(days=252)

    percentile = (vix_history < vix_current).mean() * 100

    # VIX regime
    if vix_current < 11:
        regime = 'EXTREME_COMPLACENCY'
        action = 'Buy cheap puts as protection — VIX historically mean reverts'
    elif vix_current < 14:
        regime = 'LOW'
        action = 'Sell premium aggressively — good conditions for iron condors'
    elif vix_current < 17:
        regime = 'NORMAL'
        action = 'Balanced approach — both buying and selling work'
    elif vix_current < 20:
        regime = 'ELEVATED'
        action = 'Reduce short premium exposure — prefer directional long options'
    elif vix_current < 25:
        regime = 'HIGH'
        action = 'Defensive positioning — hedge portfolio, avoid naked shorts'
    else:
        regime = 'EXTREME'
        action = 'Major hedging required — consider exiting some positions'

    # VIX term structure (VIX vs VIXM)
    vix_1m  = vix_current
    vix_3m  = get_vix_3m()  # Longer-dated VIX

    return {
        'current':      vix_current,
        'percentile':   round(percentile, 0),
        'regime':       regime,
        'action':       action,
        'term_shape':   'CONTANGO' if vix_3m > vix_1m else 'BACKWARDATION',
        '52w_high':     vix_history.max(),
        '52w_low':      vix_history.min(),
        'mean':         round(vix_history.mean(), 2)
    }
```

---

# SECTION 33 — MARKET MICROSTRUCTURE

## 33.1 Order Book Analysis

```python
class OrderBookAnalyzer:
    """
    Level 2 order book intelligence.
    Large bids = support, Large asks = resistance.
    """

    def get_kite_depth(self, trading_symbol, exchange='NSE'):
        """Fetch Level 2 data via Zerodha Kite"""
        kite    = get_kite_client()
        quote   = kite.quote([f"{exchange}:{trading_symbol}"])
        depth   = quote[f"{exchange}:{trading_symbol}"]['depth']

        buy_depth  = depth['buy']   # List of {price, quantity, orders}
        sell_depth = depth['sell']  # List of {price, quantity, orders}

        return buy_depth, sell_depth

    def order_book_imbalance(self, buy_depth, sell_depth):
        """
        OBI = (Total Buy Volume - Total Sell Volume) /
              (Total Buy Volume + Total Sell Volume)

        OBI > 0.2:  Strong buying pressure
        OBI < -0.2: Strong selling pressure
        """
        total_buy  = sum(d['quantity'] for d in buy_depth)
        total_sell = sum(d['quantity'] for d in sell_depth)

        obi = (total_buy - total_sell) / (total_buy + total_sell) if (total_buy + total_sell) > 0 else 0

        return {
            'obi':          round(obi, 3),
            'total_buy':    total_buy,
            'total_sell':   total_sell,
            'signal':       'STRONG BUY PRESSURE' if obi > 0.3
                            else 'BUY PRESSURE' if obi > 0.1
                            else 'STRONG SELL PRESSURE' if obi < -0.3
                            else 'SELL PRESSURE' if obi < -0.1
                            else 'BALANCED'
        }

    def large_order_detection(self, buy_depth, sell_depth, threshold_multiplier=5):
        """
        Detect unusually large orders — potential institutional activity.
        """
        all_buy_qty  = [d['quantity'] for d in buy_depth]
        all_sell_qty = [d['quantity'] for d in sell_depth]

        avg_buy  = np.mean(all_buy_qty)  if all_buy_qty  else 0
        avg_sell = np.mean(all_sell_qty) if all_sell_qty else 0

        large_bids = [d for d in buy_depth  if d['quantity'] > avg_buy  * threshold_multiplier]
        large_asks = [d for d in sell_depth if d['quantity'] > avg_sell * threshold_multiplier]

        return {
            'large_bids': large_bids,
            'large_asks': large_asks,
            'interpretation': (
                f"Large buy order at ₹{large_bids[0]['price']} — possible accumulation"
                if large_bids else
                f"Large sell wall at ₹{large_asks[0]['price']} — resistance"
                if large_asks else
                'No unusual order sizes detected'
            )
        }

    def bid_ask_spread_cost(self, buy_depth, sell_depth, quantity):
        """
        Calculate actual slippage cost for your order size.
        """
        best_ask = sell_depth[0]['price']
        best_bid = buy_depth[0]['price']
        spread   = best_ask - best_bid
        spread_pct = spread / best_ask * 100

        # Market impact for larger orders
        remaining = quantity
        avg_cost  = 0
        total_qty = 0

        for level in sell_depth:
            fill_qty = min(remaining, level['quantity'])
            avg_cost += fill_qty * level['price']
            total_qty += fill_qty
            remaining -= fill_qty
            if remaining <= 0:
                break

        avg_fill = avg_cost / total_qty if total_qty > 0 else best_ask
        slippage = avg_fill - best_ask
        slippage_pct = slippage / best_ask * 100

        return {
            'best_ask':     best_ask,
            'best_bid':     best_bid,
            'spread':       round(spread, 2),
            'spread_pct':   round(spread_pct, 3),
            'avg_fill':     round(avg_fill, 2),
            'slippage':     round(slippage, 2),
            'slippage_pct': round(slippage_pct, 3),
            'recommendation': 'Use limit order' if spread_pct > 0.2 else 'Market order acceptable'
        }
```

## 33.2 VWAP and Market Impact

```python
def calculate_vwap(price_data):
    """
    Volume Weighted Average Price.
    Most important intraday reference price.
    Price above VWAP = bullish intraday
    Price below VWAP = bearish intraday
    """
    typical_price = (price_data['high'] + price_data['low'] + price_data['close']) / 3
    vwap = (typical_price * price_data['volume']).cumsum() / price_data['volume'].cumsum()
    return vwap

def estimate_market_impact(ticker, order_value):
    """
    How much will YOUR order move the market?
    Critical for large positions.
    """
    adtv = get_average_daily_turnover(ticker)  # Average Daily Turnover Value

    participation_rate = order_value / adtv

    if participation_rate < 0.01:
        impact = 'NEGLIGIBLE — < 1% of daily volume'
        bps    = participation_rate * 10  # Very rough estimate
    elif participation_rate < 0.05:
        impact = 'LOW — 1-5% of daily volume, use limit orders'
        bps    = participation_rate * 20
    elif participation_rate < 0.10:
        impact = 'MEDIUM — use TWAP/VWAP execution'
        bps    = participation_rate * 40
    else:
        impact = 'HIGH — split across multiple days'
        bps    = participation_rate * 80

    return {
        'order_value':      order_value,
        'adtv':             adtv,
        'participation':    f"{participation_rate*100:.1f}%",
        'impact':           impact,
        'estimated_cost_bps': round(bps * 100, 1),
        'recommendation':   f"Split into {max(2, int(participation_rate/0.03))} orders"
                            if participation_rate > 0.05 else 'Single order fine'
    }
```

---

# SECTION 34 — FACTOR MODEL — SYSTEMATIC ALPHA

## 34.1 Fama-French Five Factor Model

```python
class FactorModel:
    """
    Decompose your returns into factor exposures.
    Shows where alpha actually comes from.
    """

    def calculate_factor_exposures(self, portfolio_returns, factor_returns):
        """
        Run regression of portfolio vs factors.
        Returns factor betas and alpha.
        """
        from sklearn.linear_model import LinearRegression
        import statsmodels.api as sm

        X = factor_returns[['MKT_RF', 'SMB', 'HML', 'RMW', 'CMA']]
        y = portfolio_returns - factor_returns['RF']  # Excess return

        X = sm.add_constant(X)
        model = sm.OLS(y, X).fit()

        return {
            'alpha':            model.params['const'],
            'alpha_annualized': model.params['const'] * 252,
            'alpha_tstat':      model.tvalues['const'],
            'alpha_significant': abs(model.tvalues['const']) > 2,
            'market_beta':      model.params['MKT_RF'],
            'size_factor':      model.params['SMB'],   # + = small cap tilt
            'value_factor':     model.params['HML'],   # + = value tilt
            'profitability':    model.params['RMW'],   # + = profitable companies
            'investment':       model.params['CMA'],   # - = aggressive investment
            'r_squared':        model.rsquared,
            'interpretation':   self.interpret_factors(model.params)
        }

    def interpret_factors(self, params):
        explanations = []

        if params['SMB'] > 0.3:
            explanations.append("Significant small-cap tilt — higher risk/reward")
        if params['HML'] > 0.3:
            explanations.append("Value tilt — cheap stocks by book value")
        if params['RMW'] > 0.3:
            explanations.append("Quality tilt — profitable companies preferred")
        if params['CMA'] < -0.3:
            explanations.append("Growth tilt — high-investment companies")
        if params['MKT_RF'] > 1.2:
            explanations.append("High beta — amplifies market moves")

        return explanations if explanations else ["Market-like exposure, minimal tilts"]

    def india_factor_data(self):
        """
        Construct India-specific factor returns.
        Using NSE index family as proxies.
        """
        import yfinance as yf

        # Factor proxies for India
        factors = {
            'MKT':      '^NSEI',            # Market return
            'SMALL':    '^CNXSC',           # Small cap
            'LARGE':    '^NSEI',            # Large cap
            'VALUE':    '^CNXPSE',          # PSU (value proxy)
            'QUALITY':  '^CNXINFRA',        # Quality infrastructure
            'MOMENTUM': '^CNX500',          # 500 for broad momentum
        }

        data = yf.download(
            list(factors.values()),
            period='2y',
            auto_adjust=True,
            progress=False
        )['Close']

        returns = data.pct_change().dropna()

        # Construct SMB (Small minus Big)
        smb = returns['^CNXSC'] - returns['^NSEI']

        # Construct HML (High minus Low book-to-market)
        # Using PSU (high book) vs tech (low book) as proxy
        hml = returns['^CNXPSE'] - returns['^CNXIT'] if '^CNXIT' in returns else None

        return {
            'market':   returns['^NSEI'],
            'smb':      smb,
            'hml':      hml,
        }
```

## 34.2 Momentum Factor

```python
def calculate_momentum_factor(tickers, lookback=252, skip=21):
    """
    Classic 12-1 momentum factor.
    12-month return, skipping last 1 month.
    One of the most robust factors in India.
    """
    import yfinance as yf

    prices = yf.download(tickers, period='2y', auto_adjust=True, progress=False)['Close']
    returns = prices.pct_change()

    # 12-month return, skipping last month
    momentum = {}
    for ticker in tickers:
        if ticker in returns.columns:
            ret_12m = prices[ticker].pct_change(lookback)
            ret_1m  = prices[ticker].pct_change(skip)
            # Momentum = 12m return minus last month's return
            mom     = ret_12m - ret_1m
            momentum[ticker] = {
                'momentum_score':   float(mom.iloc[-1]),
                'rank':             None,  # Filled after all computed
                'signal':           'STRONG' if mom.iloc[-1] > 0.20
                                    else 'POSITIVE' if mom.iloc[-1] > 0
                                    else 'NEGATIVE'
            }

    # Rank momentum
    ranked = sorted(momentum.items(), key=lambda x: x[1]['momentum_score'], reverse=True)
    for i, (ticker, data) in enumerate(ranked):
        momentum[ticker]['rank']    = i + 1
        momentum[ticker]['decile']  = (i // max(1, len(ranked)//10)) + 1

    return momentum

def regime_factor_recommendation(macro_regime):
    """
    Which factors work in current macro regime.
    """
    recommendations = {
        'GOLDILOCKS': {
            'overweight':   ['Momentum', 'Quality', 'Small Cap Growth'],
            'underweight':  ['Value', 'Low Volatility'],
            'reason':       'Risk-on — momentum and quality rewarded'
        },
        'REFLATION': {
            'overweight':   ['Value', 'Size (Small Cap)', 'Cyclicals'],
            'underweight':  ['Quality Growth', 'Momentum'],
            'reason':       'Inflation benefits value stocks and cyclicals'
        },
        'STAGFLATION': {
            'overweight':   ['Low Volatility', 'Dividend', 'Real Assets'],
            'underweight':  ['Growth', 'Momentum', 'Small Cap'],
            'reason':       'Capital preservation — defensive factors'
        },
        'DEFLATION': {
            'overweight':   ['Quality', 'Low Volatility', 'Dividend'],
            'underweight':  ['Value', 'Cyclicals', 'Small Cap'],
            'reason':       'Safety first — quality and yield'
        }
    }

    return recommendations.get(macro_regime, {})
```

---

# SECTION 35 — CORPORATE ACTION INTELLIGENCE

## 35.1 Complete Corporate Action Tracker

```python
class CorporateActionTracker:
    """
    Tracks all corporate actions that directly affect positions.
    Runs daily against your entire portfolio.
    """

    def get_nse_corporate_actions(self, symbol=None):
        """Fetch all upcoming corporate actions from NSE"""
        session = create_nse_session()

        if symbol:
            url = f"https://www.nseindia.com/api/corporates-corporateActions?index=equities&symbol={symbol}"
        else:
            url = "https://www.nseindia.com/api/corporates-corporateActions?index=equities"

        response = session.get(url, headers=NSE_HEADERS, timeout=10)
        return response.json()

    def process_actions_for_portfolio(self, portfolio):
        """Check all upcoming actions affecting portfolio holdings"""
        alerts = []
        today  = date.today()

        for position in portfolio.positions:
            actions = self.get_nse_corporate_actions(position.ticker)

            for action in actions:
                action_date = parse_date(action.get('exDate'))
                if not action_date:
                    continue

                days_away = (action_date - today).days

                if days_away < 0 or days_away > 60:
                    continue

                action_type = action.get('purpose', '').lower()

                # Dividend
                if 'dividend' in action_type:
                    div_amount = parse_dividend_amount(action.get('purpose', ''))
                    total_div  = div_amount * position.shares if div_amount else None

                    alerts.append({
                        'ticker':       position.ticker,
                        'action':       'DIVIDEND',
                        'ex_date':      action_date,
                        'days_away':    days_away,
                        'amount':       div_amount,
                        'total_income': total_div,
                        'urgency':      'HIGH' if days_away <= 5 else 'MEDIUM',
                        'action_required': f"Must hold before {action_date} to receive dividend"
                    })

                # Bonus shares
                elif 'bonus' in action_type:
                    ratio = parse_bonus_ratio(action.get('purpose', ''))
                    alerts.append({
                        'ticker':       position.ticker,
                        'action':       'BONUS',
                        'ex_date':      action_date,
                        'days_away':    days_away,
                        'ratio':        ratio,
                        'new_shares':   int(position.shares * ratio) if ratio else None,
                        'urgency':      'HIGH' if days_away <= 5 else 'MEDIUM',
                        'tax_note':     'Cost basis splits proportionally — no tax event'
                    })

                # Stock split
                elif 'split' in action_type:
                    alerts.append({
                        'ticker':       position.ticker,
                        'action':       'STOCK_SPLIT',
                        'ex_date':      action_date,
                        'days_away':    days_away,
                        'urgency':      'MEDIUM',
                        'note':         'Price adjusts automatically — no action needed'
                    })

                # Rights issue
                elif 'rights' in action_type:
                    alerts.append({
                        'ticker':       position.ticker,
                        'action':       'RIGHTS_ISSUE',
                        'ex_date':      action_date,
                        'days_away':    days_away,
                        'urgency':      'HIGH',
                        'decision_needed': 'Subscribe / Sell rights / Let lapse — decision required'
                    })

                # Buyback
                elif 'buyback' in action_type or 'buy-back' in action_type:
                    alerts.append({
                        'ticker':       position.ticker,
                        'action':       'BUYBACK',
                        'ex_date':      action_date,
                        'days_away':    days_away,
                        'urgency':      'HIGH',
                        'note':         'Buyback tax now on company side (post Oct 2024)',
                        'decision':     'Tender into buyback if offer > market price'
                    })

        # Sort by urgency and date
        alerts.sort(key=lambda x: (x['days_away']))

        return alerts

    def dividend_calendar_income_projection(self, portfolio, months_ahead=12):
        """
        Project total dividend income for next 12 months.
        Shows monthly income from portfolio.
        """
        monthly_income = {m: 0 for m in range(1, 13)}

        for position in portfolio.positions:
            div_history = get_dividend_history(position.ticker)

            if not div_history:
                continue

            # Project based on last 4 dividends
            recent_divs = div_history[-4:]
            avg_annual  = sum(d['amount'] for d in recent_divs)
            per_share   = avg_annual / len(recent_divs)

            # Estimate month of payment
            for div in recent_divs:
                pay_month = parse_date(div.get('payDate')).month if div.get('payDate') else None
                if pay_month:
                    monthly_income[pay_month] += per_share * position.shares

        return {
            'monthly_projection':   monthly_income,
            'annual_total':         sum(monthly_income.values()),
            'monthly_average':      sum(monthly_income.values()) / 12,
            'peak_month':           max(monthly_income, key=monthly_income.get)
        }

    def merger_arbitrage_tracker(self):
        """
        Track announced M&A deals for arbitrage opportunities.
        Buy target at discount to deal price.
        """
        # Fetch from MoneyControl / Business Standard M&A news
        deals = fetch_announced_deals()

        arb_opportunities = []
        for deal in deals:
            target_price = get_latest_price(deal['target_ticker'])
            offer_price  = deal['offer_price']
            spread_pct   = (offer_price - target_price) / target_price * 100
            annualized   = spread_pct / (deal['days_to_completion'] / 365)

            arb_opportunities.append({
                'acquirer':         deal['acquirer'],
                'target':           deal['target_ticker'],
                'offer_price':      offer_price,
                'current_price':    target_price,
                'spread_pct':       round(spread_pct, 2),
                'annualized_return': round(annualized, 1),
                'deal_risk':        deal.get('risk_level', 'MEDIUM'),
                'days_to_close':    deal['days_to_completion'],
                'recommendation':   'ATTRACTIVE' if annualized > 15 and deal.get('risk_level') == 'LOW'
                                    else 'MONITOR'
            })

        return sorted(arb_opportunities, key=lambda x: x['annualized_return'], reverse=True)
```

---

# SECTION 36 — CREDIT ANALYSIS ENGINE

## 36.1 Altman Z-Score

```python
def calculate_altman_zscore(ticker, financial_data):
    """
    Altman Z-Score: Bankruptcy prediction model.
    Original model for listed manufacturing companies.

    Z > 2.99: Safe zone
    Z 1.81-2.99: Grey zone (caution)
    Z < 1.81: Distress zone (high bankruptcy risk)
    """
    # Financial inputs required
    working_capital     = financial_data['current_assets'] - financial_data['current_liabilities']
    total_assets        = financial_data['total_assets']
    retained_earnings   = financial_data['retained_earnings']
    ebit                = financial_data['ebit']
    market_cap          = get_market_cap(ticker)
    total_debt          = financial_data['total_debt']
    revenue             = financial_data['revenue']

    # Five ratios
    x1 = working_capital / total_assets              # Liquidity
    x2 = retained_earnings / total_assets             # Profitability
    x3 = ebit / total_assets                          # Operating efficiency
    x4 = market_cap / total_debt if total_debt > 0 else 10  # Financial leverage
    x5 = revenue / total_assets                       # Asset efficiency

    # Z-Score (original coefficients)
    z = 1.2*x1 + 1.4*x2 + 3.3*x3 + 0.6*x4 + 1.0*x5

    if z > 2.99:
        zone    = 'SAFE'
        color   = 'green'
        action  = 'No immediate financial distress concern'
    elif z > 1.81:
        zone    = 'GREY'
        color   = 'orange'
        action  = 'Monitor closely — some financial stress signals'
    else:
        zone    = 'DISTRESS'
        color   = 'red'
        action  = '⚠️ HIGH BANKRUPTCY RISK — review position urgently'

    return {
        'z_score':      round(z, 2),
        'zone':         zone,
        'action':       action,
        'components':   {'x1': round(x1,3), 'x2': round(x2,3), 'x3': round(x3,3),
                        'x4': round(x4,3), 'x5': round(x5,3)}
    }

def credit_health_score(ticker, financials):
    """
    Comprehensive credit health for any holding.
    Particularly important for bond holders and NBFC stocks.
    """
    score    = 100
    warnings = []

    # Interest coverage ratio (EBIT / Interest expense)
    if financials.get('interest_expense', 0) > 0:
        icr = financials['ebit'] / financials['interest_expense']
        if icr < 1.5:
            score -= 25
            warnings.append(f"CRITICAL: ICR {icr:.1f}x — cannot comfortably service debt")
        elif icr < 2.5:
            score -= 10
            warnings.append(f"LOW: ICR {icr:.1f}x — limited debt service cushion")

    # Debt/EBITDA
    ebitda = financials.get('ebitda', financials.get('ebit', 0))
    if ebitda > 0:
        debt_ebitda = financials['total_debt'] / ebitda
        if debt_ebitda > 5:
            score -= 20
            warnings.append(f"HIGH LEVERAGE: Debt/EBITDA {debt_ebitda:.1f}x")
        elif debt_ebitda > 3:
            score -= 10
            warnings.append(f"ELEVATED: Debt/EBITDA {debt_ebitda:.1f}x — watch cash flow")

    # Current ratio
    if financials.get('current_liabilities', 0) > 0:
        current_ratio = financials['current_assets'] / financials['current_liabilities']
        if current_ratio < 1.0:
            score -= 20
            warnings.append(f"LIQUIDITY RISK: Current ratio {current_ratio:.2f} < 1")
        elif current_ratio < 1.5:
            score -= 5
            warnings.append(f"LOW LIQUIDITY: Current ratio {current_ratio:.2f}")

    # Free cash flow
    fcf = financials.get('free_cash_flow', 0)
    if fcf < 0:
        score -= 15
        warnings.append(f"NEGATIVE FREE CASH FLOW: ₹{fcf/1e7:.1f}Cr — burning cash")

    # Altman Z-Score
    z = calculate_altman_zscore(ticker, financials)
    if z['zone'] == 'DISTRESS':
        score -= 30
        warnings.append("ALTMAN Z-SCORE: Distress zone")
    elif z['zone'] == 'GREY':
        score -= 10
        warnings.append("ALTMAN Z-SCORE: Grey zone — monitor")

    return {
        'credit_score':     max(0, score),
        'grade':            'AAA' if score >= 90 else 'AA' if score >= 80
                            else 'A' if score >= 70 else 'BBB' if score >= 60
                            else 'BB' if score >= 50 else 'B' if score >= 40
                            else 'CCC',
        'warnings':         warnings,
        'z_score':          z
    }
```

---

# SECTION 37 — GEOPOLITICAL RISK ENGINE

## 37.1 Event Impact Mapping

```python
GEOPOLITICAL_IMPACT_MAP = {
    'india_pakistan_tension': {
        'beneficiaries': ['BEL.NS', 'HAL.NS', 'BEML.NS', 'BDL.NS', 'PARAS.NS'],
        'negatives':     ['INDIGO.NS', 'SPICEJET.NS', 'INDHOTEL.NS', 'EIHOTEL.NS'],
        'forex_impact':  'INR_WEAKENS',
        'severity':      'HIGH',
        'keywords':      ['pakistan', 'border', 'army', 'surgical strike', 'ceasefire violation']
    },
    'india_china_tension': {
        'beneficiaries': ['DIVI.NS', 'DIXON.NS', 'AMBER.NS', 'PGIL.NS'],  # Import substitution
        'negatives':     ['TATAMOTORS.NS'],  # JLR China exposure
        'forex_impact':  'INR_WEAKENS_SLIGHTLY',
        'severity':      'MEDIUM',
        'keywords':      ['china border', 'LAC', 'Galwan', 'doklam', 'ban chinese']
    },
    'opec_production_cut': {
        'beneficiaries': ['ONGC.NS', 'OIL.NS', 'CAIRN.NS'],
        'negatives':     ['INDIGO.NS', 'HINDUNILVR.NS', 'PIDILITIND.NS'],  # Cost push
        'macro_impact':  'INR_WEAKENS, INFLATION_RISES',
        'severity':      'HIGH',
        'keywords':      ['opec cut', 'production cut', 'crude rises', 'oil jump']
    },
    'fed_rate_hike': {
        'beneficiaries': ['Gold ETFs', 'Defensive stocks'],
        'negatives':     ['FII_OUTFLOWS_INDIA', 'NIFTY_FALLS'],
        'macro_impact':  'FII_SELLING, NIFTY_PRESSURE',
        'severity':      'HIGH',
        'keywords':      ['fed hike', 'rate hike', 'powell hawkish', 'fomc hawkish']
    },
    'russia_ukraine_war': {
        'beneficiaries': ['ONGC.NS', 'OIL.NS', 'Defence stocks'],
        'negatives':     ['Metals consumers', 'Fertilizer companies'],
        'macro_impact':  'COMMODITY_SPIKE, GLOBAL_INFLATION',
        'severity':      'VERY_HIGH',
        'keywords':      ['ukraine', 'russia war', 'nato', 'sanctions russia']
    },
    'israel_hamas_conflict': {
        'beneficiaries': ['Gold', 'Oil'],
        'negatives':     ['Airlines', 'Tourism'],
        'forex_impact':  'SAFE_HAVEN_FLOWS',
        'severity':      'MEDIUM',
        'keywords':      ['israel', 'hamas', 'middle east conflict', 'Gaza']
    },
    'us_china_trade_war': {
        'beneficiaries': ['India IT (China+1)', 'India manufacturing'],
        'negatives':     ['Global tech supply chain'],
        'macro_impact':  'GLOBAL_SLOWDOWN_RISK',
        'severity':      'HIGH',
        'keywords':      ['tariff china', 'trade war', 'semiconductor ban']
    }
}

class GeopoliticalRiskEngine:

    def scan_news_for_geopolitical(self, news_items):
        """
        Scan today's news for geopolitical keywords.
        Map to portfolio impact.
        """
        detected_events = []

        for event_name, config in GEOPOLITICAL_IMPACT_MAP.items():
            for news in news_items:
                text = (news.get('headline', '') + ' ' + news.get('content', '')).lower()

                if any(kw.lower() in text for kw in config['keywords']):
                    detected_events.append({
                        'event':        event_name,
                        'severity':     config['severity'],
                        'news':         news['headline'],
                        'beneficiaries': config['beneficiaries'],
                        'negatives':    config['negatives'],
                        'forex_impact': config.get('forex_impact', 'UNKNOWN'),
                        'macro_impact': config.get('macro_impact', 'UNKNOWN'),
                    })
                    break  # One detection per event type

        return detected_events

    def portfolio_geo_impact(self, portfolio, detected_events):
        """
        How do detected geopolitical events affect YOUR portfolio?
        """
        portfolio_tickers = [p.ticker for p in portfolio.positions]
        impacts = []

        for event in detected_events:
            for ticker in portfolio_tickers:
                if ticker in event['beneficiaries']:
                    impacts.append({
                        'ticker':   ticker,
                        'impact':   'POSITIVE',
                        'reason':   f"{event['event']} — beneficiary",
                        'action':   'Consider adding' if event['severity'] in ['HIGH', 'VERY_HIGH'] else 'Monitor'
                    })
                elif ticker in event['negatives']:
                    impacts.append({
                        'ticker':   ticker,
                        'impact':   'NEGATIVE',
                        'reason':   f"{event['event']} — headwind",
                        'action':   'Consider reducing' if event['severity'] in ['HIGH', 'VERY_HIGH'] else 'Monitor stop loss'
                    })

        return impacts
```

---

# SECTION 38 — NATURAL LANGUAGE QUERY INTERFACE

## 38.1 Query Engine

```python
class NaturalLanguageQueryEngine:
    """
    Ask questions about your portfolio in plain English.
    AI converts to database queries and returns formatted results.
    """

    QUERY_EXAMPLES = [
        "Show me all IT stocks where FII bought more than 100 crore last week",
        "Which of my positions have earnings in next 10 days",
        "What is my total tax liability if I sell everything today",
        "Find stocks like INFY but cheaper on PEG ratio",
        "Show positions where I violated my stop loss rule",
        "What would my portfolio look like if NIFTY drops 15%",
        "Which holdings have promoter pledge above 30%",
        "Show all trades where I overrode AI and lost money",
        "What is my annualized return on each position",
        "Find mid-cap stocks with FII buying and RSI below 40",
        "Which positions am I closest to LTCG threshold",
        "What is my sector concentration today",
        "Show me stocks with high IV where I could sell premium",
        "Which of my trades had the highest broker cost percentage",
        "Find positions where my thesis score and AI score diverge most"
    ]

    def parse_and_execute(self, natural_query, profile_id):
        """
        Convert natural language to SQL query via Ollama.
        Execute and return formatted result.
        """
        import ollama

        # Get database schema context
        schema_context = self.get_schema_summary()

        # Convert to SQL via AI
        sql_response = ollama.chat(
            model='llama3.1:8b',
            messages=[{
                'role': 'system',
                'content': f"""You are a SQL expert for a trading portfolio database.
                Convert the user's natural language question to a SQL query.
                Return ONLY the SQL query, nothing else.

                Database schema:
                {schema_context}

                Profile ID for this user: {profile_id}
                Always filter by profile_id = {profile_id} unless asking for admin data.
                Use PostgreSQL syntax.
                If the query cannot be answered with available data, return: SELECT 'CANNOT_ANSWER' as result;
                """
            }, {
                'role': 'user',
                'content': natural_query
            }],
            options={'temperature': 0.1}
        )

        sql_query = sql_response['message']['content'].strip()

        # Safety check — only allow SELECT
        if not sql_query.upper().startswith('SELECT'):
            return {'error': 'Only SELECT queries allowed'}

        # Execute query
        try:
            results = execute_query(sql_query)

            # Format results via AI
            format_response = ollama.chat(
                model='llama3.1:8b',
                messages=[{
                    'role': 'user',
                    'content': f"""Question: {natural_query}

                    Raw data: {results[:20]}  # Limit for context

                    Format this data as a clear, concise answer to the question.
                    Use bullet points if multiple items.
                    Highlight the most important findings.
                    Add actionable insight at the end.
                    Keep response under 200 words."""
                }],
                options={'temperature': 0.3}
            )

            return {
                'query':        natural_query,
                'sql':          sql_query,
                'raw_results':  results,
                'formatted':    format_response['message']['content'],
                'row_count':    len(results)
            }

        except Exception as e:
            return {'error': str(e), 'sql': sql_query}

    def get_schema_summary(self):
        """Return concise schema for AI context"""
        return """
        TABLES:
        positions (profile_id, ticker, shares, avg_cost, purchase_date, stop_loss, current_price, unrealized_pnl)
        trades (profile_id, ticker, action, price, quantity, return_pct, entry_date, exit_date, ai_score, override)
        stock_scores (ticker, date, composite_score, valuation, technical, fundamental, sentiment, option_chain)
        research_notes (profile_id, ticker, thesis, fair_value, conviction, ai_analysis, thesis_score)
        tax_events (profile_id, ticker, holding_days, gain_loss, treatment, tax_owed)
        social_sentiment (ticker, sentiment_score, source, created_at)
        news (ticker, headline, sentiment_score, created_at)
        fundamentals (ticker, pe_ratio, peg_ratio, roe, debt_equity, promoter_pledge, revenue_growth)
        fii_dii (date, fii_net, dii_net, fii_equity, dii_equity)
        option_chains (ticker, strike, expiry, call_oi, put_oi, call_iv, put_iv, max_pain, pcr)
        corporate_actions (ticker, action_type, ex_date, amount, ratio)
        consistency_log (profile_id, date, checklist_completed, position_size_pct, ai_override, override_reason)
        """
```

## 38.2 Voice Query (Siri Integration)

```swift
// iOS Shortcut — "Hey Siri, portfolio status"
// Creates HTTP request to your FastAPI endpoint

// In iOS Shortcuts app:
// Action: Get Contents of URL
// URL: https://api.yourdomain.com/voice/query
// Method: POST
// Body: {"query": "portfolio status", "profile_id": 1}
// Headers: Authorization: Bearer YOUR_JWT_TOKEN

// FastAPI endpoint receives this
// Returns text response
// Shortcut reads it aloud via "Speak Text" action

// Example queries via Siri:
// "Hey Siri, what is my NIFTY loss today"
// "Hey Siri, any alerts on my portfolio"
// "Hey Siri, INFY current price"
// "Hey Siri, should I hold TATAMOTORS"
```

---

# SECTION 39 — SECTOR ROTATION MODEL

## 39.1 Economic Cycle Sector Clock

```python
SECTOR_CYCLE_MAP = {
    'early_cycle': {
        'description':  'Recovery phase — economy turning up from recession',
        'india_sectors': {
            'OVERWEIGHT':   ['Financials', 'Consumer Discretionary', 'Real Estate', 'Industrials'],
            'NEUTRAL':      ['Technology', 'Materials'],
            'UNDERWEIGHT':  ['Utilities', 'Consumer Staples', 'Healthcare']
        },
        'india_indices': {
            'BUY':  ['^NSEBANK', '^CNXREALTY', '^CNXINFRA'],
            'SELL': ['^CNXFMCG', '^CNXPHARMA']
        },
        'signals':      ['PMI rising above 50', 'Credit growth turning positive',
                        'Interest rates bottoming', 'IIP recovery']
    },
    'mid_cycle': {
        'description':  'Expansion phase — strongest growth',
        'india_sectors': {
            'OVERWEIGHT':   ['Technology', 'Materials', 'Energy', 'Industrials'],
            'NEUTRAL':      ['Financials', 'Consumer Discretionary'],
            'UNDERWEIGHT':  ['Utilities', 'Consumer Staples']
        },
        'india_indices': {
            'BUY':  ['^CNXIT', '^CNXMETAL', '^CNXENERGY'],
            'SELL': ['^CNXFMCG']
        },
        'signals':      ['PMI above 54', 'Credit growth robust', 'Capex cycle starting']
    },
    'late_cycle': {
        'description':  'Slowdown phase — growth peaking',
        'india_sectors': {
            'OVERWEIGHT':   ['Energy', 'Materials', 'Healthcare', 'Consumer Staples'],
            'NEUTRAL':      ['Technology', 'Industrials'],
            'UNDERWEIGHT':  ['Financials', 'Consumer Discretionary', 'Real Estate']
        },
        'india_indices': {
            'BUY':  ['^CNXENERGY', '^CNXPHARMA', '^CNXFMCG'],
            'SELL': ['^NSEBANK', '^CNXREALTY']
        },
        'signals':      ['PMI plateauing', 'Inflation rising', 'Credit tightening']
    },
    'recession': {
        'description':  'Contraction phase — seek safety',
        'india_sectors': {
            'OVERWEIGHT':   ['Healthcare', 'Consumer Staples', 'Utilities'],
            'NEUTRAL':      ['Technology (defensive names)'],
            'UNDERWEIGHT':  ['Cyclicals', 'Financials', 'Real Estate', 'Industrials']
        },
        'india_indices': {
            'BUY':  ['^CNXPHARMA', '^CNXFMCG'],
            'SELL': ['^CNXMETAL', '^CNXAUTO', '^CNXREALTY']
        },
        'signals':      ['PMI below 50', 'Credit contraction', 'Rising defaults']
    }
}

def detect_india_economic_cycle():
    """
    Detect current cycle position using India-specific indicators.
    """
    from fredapi import Fred
    import os

    fred = Fred(api_key=os.getenv('FRED_API_KEY'))

    indicators = {
        'india_pmi':        get_india_pmi(),              # Manufacturing PMI
        'credit_growth':    get_rbi_credit_growth(),      # Bank credit YoY
        'iip_growth':       get_india_iip(),              # Industrial production
        'inflation':        get_india_cpi(),              # CPI YoY
        'fii_flows_3m':     get_fii_flows(months=3),      # FII 3-month net
        'nifty_vs_200dma':  get_nifty_vs_200dma(),        # Technical indicator
    }

    # Score each indicator
    score = 0

    if indicators['india_pmi'] > 54:    score += 2
    elif indicators['india_pmi'] > 50:  score += 1
    else:                               score -= 1

    if indicators['credit_growth'] > 15: score += 2
    elif indicators['credit_growth'] > 10: score += 1
    else:                               score -= 1

    if indicators['iip_growth'] > 8:    score += 1
    if indicators['inflation'] > 6:     score -= 1   # High inflation = late/stagflation
    if indicators['fii_flows_3m'] > 0:  score += 1

    # Map score to cycle
    if score >= 4:      cycle = 'mid_cycle'
    elif score >= 2:    cycle = 'early_cycle'
    elif score >= 0:    cycle = 'late_cycle'
    else:               cycle = 'recession'

    recommendation = SECTOR_CYCLE_MAP[cycle]

    return {
        'current_cycle':    cycle,
        'description':      recommendation['description'],
        'indicators':       indicators,
        'overweight':       recommendation['india_sectors']['OVERWEIGHT'],
        'underweight':      recommendation['india_sectors']['UNDERWEIGHT'],
        'buy_indices':      recommendation['india_indices']['BUY'],
        'sell_indices':     recommendation['india_indices']['SELL'],
        'portfolio_alignment': check_portfolio_alignment(cycle)
    }
```

---

# SECTION 40 — DIVIDEND INTELLIGENCE AND INCOME TRACKING

## 40.1 Dividend Capture Strategy

```python
class DividendIntelligence:

    def analyze_dividend_capture(self, ticker, div_amount, ex_date):
        """
        Is the dividend worth capturing?
        Buy before ex-date, sell after.
        Net benefit must exceed price drop + costs + tax.
        """
        current_price   = get_latest_price(ticker)
        shares          = 100  # Analysis per 100 shares

        # Income
        gross_dividend  = div_amount * shares
        # Tax: India dividends taxed at slab rate (30%)
        tax_on_dividend = gross_dividend * 0.30
        net_dividend    = gross_dividend - tax_on_dividend

        # Typical price drop on ex-date (approximately dividend amount)
        expected_drop   = div_amount * shares
        # Sometimes stock recovers faster than drop
        historical_recovery = get_ex_date_recovery(ticker)

        # Transaction costs (buy + sell round trip)
        broker_cost     = calculate_round_trip_cost(ticker, shares, current_price, 'zerodha')

        # Net benefit
        net_benefit = net_dividend - expected_drop + historical_recovery - broker_cost

        return {
            'ticker':               ticker,
            'ex_date':              ex_date,
            'dividend_per_share':   div_amount,
            'gross_dividend':       gross_dividend,
            'tax_on_dividend':      tax_on_dividend,
            'net_dividend':         net_dividend,
            'expected_price_drop':  expected_drop,
            'historical_recovery':  historical_recovery,
            'broker_cost':          broker_cost,
            'net_benefit':          round(net_benefit, 2),
            'recommendation':       'CAPTURE' if net_benefit > 200 else 'SKIP',
            'div_yield':            round(div_amount / current_price * 100, 2)
        }

    def sustainable_dividend_score(self, ticker, financials):
        """
        Is the dividend sustainable?
        High yield + declining FCF = dividend cut risk.
        """
        score    = 100
        warnings = []

        # Payout ratio
        payout_ratio = financials['dividends_paid'] / financials['net_income'] if financials['net_income'] > 0 else 1

        if payout_ratio > 0.90:
            score -= 30
            warnings.append(f"HIGH PAYOUT: {payout_ratio*100:.0f}% of earnings — unsustainable")
        elif payout_ratio > 0.70:
            score -= 10
            warnings.append(f"ELEVATED PAYOUT: {payout_ratio*100:.0f}%")

        # Free cash flow coverage
        fcf_coverage = financials['free_cash_flow'] / financials['dividends_paid'] if financials['dividends_paid'] > 0 else 0

        if fcf_coverage < 1.0:
            score -= 25
            warnings.append("FCF DOESN'T COVER DIVIDEND — borrowing to pay dividend")
        elif fcf_coverage < 1.5:
            score -= 10
            warnings.append("LOW FCF COVERAGE — limited dividend growth potential")

        # Dividend growth trend
        div_history = get_dividend_history(ticker, years=5)
        if len(div_history) >= 4:
            recent_cut = any(
                div_history[i]['amount'] < div_history[i-1]['amount']
                for i in range(1, len(div_history))
            )
            if recent_cut:
                score -= 20
                warnings.append("DIVIDEND CUT in history — credibility concern")

        return {
            'sustainability_score': max(0, score),
            'payout_ratio':         f"{payout_ratio*100:.0f}%",
            'fcf_coverage':         f"{fcf_coverage:.1f}x",
            'warnings':             warnings,
            'verdict':              'SUSTAINABLE' if score >= 70
                                    else 'WATCH' if score >= 50
                                    else 'AT RISK'
        }

    def income_dashboard(self, portfolio):
        """
        Complete income tracking across all asset types.
        """
        income_streams = {
            'dividends':        [],
            'bond_coupons':     [],
            'reit_distributions': [],
            'option_premium':   [],
            'staking_rewards':  [],
        }

        # Dividends from equity
        for position in portfolio.equity_positions:
            div = get_dividend_history(position.ticker)
            if div:
                annual = sum(d['amount'] for d in div[-4:]) * position.shares
                income_streams['dividends'].append({
                    'ticker': position.ticker,
                    'annual': annual,
                    'monthly': annual / 12
                })

        # Coupon from bonds
        for bond in portfolio.bond_positions:
            annual_coupon = bond.face_value * bond.coupon_rate * bond.quantity
            income_streams['bond_coupons'].append({
                'issuer': bond.issuer,
                'annual': annual_coupon,
                'monthly': annual_coupon / bond.coupon_frequency
            })

        total_annual = sum(
            sum(item['annual'] for item in stream)
            for stream in income_streams.values()
        )

        return {
            'streams':              income_streams,
            'total_annual_income':  total_annual,
            'monthly_average':      total_annual / 12,
            'yield_on_portfolio':   total_annual / portfolio.total_value * 100,
            'tax_efficiency':       self.income_tax_efficiency(income_streams)
        }
```

---

# SECTION 41 — INSIDER CLUSTER ANALYSIS

## 41.1 Cluster Detection

```python
class InsiderClusterEngine:

    def get_india_insider_transactions(self, ticker, months=6):
        """
        NSE/BSE mandatory insider transaction disclosures.
        All directors and KMPs must disclose within 2 days.
        """
        session  = create_nse_session()
        end_date = date.today()
        start    = end_date - timedelta(days=months*30)

        url = (f"https://www.nseindia.com/api/corporates-pit?"
               f"symbol={ticker}&from={start}&to={end_date}")

        response = session.get(url, headers=NSE_HEADERS)
        data     = response.json()

        transactions = []
        for item in data.get('data', []):
            transactions.append({
                'ticker':       ticker,
                'person':       item.get('acquirerName'),
                'designation':  item.get('category'),
                'action':       item.get('transactionType'),  # Buy/Sell/Pledge
                'quantity':     item.get('noOfSharesAcquired'),
                'value':        item.get('valueOfShares'),
                'date':         item.get('dateOfAllotment'),
                'mode':         item.get('modeOfAcquisition'),  # Market/Off-market/ESOP
            })

        return transactions

    def detect_cluster(self, transactions, window_days=14):
        """
        Find clusters of insider buying/selling.
        Multiple insiders buying in same period = VERY STRONG signal.
        """
        buys  = [t for t in transactions if 'buy' in t.get('action', '').lower()
                 and 'market' in t.get('mode', '').lower()]  # Open market only

        # Group by 2-week windows
        if not buys:
            return {'cluster_detected': False}

        # Sort by date
        buys.sort(key=lambda x: x['date'])

        clusters    = []
        current     = [buys[0]]

        for buy in buys[1:]:
            date_diff = (parse_date(buy['date']) - parse_date(current[0]['date'])).days

            if date_diff <= window_days:
                current.append(buy)
            else:
                if len(current) >= 2:
                    clusters.append(current)
                current = [buy]

        if len(current) >= 2:
            clusters.append(current)

        # Score the clusters
        scored_clusters = []
        for cluster in clusters:
            score     = self.score_cluster(cluster)
            total_val = sum(t.get('value', 0) for t in cluster)

            scored_clusters.append({
                'insiders':         len(cluster),
                'total_value':      total_val,
                'cluster_score':    score,
                'transactions':     cluster,
                'signal':           'VERY_STRONG' if len(cluster) >= 4 and score > 80
                                    else 'STRONG' if len(cluster) >= 3 and score > 60
                                    else 'MODERATE' if len(cluster) >= 2
                                    else 'WEAK',
                'implication':      f"{len(cluster)} insiders buying ₹{total_val/1e7:.1f}Cr "
                                    f"in {window_days} days — highly unusual, strongly bullish"
                                    if len(cluster) >= 3 else
                                    f"{len(cluster)} insiders buying — positive signal"
            })

        return {
            'cluster_detected': len(scored_clusters) > 0,
            'clusters':         scored_clusters,
            'best_cluster':     max(scored_clusters, key=lambda x: x['cluster_score'])
                                if scored_clusters else None
        }

    def score_cluster(self, cluster):
        """Score a cluster by quality of insiders and transaction type"""
        score = 0

        for t in cluster:
            # Higher score for CEO/MD/Promoter
            designation = t.get('designation', '').lower()
            if any(k in designation for k in ['promoter', 'md', 'ceo', 'chairman']):
                score += 30
            elif any(k in designation for k in ['director', 'cfo', 'coo']):
                score += 20
            elif 'independent' in designation:
                score += 10

            # Higher score for open market vs ESOP
            if 'market' in t.get('mode', '').lower():
                score += 20
            elif 'esop' in t.get('mode', '').lower():
                score += 5  # ESOP exercise not as strong a signal

            # Higher score for large amount
            value = t.get('value', 0)
            if value > 1e8:     score += 20  # > ₹10 crore
            elif value > 1e7:   score += 10  # > ₹1 crore
            else:               score += 5

        return min(100, score)
```

---

# SECTION 42 — SHORT SQUEEZE DETECTOR

## 42.1 India Short Squeeze via F&O Data

```python
class ShortSqueezeDetector:
    """
    India doesn't publish short interest directly.
    Use F&O data as proxy for short positioning.
    """

    def detect_squeeze_setup(self, ticker):
        """
        Squeeze conditions in India F&O context:
        1. High put OI (implies heavy short/hedge positioning)
        2. Negative futures basis (short heavy in futures)
        3. Stock starting to rise despite shorts
        4. Catalyst (news, results) incoming
        """
        chain   = get_option_chain(ticker)
        futures = get_futures_data(ticker)
        price   = get_latest_price(ticker)

        # Calculate PCR
        put_oi  = sum(s['put_oi']  for s in chain if abs(s['strike'] - price) / price < 0.10)
        call_oi = sum(s['call_oi'] for s in chain if abs(s['strike'] - price) / price < 0.10)
        pcr     = put_oi / call_oi if call_oi > 0 else 0

        # Futures basis
        futures_price  = futures.get('price', price)
        theoretical    = price * (1 + 0.07 * futures.get('dte', 30) / 365)  # 7% risk-free
        actual_premium = futures_price - price
        theoretical_premium = theoretical - price
        basis_deviation = actual_premium - theoretical_premium

        # Score squeeze potential
        squeeze_score = 0
        signals       = []

        if pcr > 1.5:
            squeeze_score += 30
            signals.append(f"High PCR {pcr:.2f} — heavy put/short positioning")

        if basis_deviation < -5:
            squeeze_score += 25
            signals.append(f"Negative basis ₹{basis_deviation:.0f} — shorts in futures")

        # Price rising despite shorts
        momentum_5d = get_price_change(ticker, days=5)
        if momentum_5d > 3 and squeeze_score > 30:
            squeeze_score += 25
            signals.append(f"Price rising +{momentum_5d:.1f}% despite heavy shorts")

        # Upcoming catalyst
        earnings_days = get_days_to_earnings(ticker)
        if earnings_days and earnings_days <= 15:
            squeeze_score += 20
            signals.append(f"Earnings in {earnings_days} days — potential catalyst")

        return {
            'ticker':           ticker,
            'squeeze_score':    squeeze_score,
            'pcr':              round(pcr, 2),
            'basis_deviation':  round(basis_deviation, 2),
            'momentum_5d':      round(momentum_5d, 2),
            'signals':          signals,
            'potential':        'HIGH' if squeeze_score >= 70
                                else 'MODERATE' if squeeze_score >= 40
                                else 'LOW'
        }
```

---

# SECTION 43 — ARBITRAGE SCANNER

## 43.1 Cash-Futures Arbitrage

```python
class ArbitrageScanner:

    def cash_futures_spread(self, ticker, exchange='NSE'):
        """
        Theoretical futures price = Cash × (1 + r × DTE/365)
        Where r = risk-free rate (currently ~7% India)
        When actual premium deviates significantly = opportunity
        """
        cash_price    = get_cash_price(ticker)
        futures_data  = get_near_month_futures(ticker)

        dte           = futures_data['days_to_expiry']
        futures_price = futures_data['price']
        risk_free     = 0.07  # 7% India risk-free

        # Theoretical premium
        theoretical   = cash_price * (1 + risk_free * dte / 365)
        actual_premium = futures_price - cash_price
        theo_premium  = theoretical - cash_price

        # Fair value deviation
        deviation     = actual_premium - theo_premium
        deviation_pct = deviation / cash_price * 100

        # Annualized return from arbitrage
        if actual_premium > theo_premium:
            # Sell futures, buy cash — earn excess premium
            annualized = (deviation / cash_price) * (365 / dte) * 100
        else:
            annualized = 0  # Reverse arb requires shorting cash (hard for retail)

        return {
            'ticker':           ticker,
            'cash_price':       cash_price,
            'futures_price':    futures_price,
            'theoretical':      round(theoretical, 2),
            'actual_premium':   round(actual_premium, 2),
            'theo_premium':     round(theo_premium, 2),
            'deviation':        round(deviation, 2),
            'deviation_pct':    round(deviation_pct, 3),
            'annualized_return': round(annualized, 1),
            'opportunity':      'YES' if annualized > 9 else 'NO',
            'note':             'Buy cash, sell futures. Lock in spread.' if annualized > 9 else None
        }

    def etf_premium_discount(self, etf_tickers):
        """
        Track ETF premium/discount to NAV.
        If ETF trades at premium → sell ETF, buy underlying.
        If ETF trades at discount → buy ETF, sell underlying.
        Retail can profit from the discount side.
        """
        results = []

        for ticker in etf_tickers:
            try:
                etf_price = get_latest_price(ticker)
                nav       = get_etf_nav(ticker)  # From AMC website

                premium_pct = (etf_price - nav) / nav * 100

                results.append({
                    'ticker':       ticker,
                    'etf_price':    etf_price,
                    'nav':          nav,
                    'premium_pct':  round(premium_pct, 3),
                    'signal':       'BUY — trading at discount' if premium_pct < -0.5
                                    else 'SELL — trading at premium' if premium_pct > 0.5
                                    else 'FAIR VALUE'
                })

            except Exception as e:
                results.append({'ticker': ticker, 'error': str(e)})

        return results

    def pair_trade_signals(self, pairs, lookback=60):
        """
        Pair trading: Long underperformer, short outperformer.
        Best pairs: High historical correlation + temporary divergence.
        """
        import yfinance as yf
        import numpy as np
        from scipy import stats

        signals = []

        for ticker_a, ticker_b in pairs:
            prices = yf.download(
                [ticker_a, ticker_b],
                period=f"{lookback}d",
                auto_adjust=True,
                progress=False
            )['Close']

            # Calculate spread (ratio)
            ratio       = prices[ticker_a] / prices[ticker_b]
            ratio_mean  = ratio.mean()
            ratio_std   = ratio.std()
            current     = ratio.iloc[-1]
            z_score     = (current - ratio_mean) / ratio_std

            # Correlation
            corr = prices[ticker_a].corr(prices[ticker_b])

            if abs(z_score) > 2 and corr > 0.80:
                if z_score > 2:
                    action = f"SHORT {ticker_a}, LONG {ticker_b} — ratio too high"
                else:
                    action = f"LONG {ticker_a}, SHORT {ticker_b} — ratio too low"

                signals.append({
                    'pair':         f"{ticker_a}/{ticker_b}",
                    'z_score':      round(z_score, 2),
                    'correlation':  round(corr, 3),
                    'action':       action,
                    'current_ratio': round(current, 4),
                    'mean_ratio':   round(ratio_mean, 4),
                    'signal':       'STRONG' if abs(z_score) > 2.5 else 'MODERATE'
                })

        return sorted(signals, key=lambda x: abs(x['z_score']), reverse=True)

# Key India pairs to monitor
INDIA_PAIRS = [
    ('HDFCBANK.NS', 'ICICIBANK.NS'),
    ('TCS.NS',      'INFY.NS'),
    ('HINDUNILVR.NS', 'ITC.NS'),
    ('MARUTI.NS',   'TATAMOTORS.NS'),
    ('ONGC.NS',     'OIL.NS'),
    ('ADANIPORTS.NS', 'CONCOR.NS'),
]
```

---

# SECTION 44 — MACHINE LEARNING LAYER

## 44.1 Price Direction Classifier

```python
class TradingMLEngine:
    """
    Train ML models on your own TimescaleDB data.
    Personalized to how YOUR market context works.
    """

    def build_feature_set(self, ticker, date_range):
        """
        Build feature matrix for ML training.
        50+ features from technical, fundamental, sentiment.
        """
        features = {}

        price_data = get_price_history(ticker, date_range)

        # Technical features
        features['rsi_14']          = calculate_rsi(price_data, 14)
        features['rsi_5']           = calculate_rsi(price_data, 5)
        features['macd_signal']     = calculate_macd(price_data)['signal']
        features['bb_position']     = calculate_bb_position(price_data)
        features['atr_14']          = calculate_atr(price_data, 14)
        features['volume_ratio']    = calculate_volume_ratio(price_data)
        features['price_vs_20ma']   = calculate_ma_deviation(price_data, 20)
        features['price_vs_50ma']   = calculate_ma_deviation(price_data, 50)
        features['price_vs_200ma']  = calculate_ma_deviation(price_data, 200)

        # Momentum features
        features['mom_5d']  = price_data['close'].pct_change(5).iloc[-1]
        features['mom_21d'] = price_data['close'].pct_change(21).iloc[-1]
        features['mom_63d'] = price_data['close'].pct_change(63).iloc[-1]

        # Fundamental features
        fundamentals = get_fundamentals(ticker)
        features['pe_ratio']        = fundamentals.get('pe_ratio', 0)
        features['pb_ratio']        = fundamentals.get('pb_ratio', 0)
        features['roe']             = fundamentals.get('roe', 0)
        features['revenue_growth']  = fundamentals.get('revenue_growth', 0)
        features['debt_equity']     = fundamentals.get('debt_equity', 0)

        # Sentiment features
        sentiment = get_sentiment_scores(ticker)
        features['news_sentiment']  = sentiment.get('news', 0)
        features['social_sentiment'] = sentiment.get('social', 0)
        features['fii_flow_5d']     = get_fii_flow(days=5)

        # Options features
        chain = get_option_chain(ticker)
        if chain:
            features['pcr']         = calculate_pcr(chain)
            features['atm_iv']      = get_atm_iv(chain)
            features['iv_rank']     = get_iv_rank(ticker)
            features['max_pain_distance'] = (get_max_pain(chain) - price_data['close'].iloc[-1]) / price_data['close'].iloc[-1]

        # Market context
        features['india_vix']       = get_india_vix()
        features['nifty_vs_200ma']  = get_nifty_vs_200ma()
        features['usd_inr']         = get_usdinr()

        return features

    def train_direction_classifier(self, ticker, lookback_years=3):
        """
        XGBoost classifier: Will stock beat NIFTY next 30 days?
        Binary classification — personalized to each stock.
        """
        import xgboost as xgb
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score, classification_report

        # Build training data
        X_list, y_list = [], []
        dates           = get_trading_dates(ticker, lookback_years)

        for d in dates[:-30]:  # Leave 30 days for label
            features = self.build_feature_set(ticker, d)
            label    = self.get_30d_outperformance(ticker, d)

            if features and label is not None:
                X_list.append(list(features.values()))
                y_list.append(label)

        X = np.array(X_list)
        y = np.array(y_list)

        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False  # Time-based split
        )

        # Train XGBoost
        model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.05,
            use_label_encoder=False,
            eval_metric='logloss'
        )
        model.fit(X_train, y_train)

        # Evaluate
        y_pred   = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        # Feature importance
        importance = dict(zip(features.keys(), model.feature_importances_))
        top_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            'model':            model,
            'accuracy':         accuracy,
            'top_features':     top_features,
            'training_samples': len(X_train),
            'message':          f"Model trained on {len(X_train)} samples. Accuracy: {accuracy*100:.1f}%"
        }

    def anomaly_detector(self, ticker, lookback=60):
        """
        Detect unusual market activity before announced news.
        Uses Isolation Forest — unsupervised anomaly detection.
        """
        from sklearn.ensemble import IsolationForest

        data = get_price_and_volume_history(ticker, lookback)

        features = pd.DataFrame({
            'volume_ratio':     data['volume'] / data['volume'].rolling(20).mean(),
            'price_change':     data['close'].pct_change(),
            'volatility':       data['close'].pct_change().rolling(5).std(),
            'options_volume':   data.get('options_volume', pd.Series([0]*len(data))),
        }).dropna()

        model = IsolationForest(contamination=0.05, random_state=42)
        model.fit(features)

        predictions = model.predict(features)
        anomaly_dates = features.index[predictions == -1]

        return {
            'anomaly_dates':    list(anomaly_dates.strftime('%Y-%m-%d')),
            'latest_anomaly':   anomaly_dates[-1].strftime('%Y-%m-%d') if len(anomaly_dates) > 0 else None,
            'is_current_anomaly': predictions[-1] == -1,
            'signal':           '⚠️ UNUSUAL ACTIVITY DETECTED — check for news' if predictions[-1] == -1 else 'Normal'
        }
```

## 44.2 Personalized Edge Discovery

```python
def discover_personal_edge(profile_id):
    """
    After 3+ months of trading:
    Find statistically significant edges in your own decisions.
    Where do YOU add alpha vs the AI signal?
    """
    decisions = get_all_decisions(profile_id, min_trades=50)

    # Segment by various dimensions
    analysis = {}

    # By time of day
    decisions['hour'] = pd.to_datetime(decisions['entry_time']).dt.hour
    by_hour = decisions.groupby('hour')['outcome_return'].agg(['mean', 'count', 'std'])
    analysis['best_hours'] = by_hour.nlargest(3, 'mean').to_dict()

    # By day of week
    decisions['day'] = pd.to_datetime(decisions['entry_date']).dt.day_name()
    by_day = decisions.groupby('day')['outcome_return'].agg(['mean', 'count'])
    analysis['best_days'] = by_day.nlargest(2, 'mean').to_dict()

    # By sector
    by_sector = decisions.groupby('sector')['outcome_return'].agg(['mean', 'count'])
    analysis['best_sectors'] = by_sector.nlargest(3, 'mean').to_dict()

    # AI agreement vs override
    agree_mask     = decisions['ai_override'] == False
    override_mask  = decisions['ai_override'] == True

    analysis['agreement_return'] = decisions[agree_mask]['outcome_return'].mean()
    analysis['override_return']  = decisions[override_mask]['outcome_return'].mean()
    analysis['override_edge']    = analysis['override_return'] - analysis['agreement_return']

    # By conviction level
    for conv in range(1, 11):
        mask = decisions['conviction'] == conv
        if mask.sum() >= 5:
            analysis[f'conv_{conv}_return'] = decisions[mask]['outcome_return'].mean()

    # Generate insights
    insights = []

    if analysis['override_edge'] > 0.02:
        insights.append(f"YOUR OVERRIDES ADD VALUE: +{analysis['override_edge']*100:.1f}% vs following AI")
    elif analysis['override_edge'] < -0.02:
        insights.append(f"YOUR OVERRIDES HURT: -{abs(analysis['override_edge'])*100:.1f}% vs following AI. Trust the model more.")

    best_hour = max(analysis['best_hours'], key=lambda h: analysis['best_hours'][h]['mean'])
    insights.append(f"BEST TRADING HOUR: {best_hour}:00 — {analysis['best_hours'][best_hour]['mean']*100:.1f}% avg return")

    return {
        'analysis':     analysis,
        'insights':     insights,
        'sample_size':  len(decisions),
        'message':      'Insufficient data — need 50+ completed trades' if len(decisions) < 50 else 'Edge analysis complete'
    }
```

---

# SECTION 45 — APPLE ECOSYSTEM INTEGRATION

## 45.1 Siri Shortcuts Setup

```
SHORTCUT 1: "Portfolio Status"
  Trigger: "Hey Siri, portfolio status"
  Actions:
    1. Get Contents of URL:
       URL: https://api.yourdomain.com/api/voice/portfolio-status
       Method: GET
       Headers: Authorization: Bearer {stored_token}
    2. Get text from response JSON (field: "speech_text")
    3. Speak Text: {speech_text}
    4. Show Notification: {summary_text}

SHORTCUT 2: "Market Brief"
  Trigger: "Hey Siri, morning brief"
  Actions:
    1. Get Contents of URL:
       URL: https://api.yourdomain.com/api/voice/morning-brief
    2. Speak Text: {brief}

SHORTCUT 3: "Check Ticker"
  Trigger: "Hey Siri, check [ticker]"
  Actions:
    1. Ask for Input: "Which stock?"
    2. Get Contents of URL:
       URL: https://api.yourdomain.com/api/voice/check/{input}
    3. Speak Text: {result}

SHORTCUT 4: "Add Research Note"
  Trigger: "Hey Siri, research note"
  Actions:
    1. Ask for Input: "Which stock?"
    2. Ask for Input: "Your thought?"
    3. Get Contents of URL:
       URL: https://api.yourdomain.com/api/research/voice-note
       Method: POST
       Body: {"ticker": input1, "note": input2}
    4. Show Notification: "Note saved for {input1}"
```

```python
# FastAPI endpoints for Siri integration
@app.get("/api/voice/portfolio-status")
async def voice_portfolio_status(token = Depends(verify_token)):
    portfolio = get_portfolio(int(token['sub']))
    vix       = get_india_vix()

    # Format for speech (no markdown, no symbols)
    speech = (
        f"Your portfolio is worth {format_currency_speech(portfolio.total_value)}. "
        f"Today's change is {format_pnl_speech(portfolio.day_pnl)}. "
        f"India VIX is at {vix:.1f}. "
        f"You have {len(portfolio.open_alerts)} active alerts."
    )

    return {
        'speech_text':  speech,
        'summary_text': f"Portfolio: {format_currency_speech(portfolio.total_value)} | "
                        f"Today: {format_pnl_speech(portfolio.day_pnl)}",
        'data':         portfolio.to_dict()
    }

def format_currency_speech(amount):
    """Convert number to speakable format"""
    if amount >= 1e7:
        return f"{amount/1e7:.1f} crore rupees"
    elif amount >= 1e5:
        return f"{amount/1e5:.1f} lakh rupees"
    else:
        return f"{amount:,.0f} rupees"

def format_pnl_speech(pnl):
    direction = "up" if pnl >= 0 else "down"
    return f"{direction} {format_currency_speech(abs(pnl))}"
```

## 45.2 Apple Watch Integration

```swift
// WatchKit App for FinanceLab
// Displays portfolio P&L on watch face

import WatchKit
import WatchConnectivity

class InterfaceController: WKInterfaceController {

    @IBOutlet var pnlLabel: WKInterfaceLabel!
    @IBOutlet var niftyLabel: WKInterfaceLabel!
    @IBOutlet var alertsBadge: WKInterfaceLabel!

    override func awake(withContext context: Any?) {
        super.awake(withContext: context)
        fetchPortfolioData()
    }

    func fetchPortfolioData() {
        guard let url = URL(string: "https://api.yourdomain.com/api/voice/portfolio-status") else { return }

        var request = URLRequest(url: url)
        request.setValue("Bearer \(getStoredToken())", forHTTPHeaderField: "Authorization")

        URLSession.shared.dataTask(with: request) { data, _, _ in
            guard let data = data,
                  let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                  let portfolioData = json["data"] as? [String: Any] else { return }

            DispatchQueue.main.async {
                let pnl = portfolioData["day_pnl"] as? Double ?? 0
                let pnlStr = pnl >= 0 ? "+₹\(String(format: "%.0f", pnl))" : "-₹\(String(format: "%.0f", abs(pnl)))"

                self.pnlLabel.setText(pnlStr)
                self.pnlLabel.setTextColor(pnl >= 0 ? .green : .red)

                if let alerts = portfolioData["alert_count"] as? Int, alerts > 0 {
                    self.alertsBadge.setText("\(alerts) alerts")
                    self.alertsBadge.setHidden(false)
                }
            }
        }.resume()
    }
}

// Watch Complication — shows on watch face
// Display: Portfolio P&L or NIFTY level
// Updates every 30 minutes (background refresh limit)
```

## 45.3 iPhone Widget

```swift
// iOS Home Screen Widget (WidgetKit)
// Shows portfolio summary on home screen

import WidgetKit
import SwiftUI

struct FinanceLabWidget: Widget {
    let kind: String = "FinanceLabWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: Provider()) { entry in
            PortfolioWidgetView(entry: entry)
        }
        .configurationDisplayName("FinanceLab Portfolio")
        .description("Your portfolio at a glance")
        .supportedFamilies([.systemSmall, .systemMedium])
    }
}

struct PortfolioWidgetView: View {
    var entry: PortfolioEntry

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text("FinanceLab")
                .font(.caption)
                .foregroundColor(.secondary)

            Text(entry.totalValueStr)
                .font(.title3)
                .fontWeight(.bold)

            Text(entry.dayPnlStr)
                .font(.caption)
                .foregroundColor(entry.dayPnl >= 0 ? .green : .red)

            if !entry.alerts.isEmpty {
                Text("⚠️ \(entry.alerts.count) alerts")
                    .font(.caption2)
                    .foregroundColor(.orange)
            }
        }
        .padding(8)
        .background(Color(.systemBackground))
    }
}
```

## 45.4 Apple Health Integration

```python
# Bridge: Apple Health → FinanceLab (via Shortcuts + API)

@app.post("/api/health/log")
async def log_health_data(
    sleep_hours:    float = None,
    heart_rate_avg: float = None,
    steps:          int   = None,
    stress_score:   int   = None,  # 1-10 manual entry
    token = Depends(verify_token)
):
    """
    Log health metrics before trading session.
    Correlates with trading performance over time.
    """
    health_log = {
        'profile_id':   int(token['sub']),
        'date':         date.today().isoformat(),
        'sleep_hours':  sleep_hours,
        'heart_rate':   heart_rate_avg,
        'steps':        steps,
        'stress':       stress_score,
    }

    # Save to DB
    save_health_log(health_log)

    # Calculate trading readiness score
    readiness = calculate_readiness(health_log)

    return {
        'logged':           True,
        'readiness_score':  readiness['score'],
        'recommendation':   readiness['recommendation'],
        'warning':          readiness.get('warning')
    }

def calculate_readiness(health_data):
    score = 100

    if health_data.get('sleep_hours'):
        sleep = health_data['sleep_hours']
        if sleep < 5:
            score -= 40
        elif sleep < 6:
            score -= 20
        elif sleep < 7:
            score -= 10

    if health_data.get('stress_score'):
        stress = health_data['stress_score']
        if stress >= 8:
            score -= 30
        elif stress >= 6:
            score -= 15

    if health_data.get('heart_rate_avg'):
        hr = health_data['heart_rate_avg']
        if hr > 85:
            score -= 10  # Elevated resting HR = physiological stress

    recommendation = (
        'Excellent trading conditions — proceed normally' if score >= 80
        else 'Good — slightly cautious today' if score >= 65
        else 'Suboptimal — stick to rules strictly, no overrides' if score >= 50
        else '⚠️ Poor readiness — avoid new positions today'
    )

    return {
        'score':            score,
        'recommendation':   recommendation,
        'warning':          'DISABLE GO BUTTON recommended' if score < 50 else None
    }
```

---

# SECTION 46 — TAX FORM GENERATION

## 46.1 India ITR Data Generator

```python
class IndiaITRGenerator:
    """
    Generate all data needed for India tax filing.
    Covers equity, F&O, MF, dividends.
    Output: Excel format your CA recognizes.
    """

    def generate_schedule_cg(self, profile_id, tax_year):
        """
        Schedule CG (Capital Gains) for ITR-3.
        Lists every equity/MF sale with gain/loss classification.
        """
        trades = get_completed_trades(profile_id, tax_year)

        stcg_equity = []
        ltcg_equity = []

        for trade in trades:
            if trade['instrument_type'] not in ['equity', 'mf_equity']:
                continue

            holding_days = (trade['exit_date'] - trade['entry_date']).days

            entry = {
                'Name of company':  trade['company_name'],
                'Date of Purchase': trade['entry_date'].strftime('%d/%m/%Y'),
                'Date of Sale':     trade['exit_date'].strftime('%d/%m/%Y'),
                'Cost of Acquisition': round(trade['cost_basis'], 2),
                'Sale Consideration':  round(trade['proceeds'], 2),
                'Brokerage & Charges': round(trade['total_charges'], 2),
                'Net Gain/Loss':       round(trade['net_gain'], 2),
            }

            if holding_days < 365:
                stcg_equity.append(entry)
            else:
                entry['FMV as on 31/01/2018'] = trade.get('fmv_2018', 'N/A')  # Grandfathering
                ltcg_equity.append(entry)

        stcg_df = pd.DataFrame(stcg_equity)
        ltcg_df = pd.DataFrame(ltcg_equity)

        stcg_total = stcg_df['Net Gain/Loss'].sum() if not stcg_df.empty else 0
        ltcg_gross = ltcg_df['Net Gain/Loss'].sum() if not ltcg_df.empty else 0
        ltcg_exempt = min(100000, max(0, ltcg_gross))  # ₹1L exemption
        ltcg_taxable = max(0, ltcg_gross - ltcg_exempt)

        return {
            'stcg_transactions':    stcg_df,
            'ltcg_transactions':    ltcg_df,
            'stcg_total':           round(stcg_total, 2),
            'ltcg_gross':           round(ltcg_gross, 2),
            'ltcg_exempt':          round(ltcg_exempt, 2),
            'ltcg_taxable':         round(ltcg_taxable, 2),
            'stcg_tax':             round(max(0, stcg_total) * 0.15 * 1.04, 2),
            'ltcg_tax':             round(ltcg_taxable * 0.10 * 1.04, 2),
        }

    def generate_fo_summary(self, profile_id, tax_year):
        """
        F&O Summary for Schedule BP (Business Profit).
        Turnover calculation as per ICAI guidelines.
        """
        fo_trades = get_fo_trades(profile_id, tax_year)

        total_profit    = 0
        total_loss      = 0
        turnover        = 0
        expenses        = {}

        for trade in fo_trades:
            pnl = trade['realized_pnl']
            if pnl > 0:
                total_profit += pnl
            else:
                total_loss += abs(pnl)

            # F&O turnover = absolute value of all P&L
            turnover += abs(pnl)

            # Track expenses
            expenses['brokerage']   = expenses.get('brokerage', 0) + trade['brokerage']
            expenses['stt']         = expenses.get('stt', 0) + trade['stt']
            expenses['gst']         = expenses.get('gst', 0) + trade['gst']
            expenses['stamp_duty']  = expenses.get('stamp_duty', 0) + trade['stamp_duty']

        net_fo_income   = total_profit - total_loss
        total_expenses  = sum(expenses.values())
        taxable_income  = net_fo_income - total_expenses

        # Audit requirement check
        audit_required = (
            turnover > 10_00_00_00_000 or  # > ₹10 crore
            (net_fo_income < 0 and turnover > 1_00_00_000)  # Loss with turnover > ₹1Cr
        )

        return {
            'gross_profit':     round(total_profit, 2),
            'gross_loss':       round(total_loss, 2),
            'net_income':       round(net_fo_income, 2),
            'turnover':         round(turnover, 2),
            'expenses':         {k: round(v, 2) for k, v in expenses.items()},
            'total_expenses':   round(total_expenses, 2),
            'taxable_income':   round(taxable_income, 2),
            'audit_required':   audit_required,
            'audit_threshold':  f"Turnover: ₹{turnover/1e7:.1f}Cr vs ₹10Cr threshold",
            'carry_forward':    round(max(0, -taxable_income), 2) if taxable_income < 0 else 0
        }

    def export_to_excel(self, profile_id, tax_year):
        """
        Export complete tax data to Excel.
        Format your CA expects.
        """
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

        wb = openpyxl.Workbook()

        # Sheet 1: STCG
        stcg_data = self.generate_schedule_cg(profile_id, tax_year)

        ws_stcg = wb.active
        ws_stcg.title = "STCG - Equity"
        stcg_data['stcg_transactions'].to_excel(ws_stcg, index=False)

        # Sheet 2: LTCG
        ws_ltcg = wb.create_sheet("LTCG - Equity")
        stcg_data['ltcg_transactions'].to_excel(ws_ltcg, index=False)

        # Sheet 3: F&O
        ws_fo = wb.create_sheet("F&O - Business Income")
        fo_data = self.generate_fo_summary(profile_id, tax_year)
        fo_df   = pd.DataFrame([fo_data])
        fo_df.to_excel(ws_fo, index=False)

        # Sheet 4: Summary
        ws_summary = wb.create_sheet("TAX SUMMARY")
        summary = [
            ['FinanceLab Tax Summary', f'FY {tax_year}'],
            [''],
            ['STCG (15% flat)', stcg_data['stcg_total'], stcg_data['stcg_tax']],
            ['LTCG (10% above ₹1L)', stcg_data['ltcg_taxable'], stcg_data['ltcg_tax']],
            ['F&O Business Income', fo_data['taxable_income'], fo_data['taxable_income'] * 0.30],
            [''],
            ['TOTAL ESTIMATED TAX', '', stcg_data['stcg_tax'] + stcg_data['ltcg_tax'] + fo_data.get('taxable_income', 0) * 0.30],
        ]

        for row in summary:
            ws_summary.append(row)

        # Save
        filename = f"FinanceLab_Tax_FY{tax_year}_{date.today()}.xlsx"
        filepath = f"/tmp/{filename}"
        wb.save(filepath)

        return filepath
```

---

# SECTION 47 — INSURANCE AND LIABILITY INTEGRATION

## 47.1 Complete Liability Tracker

```python
class LiabilityTracker:
    """
    True net worth = Assets - Liabilities.
    Most portfolio systems ignore liabilities.
    """

    def calculate_true_net_worth(self, profile_id):
        assets      = get_total_assets(profile_id)        # From portfolio system
        liabilities = self.get_all_liabilities(profile_id)

        total_liabilities = sum(l['outstanding'] for l in liabilities)
        net_worth         = assets - total_liabilities

        # Liquidity analysis
        liquid_assets   = get_liquid_assets(profile_id)
        short_term_liab = sum(l['outstanding'] for l in liabilities if l.get('months_to_maturity', 999) <= 12)

        return {
            'gross_assets':         assets,
            'total_liabilities':    total_liabilities,
            'net_worth':            net_worth,
            'liquid_assets':        liquid_assets,
            'short_term_liabilities': short_term_liab,
            'quick_ratio':          liquid_assets / short_term_liab if short_term_liab > 0 else float('inf'),
            'liabilities_detail':   liabilities
        }

    def insurance_adequacy_check(self, profile_id):
        """
        Is your insurance coverage adequate?
        Most people are severely underinsured.
        """
        profile        = get_profile(profile_id)
        annual_income  = profile.annual_income
        total_loans    = self.get_total_loan_outstanding(profile_id)
        dependents     = profile.num_dependents

        # Recommended term cover
        recommended_term = max(
            annual_income * 15,         # 15x annual income
            total_loans * 1.5,          # 1.5x all loans
            annual_income * 10 * dependents  # 10x income per dependent
        )

        current_life_cover = get_life_insurance_cover(profile_id)
        gap_life           = max(0, recommended_term - current_life_cover)

        # Health insurance adequacy
        # Minimum ₹10L for family in metro city
        recommended_health = 2000000 if profile.city_tier == 1 else 1000000
        current_health     = get_health_insurance_cover(profile_id)
        gap_health         = max(0, recommended_health - current_health)

        alerts = []
        if gap_life > 0:
            alerts.append({
                'type':     'LIFE_INSURANCE',
                'urgency':  'HIGH',
                'message':  f"Underinsured by ₹{gap_life/1e7:.1f}Cr in life cover",
                'action':   f"Get term plan for ₹{recommended_term/1e7:.0f}Cr — costs ~₹{self.estimate_term_premium(recommended_term, profile.age):,.0f}/year"
            })

        if gap_health > 0:
            alerts.append({
                'type':     'HEALTH_INSURANCE',
                'urgency':  'HIGH',
                'message':  f"Health cover inadequate — need ₹{recommended_health/1e5:.0f}L minimum",
                'action':   f"Top-up policy for additional ₹{gap_health/1e5:.0f}L"
            })

        # Check renewal dates
        upcoming_renewals = self.get_upcoming_renewals(profile_id, days=60)
        for renewal in upcoming_renewals:
            alerts.append({
                'type':     'RENEWAL',
                'urgency':  'MEDIUM',
                'message':  f"{renewal['policy_name']} renews in {renewal['days']} days",
                'action':   f"Renew before {renewal['renewal_date']} to avoid lapse"
            })

        return {
            'life_cover':       current_life_cover,
            'recommended_life': recommended_term,
            'life_gap':         gap_life,
            'health_cover':     current_health,
            'health_gap':       gap_health,
            'adequacy_score':   self.insurance_score(current_life_cover, recommended_term,
                                                      current_health, recommended_health),
            'alerts':           alerts
        }

    def nomination_audit(self, profile_id):
        """
        Most people die with unnominated accounts.
        Force a systematic check.
        """
        accounts = get_all_financial_accounts(profile_id)
        unnominated = []

        for account in accounts:
            if not account.get('nominee'):
                unnominated.append({
                    'account':  account['name'],
                    'type':     account['type'],
                    'value':    account['current_value'],
                    'urgency':  'HIGH' — this money could be inaccessible to family'
                })

        return {
            'total_accounts':       len(accounts),
            'unnominated_count':    len(unnominated),
            'unnominated_value':    sum(a['value'] for a in unnominated),
            'unnominated':          unnominated,
            'action_required':      len(unnominated) > 0
        }
```

---

# SECTION 48 — COMPETITIVE INTELLIGENCE

## 48.1 Company vs Competitors

```python
class CompetitiveIntelligence:

    def peer_comparison(self, ticker, metrics=['pe_ratio', 'pb_ratio', 'roe', 'revenue_growth', 'peg_ratio']):
        """
        How does this stock compare to sector peers?
        Identify relative value.
        """
        sector  = get_sector(ticker)
        peers   = get_sector_peers(sector, exclude=[ticker])[:10]

        company_data = get_fundamentals(ticker)
        peer_data    = {}

        for peer in peers:
            peer_data[peer] = get_fundamentals(peer)

        # Calculate percentile rank for each metric
        results = {'company': ticker, 'metrics': {}}

        for metric in metrics:
            company_val = company_data.get(metric)
            peer_vals   = [peer_data[p].get(metric) for p in peers if peer_data[p].get(metric)]

            if company_val is None or not peer_vals:
                continue

            # Percentile rank (higher = more expensive / better depending on metric)
            rank = sum(1 for v in peer_vals if v < company_val) / len(peer_vals)

            results['metrics'][metric] = {
                'company_value':    company_val,
                'sector_median':    np.median(peer_vals),
                'sector_min':       min(peer_vals),
                'sector_max':       max(peer_vals),
                'percentile':       round(rank * 100, 0),
                'interpretation':   self.interpret_metric(metric, rank)
            }

        # Overall relative value score
        pe_pct  = results['metrics'].get('pe_ratio', {}).get('percentile', 50)
        roe_pct = results['metrics'].get('roe', {}).get('percentile', 50)

        # Cheap PE + high ROE = value opportunity
        value_score = (100 - pe_pct) * 0.5 + roe_pct * 0.5

        results['relative_value_score'] = round(value_score, 0)
        results['verdict'] = (
            'ATTRACTIVELY VALUED vs peers' if value_score >= 70
            else 'FAIRLY VALUED vs peers' if value_score >= 40
            else 'EXPENSIVE vs peers — need strong growth justification'
        )

        return results

    def market_share_tracker(self, company, competitors, metric='revenue'):
        """
        Track market share evolution over quarters.
        """
        all_companies = [company] + competitors
        data          = {}

        for c in all_companies:
            financials = get_quarterly_financials(c, quarters=8)
            data[c]    = [q.get(metric, 0) for q in financials]

        # Calculate market share
        total_market  = [sum(data[c][i] for c in all_companies) for i in range(len(data[company]))]
        market_share  = {c: [data[c][i] / total_market[i] if total_market[i] > 0 else 0
                              for i in range(len(data[company]))]
                         for c in all_companies}

        # Trend
        company_trend = market_share[company]
        recent_change = company_trend[-1] - company_trend[0] if len(company_trend) > 1 else 0

        return {
            'market_shares':    market_share,
            'trend':            'GAINING' if recent_change > 0.01
                                else 'LOSING' if recent_change < -0.01
                                else 'STABLE',
            'change_pct':       round(recent_change * 100, 2),
            'current_share':    round(company_trend[-1] * 100, 2)
        }
```

---

# SECTION 49 — FAMILY OFFICE AND PORTFOLIO CONSOLIDATION

## 49.1 Consolidated Family Dashboard

```python
class FamilyOfficeEngine:
    """
    Aggregate wealth view across all family members.
    True family office functionality.
    """

    def consolidated_net_worth(self, family_profile_ids):
        """
        Aggregate net worth across all family members.
        Identify concentration, gaps, opportunities.
        """
        family_data = {}
        total_assets = 0
        total_liabilities = 0

        for pid in family_profile_ids:
            portfolio    = get_portfolio(pid)
            liabilities  = get_liabilities(pid)
            profile      = get_profile(pid)

            member_assets = portfolio.total_value
            member_liab   = sum(l['outstanding'] for l in liabilities)
            member_nw     = member_assets - member_liab

            family_data[pid] = {
                'name':         profile.name,
                'assets':       member_assets,
                'liabilities':  member_liab,
                'net_worth':    member_nw,
                'allocation':   portfolio.allocation_breakdown()
            }

            total_assets      += member_assets
            total_liabilities += member_liab

        family_nw = total_assets - total_liabilities

        # Family-level concentration analysis
        all_tickers = []
        for pid in family_profile_ids:
            portfolio = get_portfolio(pid)
            for pos in portfolio.positions:
                all_tickers.append({
                    'ticker':       pos.ticker,
                    'value':        pos.market_value,
                    'holder':       get_profile(pid).name
                })

        # Find overlapping positions
        ticker_exposure = {}
        for item in all_tickers:
            t = item['ticker']
            if t not in ticker_exposure:
                ticker_exposure[t] = {'total_value': 0, 'holders': []}
            ticker_exposure[t]['total_value'] += item['value']
            ticker_exposure[t]['holders'].append(item['holder'])

        # High family concentration
        concentrated = {
            t: data for t, data in ticker_exposure.items()
            if data['total_value'] / family_nw > 0.05
        }

        return {
            'family_net_worth':     family_nw,
            'total_assets':         total_assets,
            'total_liabilities':    total_liabilities,
            'members':              family_data,
            'concentrated_positions': concentrated,
            'concentration_alert':  len(concentrated) > 0,
            'diversification_score': self.family_diversification(family_data)
        }

    def gift_tax_optimizer(self, profile_id, recipient_id, amount):
        """
        Optimize asset transfers within family for tax efficiency.

        India gift tax rules:
        - Gifts from specified relatives: NOT TAXABLE (any amount)
        - Gifts from others: Taxable above ₹50,000

        Specified relatives include:
        Spouse, brother/sister, parents, grandparents,
        children, spouse's parents/siblings
        """
        sender   = get_profile(profile_id)
        receiver = get_profile(recipient_id)

        relationship = get_relationship(profile_id, recipient_id)

        SPECIFIED_RELATIVES = [
            'spouse', 'brother', 'sister', 'parent',
            'grandparent', 'child', 'grandchild',
            'spouse_parent', 'spouse_sibling'
        ]

        is_relative = relationship in SPECIFIED_RELATIVES

        return {
            'amount':           amount,
            'relationship':     relationship,
            'tax_free':         is_relative,
            'tax_if_not_relative': max(0, amount - 50000) * 0.30 if not is_relative else 0,
            'recommendation':   'TAX-FREE TRANSFER — document the relationship' if is_relative
                                else f"TAXABLE — ₹{max(0, amount-50000)*0.30:,.0f} tax on receiver"
        }
```

---

# SECTION 50 — TRADE JOURNALING WITH EMOTION

## 50.1 Emotion and Physical State Logging

```python
class EmotionTracker:
    """
    Correlate mental/physical state with trading outcomes.
    The most underrated edge in trading psychology.
    """

    PRE_TRADE_QUESTIONS = [
        {
            'id':       'mental_clarity',
            'question': 'Rate your mental clarity right now (1=foggy, 10=crystal clear)',
            'type':     'scale',
            'range':    (1, 10)
        },
        {
            'id':       'emotional_state',
            'question': 'How are you feeling emotionally? (1=very anxious, 10=calm and confident)',
            'type':     'scale',
            'range':    (1, 10)
        },
        {
            'id':       'sleep_quality',
            'question': 'How well did you sleep last night? (1=terrible, 10=excellent)',
            'type':     'scale',
            'range':    (1, 10)
        },
        {
            'id':       'recent_loss',
            'question': 'Did you have a significant loss in the last 48 hours?',
            'type':     'boolean'
        },
        {
            'id':       'fomo',
            'question': 'Are you entering this trade out of FOMO or genuine analysis?',
            'type':     'choice',
            'options':  ['Genuine analysis', 'Mild FOMO', 'Strong FOMO']
        },
        {
            'id':       'financial_pressure',
            'question': 'Are you under financial pressure that might affect your judgment?',
            'type':     'boolean'
        }
    ]

    def log_pre_trade_state(self, profile_id, ticker, responses):
        """Save pre-trade psychological state"""
        readiness = self.calculate_trading_readiness(responses)

        log = {
            'profile_id':       profile_id,
            'ticker':           ticker,
            'timestamp':        datetime.now().isoformat(),
            'mental_clarity':   responses.get('mental_clarity'),
            'emotional_state':  responses.get('emotional_state'),
            'sleep_quality':    responses.get('sleep_quality'),
            'recent_loss':      responses.get('recent_loss'),
            'fomo_level':       responses.get('fomo'),
            'financial_pressure': responses.get('financial_pressure'),
            'readiness_score':  readiness['score'],
        }

        trade_log_id = save_emotion_log(log)

        return {
            'log_id':           trade_log_id,
            'readiness_score':  readiness['score'],
            'recommendation':   readiness['recommendation'],
            'go_enabled':       readiness['score'] >= 50,
            'warning':          readiness.get('warning')
        }

    def calculate_trading_readiness(self, responses):
        score = 100

        # Mental clarity
        clarity = responses.get('mental_clarity', 7)
        if clarity < 5:     score -= 30
        elif clarity < 7:   score -= 15

        # Emotional state
        emotion = responses.get('emotional_state', 7)
        if emotion < 4:     score -= 35
        elif emotion < 6:   score -= 15

        # Sleep
        sleep = responses.get('sleep_quality', 7)
        if sleep < 4:       score -= 25
        elif sleep < 6:     score -= 10

        # Recent loss (revenge trading risk)
        if responses.get('recent_loss'):
            score -= 25

        # FOMO
        fomo = responses.get('fomo', 'Genuine analysis')
        if fomo == 'Strong FOMO':   score -= 40
        elif fomo == 'Mild FOMO':   score -= 15

        # Financial pressure
        if responses.get('financial_pressure'):
            score -= 20

        score = max(0, score)

        return {
            'score':            score,
            'recommendation':   'EXCELLENT CONDITIONS — trade normally' if score >= 85
                                else 'GOOD — proceed with care' if score >= 70
                                else 'SUBOPTIMAL — strict rules only, no overrides' if score >= 55
                                else '⚠️ POOR — avoid new positions today' if score >= 40
                                else '🔴 DANGER — do not trade today',
            'warning':          'GO button disabled — come back tomorrow' if score < 40 else None
        }

    def correlate_health_with_performance(self, profile_id):
        """
        After 50+ trades:
        Find which physical/mental states produce best returns.
        """
        emotion_logs = get_emotion_logs(profile_id)
        trade_outcomes = get_completed_trades(profile_id)

        # Join on date and ticker
        merged = pd.merge(
            emotion_logs,
            trade_outcomes,
            on=['date', 'ticker'],
            how='inner'
        )

        if len(merged) < 20:
            return {'message': 'Need 20+ trades to generate insights'}

        insights = []

        # Sleep correlation
        sleep_corr = merged['sleep_quality'].corr(merged['return_pct'])
        if abs(sleep_corr) > 0.2:
            insights.append({
                'factor':   'Sleep Quality',
                'correlation': round(sleep_corr, 3),
                'insight':  f"Strong correlation ({sleep_corr:.2f}) — sleep quality significantly impacts your returns"
            })

        # Best mental states
        merged['readiness_bucket'] = pd.cut(merged['readiness_score'], bins=[0,40,60,80,100],
                                             labels=['Poor','Below Avg','Good','Excellent'])
        by_readiness = merged.groupby('readiness_bucket')['return_pct'].mean()

        insights.append({
            'factor':   'Trading Readiness vs Returns',
            'data':     by_readiness.to_dict(),
            'insight':  f"Excellent readiness trades avg {by_readiness.get('Excellent',0)*100:.1f}% "
                        f"vs Poor readiness {by_readiness.get('Poor',0)*100:.1f}%"
        })

        return {
            'insights':     insights,
            'data':         merged.to_dict('records'),
            'sample_size':  len(merged)
        }
```

---

# SECTION 51 — LEADING INDICATORS NETWORK

## 51.1 India Early Signal Dashboard

```python
class LeadingIndicatorEngine:
    """
    Data that leads official GDP by 1-3 months.
    Free sources, genuinely predictive.
    """

    def fetch_all_leading_indicators(self):
        indicators = {}

        # 1. GST Collections (monthly - Finance Ministry)
        indicators['gst_collection'] = self.get_gst_collections()

        # 2. E-way Bills (daily/monthly - GST portal)
        indicators['eway_bills'] = self.get_eway_bill_data()

        # 3. Power Consumption (RBI bulletin)
        indicators['power_consumption'] = self.get_power_data()

        # 4. PMI Manufacturing (monthly)
        indicators['pmi_manufacturing'] = self.get_india_pmi()

        # 5. PMI Services (monthly)
        indicators['pmi_services'] = self.get_india_services_pmi()

        # 6. Credit Growth (RBI weekly)
        indicators['credit_growth'] = self.get_rbi_credit_data()

        # 7. DGCA aviation data (monthly)
        indicators['aviation'] = self.get_aviation_data()

        # 8. UPI transaction volume (NPCI monthly)
        indicators['upi_volume'] = self.get_upi_data()

        # 9. Foreign Tourist Arrivals (Tourism Ministry)
        indicators['tourism'] = self.get_tourism_data()

        # 10. Auto Sales (SIAM monthly)
        indicators['auto_sales'] = self.get_auto_sales()

        # Calculate composite leading indicator
        composite = self.composite_cli(indicators)

        return {
            'indicators':   indicators,
            'composite':    composite,
            'regime':       'EXPANSION' if composite > 102
                            else 'RECOVERY' if composite > 100
                            else 'SLOWDOWN' if composite > 98
                            else 'CONTRACTION'
        }

    def get_gst_collections(self):
        """
        Monthly GST collections from Finance Ministry press release.
        Rising collections = economic activity increasing.
        """
        # Finance Ministry website scraping
        url = "https://pib.gov.in/search.aspx?reg=3&lang=1&k=GST+collection&rss=yes"
        # Parse latest press release for GST numbers
        # Usually released 1st of every month

        return {
            'latest_month':     'Jan 2025',
            'collection_cr':    185000,  # ₹1.85L crore
            'yoy_growth':       8.4,
            'signal':           'STRONG' if 185000 > 175000 else 'WEAK',
            'source':           'Finance Ministry press release'
        }

    def get_upi_data(self):
        """
        UPI transaction data from NPCI.
        Rising UPI = rising consumer activity.
        Free monthly data published by NPCI.
        """
        url = "https://www.npci.org.in/what-we-do/upi/upi-ecosystem-statistics"
        # Scrape latest UPI volume and value data

        return {
            'transactions_cr':  1500,    # 1500 crore transactions
            'value_lakh_cr':    210,     # ₹210 lakh crore value
            'yoy_volume_growth': 42,
            'yoy_value_growth':  33,
            'signal':           'VERY_STRONG'
        }

    def get_auto_sales(self):
        """
        Monthly auto sales from SIAM.
        Leading indicator for consumer confidence and credit.
        """
        # SIAM website monthly data
        return {
            'passenger_vehicles':   350000,
            'two_wheelers':         1800000,
            'commercial_vehicles':  80000,
            'yoy_growth':           14.2,
            'signal':               'POSITIVE',
            'implication':          'Positive for auto, NBFC, insurance, fuel sectors'
        }

    def composite_cli(self, indicators):
        """
        Composite Leading Indicator (0-110 scale).
        Similar to OECD CLI methodology.
        Above 100 = expansion, below 100 = contraction.
        """
        weights = {
            'gst_collection':   0.25,
            'pmi_manufacturing': 0.20,
            'credit_growth':    0.20,
            'upi_volume':       0.15,
            'auto_sales':       0.10,
            'aviation':         0.10,
        }

        scores = {
            'gst_collection':   100 + indicators.get('gst_collection', {}).get('yoy_growth', 0) * 0.5,
            'pmi_manufacturing': indicators.get('pmi_manufacturing', 50) * 2,  # Scale 50 → 100
            'credit_growth':    100 + indicators.get('credit_growth', {}).get('yoy_growth', 0) * 0.3,
            'upi_volume':       100 + indicators.get('upi_volume', {}).get('yoy_volume_growth', 0) * 0.2,
            'auto_sales':       100 + indicators.get('auto_sales', {}).get('yoy_growth', 0) * 0.3,
            'aviation':         100 + indicators.get('aviation', {}).get('yoy_growth', 0) * 0.3,
        }

        cli = sum(scores.get(k, 100) * w for k, w in weights.items())
        return round(cli, 1)
```

---

# SECTION 52 — RISK-ADJUSTED PERFORMANCE ATTRIBUTION

## 52.1 Complete Attribution Framework

```python
class PerformanceAttributor:
    """
    Decompose returns to understand WHERE alpha comes from.
    This is what institutional fund managers track.
    """

    def full_attribution(self, profile_id, period='YTD'):
        """
        Break down returns into:
        1. Market beta (unavoidable)
        2. Sector selection (which sectors you chose)
        3. Stock selection (which stocks within sector)
        4. Timing (when you bought and sold)
        5. Pure alpha (unexplained — your skill)
        """
        trades      = get_period_trades(profile_id, period)
        benchmark   = get_nifty_return(period)
        portfolio_r = calculate_portfolio_return(profile_id, period)

        # Market contribution
        portfolio_beta      = calculate_portfolio_beta(profile_id)
        market_contribution = portfolio_beta * benchmark

        # Sector allocation effect
        sector_allocation   = self.sector_allocation_effect(trades, benchmark)

        # Stock selection effect
        stock_selection     = self.stock_selection_effect(trades)

        # Timing effect
        timing_effect       = self.timing_effect(trades)

        # Pure alpha
        total_explained     = market_contribution + sector_allocation + stock_selection + timing_effect
        pure_alpha          = portfolio_r - total_explained

        return {
            'total_return':         round(portfolio_r * 100, 2),
            'benchmark_return':     round(benchmark * 100, 2),
            'active_return':        round((portfolio_r - benchmark) * 100, 2),
            'attribution': {
                'market_beta':      round(market_contribution * 100, 2),
                'sector_selection': round(sector_allocation * 100, 2),
                'stock_selection':  round(stock_selection * 100, 2),
                'timing':           round(timing_effect * 100, 2),
                'pure_alpha':       round(pure_alpha * 100, 2),
            },
            'ratios': {
                'sharpe':           self.sharpe_ratio(profile_id, period),
                'sortino':          self.sortino_ratio(profile_id, period),
                'calmar':           self.calmar_ratio(profile_id, period),
                'information_ratio': round((portfolio_r - benchmark) / self.tracking_error(profile_id, period), 2),
            },
            'mae_mfe': self.mae_mfe_analysis(trades)
        }

    def mae_mfe_analysis(self, trades):
        """
        Maximum Adverse Excursion (MAE): How far against you before winning?
        Maximum Favorable Excursion (MFE): What was the max profit before exit?

        MAE > stop loss on winning trades = you got lucky
        MFE >> exit price on winning trades = leaving money on table
        """
        mae_list = []
        mfe_list = []
        capture_list = []

        for trade in trades:
            if not trade.get('price_path'):
                continue

            path    = trade['price_path']  # List of prices during holding
            entry   = trade['entry_price']

            # MAE (worst point against entry)
            if trade['action'] == 'buy':
                mae = (min(path) - entry) / entry * 100  # Negative = adverse
                mfe = (max(path) - entry) / entry * 100  # Positive = favorable
            else:  # Short
                mae = (max(path) - entry) / entry * 100
                mfe = (min(path) - entry) / entry * 100

            actual_return = (trade['exit_price'] - entry) / entry * 100

            mae_list.append(mae)
            mfe_list.append(mfe)

            if mfe > 0:
                capture_list.append(actual_return / mfe)  # Profit capture ratio

        return {
            'avg_mae':              round(np.mean(mae_list), 2) if mae_list else None,
            'avg_mfe':              round(np.mean(mfe_list), 2) if mfe_list else None,
            'avg_profit_capture':   round(np.mean(capture_list) * 100, 1) if capture_list else None,
            'interpretation': {
                'mae':  'Stops appropriately sized' if abs(np.mean(mae_list)) < 3
                        else 'Stops too wide — taking unnecessary risk',
                'mfe':  f"Capturing {np.mean(capture_list)*100:.0f}% of available profit"
                        if capture_list else 'Insufficient data'
            }
        }
```

---

# SECTION 53 — CONTENT CREATION TOOLS

## 53.1 Shareable Content Generator

```python
class ContentEngine:
    """
    Generate shareable financial content from your system data.
    Builds audience before product launch.
    """

    def generate_morning_brief_post(self, brief_data, platform='twitter'):
        """
        Convert morning brief to platform-optimized content.
        """
        import ollama

        if platform == 'twitter':
            prompt = f"""
            Convert this market brief into a Twitter/X thread.
            Each tweet max 280 characters.
            Make it engaging, data-driven, non-advisory.
            Use numbers and % changes.
            End with "Analysis powered by FinanceLab 📊"

            Brief: {brief_data}

            Format as:
            1/ [Tweet 1]
            2/ [Tweet 2]
            ...
            """
        elif platform == 'linkedin':
            prompt = f"""
            Convert this market brief into a LinkedIn post.
            Professional tone, 300-500 words.
            Include key data points.
            End with "Built with FinanceLab — my personal trading intelligence system"

            Brief: {brief_data}
            """
        elif platform == 'substack':
            prompt = f"""
            Expand this brief into a Substack newsletter section.
            800-1000 words, engaging but educational.
            Include context and implications.
            Not investment advice — educational only.

            Brief: {brief_data}
            """

        response = ollama.chat(
            model='llama3.1:8b',
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.7}
        )

        return response['message']['content']

    def generate_portfolio_wrapped(self, profile_id, year):
        """
        Year-end portfolio performance card.
        Like Spotify Wrapped but for your portfolio.
        Shareable image with key stats.
        """
        # Calculate stats
        ytd_return      = get_ytd_return(profile_id)
        best_trade      = get_best_trade(profile_id, year)
        worst_trade     = get_worst_trade(profile_id, year)
        total_trades    = get_trade_count(profile_id, year)
        win_rate        = get_win_rate(profile_id, year)
        vs_nifty        = ytd_return - get_nifty_return(year)
        tax_saved       = get_total_tax_saved(profile_id, year)

        # Generate shareable card (HTML → screenshot)
        html_card = f"""
        <div style="background: #131722; color: white; padding: 40px;
                    font-family: Arial; border-radius: 16px; width: 600px;">
            <h1 style="color: #26A69A; font-size: 28px;">My {year} FinanceLab Wrapped</h1>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 30px;">
                <div style="background: #1E2132; padding: 20px; border-radius: 12px;">
                    <div style="color: #888; font-size: 14px;">Portfolio Return</div>
                    <div style="color: {'#26A69A' if ytd_return >= 0 else '#EF5350'}; font-size: 36px; font-weight: bold;">
                        {ytd_return:+.1f}%
                    </div>
                    <div style="color: #888; font-size: 12px;">vs NIFTY: {vs_nifty:+.1f}%</div>
                </div>

                <div style="background: #1E2132; padding: 20px; border-radius: 12px;">
                    <div style="color: #888; font-size: 14px;">Win Rate</div>
                    <div style="color: #FFD700; font-size: 36px; font-weight: bold;">
                        {win_rate:.0f}%
                    </div>
                    <div style="color: #888; font-size: 12px;">{total_trades} trades</div>
                </div>

                <div style="background: #1E2132; padding: 20px; border-radius: 12px;">
                    <div style="color: #888; font-size: 14px;">Best Trade</div>
                    <div style="color: #26A69A; font-size: 24px; font-weight: bold;">
                        {best_trade['ticker']} +{best_trade['return']:.0f}%
                    </div>
                </div>

                <div style="background: #1E2132; padding: 20px; border-radius: 12px;">
                    <div style="color: #888; font-size: 14px;">Tax Saved</div>
                    <div style="color: #9C27B0; font-size: 24px; font-weight: bold;">
                        ₹{tax_saved/1000:.0f}K
                    </div>
                    <div style="color: #888; font-size: 12px;">via tax optimization</div>
                </div>
            </div>

            <div style="margin-top: 20px; color: #888; font-size: 12px; text-align: center;">
                Analyzed by FinanceLab • Personal Trading Intelligence System
            </div>
        </div>
        """

        return {
            'html':     html_card,
            'stats':    {
                'return':   ytd_return,
                'win_rate': win_rate,
                'trades':   total_trades,
                'alpha':    vs_nifty,
                'tax_saved': tax_saved
            }
        }

    def chart_of_the_day(self, ticker=None):
        """
        Generate a notable chart with annotation.
        For daily content creation.
        """
        if not ticker:
            # Find most interesting chart today
            ticker = find_most_notable_setup()

        chart_data = get_chart_data(ticker)
        pattern    = detect_pattern(ticker)
        insight    = generate_chart_insight(ticker, pattern)

        return {
            'ticker':   ticker,
            'pattern':  pattern,
            'insight':  insight,
            'caption':  f"{ticker} — {pattern}\n\n{insight}\n\n📊 FinanceLab Chart Analysis"
        }
```

---

# SECTION 54 — REGULATORY FILING TRACKER

## 54.1 NSE/BSE Filing Monitor

```python
class RegulatoryFilingTracker:
    """
    Monitor regulatory filings that move stock prices.
    Most retail investors miss these entirely.
    """

    def monitor_sebi_orders(self):
        """
        SEBI enforcement actions.
        Trading suspensions, show cause notices.
        These are material events.
        """
        url = "https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doOrders=yes"
        # Scrape SEBI orders for your watchlist companies

        return self.parse_sebi_orders(url)

    def monitor_nclt_filings(self):
        """
        NCLT (National Company Law Tribunal) filings.
        Insolvency proceedings — very negative signal.
        """
        url = "https://nclt.gov.in/case-list"
        # Monitor for companies in your watchlist appearing here

        return self.parse_nclt_cases(url)

    def monitor_drug_approvals(self):
        """
        CDSCO drug approvals/rejections for pharma holdings.
        Single most impactful event for pharma stocks.
        """
        cdsco_url = "https://cdsco.gov.in/opencms/opencms/en/Drugs/New-drug-approvals/"
        usfda_url = "https://www.fda.gov/drugs/drug-approvals-and-databases/drug-approvals"

        return {
            'india_approvals':  self.parse_cdsco(cdsco_url),
            'us_approvals':     self.parse_fda(usfda_url)
        }

    def monitor_mca_filings(self):
        """
        Ministry of Corporate Affairs — company law filings.
        Director changes, company petitions.
        """
        # MCA21 database
        url = "https://www.mca.gov.in/content/mca/global/en/mca/master-data/MDS.html"
        return self.parse_mca_filings(url)

    def edgar_8k_monitor(self, us_tickers):
        """
        SEC EDGAR 8-K filings = material events in US.
        Must be filed within 4 business days.
        Free, real-time API.
        """
        results = []

        for ticker in us_tickers:
            # Get CIK (Central Index Key) for this ticker
            cik_url = f"https://efts.sec.gov/LATEST/search-index?q={ticker}&dateRange=custom&startdt={date.today() - timedelta(7)}&enddt={date.today()}&forms=8-K"

            response = requests.get(cik_url, timeout=10)
            filings  = response.json()

            for filing in filings.get('hits', {}).get('hits', [])[:5]:
                results.append({
                    'ticker':       ticker,
                    'form_type':    '8-K',
                    'filed_date':   filing.get('_source', {}).get('file_date'),
                    'description':  filing.get('_source', {}).get('entity_name'),
                    'url':          f"https://www.sec.gov{filing.get('_source', {}).get('file_path', '')}",
                    'signal':       'MATERIAL EVENT — review immediately'
                })

        return results

    def patent_filing_monitor(self, companies):
        """
        Rising patent filings = R&D investment.
        Important signal for tech and pharma.
        """
        results = {}

        for company in companies:
            # Indian Patent Office
            url = f"https://ipindiaservices.gov.in/publicsearch/result?patentapplicant={company}"
            # Scrape patent application count and recent filings

            results[company] = {
                'recent_patents':   0,  # Count of last 12 months
                'yoy_change':       0,
                'technology_areas': [],
                'signal':           'ACTIVE R&D' if True else 'DECLINING INNOVATION'
            }

        return results

    def important_filing_score(self, filing):
        """
        Score importance of a regulatory filing.
        Higher = more urgent to review.
        """
        importance_map = {
            '8-K':                          90,  # Material event
            'SEBI_ORDER':                   95,  # Regulatory action
            'NCLT_ADMISSION':               100, # Insolvency filing
            'DRUG_APPROVAL':                85,  # FDA/CDSCO approval
            'DRUG_REJECTION':               90,  # FDA complete response letter
            'PROMOTER_PLEDGE_INCREASE':     75,
            'INSIDER_LARGE_SELL':           70,
            'AUDITOR_CHANGE':               80,
            'DIRECTOR_RESIGNATION':         65,
            'BOARD_MEETING_RESULTS':        85,
            'DIVIDEND_ANNOUNCEMENT':        60,
            'MERGER_ANNOUNCEMENT':          90,
            'BUYBACK_ANNOUNCEMENT':         70,
        }

        return importance_map.get(filing.get('type'), 50)
```

---

# SECTION 55 — EDGE CDN AND INFRASTRUCTURE OPTIMIZATION

## 55.1 Cloudflare Workers for Market Data

```javascript
// Cloudflare Worker — caches market data at global edge
// Deploy: wrangler deploy
// URL: data.yourdomain.com/api/prices/{ticker}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    // Cache configuration by data type
    const cacheConfig = {
      '/api/prices/':         { ttl: 60,    label: 'live-prices' },
      '/api/option-chain/':   { ttl: 60,    label: 'option-chain' },
      '/api/market-summary':  { ttl: 300,   label: 'market-summary' },
      '/api/indices/':        { ttl: 30,    label: 'indices' },
      '/api/fundamentals/':   { ttl: 86400, label: 'fundamentals' },
      '/api/isin/':           { ttl: 86400, label: 'isin-master' },
      '/api/lot-sizes':       { ttl: 86400, label: 'lot-sizes' },
    };

    // Determine TTL
    let ttl = 60;
    for (const [prefix, config] of Object.entries(cacheConfig)) {
      if (path.startsWith(prefix)) {
        ttl = config.ttl;
        break;
      }
    }

    // Check Cloudflare cache
    const cache = caches.default;
    const cacheKey = new Request(url.toString(), request);
    let response = await cache.match(cacheKey);

    if (response) {
      // Cache hit — return with cache header
      const headers = new Headers(response.headers);
      headers.set('X-Cache', 'HIT');
      return new Response(response.body, { headers });
    }

    // Cache miss — fetch from Mac Mini API
    const macMiniUrl = `https://api-internal.yourdomain.com${path}${url.search}`;
    const macResponse = await fetch(macMiniUrl, {
      headers: {
        'X-Internal-Key': env.INTERNAL_API_KEY,
        'CF-Connecting-IP': request.headers.get('CF-Connecting-IP')
      }
    });

    if (!macResponse.ok) {
      // Mac Mini offline — return cached data or error
      return new Response(
        JSON.stringify({
          error: 'Mac Mini temporarily unavailable',
          cached: false,
          timestamp: new Date().toISOString()
        }),
        { status: 503, headers: { 'Content-Type': 'application/json' } }
      );
    }

    // Clone and cache the response
    const responseToCache = macResponse.clone();
    const headers         = new Headers(responseToCache.headers);
    headers.set('Cache-Control', `public, max-age=${ttl}`);
    headers.set('X-Cache', 'MISS');
    headers.set('X-TTL', ttl.toString());

    const cachedResponse = new Response(responseToCache.body, { headers });
    event.waitUntil(cache.put(cacheKey, cachedResponse));

    return new Response(macResponse.body, { headers });
  }
};
```

## 55.2 Cloudflare D1 for Edge Data

```javascript
// Store non-real-time data at Cloudflare edge
// Zero latency reads globally

// wrangler.toml
// [[d1_databases]]
// binding = "DB"
// database_name = "financelab-edge"
// database_id = "your-d1-id"

// Sync from Mac Mini to D1 (runs every 5 minutes)
async function syncToD1(db, data) {
  // Sync lot sizes (changes rarely)
  await db.prepare(`
    INSERT OR REPLACE INTO lot_sizes (ticker, lot_size, updated_at)
    VALUES (?, ?, ?)
  `).bind(data.ticker, data.lotSize, Date.now()).run();

  // Sync ISIN master
  await db.prepare(`
    INSERT OR REPLACE INTO isin_master (ticker, isin, exchange, company_name)
    VALUES (?, ?, ?, ?)
  `).bind(data.ticker, data.isin, data.exchange, data.companyName).run();

  // Sync watchlist scores (daily)
  await db.prepare(`
    INSERT OR REPLACE INTO scores (ticker, composite_score, date)
    VALUES (?, ?, ?)
  `).bind(data.ticker, data.score, data.date).run();
}

// Read from D1 at edge — zero Mac Mini load for static data
export async function fetchLotSize(ticker, db) {
  const result = await db.prepare(
    'SELECT lot_size FROM lot_sizes WHERE ticker = ?'
  ).bind(ticker).first();

  return result?.lot_size;
}
```

## 55.3 Graceful Degradation Architecture

```python
class GracefulDegradation:
    """
    When Mac Mini is offline, system should still work
    for read operations using cached/edge data.
    """

    DEGRADATION_LEVELS = {
        'FULL':         'Mac Mini online — all features available',
        'PARTIAL':      'Mac Mini online but slow — using cache',
        'DEGRADED':     'Mac Mini offline — showing last cached data',
        'EMERGENCY':    'All data sources down — static mode only'
    }

    def check_system_health(self):
        checks = {
            'mac_mini_api':     self.ping_mac_mini(),
            'timescaledb':      self.ping_database(),
            'redis':            self.ping_redis(),
            'ollama':           self.ping_ollama(),
            'nse_api':          self.ping_nse(),
            'cloudflare':       True,   # Always up if you can reach this code
        }

        if all(checks.values()):
            level = 'FULL'
        elif checks['mac_mini_api'] and checks['timescaledb']:
            level = 'PARTIAL'
        elif checks['cloudflare']:
            level = 'DEGRADED'
        else:
            level = 'EMERGENCY'

        return {
            'level':        level,
            'description':  self.DEGRADATION_LEVELS[level],
            'checks':       checks,
            'user_message': self.get_user_message(level)
        }

    def get_user_message(self, level):
        messages = {
            'FULL':       None,
            'PARTIAL':    'System running on cache — data may be up to 5 minutes delayed',
            'DEGRADED':   '⚠️ Mac Mini offline — showing data from last sync. Live trading features unavailable.',
            'EMERGENCY':  '🔴 System offline — showing last known portfolio state. Do not make trading decisions.'
        }
        return messages[level]

    def fallback_portfolio_data(self, profile_id):
        """
        Return last cached portfolio state when Mac Mini is down.
        Supabase always available as fallback.
        """
        from supabase import create_client
        import os

        supabase = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_ANON_KEY')
        )

        # Last synced portfolio from Supabase mirror
        result = supabase.table('portfolio_mirror')\
            .select('*')\
            .eq('profile_id', profile_id)\
            .order('synced_at', desc=True)\
            .limit(1)\
            .execute()

        if result.data:
            data = result.data[0]
            return {
                **data,
                'is_cached':    True,
                'cache_age':    calculate_age(data['synced_at']),
                'warning':      f"Data from {data['synced_at']} — Mac Mini offline"
            }

        return {'error': 'No cached data available'}
```

## 55.4 UPS and Power Continuity

```
HARDWARE RECOMMENDATION for Mac Mini 24/7 server:

APS UPS (₹5,000-15,000):
  → APC Back-UPS 600VA (₹5,500) — basic protection
  → APC Smart-UPS 1000VA (₹12,000) — better runtime
  
  Runtime at Mac Mini M4 load (~30W):
  → 600VA: ~45 minutes
  → 1000VA: ~90 minutes

  Mac Mini UPS integration (macOS):
    System Preferences → Energy → UPS
    Set: "Sleep when UPS battery is at 20%"
    This gives graceful shutdown before power dies

  Recommended UPS settings:
    → Shutdown when battery reaches 15%
    → Cloudflare Tunnel reconnects automatically after power returns
    → TimescaleDB has WAL (Write Ahead Logging) — safe crash recovery
    → Redis is append-only — safe crash recovery
    → All sessions reconnect automatically

Secondary internet:
  → Airtel 4G hotspot as backup (~₹500/month)
  → Some routers (TP-Link, Asus) support 4G failover
  → Tailscale reconnects automatically to new IP
  → Cloudflare Tunnel reconnects in <30 seconds

Uptime Kuma alert when Mac Mini goes offline:
  → Telegram alert immediately
  → Email alert as backup
  → Monitoring continues from Uptime Kuma cloud
    (not Mac Mini — separate service)
```

---

# APPENDIX B — COMPLETE TECHNOLOGY STACK

```
LANGUAGE & RUNTIME
  Python 3.12          Core backend, data processing, AI
  TypeScript/Next.js   Web frontend
  Swift                iOS/Watch native apps

DATA LAYER
  TimescaleDB          Time-series market data
  PostgreSQL (Supabase) Profiles, decisions, research
  Redis                Cache, pub/sub, sessions
  ChromaDB             Vector embeddings for RAG
  Cloudflare D1        Edge-cached static data
  Parquet files        Historical backtesting data

AI / ML
  Ollama + llama3.1:8b Local LLM for analysis
  FinBERT              Financial news sentiment
  nomic-embed-text     RAG embeddings
  XGBoost              Direction classifier
  Prophet              Price forecasting
  scikit-learn         Anomaly detection, factor analysis

DATA SOURCES (15 free sources)
  yFinance             Global daily prices
  Kite API             India 1-min + live options
  Upstox API           India alternative data
  IBKR API             US institutional data
  OANDA API            Forex historical
  Binance API          Crypto data
  NSE unofficial       Option chains, F&O data
  FRED API             Macro economic data
  Polygon.io           US 1-min historical
  Twelve Data          Global multi-asset
  Tiingo               US prices + news sentiment
  OpenFIGI             Entity resolution
  Finnhub              News + earnings calendar
  Reddit PRAW          Social sentiment
  Binance              Crypto all intervals

HOSTING
  Mac Mini M4          Primary compute server
  Cloudflare Tunnel    Global HTTPS access
  Cloudflare Workers   Edge data caching
  Cloudflare D1        Edge SQLite
  Cloudflare Pages     Static assets CDN
  Vercel               Next.js web app hosting
  Supabase             Cloud DB mirror + auth

SERVICES
  FastAPI              REST API backend
  Streamlit            Research dashboard
  JupyterLab           Research notebooks
  Uptime Kuma          Monitoring
  Caddy                Reverse proxy
  Docker               Container management
  Tailscale            Private VPN access

ALERTS
  Telegram Bot         Real-time alerts
  Apple Push           iOS notifications
  WidgetKit            iPhone home screen
  WatchKit             Apple Watch
  Siri Shortcuts       Voice queries

CHARTING
  Apache ECharts       Bloomberg-style charts
  TradingView Widget   Quick reference charts
  Lightweight Charts   Fast candlestick
  D3.js                Custom analytics
  Plotly               Streamlit/Jupyter charts

SECURITY
  Cloudflare Zero Trust  Access authentication
  JWT tokens            API authentication
  AES-256 encryption    API key storage
  RLS (Supabase)        Row-level data isolation
  Audit logging         All admin actions tracked

COMPLIANCE
  No SEBI algo registration needed (manual execution)
  SEBI disclaimer on all pages
  F&O tax as business income (ITR-3)
  Tax form generation (Schedule CG, BP)
  Position limit monitoring
```

---

# APPENDIX C — IMPLEMENTATION PRIORITY MATRIX

```
IMPACT vs EFFORT MATRIX

HIGH IMPACT + LOW EFFORT (Do First):
  ✅ Natural language query interface
  ✅ Google Trends integration (pytrends)
  ✅ Emotion/psychology logging
  ✅ Corporate action tracker
  ✅ Tax form Excel generation
  ✅ Siri shortcuts (4 shortcuts, 1 hour setup)
  ✅ Nomination audit tracker

HIGH IMPACT + MEDIUM EFFORT (Do Next):
  ✅ Earnings intelligence system
  ✅ Insider cluster analysis
  ✅ Dividend capture optimizer
  ✅ Sector rotation model
  ✅ Altman Z-score for all holdings
  ✅ Cash-futures arbitrage scanner
  ✅ Apple Watch complication

HIGH IMPACT + HIGH EFFORT (Plan Carefully):
  ✅ ML direction classifier (needs 6mo data first)
  ✅ Full attribution framework
  ✅ Alternative data pipeline (satellite, credit card)
  ✅ Family office consolidation
  ✅ Volatility surface builder

MEDIUM IMPACT + LOW EFFORT (Quick Wins):
  ✅ App store rating tracker
  ✅ Job postings trend (basic version)
  ✅ EDGAR 8-K monitor
  ✅ Short squeeze detector (F&O proxy)
  ✅ ETF premium/discount tracker

NICE TO HAVE (When Time Allows):
  ✅ Content generation tools
  ✅ Portfolio Wrapped generator
  ✅ Patent filing monitor
  ✅ Full volatility surface 3D visualization
  ✅ Network of contacts intelligence
```

---

*FinanceLab Complete System Reference — Part 2*
*Sections 31–55 · 25 additional intelligence modules*
*Inject alongside Part 1 into Ollama RAG pipeline*
*Total system: 55 sections covering every dimension of trading intelligence*

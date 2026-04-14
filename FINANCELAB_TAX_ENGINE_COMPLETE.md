# FinanceLab — Complete Tax Engine
## India Resident · Global Investments · Cumulative Tax Bill Calculator
## US · UK · Europe · India · Cross-Border DTAA

> **Inject into:** Ollama RAG pipeline · Mac app context · FinanceLab decision engine
> **Scope:** Every asset class · Every country · Per-transaction to cumulative bill
> **User profile:** India tax resident · Trading India + US + UK + Europe markets
> **Last updated:** FY 2024-25 rates

---

## WEB SCRAPER REQUIREMENTS — TAX DATA SOURCES

```
INDIA TAX DATA:
  Income Tax Act rates:     https://incometaxindia.gov.in/pages/acts/income-tax-act.aspx
  DTAA treaties:            https://incometaxindia.gov.in/pages/international-taxation/dtaa.aspx
  Advance tax portal:       https://www.incometax.gov.in/iec/foportal/
  Form 26AS download:       https://www.incometax.gov.in/iec/foportal/ (login required)
  AIS download:             https://www.incometax.gov.in/iec/foportal/ (Annual Info Statement)
  SEBI STT rates:           https://www.sebi.gov.in/legal/circulars/
  NSE TDS data:             https://www.nseindia.com/api/tds-data
  BSE TDS data:             https://www.bseindia.com/

BROKER STATEMENT FORMATS:
  Zerodha Tax P&L:          https://console.zerodha.com/reports/tax-pnl (CSV download)
  Zerodha Contract Notes:   https://console.zerodha.com/reports/tradebook
  Upstox P&L:               https://account.upstox.com/reports
  Angel One:                https://www.angelone.in/trade/reports
  HDFC Sky:                 HDFC Securities portal
  CDSL CAS:                 https://www.cams.com/cas (email PDF)
  NSDL CAS:                 https://www.kfintech.com/cas

US TAX DATA:
  IRS tax brackets:         https://www.irs.gov/taxtopics/tc409
  FBAR portal:              https://bsaefiling.fincen.treas.gov/
  SEC EDGAR (wash sale):    https://www.sec.gov/
  Qualified dividend list:  https://www.irs.gov/pub/irs-pdf/p550.pdf

UK TAX DATA:
  HMRC CGT rates:           https://www.gov.uk/capital-gains-tax/rates
  HMRC SA100 guidance:      https://www.gov.uk/self-assessment-tax-returns
  Annual exemption:         https://www.gov.uk/capital-gains-tax/allowances

EUROPE TAX DATA:
  Germany Abgeltungsteuer:  https://www.bundesfinanzministerium.de/
  France PFU:               https://www.impots.gouv.fr/
  EU tax treaties:          https://ec.europa.eu/taxation_customs/

DTAA RATES:
  India-US DTAA:            https://incometaxindia.gov.in/Treaties/USA.pdf
  India-UK DTAA:            https://incometaxindia.gov.in/Treaties/UK.pdf
  India-Germany DTAA:       https://incometaxindia.gov.in/Treaties/Germany.pdf
  India-France DTAA:        https://incometaxindia.gov.in/Treaties/France.pdf
  India-Netherlands DTAA:   https://incometaxindia.gov.in/Treaties/Netherlands.pdf

PYTHON LIBRARIES NEEDED:
  pip install pandas numpy openpyxl pdfplumber
  pip install python-dateutil tabula-py camelot-py
  pip install babel forex-python
```

---

# SECTION A — UNIVERSAL TRANSACTION SCHEMA

## A.1 Master Transaction Record

```python
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from enum import Enum

class InstrumentType(Enum):
    EQUITY              = "equity"
    EQUITY_INTRADAY     = "equity_intraday"
    FUTURES             = "futures"
    OPTIONS             = "options"
    MUTUAL_FUND_EQUITY  = "mf_equity"
    MUTUAL_FUND_DEBT    = "mf_debt"
    ETF                 = "etf"
    BOND_GOVT           = "bond_govt"
    BOND_CORPORATE      = "bond_corporate"
    BOND_MUNI           = "bond_muni"
    REIT                = "reit"
    INVIT               = "invit"
    CRYPTO              = "crypto"
    US_EQUITY           = "us_equity"
    US_OPTIONS          = "us_options"
    US_FUTURES          = "us_futures"
    US_ETF              = "us_etf"
    US_MF               = "us_mf"
    UK_EQUITY           = "uk_equity"
    UK_ETF              = "uk_etf"
    EU_EQUITY           = "eu_equity"
    EU_ETF              = "eu_etf"
    FOREX               = "forex"
    DIVIDEND            = "dividend"
    INTEREST            = "interest"

class ActionType(Enum):
    BUY             = "buy"
    SELL            = "sell"
    DIVIDEND        = "dividend"
    INTEREST        = "interest"
    BONUS           = "bonus"
    SPLIT           = "split"
    RIGHTS_BUY      = "rights_buy"
    RIGHTS_LAPSE    = "rights_lapse"
    EXERCISE        = "exercise"     # Options exercise
    EXPIRY_ITM      = "expiry_itm"   # ITM at expiry
    EXPIRY_OTM      = "expiry_otm"   # OTM expired worthless
    ROLLOVER        = "rollover"     # Futures roll
    BUYBACK         = "buyback"      # Company buyback tender
    MERGER_RECEIVE  = "merger_receive"
    SPINOFF_RECEIVE = "spinoff_receive"

class CostBasisMethod(Enum):
    FIFO        = "fifo"          # First in first out
    LIFO        = "lifo"          # Last in first out
    HIFO        = "hifo"          # Highest cost first (US tax optimal)
    AVERAGE     = "average"       # Average cost (India default equity)
    SPECIFIC_ID = "specific_id"   # Specific lot identification
    SECTION104  = "section104"    # UK mandatory pooling

class TaxTreatment(Enum):
    # India
    INDIA_STCG_EQUITY       = "india_stcg_equity"       # 15%
    INDIA_LTCG_EQUITY       = "india_ltcg_equity"       # 10% above 1L
    INDIA_FO_BUSINESS       = "india_fo_business"       # Slab rate
    INDIA_INTRADAY_SPEC     = "india_intraday_spec"     # Slab rate
    INDIA_DEBT_SLAB         = "india_debt_slab"         # Slab rate
    INDIA_DIVIDEND_SLAB     = "india_dividend_slab"     # Slab rate
    INDIA_CRYPTO            = "india_crypto"            # 30% flat
    INDIA_REIT_ORDINARY     = "india_reit_ordinary"     # Slab rate
    # US
    US_STCG                 = "us_stcg"                 # Ordinary income
    US_LTCG_0               = "us_ltcg_0"               # 0%
    US_LTCG_15              = "us_ltcg_15"              # 15%
    US_LTCG_20              = "us_ltcg_20"              # 20%
    US_SECTION_1256         = "us_section_1256"         # 60/40 rule
    US_QUALIFIED_DIV        = "us_qualified_div"        # 15%
    US_ORDINARY_DIV         = "us_ordinary_div"         # Ordinary income
    # UK
    UK_CGT_BASIC            = "uk_cgt_basic"            # 18%
    UK_CGT_HIGHER           = "uk_cgt_higher"           # 24%
    UK_DIVIDEND_BASIC       = "uk_dividend_basic"       # 8.75%
    UK_DIVIDEND_HIGHER      = "uk_dividend_higher"      # 33.75%
    UK_ISA_EXEMPT           = "uk_isa_exempt"           # 0%
    # Germany
    DE_ABGELTUNGSTEUER      = "de_abgeltungsteuer"      # 25% + soli
    DE_CRYPTO_EXEMPT        = "de_crypto_exempt"        # 0% after 1yr
    # France
    FR_PFU                  = "fr_pfu"                  # 30% flat
    FR_PEA_EXEMPT           = "fr_pea_exempt"           # 0% after 5yr
    # Netherlands
    NL_BOX3                 = "nl_box3"                 # Deemed return
    # Spain
    ES_CGT                  = "es_cgt"                  # 19-28% progressive
    # Italy
    IT_CGT                  = "it_cgt"                  # 26%
    # Switzerland
    CH_EXEMPT               = "ch_exempt"               # 0% (private investor)
    # Cross-border
    DTAA_REDUCED            = "dtaa_reduced"            # DTAA benefit applied
    EXEMPT                  = "exempt"                  # Fully exempt

@dataclass
class Transaction:
    # Identification
    id:                 str                 # UUID
    profile_id:         int
    portfolio_id:       int                 # Which broker account

    # Instrument
    ticker:             str                 # RELIANCE.NS, AAPL, etc
    isin:               Optional[str]       # Universal identifier
    name:               str                 # Company/fund name
    instrument_type:    InstrumentType
    exchange:           str                 # NSE, BSE, NYSE, LSE, XETRA

    # Trade
    action:             ActionType
    trade_date:         date
    settlement_date:    Optional[date]      # T+1 India, T+2 US
    quantity:           Decimal
    price:              Decimal
    currency:           str                 # INR, USD, GBP, EUR

    # Charges (all in transaction currency)
    brokerage:          Decimal = Decimal('0')
    stt:                Decimal = Decimal('0')
    exchange_charges:   Decimal = Decimal('0')
    gst_on_charges:     Decimal = Decimal('0')
    stamp_duty:         Decimal = Decimal('0')
    sebi_charges:       Decimal = Decimal('0')
    dp_charges:         Decimal = Decimal('0')    # India delivery sell
    other_charges:      Decimal = Decimal('0')
    foreign_tax_withheld: Decimal = Decimal('0')  # TDS by foreign govt

    # FX (for cross-border transactions)
    inr_rate:           Optional[Decimal]   # Exchange rate at trade date
    amount_inr:         Optional[Decimal]   # Total value in INR

    # Tax calculation (auto-filled)
    total_charges:      Decimal = Decimal('0')
    net_amount:         Decimal = Decimal('0')  # After charges
    cost_basis_method:  CostBasisMethod = CostBasisMethod.AVERAGE
    matched_lots:       list = field(default_factory=list)  # FIFO/HIFO lot matching
    holding_days:       Optional[int] = None
    tax_treatment:      Optional[TaxTreatment] = None
    taxable_gain:       Optional[Decimal] = None
    tax_amount:         Optional[Decimal] = None
    wash_sale_flag:     bool = False        # US only
    wash_sale_disallowed: Decimal = Decimal('0')

    # Special fields
    option_strike:      Optional[Decimal] = None
    option_expiry:      Optional[date] = None
    option_type:        Optional[str] = None  # CE/PE/C/P
    fo_lot_size:        Optional[int] = None
    is_itm_expiry:      bool = False        # Triggers STT trap

    # Notes
    notes:              str = ""
    source:             str = "manual"      # manual, zerodha_import, etc
    verified:           bool = False        # CA verified

    # Timestamps
    created_at:         datetime = field(default_factory=datetime.now)
    updated_at:         datetime = field(default_factory=datetime.now)
```

## A.2 Portfolio (Broker Account) Schema

```python
@dataclass
class Portfolio:
    id:             int
    profile_id:     int
    name:           str             # "Zerodha - Main", "IBKR", "HDFC"
    broker:         str             # zerodha, upstox, ibkr, hdfc, angel
    account_number: str             # Masked: XXXX1234
    country:        str             # IN, US, UK, DE, FR
    currency:       str             # INR, USD, GBP, EUR
    account_type:   str             # trading, isa, roth_ira, isa_uk
                                    # regular, demat, pms

    # Tax profile for this portfolio
    cost_basis_method:  CostBasisMethod
    tax_year_start:     str         # "04-01" India, "01-01" US, "04-06" UK

    # Linked
    transactions:   list            # All transactions
    open_positions: list            # Current holdings

    is_active:      bool = True
    notes:          str = ""
```

## A.3 Broker Statement Import

```python
import pandas as pd
import pdfplumber
import re
from pathlib import Path

class BrokerStatementParser:

    def parse_zerodha_pnl(self, csv_path: str) -> list[Transaction]:
        """
        Parse Zerodha Tax P&L CSV report.
        Download from: Console → Reports → Tax P&L
        """
        df = pd.read_csv(csv_path)

        # Zerodha columns:
        # Symbol, ISIN, Quantity, Trade date, Buy price, Sell price,
        # Buy value, Sell value, Charges, Realized P&L, Trade type

        transactions = []
        for _, row in df.iterrows():
            # Parse buy transaction
            if pd.notna(row.get('Buy Date')) and row.get('Buy Value', 0) > 0:
                buy_tx = Transaction(
                    id=generate_uuid(),
                    ticker=row['Symbol'] + '.NS',
                    name=row['Symbol'],
                    instrument_type=self.detect_instrument_type(row['Symbol'], row.get('Trade Type')),
                    action=ActionType.BUY,
                    trade_date=pd.to_datetime(row['Buy Date']).date(),
                    quantity=Decimal(str(abs(row['Quantity']))),
                    price=Decimal(str(row['Buy Price'])),
                    currency='INR',
                    exchange='NSE',
                    source='zerodha_import'
                )
                # Add charges proportionally
                charges = self.calculate_zerodha_charges(buy_tx)
                buy_tx.brokerage    = charges['brokerage']
                buy_tx.stt          = charges['stt_buy']
                buy_tx.total_charges = charges['total']
                transactions.append(buy_tx)

            # Parse sell transaction
            if pd.notna(row.get('Sell Date')) and row.get('Sell Value', 0) > 0:
                sell_tx = Transaction(
                    id=generate_uuid(),
                    ticker=row['Symbol'] + '.NS',
                    name=row['Symbol'],
                    instrument_type=self.detect_instrument_type(row['Symbol'], row.get('Trade Type')),
                    action=ActionType.SELL,
                    trade_date=pd.to_datetime(row['Sell Date']).date(),
                    quantity=Decimal(str(abs(row['Quantity']))),
                    price=Decimal(str(row['Sell Price'])),
                    currency='INR',
                    exchange='NSE',
                    source='zerodha_import'
                )
                charges = self.calculate_zerodha_charges(sell_tx)
                sell_tx.brokerage   = charges['brokerage']
                sell_tx.stt         = charges['stt_sell']
                sell_tx.dp_charges  = Decimal('13.5')
                sell_tx.total_charges = charges['total']
                transactions.append(sell_tx)

        return transactions

    def parse_ibkr_activity_statement(self, csv_path: str) -> list[Transaction]:
        """
        Parse Interactive Brokers Activity Statement CSV.
        Download from: Reports → Activity → Custom Date Range → CSV
        """
        df = pd.read_csv(csv_path, skiprows=3)

        # IBKR has multiple sections in one CSV
        # Filter to Trades section
        trades_df = df[df.iloc[:, 0] == 'Trades']

        transactions = []
        for _, row in trades_df.iterrows():
            try:
                action = ActionType.BUY if float(row.get('Quantity', 0)) > 0 else ActionType.SELL
                qty    = abs(float(row.get('Quantity', 0)))
                price  = abs(float(row.get('T. Price', 0)))
                comm   = abs(float(row.get('Comm/Fee', 0)))
                curr   = row.get('Currency', 'USD')
                symbol = row.get('Symbol', '')

                # Get INR rate for the trade date
                trade_date = pd.to_datetime(row.get('Date/Time')).date()
                inr_rate   = get_historical_fx_rate(curr, 'INR', trade_date)

                tx = Transaction(
                    id=generate_uuid(),
                    ticker=symbol,
                    name=symbol,
                    instrument_type=self.detect_us_instrument_type(row),
                    action=action,
                    trade_date=trade_date,
                    quantity=Decimal(str(qty)),
                    price=Decimal(str(price)),
                    currency=curr,
                    exchange=row.get('Exchange', 'SMART'),
                    brokerage=Decimal(str(comm)),
                    inr_rate=Decimal(str(inr_rate)),
                    amount_inr=Decimal(str(qty * price * inr_rate)),
                    source='ibkr_import'
                )
                transactions.append(tx)

            except Exception as e:
                continue

        return transactions

    def parse_zerodha_fo_tradebook(self, csv_path: str) -> list[Transaction]:
        """
        Parse Zerodha F&O tradebook.
        Download from: Console → Reports → Tradebook → F&O
        """
        df = pd.read_csv(csv_path)

        transactions = []
        for _, row in df.iterrows():
            symbol = row.get('symbol', '')
            # Detect options vs futures
            if 'CE' in symbol or 'PE' in symbol:
                inst_type = InstrumentType.OPTIONS
            else:
                inst_type = InstrumentType.FUTURES

            action = ActionType.BUY if row.get('trade_type') == 'buy' else ActionType.SELL
            price  = float(row.get('price', 0))
            qty    = abs(int(row.get('quantity', 0)))

            # Calculate charges
            value   = price * qty
            charges = {
                'brokerage': min(20, value * 0.0003),
                'stt':       value * 0.000125 if action == ActionType.SELL and inst_type == InstrumentType.FUTURES
                             else value * 0.000625 if action == ActionType.SELL and inst_type == InstrumentType.OPTIONS
                             else 0,
                'exchange':  value * 0.00002,
                'gst':       0  # Calculated separately
            }

            tx = Transaction(
                id=generate_uuid(),
                ticker=symbol,
                name=symbol,
                instrument_type=inst_type,
                action=action,
                trade_date=pd.to_datetime(row.get('trade_date')).date(),
                quantity=Decimal(str(qty)),
                price=Decimal(str(price)),
                currency='INR',
                exchange='NSE',
                brokerage=Decimal(str(charges['brokerage'])),
                stt=Decimal(str(charges['stt'])),
                exchange_charges=Decimal(str(charges['exchange'])),
                source='zerodha_fo_import'
            )

            # Extract option details from symbol
            if inst_type == InstrumentType.OPTIONS:
                parts = symbol.split()
                if len(parts) >= 3:
                    tx.option_strike = Decimal(parts[-2]) if parts[-2].isdigit() else None
                    tx.option_type   = parts[-1]  # CE or PE

            transactions.append(tx)

        return transactions

    def parse_cdsl_cas(self, pdf_path: str) -> list[dict]:
        """
        Parse CDSL Consolidated Account Statement PDF.
        Shows all holdings across all brokers/DPs.
        Sent monthly to registered email.
        """
        holdings = []

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                # Parse holding details
                # CAS format: ISIN, Company, Quantity, Value
                lines = text.split('\n')
                for line in lines:
                    if re.match(r'IN[A-Z0-9]{10}', line):
                        parts = line.split()
                        if len(parts) >= 4:
                            holdings.append({
                                'isin':     parts[0],
                                'name':     ' '.join(parts[1:-2]),
                                'quantity': float(parts[-2].replace(',', '')),
                                'value':    float(parts[-1].replace(',', ''))
                            })

        return holdings

    def detect_instrument_type(self, symbol, trade_type=None):
        """Auto-detect instrument type from symbol"""
        if trade_type:
            t = str(trade_type).upper()
            if 'FUT' in t:      return InstrumentType.FUTURES
            if 'OPT' in t:      return InstrumentType.OPTIONS
            if 'EQ' in t:       return InstrumentType.EQUITY
            if 'INTRADAY' in t: return InstrumentType.EQUITY_INTRADAY

        s = symbol.upper()
        if s.endswith('-BE'):           return InstrumentType.BOND_CORPORATE
        if 'FUT' in s:                  return InstrumentType.FUTURES
        if 'CE' in s or 'PE' in s:     return InstrumentType.OPTIONS
        return InstrumentType.EQUITY
```

## A.4 Manual Transaction Entry Validation

```python
def validate_transaction(tx: Transaction) -> dict:
    """
    Validate a manually entered transaction.
    Returns errors and warnings.
    """
    errors   = []
    warnings = []

    # Required fields
    if not tx.ticker:
        errors.append("Ticker/symbol is required")
    if not tx.trade_date:
        errors.append("Trade date is required")
    if tx.quantity <= 0:
        errors.append("Quantity must be positive")
    if tx.price <= 0:
        errors.append("Price must be positive")

    # Business logic
    if tx.trade_date > date.today():
        errors.append("Trade date cannot be in the future")

    if tx.instrument_type == InstrumentType.EQUITY:
        if tx.action == ActionType.SELL:
            # Check if sufficient shares exist in portfolio
            holdings = get_current_holdings(tx.profile_id, tx.ticker, tx.portfolio_id)
            if holdings < tx.quantity:
                errors.append(f"Cannot sell {tx.quantity} — only {holdings} shares held")

    # STT warning for ITM options at expiry
    if (tx.instrument_type == InstrumentType.OPTIONS and
        tx.action == ActionType.EXPIRY_ITM):
        stt_on_intrinsic = calculate_itm_stt(tx)
        warnings.append(
            f"ITM EXPIRY STT: ₹{stt_on_intrinsic:.2f} — "
            f"vs ₹{calculate_closing_stt(tx):.2f} if closed before expiry. "
            f"Consider closing before 3:20 PM on expiry day."
        )

    # F&O turnover warning
    if tx.instrument_type in [InstrumentType.FUTURES, InstrumentType.OPTIONS]:
        ytd_turnover = get_fo_turnover_ytd(tx.profile_id)
        if ytd_turnover > 8_00_00_00_000:  # ₹8 crore
            warnings.append(
                f"F&O turnover YTD: ₹{ytd_turnover/1e7:.1f}Cr — "
                f"approaching ₹10Cr audit threshold"
            )

    # Cross-border FX rate
    if tx.currency != 'INR' and not tx.inr_rate:
        warnings.append(
            "FX rate not provided — system will use RBI reference rate for tax calculation"
        )

    return {
        'valid':    len(errors) == 0,
        'errors':   errors,
        'warnings': warnings
    }
```

---

# SECTION B — INDIA TAX ENGINE (COMPLETE)

## B.1 Tax Rates — FY 2024-25

```python
INDIA_TAX_RATES = {

    # Capital Gains — Equity (Listed)
    'stcg_equity': {
        'rate':         0.20,           # 20% from July 23, 2024 Budget
        'surcharge':    'applicable',
        'cess':         0.04,
        'holding':      '< 12 months',
        'effective':    0.208,          # 20% × 1.04 cess
        'note':         'Increased from 15% to 20% — Budget July 2024'
    },
    'ltcg_equity': {
        'rate':         0.125,          # 12.5% from July 23, 2024
        'exemption':    125000,         # ₹1.25L exempt (increased from 1L)
        'cess':         0.04,
        'holding':      '>= 12 months',
        'effective':    0.13,           # 12.5% × 1.04
        'note':         'Increased from 10% to 12.5%, exemption ₹1.25L — Budget July 2024',
        'grandfathering': 'Jan 31, 2018 FMV for pre-2018 shares'
    },

    # F&O — Business Income
    'fo_business': {
        'type':         'slab_rate',
        'slabs':        [
            (300000,    0.00),
            (600000,    0.05),
            (900000,    0.10),
            (1200000,   0.15),
            (1500000,   0.20),
            (float('inf'), 0.30)
        ],
        'regime':       'new',          # New regime default
        'cess':         0.04,
        'note':         'F&O always business income — can offset against business losses'
    },

    # Intraday Equity — Speculative Business
    'intraday_speculative': {
        'type':         'slab_rate',
        'note':         'Speculative business — can only offset against speculative profit'
    },

    # Mutual Funds
    'mf_equity_stcg': {
        'rate':         0.20,           # Same as equity STCG from July 2024
        'holding':      '< 12 months'
    },
    'mf_equity_ltcg': {
        'rate':         0.125,          # Same as equity LTCG from July 2024
        'exemption':    125000,         # ₹1.25L combined with equity LTCG
        'holding':      '>= 12 months'
    },
    'mf_debt': {
        'type':         'slab_rate',    # Post April 1, 2023 — no indexation
        'note':         'All debt MF gains at slab rate regardless of holding period'
    },

    # Dividends
    'dividend': {
        'type':         'slab_rate',
        'tds_threshold': 5000,          # TDS if dividend > ₹5,000 from one company
        'tds_rate':     0.10,
        'note':         'Grossed up and added to total income'
    },

    # Crypto / VDA (Virtual Digital Assets)
    'crypto': {
        'rate':         0.30,           # 30% flat — no exemption
        'tds':          0.01,           # 1% TDS on sale consideration
        'cess':         0.04,
        'effective':    0.312,          # 30% × 1.04
        'no_loss_offset': True,         # Cannot offset losses against anything
        'no_deductions': True,          # No deductions except cost of acquisition
        'note':         'Strictest tax regime — 30% flat regardless of holding'
    },

    # REIT/InvIT
    'reit_dividend': {
        'type':         'slab_rate',
        'note':         'Most REIT distributions = ordinary income at slab rate'
    },
    'reit_ltcg': {
        'rate':         0.20,           # Long-term
        'holding':      '>= 36 months'  # 3 years for REITs
    },

    # Bonds / Debentures (Listed)
    'bond_stcg': {
        'type':         'slab_rate',
        'holding':      '< 24 months'   # 2 years for listed bonds
    },
    'bond_ltcg': {
        'rate':         0.125,          # Post July 2024
        'holding':      '>= 24 months'
    },

    # Sovereign Gold Bonds
    'sgb_on_maturity': {
        'rate':         0.00,           # Tax-free on maturity
        'note':         'Exempt from CGT if held to 8-year maturity'
    },
    'sgb_early_redemption': {
        'rate':         0.125,          # LTCG if held > 12 months (listed)
    }
}

# Surcharge rates (on tax amount)
SURCHARGE_RATES = {
    0:          0.00,   # Up to ₹50L income
    5000000:    0.10,   # ₹50L-1Cr → 10% surcharge
    10000000:   0.15,   # ₹1Cr-2Cr → 15% surcharge
    20000000:   0.25,   # ₹2Cr-5Cr → 25% surcharge
    50000000:   0.37,   # > ₹5Cr → 37% surcharge
}

# Note: Surcharge on LTCG and STCG capped at 15%
SURCHARGE_CAP_LTCG_STCG = 0.15
```

## B.2 India Tax Calculation Engine

```python
class IndiaTaxEngine:

    def __init__(self, profile):
        self.profile        = profile
        self.tax_bracket    = profile.income_tax_bracket  # 0.05, 0.10, 0.15, 0.20, 0.30
        self.annual_income  = profile.annual_income        # Salary + other income
        self.regime         = profile.tax_regime           # 'new' or 'old'

    def classify_transaction(self, tx: Transaction) -> TaxTreatment:
        """Auto-classify every transaction"""

        # F&O
        if tx.instrument_type in [InstrumentType.FUTURES, InstrumentType.OPTIONS]:
            return TaxTreatment.INDIA_FO_BUSINESS

        # Intraday equity
        if tx.instrument_type == InstrumentType.EQUITY_INTRADAY:
            return TaxTreatment.INDIA_INTRADAY_SPEC

        # Crypto
        if tx.instrument_type == InstrumentType.CRYPTO:
            return TaxTreatment.INDIA_CRYPTO

        # Equity / ETF / MF Equity — check holding period
        if tx.instrument_type in [
            InstrumentType.EQUITY,
            InstrumentType.ETF,
            InstrumentType.MUTUAL_FUND_EQUITY,
            InstrumentType.REIT,
            InstrumentType.INVIT
        ]:
            if tx.holding_days is None:
                return None  # Need to calculate holding period first

            holding_months = tx.holding_days / 30.44  # Average days per month

            # REITs need 36 months for LTCG
            if tx.instrument_type in [InstrumentType.REIT, InstrumentType.INVIT]:
                if tx.holding_days >= 1095:  # 3 years
                    return TaxTreatment.INDIA_LTCG_EQUITY
                else:
                    return TaxTreatment.INDIA_STCG_EQUITY

            if tx.holding_days >= 365:
                return TaxTreatment.INDIA_LTCG_EQUITY
            else:
                return TaxTreatment.INDIA_STCG_EQUITY

        # Debt MF
        if tx.instrument_type == InstrumentType.MUTUAL_FUND_DEBT:
            return TaxTreatment.INDIA_DEBT_SLAB

        # Bonds
        if tx.instrument_type in [InstrumentType.BOND_GOVT, InstrumentType.BOND_CORPORATE]:
            if tx.holding_days and tx.holding_days >= 730:  # 24 months
                return TaxTreatment.INDIA_LTCG_EQUITY
            return TaxTreatment.INDIA_DEBT_SLAB

        # Dividends
        if tx.action == ActionType.DIVIDEND:
            return TaxTreatment.INDIA_DIVIDEND_SLAB

        return None

    def calculate_transaction_tax(self, tx: Transaction, cost_basis: Decimal) -> dict:
        """
        Calculate exact tax for ONE completed transaction.
        """
        # Gross gain before charges
        gross_proceeds  = tx.price * tx.quantity
        total_charges   = (tx.brokerage + tx.stt + tx.exchange_charges +
                          tx.gst_on_charges + tx.stamp_duty + tx.sebi_charges +
                          tx.dp_charges + tx.other_charges)
        net_proceeds    = gross_proceeds - total_charges
        gross_gain      = net_proceeds - cost_basis
        cost_of_acq     = cost_basis  # For clean display

        # Special case: crypto — no deductions except cost
        if tx.instrument_type == InstrumentType.CRYPTO:
            taxable_gain    = max(Decimal('0'), gross_proceeds - cost_basis)
            tax_amount      = taxable_gain * Decimal('0.30')
            cess            = tax_amount * Decimal('0.04')
            tds_deducted    = gross_proceeds * Decimal('0.01')

            return {
                'gross_proceeds':   gross_proceeds,
                'cost_basis':       cost_of_acq,
                'gross_gain':       gross_gain,
                'taxable_gain':     taxable_gain,
                'tax_rate':         '30% flat',
                'tax_amount':       tax_amount,
                'cess':             cess,
                'total_tax':        tax_amount + cess,
                'tds_deducted':     tds_deducted,
                'net_tax_payable':  max(Decimal('0'), tax_amount + cess - tds_deducted),
                'treatment':        'CRYPTO_VDA_30%_FLAT',
                'charges_deductible': False
            }

        # LTCG — grandfathering calculation (for shares bought before Jan 31, 2018)
        if (tx.tax_treatment == TaxTreatment.INDIA_LTCG_EQUITY and
            tx.trade_date >= date(2018, 1, 31)):  # Pre-2018 purchase

            fmv_jan2018     = get_historical_price(tx.ticker, date(2018, 1, 31))
            grandfathered   = max(cost_basis, min(fmv_jan2018 * tx.quantity, gross_proceeds))
            taxable_gain    = max(Decimal('0'), gross_proceeds - grandfathered)
        else:
            # Post-July 23, 2024 LTCG — no indexation
            taxable_gain    = max(Decimal('0'), gross_gain)

        # Apply LTCG exemption (₹1.25L per year — shared across all LTCG)
        # Note: Exemption applied at portfolio level, not per transaction
        # Here we just calculate the gross taxable gain

        # Tax amount
        if tx.tax_treatment == TaxTreatment.INDIA_STCG_EQUITY:
            rate            = Decimal('0.20')
            tax_amount      = taxable_gain * rate
            cess            = tax_amount * Decimal('0.04')

        elif tx.tax_treatment == TaxTreatment.INDIA_LTCG_EQUITY:
            rate            = Decimal('0.125')
            tax_amount      = taxable_gain * rate
            cess            = tax_amount * Decimal('0.04')

        elif tx.tax_treatment in [TaxTreatment.INDIA_FO_BUSINESS,
                                   TaxTreatment.INDIA_INTRADAY_SPEC,
                                   TaxTreatment.INDIA_DEBT_SLAB,
                                   TaxTreatment.INDIA_DIVIDEND_SLAB]:
            rate            = Decimal(str(self.tax_bracket))
            tax_amount      = taxable_gain * rate
            cess            = tax_amount * Decimal('0.04')

        else:
            rate            = Decimal('0')
            tax_amount      = Decimal('0')
            cess            = Decimal('0')

        # Surcharge (on capital gains, capped at 15%)
        surcharge = self.calculate_surcharge(tax_amount, is_capital_gain=True)

        total_tax = tax_amount + cess + surcharge

        return {
            'gross_proceeds':   round(gross_proceeds, 2),
            'total_charges':    round(total_charges, 2),
            'net_proceeds':     round(net_proceeds, 2),
            'cost_basis':       round(cost_of_acq, 2),
            'gross_gain':       round(gross_gain, 2),
            'taxable_gain':     round(taxable_gain, 2),
            'tax_rate':         f"{float(rate)*100:.1f}%",
            'tax_amount':       round(tax_amount, 2),
            'surcharge':        round(surcharge, 2),
            'cess':             round(cess, 2),
            'total_tax':        round(total_tax, 2),
            'net_in_pocket':    round(net_proceeds - total_tax, 2),
            'effective_rate':   round(float(total_tax / gross_gain) * 100, 2) if gross_gain > 0 else 0,
            'treatment':        tx.tax_treatment.value if tx.tax_treatment else 'unknown',
            'charges_deductible': tx.tax_treatment == TaxTreatment.INDIA_FO_BUSINESS
        }

    def calculate_surcharge(self, tax_amount: Decimal, is_capital_gain: bool = False) -> Decimal:
        """Calculate surcharge on tax amount"""
        # Estimate total income for surcharge bracket
        total_income = self.annual_income
        surcharge_rate = Decimal('0')

        for threshold, rate in sorted(SURCHARGE_RATES.items()):
            if total_income >= threshold:
                surcharge_rate = Decimal(str(rate))

        # Cap surcharge at 15% for LTCG and STCG
        if is_capital_gain:
            surcharge_rate = min(surcharge_rate, Decimal('0.15'))

        return tax_amount * surcharge_rate

    def fo_turnover_calculation(self, fo_transactions: list) -> dict:
        """
        F&O Turnover as per ICAI guidelines.
        Used to determine audit threshold.

        Futures: Absolute value of each trade's P&L
        Options: Premium received on sells +
                 Absolute value of P&L on squared-off positions
        """
        futures_turnover    = Decimal('0')
        options_turnover    = Decimal('0')
        total_profit        = Decimal('0')
        total_loss          = Decimal('0')

        # Match buy and sell pairs
        matched_trades = self.match_fo_trades(fo_transactions)

        for trade in matched_trades:
            pnl = trade['sell_value'] - trade['buy_value'] - trade['charges']

            if trade['instrument'] == 'futures':
                futures_turnover += abs(pnl)
            else:  # options
                options_turnover += trade['sell_premium_total']  # Premium received
                options_turnover += abs(pnl)  # Abs P&L on squared off

            if pnl > 0:
                total_profit += pnl
            else:
                total_loss += abs(pnl)

        total_turnover  = futures_turnover + options_turnover
        net_income      = total_profit - total_loss

        return {
            'futures_turnover':     round(futures_turnover, 2),
            'options_turnover':     round(options_turnover, 2),
            'total_turnover':       round(total_turnover, 2),
            'total_profit':         round(total_profit, 2),
            'total_loss':           round(total_loss, 2),
            'net_fo_income':        round(net_income, 2),
            'audit_required':       total_turnover >= 10_00_00_000,  # ₹10Cr
            'audit_threshold_pct':  round(float(total_turnover / 10_00_00_000) * 100, 1),
            'presumptive_tax_eligible': total_turnover <= 2_00_00_00_000  # ₹2Cr
        }
```

## B.3 India Loss Offset Rules Engine

```python
class IndiaLossOffsetEngine:
    """
    Implements India's complex loss offset rules.
    What can offset what — critical for tax minimization.
    """

    # Loss offset matrix
    # Format: source_loss → [what it can offset]
    OFFSET_RULES = {
        'stcg_equity_loss': [
            'stcg_equity_gain',     # Same type ✅
            'ltcg_equity_gain',     # STCG loss can offset LTCG ✅
        ],
        'ltcg_equity_loss': [
            'ltcg_equity_gain',     # Same type only ✅
            # CANNOT offset STCG ❌
        ],
        'fo_non_speculative_loss': [
            'fo_non_speculative_profit',    # Same ✅
            'other_business_income',        # ✅
            'rental_income',               # ✅
            # CANNOT offset salary ❌
            # CANNOT offset capital gains ❌
        ],
        'intraday_speculative_loss': [
            'intraday_speculative_profit',  # Same only ✅
            # CANNOT offset anything else ❌
        ],
        'crypto_loss': [
            # CANNOT offset ANYTHING ❌
            # This is the harshest rule in India tax
        ],
        'debt_mf_loss': [
            'debt_mf_gain',         # ✅
            'other_capital_gains',  # ✅ (treated as capital loss)
        ]
    }

    # Carry forward periods
    CARRY_FORWARD = {
        'stcg_loss':                8,  # 8 years
        'ltcg_loss':                8,  # 8 years
        'fo_non_speculative_loss':  8,  # 8 years
        'intraday_speculative_loss': 4, # 4 years
        'business_loss':            8,  # 8 years (set off against business only)
        'crypto_loss':              0,  # CANNOT be carried forward
    }

    def calculate_net_taxable(self, year_transactions: list, carry_forward_losses: dict) -> dict:
        """
        Calculate net taxable income after all loss offsets.
        """
        # Step 1: Segregate all gains and losses
        stcg_gains      = []
        stcg_losses     = []
        ltcg_gains      = []
        ltcg_losses     = []
        fo_profits      = []
        fo_losses       = []
        intraday_profits = []
        intraday_losses  = []
        dividends       = []
        crypto_gains    = []
        crypto_losses   = []

        for tx in year_transactions:
            if tx.action not in [ActionType.SELL, ActionType.EXPIRY_ITM,
                                  ActionType.EXPIRY_OTM, ActionType.DIVIDEND]:
                continue

            gain = tx.taxable_gain if tx.taxable_gain else Decimal('0')

            if tx.tax_treatment == TaxTreatment.INDIA_STCG_EQUITY:
                if gain >= 0:   stcg_gains.append(gain)
                else:           stcg_losses.append(abs(gain))

            elif tx.tax_treatment == TaxTreatment.INDIA_LTCG_EQUITY:
                if gain >= 0:   ltcg_gains.append(gain)
                else:           ltcg_losses.append(abs(gain))

            elif tx.tax_treatment == TaxTreatment.INDIA_FO_BUSINESS:
                if gain >= 0:   fo_profits.append(gain)
                else:           fo_losses.append(abs(gain))

            elif tx.tax_treatment == TaxTreatment.INDIA_INTRADAY_SPEC:
                if gain >= 0:   intraday_profits.append(gain)
                else:           intraday_losses.append(abs(gain))

            elif tx.tax_treatment == TaxTreatment.INDIA_CRYPTO:
                if gain >= 0:   crypto_gains.append(gain)
                else:           crypto_losses.append(abs(gain))

            elif tx.tax_treatment == TaxTreatment.INDIA_DIVIDEND_SLAB:
                dividends.append(abs(gain))

        # Step 2: Calculate gross amounts
        gross_stcg      = sum(stcg_gains)
        gross_stcg_loss = sum(stcg_losses)
        gross_ltcg      = sum(ltcg_gains)
        gross_ltcg_loss = sum(ltcg_losses)
        gross_fo        = sum(fo_profits)
        gross_fo_loss   = sum(fo_losses)
        gross_intraday  = sum(intraday_profits)
        gross_intraday_loss = sum(intraday_losses)
        total_dividends = sum(dividends)
        total_crypto    = sum(crypto_gains)
        # Crypto losses CANNOT offset anything

        # Step 3: Apply offset rules
        # STCG loss first offsets STCG gains
        net_stcg_after_own_loss = max(Decimal('0'), gross_stcg - gross_stcg_loss)
        stcg_loss_remaining     = max(Decimal('0'), gross_stcg_loss - gross_stcg)

        # STCG loss remaining can offset LTCG
        net_ltcg_after_stcg     = max(Decimal('0'), gross_ltcg - stcg_loss_remaining)
        stcg_loss_unabsorbed    = max(Decimal('0'), stcg_loss_remaining - gross_ltcg)

        # LTCG loss can only offset LTCG gains
        net_ltcg_after_ltcg_loss = max(Decimal('0'), net_ltcg_after_stcg - gross_ltcg_loss)
        ltcg_loss_remaining     = max(Decimal('0'), gross_ltcg_loss - net_ltcg_after_stcg)

        # Apply LTCG exemption (₹1.25L)
        ltcg_exemption          = Decimal('125000')
        taxable_ltcg            = max(Decimal('0'), net_ltcg_after_ltcg_loss - ltcg_exemption)

        # F&O net (can be offset against business income)
        net_fo                  = gross_fo - gross_fo_loss  # Can be negative (carry forward)
        fo_loss_to_carryforward = max(Decimal('0'), -net_fo)
        taxable_fo              = max(Decimal('0'), net_fo)

        # Intraday — can only offset against intraday
        net_intraday            = max(Decimal('0'), gross_intraday - gross_intraday_loss)
        intraday_loss_carry     = max(Decimal('0'), gross_intraday_loss - gross_intraday)

        # Step 4: Apply carry-forward losses from prior years
        cf_stcg_loss    = Decimal(str(carry_forward_losses.get('stcg_loss', 0)))
        cf_ltcg_loss    = Decimal(str(carry_forward_losses.get('ltcg_loss', 0)))
        cf_fo_loss      = Decimal(str(carry_forward_losses.get('fo_loss', 0)))

        # Apply prior year CF losses
        net_stcg_after_cf = max(Decimal('0'), net_stcg_after_own_loss - cf_stcg_loss)
        net_ltcg_after_cf = max(Decimal('0'), taxable_ltcg - cf_ltcg_loss)
        taxable_fo_after_cf = max(Decimal('0'), taxable_fo - cf_fo_loss)

        return {
            # Gross amounts
            'gross_stcg':           round(gross_stcg, 2),
            'gross_ltcg':           round(gross_ltcg, 2),
            'gross_fo_profit':      round(gross_fo, 2),
            'gross_dividends':      round(total_dividends, 2),
            'gross_crypto':         round(total_crypto, 2),

            # Losses
            'stcg_loss':            round(gross_stcg_loss, 2),
            'ltcg_loss':            round(gross_ltcg_loss, 2),
            'fo_loss':              round(gross_fo_loss, 2),
            'crypto_loss':          round(sum(crypto_losses), 2),

            # Net taxable after offsets
            'taxable_stcg':         round(net_stcg_after_cf, 2),
            'taxable_ltcg':         round(net_ltcg_after_cf, 2),
            'taxable_fo':           round(taxable_fo_after_cf, 2),
            'taxable_intraday':     round(net_intraday, 2),
            'taxable_dividends':    round(total_dividends, 2),
            'taxable_crypto':       round(total_crypto, 2),

            # Losses to carry forward
            'carry_forward': {
                'stcg_loss':        round(stcg_loss_unabsorbed, 2),
                'ltcg_loss':        round(ltcg_loss_remaining, 2),
                'fo_loss':          round(fo_loss_to_carryforward, 2),
                'intraday_loss':    round(intraday_loss_carry, 2),
                # Note: crypto losses CANNOT be carried forward
            },

            # Warnings
            'warnings': [
                "CRYPTO LOSS ₹{:.0f} CANNOT be offset or carried forward".format(sum(crypto_losses))
                if sum(crypto_losses) > 0 else None,
                "INTRADAY LOSS can only offset intraday profit"
                if gross_intraday_loss > gross_intraday else None,
            ]
        }
```

## B.4 Advance Tax Calculator

```python
class AdvanceTaxCalculator:
    """
    Calculate advance tax installments and penalties.
    India mandatory if tax liability > ₹10,000.
    """

    INSTALLMENT_SCHEDULE = {
        'Q1': {'by_date': (6, 15),   'cumulative_pct': 0.15},  # June 15
        'Q2': {'by_date': (9, 15),   'cumulative_pct': 0.45},  # September 15
        'Q3': {'by_date': (12, 15),  'cumulative_pct': 0.75},  # December 15
        'Q4': {'by_date': (3, 15),   'cumulative_pct': 1.00},  # March 15
    }

    def calculate_installments(
        self,
        estimated_annual_tax: Decimal,
        tds_deducted: Decimal,
        year: int = None
    ) -> dict:
        """
        Calculate all 4 advance tax installments.
        TDS already deducted counts toward advance tax.
        """
        if year is None:
            year = date.today().year

        net_tax     = max(Decimal('0'), estimated_annual_tax - tds_deducted)
        installments = {}

        for quarter, schedule in self.INSTALLMENT_SCHEDULE.items():
            due_date        = date(year, *schedule['by_date'])
            cumulative_req  = net_tax * Decimal(str(schedule['cumulative_pct']))

            installments[quarter] = {
                'due_date':         due_date,
                'cumulative_required': round(cumulative_req, 2),
                'status':           'UPCOMING' if due_date >= date.today() else 'DUE',
            }

        # Calculate each installment amount
        prev_cumulative = Decimal('0')
        for q in ['Q1', 'Q2', 'Q3', 'Q4']:
            inst = installments[q]
            inst['installment_amount'] = round(
                inst['cumulative_required'] - prev_cumulative, 2
            )
            prev_cumulative = inst['cumulative_required']

        return {
            'estimated_annual_tax':     round(estimated_annual_tax, 2),
            'tds_deducted':             round(tds_deducted, 2),
            'net_advance_tax':          round(net_tax, 2),
            'threshold_met':            net_tax >= 10000,
            'installments':             installments,
            'next_installment':         self.next_due_installment(installments)
        }

    def calculate_penalty_234b(
        self,
        assessed_tax: Decimal,
        tds: Decimal,
        advance_tax_paid: Decimal,
        payment_date: date
    ) -> Decimal:
        """
        Section 234B: Penalty for not paying advance tax.
        1% per month from April 1 to date of assessment.
        Applies if advance tax paid < 90% of assessed tax.
        """
        net_tax         = assessed_tax - tds
        threshold_90pct = net_tax * Decimal('0.90')

        if advance_tax_paid >= threshold_90pct:
            return Decimal('0')  # No penalty

        shortfall       = net_tax - advance_tax_paid
        # Calculate months from April 1 to payment date
        april_1         = date(payment_date.year, 4, 1)
        if payment_date < april_1:
            april_1 = date(payment_date.year - 1, 4, 1)

        months          = max(1, (payment_date - april_1).days // 30)
        penalty         = shortfall * Decimal('0.01') * Decimal(str(months))

        return round(penalty, 2)

    def calculate_penalty_234c(
        self,
        assessed_tax: Decimal,
        tds: Decimal,
        payments_made: dict  # {'Q1': amount, 'Q2': amount, etc}
    ) -> Decimal:
        """
        Section 234C: Deferral penalty for short/late installments.
        1% per month on shortfall for 3 months per quarter.
        """
        net_tax     = assessed_tax - tds
        total_penalty = Decimal('0')

        required_cumulative = {
            'Q1': net_tax * Decimal('0.15'),
            'Q2': net_tax * Decimal('0.45'),
            'Q3': net_tax * Decimal('0.75'),
            'Q4': net_tax * Decimal('1.00'),
        }

        paid_cumulative = Decimal('0')
        for quarter in ['Q1', 'Q2', 'Q3', 'Q4']:
            paid_cumulative += Decimal(str(payments_made.get(quarter, 0)))
            required        = required_cumulative[quarter]

            if paid_cumulative < required:
                shortfall   = required - paid_cumulative
                months      = 3 if quarter != 'Q4' else 1  # Q4 = 1 month
                penalty     = shortfall * Decimal('0.01') * Decimal(str(months))
                total_penalty += penalty

        return round(total_penalty, 2)

    def next_due_installment(self, installments: dict) -> dict:
        """Find next upcoming installment"""
        today = date.today()
        for q in ['Q1', 'Q2', 'Q3', 'Q4']:
            if installments[q]['due_date'] >= today:
                inst = installments[q]
                days_away = (inst['due_date'] - today).days
                return {
                    'quarter':      q,
                    'due_date':     inst['due_date'],
                    'amount':       inst['installment_amount'],
                    'days_away':    days_away,
                    'alert':        f"⚠️ Advance tax due in {days_away} days: ₹{inst['installment_amount']:,.0f}"
                                    if days_away <= 15 else
                                    f"Next advance tax ({q}): ₹{inst['installment_amount']:,.0f} due {inst['due_date']}"
                }
        return None
```

## B.5 STT Deductible Expense Tracker

```python
class ChargesDeductionTracker:
    """
    For F&O traders: All charges are deductible business expenses.
    System tracks cumulative deductible charges.
    """

    DEDUCTIBLE_FOR_FO = [
        'brokerage',
        'stt',
        'exchange_charges',
        'gst_on_charges',
        'stamp_duty',
        'sebi_charges',
        'internet_charges',     # Proportionate
        'software_subscription', # FinanceLab subscription!
        'trading_equipment',    # Mac Mini, screens
        'electricity',          # Proportionate for home office
        'professional_fees',    # CA fees for F&O assessment
    ]

    def calculate_deductible_expenses(self, fo_transactions: list, other_expenses: dict) -> dict:
        """
        Sum all deductible expenses for F&O business income.
        Reduces taxable F&O income.
        """
        # Transaction-level charges
        tx_charges = {
            'brokerage':        sum(tx.brokerage for tx in fo_transactions),
            'stt':              sum(tx.stt for tx in fo_transactions),
            'exchange_charges': sum(tx.exchange_charges for tx in fo_transactions),
            'gst_on_charges':   sum(tx.gst_on_charges for tx in fo_transactions),
            'stamp_duty':       sum(tx.stamp_duty for tx in fo_transactions),
            'sebi_charges':     sum(tx.sebi_charges for tx in fo_transactions),
        }

        # Other business expenses
        other = {
            'financelab_subscription':  other_expenses.get('financelab', 0),
            'internet':                 other_expenses.get('internet', 0),
            'electricity':              other_expenses.get('electricity', 0),
            'professional_fees':        other_expenses.get('professional_fees', 0),
            'equipment':                other_expenses.get('equipment', 0),
        }

        total_tx_charges = sum(tx_charges.values())
        total_other      = sum(other.values())
        total_deductible = total_tx_charges + total_other

        return {
            'transaction_charges':  {k: round(float(v), 2) for k, v in tx_charges.items()},
            'other_expenses':       other,
            'total_deductible':     round(float(total_deductible), 2),
            'tax_saving':           round(float(total_deductible) * 0.30 * 1.04, 2),
            'note':                 'All expenses above deductible from F&O business income'
        }
```

---

# SECTION C — US TAX ENGINE

## C.1 US Tax Rates (2024)

```python
US_TAX_RATES_2024 = {

    'ltcg_single': [
        (47025,    0.00),   # 0% up to $47,025
        (518900,   0.15),   # 15%
        (float('inf'), 0.20)
    ],
    'ltcg_married': [
        (94050,    0.00),
        (583750,   0.15),
        (float('inf'), 0.20)
    ],

    'ordinary_income_single': [
        (11600,    0.10),
        (47150,    0.12),
        (100525,   0.22),
        (191950,   0.24),
        (243725,   0.32),
        (609350,   0.35),
        (float('inf'), 0.37)
    ],

    'niit': {
        'rate':         0.038,  # Net Investment Income Tax
        'threshold':    200000  # Single filer
    },

    'section_1256': {
        'lt_portion':   0.60,
        'st_portion':   0.40,
        'description':  '60% LTCG rate + 40% ordinary income rate'
    },

    'qualified_dividends': 'same_as_ltcg',

    'state_taxes': {
        # India resident filing — state tax typically not applicable
        # But if US-sourced income, DTAA provides credit
        'california':   0.133,  # Highest US state
        'texas':        0.000,  # No state income tax
        'florida':      0.000,
        'new_york':     0.109,
    }
}
```

## C.2 India Resident — US Income Tax Rules

```python
class IndiaResidentUSTaxEngine:
    """
    India resident investing in US stocks/ETFs.
    Key: India taxes ALL global income.
    US withholds tax at source.
    DTAA provides credit mechanism.
    """

    # DTAA India-USA rates
    INDIA_US_DTAA = {
        'dividends': {
            'standard_withholding':     0.30,   # US default
            'dtaa_rate':                0.25,   # DTAA reduced rate
            'portfolio_dividends':      0.25,   # If <10% shareholding
            'substantial_holding':      0.15,   # If >=10% shareholding
            'how_to_claim':             'File Form W-8BEN with US broker'
        },
        'interest': {
            'standard_withholding':     0.30,
            'dtaa_rate':                0.15,
            'bank_interest':            0.15,
        },
        'capital_gains': {
            'us_tax':                   'Generally exempt for India residents',
            'exception':               'US real property gains still taxed by US',
            'india_tax':               'Yes — India taxes capital gains on US stocks',
            'dtaa_article':            'Article 13 — Capital Gains'
        }
    }

    def calculate_us_stock_tax_india_resident(
        self,
        us_gain: Decimal,
        us_dividend: Decimal,
        us_tax_withheld: Decimal,
        holding_days: int,
        profile
    ) -> dict:
        """
        Complete tax calculation for India resident with US investments.

        Key principle:
        India taxes the GROSS income.
        Credit given for US tax already paid.
        If India tax > US tax: pay the difference to India.
        If India tax < US tax: no refund (excess credit lost).
        """

        # Step 1: US capital gains tax
        # India residents generally NOT subject to US CGT on stocks
        # (per DTAA Article 13)
        us_cgt = Decimal('0')

        # Step 2: US dividend withholding
        # US withholds at 25% (DTAA rate for portfolio dividends)
        us_dividend_withheld    = us_dividend * Decimal('0.25')

        # Step 3: India tax on US gain
        # India treats US stock gains same as domestic
        if holding_days >= 365:
            # LTCG — but in FOREIGN currency
            # RBI reference rate at acquisition and disposal dates
            gain_inr        = us_gain * profile.usd_inr_rate
            india_ltcg_rate = Decimal('0.125')
            india_cgt_inr   = max(Decimal('0'), gain_inr - Decimal('125000')) * india_ltcg_rate
        else:
            gain_inr        = us_gain * profile.usd_inr_rate
            india_stcg_rate = Decimal('0.20')
            india_cgt_inr   = gain_inr * india_stcg_rate

        # Step 4: India tax on US dividend
        # India taxes at slab rate
        dividend_inr        = us_dividend * profile.usd_inr_rate
        india_div_tax       = dividend_inr * Decimal(str(profile.tax_bracket))

        # Step 5: Foreign Tax Credit
        # US tax withheld on dividend converted to INR
        us_div_tax_inr      = us_dividend_withheld * profile.usd_inr_rate

        # FTC available = min(US tax paid, India tax on same income)
        ftc_available       = min(us_div_tax_inr, india_div_tax)

        # Net India tax after FTC
        net_india_div_tax   = india_div_tax - ftc_available

        # Capital gains — US generally doesn't tax India residents
        # India taxes the gain at Indian rates
        # No FTC since no US tax paid on CG

        total_india_tax     = india_cgt_inr + net_india_div_tax
        cess                = total_india_tax * Decimal('0.04')

        return {
            'us_income': {
                'capital_gain_usd':         round(float(us_gain), 2),
                'dividend_usd':             round(float(us_dividend), 2),
                'us_withholding_tax_usd':   round(float(us_dividend_withheld), 2),
                'us_cgt_usd':               0  # Exempt under DTAA
            },
            'india_tax': {
                'gain_in_inr':              round(float(gain_inr), 2),
                'dividend_in_inr':          round(float(dividend_inr), 2),
                'india_cgt_inr':            round(float(india_cgt_inr), 2),
                'india_div_tax_before_ftc': round(float(india_div_tax), 2),
                'ftc_available_inr':        round(float(ftc_available), 2),
                'net_india_div_tax':        round(float(net_india_div_tax), 2),
                'cess':                     round(float(cess), 2),
                'total_india_tax':          round(float(total_india_tax + cess), 2),
            },
            'to_report': {
                'schedule_fsi':     'Foreign Source Income — US capital gains + dividends',
                'schedule_fa':      'Foreign Assets — US brokerage account details',
                'form_w8ben':       'Submit to broker to claim 25% DTAA dividend rate',
                'itr_form':         'ITR-2 or ITR-3 (if F&O also)',
            }
        }

    def wash_sale_tracker(self, transactions: list) -> list:
        """
        US wash sale rule: Cannot claim loss if you buy
        substantially identical security 30 days before/after loss sale.
        India residents filing US taxes must also follow this.
        """
        flagged = []

        sells_at_loss = [tx for tx in transactions
                        if tx.action == ActionType.SELL
                        and tx.tax_treatment in [TaxTreatment.US_STCG, TaxTreatment.US_LTCG_15]
                        and tx.taxable_gain and tx.taxable_gain < 0]

        for loss_sale in sells_at_loss:
            sale_date = loss_sale.trade_date
            window_start = date(sale_date.year, sale_date.month - 1, sale_date.day)
            window_end   = date(sale_date.year, sale_date.month + 1, sale_date.day)

            # Look for buys of same ticker in 30-day window
            same_ticker_buys = [
                tx for tx in transactions
                if tx.ticker == loss_sale.ticker
                and tx.action == ActionType.BUY
                and window_start <= tx.trade_date <= window_end
                and tx.trade_date != sale_date
            ]

            if same_ticker_buys:
                disallowed = abs(loss_sale.taxable_gain)
                flagged.append({
                    'ticker':               loss_sale.ticker,
                    'loss_sale_date':       sale_date,
                    'loss_amount':          float(disallowed),
                    'replacement_buy':      same_ticker_buys[0].trade_date,
                    'wash_sale':            True,
                    'disallowed_loss':      float(disallowed),
                    'added_to_basis':       float(disallowed),
                    'warning':              f"WASH SALE: Loss of ${float(disallowed):.2f} disallowed. "
                                           f"Added to cost basis of replacement shares."
                })

        return flagged

    def fbar_fatca_check(self, foreign_accounts: list, profile) -> dict:
        """
        FBAR: File if any foreign account > $10,000 at any point
        FATCA: File if aggregate > $50,000 year-end or $75,000 at any point

        Relevant for: US citizens/green card holders with India accounts
        India residents: Not subject to FBAR/FATCA for US accounts
        """
        total_max      = sum(a.get('max_balance_usd', 0) for a in foreign_accounts)
        total_yearend  = sum(a.get('yearend_balance_usd', 0) for a in foreign_accounts)

        fbar_required  = total_max >= 10000
        fatca_required = total_yearend >= 50000 or total_max >= 75000

        return {
            'fbar_required':    fbar_required,
            'fatca_required':   fatca_required,
            'fbar_due':         'April 15 (automatic extension to Oct 15)',
            'fatca_form':       'Form 8938 — filed with federal tax return',
            'fbar_form':        'FinCEN 114 — filed separately at bsaefiling.fincen.treas.gov',
            'note':             'India residents with US brokerage accounts — US accounts are NOT foreign accounts for FBAR purposes'
                                if profile.country == 'IN' else
                                'US persons with India Demat accounts must report'
        }
```

---

# SECTION D — UK TAX ENGINE

## D.1 UK Tax Rates and Rules

```python
UK_TAX_RATES_2024_25 = {
    'cgt': {
        'basic_rate':           0.18,   # For assets (increased from 10% in Oct 2024)
        'higher_rate':          0.24,   # For assets (increased from 20% in Oct 2024)
        'residential_property_basic': 0.18,
        'residential_property_higher': 0.24,
        'annual_exemption':     3000,   # £3,000 (reduced from £12,300 in 2022)
        'note':                 'Rates increased in Autumn Budget Oct 2024'
    },
    'income_tax': {
        'personal_allowance':   12570,
        'basic_rate':           0.20,
        'higher_rate':          0.40,
        'additional_rate':      0.45,
        'basic_threshold':      50270,
        'higher_threshold':     125140
    },
    'dividend': {
        'allowance':            500,    # £500 (reduced from £2,000)
        'basic_rate':           0.0875,
        'higher_rate':          0.3375,
        'additional_rate':      0.3938
    },
    'isa': {
        'annual_allowance':     20000,  # £20,000
        'tax':                  0.00,   # Completely tax-free
        'types':                ['Cash ISA', 'Stocks & Shares ISA', 'Lifetime ISA', 'JISA']
    }
}

# India-UK DTAA rates
INDIA_UK_DTAA = {
    'dividends':    0.15,   # Max withholding
    'interest':     0.15,
    'royalties':    0.15,
    'capital_gains': 'Source country right — usually where asset located'
}
```

## D.2 UK Section 104 Pool (Mandatory Averaging)

```python
class UKSection104Pool:
    """
    UK mandatory cost basis method.
    All shares of same company in same account
    are pooled into one average cost.

    Three matching rules applied in order:
    1. Same-day rule: Buys on same day as sell
    2. 30-day rule: Buys within 30 days AFTER sell (anti-avoidance)
    3. Section 104 pool: Remaining matched to pool average

    This prevents bed-and-breakfast tax avoidance.
    """

    def __init__(self):
        self.pools = {}  # ticker → {'quantity': Decimal, 'total_cost': Decimal}

    def add_acquisition(self, ticker: str, quantity: Decimal, total_cost: Decimal):
        """Add shares to Section 104 pool"""
        if ticker not in self.pools:
            self.pools[ticker] = {'quantity': Decimal('0'), 'total_cost': Decimal('0')}

        self.pools[ticker]['quantity']   += quantity
        self.pools[ticker]['total_cost'] += total_cost

    def calculate_disposal(
        self,
        ticker:         str,
        sell_date:      date,
        sell_quantity:  Decimal,
        sell_proceeds:  Decimal,
        all_transactions: list  # All transactions for wash sale check
    ) -> dict:
        """
        Calculate gain/loss on UK disposal applying 3-tier matching.
        """
        remaining_to_match = sell_quantity
        total_cost_matched = Decimal('0')
        matching_detail    = []

        # RULE 1: Same-day acquisitions
        same_day_buys = [
            tx for tx in all_transactions
            if tx.ticker == ticker
            and tx.action == ActionType.BUY
            and tx.trade_date == sell_date
        ]

        for buy in same_day_buys:
            match_qty = min(remaining_to_match, buy.quantity)
            match_cost = (buy.price * match_qty) + (buy.total_charges * match_qty / buy.quantity)
            total_cost_matched += match_cost
            remaining_to_match -= match_qty
            matching_detail.append({
                'rule':         'SAME_DAY',
                'quantity':     float(match_qty),
                'cost':         float(match_cost),
                'date':         buy.trade_date
            })
            if remaining_to_match == 0:
                break

        # RULE 2: Next 30 days (BED AND BREAKFAST RULE)
        if remaining_to_match > 0:
            thirty_day_end = date(sell_date.year, sell_date.month + 1, sell_date.day)
            next_30_buys = sorted([
                tx for tx in all_transactions
                if tx.ticker == ticker
                and tx.action == ActionType.BUY
                and sell_date < tx.trade_date <= thirty_day_end
            ], key=lambda x: x.trade_date)

            for buy in next_30_buys:
                if remaining_to_match == 0:
                    break
                match_qty   = min(remaining_to_match, buy.quantity)
                match_cost  = buy.price * match_qty
                total_cost_matched += match_cost
                remaining_to_match -= match_qty
                matching_detail.append({
                    'rule':         'BED_AND_BREAKFAST_30DAY',
                    'quantity':     float(match_qty),
                    'cost':         float(match_cost),
                    'date':         buy.trade_date
                })

        # RULE 3: Section 104 pool (remaining quantity)
        if remaining_to_match > 0 and ticker in self.pools:
            pool        = self.pools[ticker]
            if pool['quantity'] > 0:
                avg_cost    = pool['total_cost'] / pool['quantity']
                match_cost  = avg_cost * remaining_to_match
                total_cost_matched += match_cost

                # Reduce pool
                pool['quantity']    -= remaining_to_match
                pool['total_cost']  -= match_cost

                matching_detail.append({
                    'rule':         'SECTION_104_POOL',
                    'quantity':     float(remaining_to_match),
                    'avg_cost':     float(avg_cost),
                    'cost':         float(match_cost)
                })
                remaining_to_match = Decimal('0')

        # Calculate gain/loss
        gross_gain          = sell_proceeds - total_cost_matched
        annual_exemption    = Decimal('3000')  # £3,000
        taxable_gain        = max(Decimal('0'), gross_gain - annual_exemption)

        return {
            'sell_quantity':        float(sell_quantity),
            'sell_proceeds':        float(sell_proceeds),
            'total_cost_matched':   float(total_cost_matched),
            'gross_gain':           float(gross_gain),
            'is_loss':              gross_gain < 0,
            'taxable_gain':         float(taxable_gain),  # Before exemption split
            'matching_detail':      matching_detail,
            'uk_cgt_basic':         float(taxable_gain * Decimal('0.18')),
            'uk_cgt_higher':        float(taxable_gain * Decimal('0.24')),
        }

class IndiaResidentUKTaxEngine:
    """
    India resident investing in UK stocks.
    UK CGT generally applies at source.
    DTAA provides credit in India.
    """

    def calculate_india_tax_on_uk_gain(
        self,
        uk_gain_gbp:    Decimal,
        uk_tax_paid_gbp: Decimal,
        holding_days:   int,
        gbp_inr_rate:   Decimal,
        profile
    ) -> dict:

        gain_inr        = uk_gain_gbp * gbp_inr_rate
        uk_tax_inr      = uk_tax_paid_gbp * gbp_inr_rate

        # India taxes the gain at Indian rates
        if holding_days >= 365:
            india_rate  = Decimal('0.125')
        else:
            india_rate  = Decimal('0.20')

        india_tax_inr   = max(Decimal('0'), gain_inr - Decimal('125000')) * india_rate \
                          if holding_days >= 365 else gain_inr * india_rate

        # FTC: Credit for UK CGT paid
        ftc             = min(uk_tax_inr, india_tax_inr)
        net_india_tax   = india_tax_inr - ftc
        cess            = net_india_tax * Decimal('0.04')

        return {
            'gain_gbp':         float(uk_gain_gbp),
            'gain_inr':         float(gain_inr),
            'uk_tax_gbp':       float(uk_tax_paid_gbp),
            'uk_tax_inr':       float(uk_tax_inr),
            'india_tax_gross':  float(india_tax_inr),
            'ftc':              float(ftc),
            'net_india_tax':    float(net_india_tax),
            'cess':             float(cess),
            'total_payable':    float(net_india_tax + cess),
            'dtaa_article':     'India-UK DTAA Article 13 — Capital Gains'
        }
```

---

# SECTION E — EUROPEAN TAX ENGINES

## E.1 Germany — Abgeltungsteuer

```python
class GermanyTaxEngine:
    """
    Germany Abgeltungsteuer: 25% flat on all investment income.
    + 5.5% solidarity surcharge on tax = effective 26.375%
    + Church tax if applicable (~8-9% on tax amount)

    Key Germany-specific rules:
    1. FIFO mandatory
    2. Annual exemption: €1,000 (from 2023)
    3. Verlustverrechnungstopf: separate loss pots
    4. Crypto: Tax-free if held > 1 year
    5. Partial exemption for equity funds (30% exempt)
    """

    RATES = {
        'abgeltungsteuer':      0.25,
        'solidarity_surcharge': 0.055,  # 5.5% of tax amount
        'effective_rate':       0.26375,
        'annual_exemption':     1000,   # €1,000
        'church_tax_rate':      0.09,   # If applicable (8-9% of tax)
    }

    # Germany loss pots (Verlustverrechnungstopf)
    # Different loss pots for different income types
    LOSS_POTS = {
        'general':          'Stocks, bonds, dividends, interest — can offset each other',
        'equity_specific':  'Stock losses only — cannot offset bond gains',
        # Note: From 2020, stock losses can only offset stock gains (important!)
    }

    def calculate_transaction_tax(
        self,
        gain_eur:       Decimal,
        asset_type:     str,   # 'stock', 'bond', 'fund', 'crypto'
        holding_days:   int,
        uses_church_tax: bool = False
    ) -> dict:

        # Crypto: Tax-free if held > 1 year
        if asset_type == 'crypto' and holding_days > 365:
            return {
                'taxable_gain':     0,
                'tax':              0,
                'treatment':        'STEUERFREI — Crypto held > 1 year, tax-free in Germany',
                'note':             'India resident still must pay India tax on this gain'
            }

        # Equity funds: 30% partial exemption (Teilfreistellung)
        if asset_type in ['equity_fund', 'equity_etf']:
            exempt_portion  = gain_eur * Decimal('0.30')
            taxable         = gain_eur - exempt_portion
        else:
            taxable         = gain_eur

        # Apply annual exemption (shared across all investment income)
        # Note: Exemption applied at portfolio level
        # Per transaction: show gross taxable

        abgeltung   = taxable * Decimal('0.25')
        soli        = abgeltung * Decimal('0.055')
        church      = abgeltung * Decimal('0.09') if uses_church_tax else Decimal('0')

        total_de_tax = abgeltung + soli + church

        # India tax
        # Germany withholds — India gives FTC
        # India resident still pays Indian CGT rates
        # Net India additional tax after FTC

        return {
            'gross_gain_eur':       float(gain_eur),
            'taxable_gain_eur':     float(taxable),
            'abgeltungsteuer':      float(abgeltung),
            'solidarity_surcharge': float(soli),
            'church_tax':           float(church),
            'total_german_tax':     float(total_de_tax),
            'effective_rate_pct':   round(float(total_de_tax / gain_eur) * 100, 2) if gain_eur > 0 else 0,
            'annual_exemption':     '€1,000 (shared across all investment income)',
            'crypto_note':          'Held < 1 year — taxable. If > 1 year: tax-free' if asset_type == 'crypto' else None
        }

    def india_resident_germany_tax(
        self,
        gain_eur:       Decimal,
        de_tax_paid_eur: Decimal,
        eur_inr_rate:   Decimal,
        holding_days:   int,
        profile
    ) -> dict:

        gain_inr        = gain_eur * eur_inr_rate
        de_tax_inr      = de_tax_paid_eur * eur_inr_rate

        # India tax
        if holding_days >= 365:
            india_tax   = max(Decimal('0'), gain_inr - Decimal('125000')) * Decimal('0.125')
        else:
            india_tax   = gain_inr * Decimal('0.20')

        # DTAA India-Germany: Article 23 provides FTC mechanism
        # Credit limited to lower of DE tax or India tax on same income
        ftc             = min(de_tax_inr, india_tax)
        net_india       = india_tax - ftc
        cess            = net_india * Decimal('0.04')

        return {
            'germany_tax_eur':  float(de_tax_paid_eur),
            'gain_inr':         float(gain_inr),
            'india_tax_gross':  float(india_tax),
            'ftc_inr':          float(ftc),
            'net_india_tax':    float(net_india + cess),
            'dtaa':             'India-Germany DTAA Article 23'
        }
```

## E.2 France — Prélèvement Forfaitaire Unique (PFU)

```python
class FranceTaxEngine:
    """
    France PFU (Flat Tax): 30% on all investment income.
    = 12.8% income tax + 17.2% social charges (CSG/CRDS)

    PEA (Plan d'Épargne en Actions):
    After 5 years: Only 17.2% social charges (no income tax)
    Essentially 17.2% instead of 30% — very beneficial

    FIFO mandatory for shares.
    """

    RATES = {
        'pfu_total':            0.30,   # 30% flat
        'income_tax_portion':   0.128,  # 12.8%
        'social_charges':       0.172,  # 17.2% CSG/CRDS
        'pea_after_5yr':        0.172,  # Only social charges after 5 years
        'pea_account_limit':    150000, # €150,000 PEA limit
    }

    # India-France DTAA
    INDIA_FRANCE_DTAA = {
        'dividends':    0.10,   # If India company paying to France resident
        'interest':     0.10,
        'note':         'France is source country for French stocks — PFU applies'
    }

    def calculate_transaction_tax(
        self,
        gain_eur:       Decimal,
        is_pea_account: bool = False,
        pea_years:      int = 0
    ) -> dict:

        if is_pea_account and pea_years >= 5:
            tax_rate    = Decimal('0.172')  # Only social charges
            treatment   = 'PEA_5YR_REDUCED'
        else:
            tax_rate    = Decimal('0.30')
            treatment   = 'PFU_30_PERCENT'

        tax         = gain_eur * tax_rate
        income_tax  = gain_eur * Decimal('0.128') if not (is_pea_account and pea_years >= 5) else Decimal('0')
        social      = gain_eur * Decimal('0.172')

        return {
            'taxable_gain_eur': float(gain_eur),
            'income_tax':       float(income_tax),
            'social_charges':   float(social),
            'total_french_tax': float(tax),
            'effective_rate':   float(tax_rate) * 100,
            'treatment':        treatment,
            'pea_note':         'PEA after 5 years: only 17.2% vs 30% — significant saving' if is_pea_account else None
        }
```

## E.3 Netherlands — Box 3 System

```python
class NetherlandsTaxEngine:
    """
    Netherlands Box 3: Most unusual tax system globally.
    Tax on DEEMED (assumed) return — not actual return.

    2024 rates:
    Assets up to €57,000: 1.79% assumed return
    Assets €57,000-€1,015,520: 6.04% assumed return
    Assets above €1,015,520: 6.04% assumed return

    Tax rate: 36% on the assumed return

    Example:
    Portfolio value: €100,000
    Assumed return: €100,000 × 6.04% = €6,040
    Tax: €6,040 × 36% = €2,174
    You pay €2,174 even if your portfolio lost money!
    """

    RATES_2024 = {
        'tier1': {'up_to': 57000,   'assumed_return': 0.0179},
        'tier2': {'up_to': 1015520, 'assumed_return': 0.0604},
        'tier3': {'above': 1015520, 'assumed_return': 0.0604},
        'tax_rate': 0.36,
        'exemption': 57000,  # Personal exemption per person
    }

    def calculate_box3_tax(self, portfolio_value_eur: Decimal) -> dict:
        """
        Calculate Netherlands Box 3 tax on portfolio.
        This replaces capital gains tax entirely.
        """
        # Apply exemption
        taxable_value   = max(Decimal('0'), portfolio_value_eur - Decimal('57000'))

        # Calculate assumed return
        tier1_value     = min(taxable_value, Decimal('57000'))
        tier2_value     = max(Decimal('0'), taxable_value - Decimal('57000'))

        assumed_return  = (tier1_value * Decimal('0.0179') +
                          tier2_value * Decimal('0.0604'))

        # Tax on assumed return
        tax             = assumed_return * Decimal('0.36')

        return {
            'portfolio_value':      float(portfolio_value_eur),
            'taxable_value':        float(taxable_value),
            'assumed_return':       float(assumed_return),
            'box3_tax':             float(tax),
            'effective_rate_on_portfolio': round(float(tax / portfolio_value_eur) * 100, 3) if portfolio_value_eur > 0 else 0,
            'warning':              '⚠️ Box 3 taxes assumed return regardless of actual performance',
            'note':                 'India resident: NL Box 3 tax paid → FTC credit in India',
            'dutch_court_ruling':   'Courts found Box 3 violates property rights — transitional rules apply 2024'
        }
```

## E.4 Other European Countries

```python
EUROPEAN_CGT_RATES = {
    'spain': {
        'brackets': [
            (6000,   0.19),
            (50000,  0.21),
            (200000, 0.23),
            (300000, 0.27),
            (float('inf'), 0.28)
        ],
        'dtaa_india_spain':     'India-Spain DTAA — dividends 15%, interest 15%',
        'annual_exemption':     None,
        'fifo':                 True
    },
    'italy': {
        'rate':                 0.26,   # Flat rate
        'annual_exemption':     None,
        'dtaa_india_italy':     'India-Italy DTAA — dividends 15-25%',
        'regime':               'Regime dichiarativo (self-reporting) or amministrato (bank withholds)'
    },
    'switzerland': {
        'cgt_rate':             0.00,   # Private investors exempt from CGT!
        'dividend_withholding': 0.35,   # High dividend withholding
        'dtaa_india_swiss':     'India-Switzerland DTAA — dividends 10%',
        'note':                 'ZERO capital gains tax for private investors — major advantage',
        'professional_trader':  'If classified as professional trader — income tax applies'
    },
    'ireland': {
        'rate':                 0.33,   # 33% CGT
        'annual_exemption':     1270,   # €1,270
        'dtaa_india_ireland':   'India-Ireland DTAA exists'
    },
    'portugal': {
        'standard_rate':        0.28,   # 28% standard
        'nhr_rate':             0.10,   # 10% for NHR holders
        'nhr_note':             'Non-Habitual Resident regime — attractive for retirees/digital nomads'
    },
    'sweden': {
        'rate':                 0.30,   # 30% CGT
        'isk_account':          'Investment Savings Account — standard rate ~0.66% on value',
        'dtaa_india_sweden':    'India-Sweden DTAA exists'
    },
    'netherlands': {
        'system':               'Box 3 — deemed return system (see Section E.3)'
    }
}
```

---

# SECTION F — CROSS-BORDER DTAA FRAMEWORK

## F.1 India-US DTAA Quick Reference

```
INDIA-US DTAA (Convention for Avoidance of Double Taxation)
Signed: September 12, 1989
Amended: Protocol 2006

DIVIDENDS (Article 10):
  India resident receiving US dividends:
  Standard US withholding: 30%
  DTAA rate: 25% (portfolio holding < 10%)
             15% (substantial holding ≥ 10%)
  How to claim: File W-8BEN with US broker
  India taxation: Full amount at slab rate
  FTC: Credit for US withholding (max India tax on same income)

INTEREST (Article 11):
  US source interest to India resident:
  DTAA rate: 15%
  India taxation: At slab rate
  FTC: Credit for US 15% withholding

CAPITAL GAINS (Article 13):
  Stocks sold in US by India resident:
  US right: Generally only US can tax US real property
  Stocks: India resident NOT taxed by US on stock gains
  India taxation: Yes — at Indian STCG/LTCG rates
  US withholding: None for stocks (only real property)
  FTC: N/A (no US tax to credit)

KEY FORMS:
  W-8BEN: File with US broker to claim treaty rates
          Without it: US withholds at 30% default
  Schedule FSI (ITR): Report foreign source income
  Schedule FA (ITR): Report foreign assets
  Form 67: Claim foreign tax credit in India

FBAR / FATCA:
  India residents: NOT applicable for US brokerage accounts
  US persons in India: Must report Indian accounts
```

## F.2 India-UK DTAA Quick Reference

```
INDIA-UK DTAA (Double Taxation Convention)
Signed: November 25, 1993

DIVIDENDS (Article 11):
  UK source dividend to India resident:
  UK standard withholding: 0% (UK abolished dividend WHT)
  DTAA rate: N/A (UK doesn't withhold)
  India taxation: At full slab rate
  FTC: N/A (no UK tax to credit)

CAPITAL GAINS (Article 13):
  UK stocks sold by India resident:
  UK right: UK CGT applies to UK source gains
  CGT rates: 18% basic / 24% higher
  India right: India also taxes
  FTC: Credit in India for UK CGT paid
  Net: Pay UK CGT, top up to India rate if India rate higher

INTEREST:
  DTAA rate: 15%

KEY FORMS:
  India ITR: Report in Schedule FSI and FA
  Form 67: Claim FTC for UK CGT paid
```

## F.3 India-Germany DTAA Quick Reference

```
INDIA-GERMANY DTAA
Signed: June 19, 1995

DIVIDENDS (Article 10):
  German dividends to India resident:
  Germany withholds: 26.375% (Abgeltungsteuer)
  DTAA reduced rate: 10% (portfolio) / 10% (substantial)
  How to claim: File with German tax authority (complex)
  India taxation: At slab rate
  FTC: Credit for German withholding (up to India rate)

CAPITAL GAINS (Article 13):
  German stocks sold by India resident:
  Germany: Abgeltungsteuer 26.375% applies
  India: Also taxes at Indian rates
  FTC: Credit in India for German tax paid

INTEREST (Article 11):
  DTAA rate: 10%
```

## F.4 Form 67 — Foreign Tax Credit Claim

```
FORM 67: Mandatory for claiming FTC in India
Must be filed BEFORE filing ITR

Required information:
  Country name
  Tax identification number in that country
  Nature of income (dividend/interest/capital gain)
  Income in foreign currency
  Income in INR (at RBML rate)
  Foreign tax paid in foreign currency
  Foreign tax paid in INR
  FTC claimed (lower of foreign tax or India tax on same income)

KEY RULE:
  FTC cannot exceed Indian tax on the same foreign income.
  If US withholds 25% but Indian tax is only 20%:
  FTC = 20% (the excess 5% is LOST — no refund from India)

FILING DEADLINE:
  File Form 67 along with or before ITR filing
  Late filing = FTC claim may be rejected
```

---

# SECTION G — CUMULATIVE TAX BILL ENGINE

## G.1 Real-Time Tax Liability Dashboard

```python
class CumulativeTaxBillEngine:
    """
    The main engine: aggregates ALL transactions
    across ALL portfolios across ALL countries
    into one running tax bill.
    """

    def calculate_cumulative_bill(
        self,
        profile_id:     int,
        financial_year: str = '2024-25'  # or '2024' for US/UK
    ) -> dict:
        """
        Master tax calculation function.
        Returns complete YTD tax bill across all jurisdictions.
        """
        # Get all transactions for the year
        all_transactions = get_all_transactions(profile_id, financial_year)

        # Split by country/jurisdiction
        india_txs   = [tx for tx in all_transactions if tx.currency == 'INR']
        us_txs      = [tx for tx in all_transactions
                      if tx.instrument_type in [InstrumentType.US_EQUITY, InstrumentType.US_ETF,
                                                InstrumentType.US_OPTIONS, InstrumentType.US_FUTURES]]
        uk_txs      = [tx for tx in all_transactions if 'UK' in str(tx.instrument_type)]
        eu_txs      = [tx for tx in all_transactions if 'EU' in str(tx.instrument_type)]

        profile = get_profile(profile_id)

        # India tax calculation
        india_engine = IndiaTaxEngine(profile)
        india_tax    = self.calculate_india_total(india_txs, india_engine, profile)

        # US-sourced income (India resident pays Indian tax with FTC)
        us_engine = IndiaResidentUSTaxEngine()
        us_tax    = self.calculate_us_total(us_txs, us_engine, profile)

        # UK-sourced income
        uk_engine = IndiaResidentUKTaxEngine()
        uk_tax    = self.calculate_uk_total(uk_txs, uk_engine, profile)

        # EU-sourced income
        eu_tax    = self.calculate_eu_total(eu_txs, profile)

        # Advance tax already paid
        advance_paid = get_advance_tax_paid(profile_id, financial_year)

        # TDS deducted by various sources
        tds_deducted = self.calculate_tds_deducted(all_transactions)

        # Total tax liability
        total_liability = (
            india_tax['total_india_tax'] +
            us_tax['net_india_tax_on_us_income'] +
            uk_tax['net_india_tax_on_uk_income'] +
            eu_tax['net_india_tax_on_eu_income']
        )

        # Amount still to pay
        already_paid    = advance_paid + tds_deducted['total_tds']
        balance_payable = max(Decimal('0'), total_liability - already_paid)
        refund_due      = max(Decimal('0'), already_paid - total_liability)

        # Advance tax schedule
        adv_calc    = AdvanceTaxCalculator()
        schedule    = adv_calc.calculate_installments(total_liability, tds_deducted['total_tds'])

        # Penalties if applicable
        penalty_234b = adv_calc.calculate_penalty_234b(
            total_liability,
            tds_deducted['total_tds'],
            already_paid,
            date.today()
        )

        return {
            'financial_year':           financial_year,
            'calculation_date':         date.today().isoformat(),

            # India domestic
            'india': {
                'stcg_equity':          india_tax['taxable_stcg'],
                'ltcg_equity':          india_tax['taxable_ltcg'],
                'fo_income':            india_tax['taxable_fo'],
                'intraday_income':      india_tax['taxable_intraday'],
                'dividend_income':      india_tax['taxable_dividends'],
                'crypto_income':        india_tax['taxable_crypto'],
                'tax_stcg':             india_tax['tax_stcg'],
                'tax_ltcg':             india_tax['tax_ltcg'],
                'tax_fo':               india_tax['tax_fo'],
                'tax_crypto':           india_tax['tax_crypto'],
                'total_india_tax':      india_tax['total_india_tax'],
            },

            # Foreign income (India resident taxes globally)
            'foreign_income': {
                'us_gain_inr':          us_tax['gain_inr'],
                'us_dividend_inr':      us_tax['dividend_inr'],
                'us_ftc_available':     us_tax['ftc_available'],
                'net_india_tax_on_us':  us_tax['net_india_tax_on_us_income'],

                'uk_gain_inr':          uk_tax['gain_inr'],
                'uk_ftc_available':     uk_tax['ftc_available'],
                'net_india_tax_on_uk':  uk_tax['net_india_tax_on_uk_income'],

                'eu_gain_inr':          eu_tax['gain_inr'],
                'eu_ftc_available':     eu_tax['ftc_available'],
                'net_india_tax_on_eu':  eu_tax['net_india_tax_on_eu_income'],
            },

            # Summary
            'summary': {
                'total_tax_liability':  float(total_liability),
                'advance_tax_paid':     float(advance_paid),
                'tds_deducted':         float(tds_deducted['total_tds']),
                'total_paid':           float(already_paid),
                'balance_payable':      float(balance_payable),
                'refund_due':           float(refund_due),
                'penalty_234b':         float(penalty_234b),
                'effective_total':      float(total_liability + penalty_234b),
            },

            # Advance tax schedule
            'advance_tax': schedule,

            # Carry forward losses
            'carry_forward':            india_tax['carry_forward'],

            # Form 67 required
            'form_67_required':         us_tax['ftc_available'] > 0 or
                                        uk_tax['ftc_available'] > 0 or
                                        eu_tax['ftc_available'] > 0,

            # ITR form required
            'itr_form':                 self.determine_itr_form(india_txs, us_txs, uk_txs),

            # CA recommendations
            'ca_notes':                 self.generate_ca_notes(india_tax, us_tax, uk_tax)
        }

    def determine_itr_form(self, india_txs, us_txs, uk_txs) -> str:
        """Determine which ITR form to file"""
        has_fo          = any(tx.instrument_type in [InstrumentType.FUTURES, InstrumentType.OPTIONS]
                              for tx in india_txs)
        has_foreign     = len(us_txs) > 0 or len(uk_txs) > 0
        has_salary      = True  # Assumption — user to confirm
        has_business    = has_fo  # F&O = business income

        if has_foreign or has_business:
            return 'ITR-3 (Business/Profession + Capital Gains + Foreign Income)'
        elif has_salary:
            return 'ITR-2 (Salary + Capital Gains)'
        else:
            return 'ITR-1 (Simple — salary only, no capital gains)'

    def what_if_sell_today(
        self,
        profile_id:     int,
        ticker:         str,
        quantity:       Decimal = None  # None = all shares
    ) -> dict:
        """
        If I sell this position TODAY, what is my tax bill?
        Shows: Tax now vs tax if held to LTCG date.
        """
        position        = get_open_position(profile_id, ticker)
        current_price   = get_latest_price(ticker)
        qty             = quantity or position.shares
        current_value   = qty * current_price
        cost_basis      = qty * position.avg_cost
        holding_days    = (date.today() - position.purchase_date).days

        # Tax if sell today
        if holding_days < 365:
            treatment       = 'STCG'
            rate            = Decimal('0.20')
        else:
            treatment       = 'LTCG'
            rate            = Decimal('0.125')

        gross_gain      = current_value - cost_basis
        charges         = calculate_round_trip_charges(ticker, qty, current_price)
        net_gain        = gross_gain - charges

        if treatment == 'LTCG':
            taxable_gain = max(Decimal('0'), net_gain - Decimal('125000'))
        else:
            taxable_gain = max(Decimal('0'), net_gain)

        tax_today       = taxable_gain * rate * Decimal('1.04')  # Including cess
        net_in_pocket   = net_gain - tax_today

        # Tax if held to LTCG
        days_to_ltcg    = max(0, 365 - holding_days)
        if days_to_ltcg > 0:
            expected_growth = Decimal('0.08') * Decimal(str(days_to_ltcg / 365))
            projected_price = current_price * (1 + expected_growth)
            projected_value = qty * projected_price
            projected_gain  = projected_value - cost_basis - charges

            taxable_ltcg    = max(Decimal('0'), projected_gain - Decimal('125000'))
            tax_at_ltcg     = taxable_ltcg * Decimal('0.125') * Decimal('1.04')
            net_at_ltcg     = projected_gain - tax_at_ltcg

            tax_saving      = tax_today - tax_at_ltcg
            worth_waiting   = net_at_ltcg > net_in_pocket and days_to_ltcg <= 60
        else:
            days_to_ltcg    = 0
            tax_saving      = Decimal('0')
            worth_waiting   = False

        return {
            'ticker':           ticker,
            'current_price':    float(current_price),
            'cost_basis':       float(position.avg_cost),
            'holding_days':     holding_days,
            'gross_gain':       float(gross_gain),
            'transaction_charges': float(charges),
            'net_gain':         float(net_gain),

            'sell_today': {
                'treatment':    treatment,
                'tax_rate':     f"{float(rate)*100:.1f}%",
                'taxable_gain': float(taxable_gain),
                'tax_amount':   float(tax_today),
                'net_in_pocket': float(net_in_pocket),
            },

            'hold_to_ltcg': {
                'days_to_wait':     days_to_ltcg,
                'ltcg_date':        (position.purchase_date + timedelta(days=365)).isoformat(),
                'tax_saving':       float(tax_saving),
                'worth_waiting':    worth_waiting,
                'recommendation':   f"HOLD {days_to_ltcg} days — save ₹{float(tax_saving):,.0f} in tax"
                                    if worth_waiting and days_to_ltcg > 0
                                    else "OK TO SELL — tax saving not worth waiting"
                                    if not worth_waiting
                                    else "Already LTCG — sell when technically ready"
            }
        }
```

## G.2 Per-Portfolio Tax Summary

```python
def portfolio_tax_summary(portfolio_id: int, financial_year: str) -> dict:
    """
    Tax summary for ONE broker account.
    Multiple portfolios aggregate into cumulative bill.
    """
    transactions = get_portfolio_transactions(portfolio_id, financial_year)
    portfolio    = get_portfolio(portfolio_id)

    # Categorize
    categories = {
        'stcg_equity':  [],
        'ltcg_equity':  [],
        'fo':           [],
        'intraday':     [],
        'dividend':     [],
        'crypto':       [],
        'foreign':      [],
    }

    for tx in transactions:
        if tx.action not in [ActionType.SELL, ActionType.EXPIRY_ITM,
                              ActionType.EXPIRY_OTM, ActionType.DIVIDEND]:
            continue

        t = tx.tax_treatment
        if t == TaxTreatment.INDIA_STCG_EQUITY:    categories['stcg_equity'].append(tx)
        elif t == TaxTreatment.INDIA_LTCG_EQUITY:  categories['ltcg_equity'].append(tx)
        elif t == TaxTreatment.INDIA_FO_BUSINESS:  categories['fo'].append(tx)
        elif t == TaxTreatment.INDIA_INTRADAY_SPEC: categories['intraday'].append(tx)
        elif t == TaxTreatment.INDIA_DIVIDEND_SLAB: categories['dividend'].append(tx)
        elif t == TaxTreatment.INDIA_CRYPTO:        categories['crypto'].append(tx)
        else:                                        categories['foreign'].append(tx)

    def sum_gains(txs):
        return sum(tx.taxable_gain for tx in txs if tx.taxable_gain)

    def sum_tax(txs):
        return sum(tx.tax_amount for tx in txs if tx.tax_amount)

    return {
        'portfolio_id':     portfolio_id,
        'portfolio_name':   portfolio.name,
        'broker':           portfolio.broker,
        'currency':         portfolio.currency,
        'financial_year':   financial_year,

        'stcg': {
            'transactions':     len(categories['stcg_equity']),
            'gross_gain':       float(sum_gains(categories['stcg_equity'])),
            'tax':              float(sum_tax(categories['stcg_equity'])),
            'rate':             '20%'
        },
        'ltcg': {
            'transactions':     len(categories['ltcg_equity']),
            'gross_gain':       float(sum_gains(categories['ltcg_equity'])),
            'exemption_applied': 125000,
            'taxable_after_exemption': float(max(0, sum_gains(categories['ltcg_equity']) - 125000)),
            'tax':              float(sum_tax(categories['ltcg_equity'])),
            'rate':             '12.5%'
        },
        'fo': {
            'transactions':     len(categories['fo']),
            'net_income':       float(sum_gains(categories['fo'])),
            'tax':              float(sum_tax(categories['fo'])),
            'rate':             'Slab rate'
        },
        'dividend': {
            'transactions':     len(categories['dividend']),
            'gross':            float(sum_gains(categories['dividend'])),
            'tax':              float(sum_tax(categories['dividend'])),
            'tds_already_deducted': float(sum(tx.foreign_tax_withheld for tx in categories['dividend']))
        },
        'crypto': {
            'transactions':     len(categories['crypto']),
            'gains':            float(sum_gains(categories['crypto'])),
            'tax':              float(sum_tax(categories['crypto'])),
            'rate':             '30%',
            'tds':              float(sum(tx.stt for tx in categories['crypto']))  # 1% TDS on crypto
        },

        'total_tax_this_portfolio': float(sum_tax([tx for txs in categories.values() for tx in txs])),
        'fo_turnover':              float(sum(abs(tx.price * tx.quantity) for tx in categories['fo'])),
        'transaction_count':        len(transactions),
    }
```

## G.3 Tax Optimization Suggestions Engine

```python
class TaxOptimizationEngine:
    """
    Proactive suggestions to reduce tax bill legally.
    Runs daily — surfaces opportunities before they expire.
    """

    def generate_suggestions(self, profile_id: int) -> list:
        suggestions = []
        portfolio   = get_all_portfolios(profile_id)
        today       = date.today()
        fy_end      = date(today.year if today.month >= 4 else today.year - 1, 3, 31)
        days_to_fy_end = (fy_end - today).days

        # 1. LTCG threshold approaching (hold X more days)
        for position in portfolio.open_positions:
            if position.instrument_type == 'equity':
                holding_days = (today - position.purchase_date).days
                days_to_ltcg = 365 - holding_days

                if 0 < days_to_ltcg <= 30:
                    tax_saving = self.calculate_ltcg_saving(position)
                    if tax_saving > 500:
                        suggestions.append({
                            'type':         'HOLD_FOR_LTCG',
                            'priority':     'HIGH',
                            'ticker':       position.ticker,
                            'action':       f"Hold {days_to_ltcg} more days",
                            'saving':       tax_saving,
                            'deadline':     (position.purchase_date + timedelta(365)).isoformat(),
                            'description':  f"Holding {position.ticker} {days_to_ltcg} more days saves ₹{tax_saving:,.0f} in tax (STCG 20% → LTCG 12.5%)"
                        })

        # 2. LTCG exemption not fully used
        ytd_ltcg = get_ytd_ltcg(profile_id)
        if ytd_ltcg < 125000:
            remaining_exempt = 125000 - ytd_ltcg
            # Find LTCG positions that could be booked tax-free
            exempt_candidates = [
                pos for pos in portfolio.open_positions
                if (today - pos.purchase_date).days >= 365
                and pos.unrealized_gain > 0
                and pos.unrealized_gain <= remaining_exempt
            ]
            if exempt_candidates:
                suggestions.append({
                    'type':         'USE_LTCG_EXEMPTION',
                    'priority':     'MEDIUM',
                    'action':       'Book LTCG gains within ₹1.25L exemption',
                    'saving':       remaining_exempt * 0.125 * 1.04,
                    'description':  f"₹{remaining_exempt:,.0f} of LTCG exemption unused. Book profits on: {', '.join(p.ticker for p in exempt_candidates[:3])} TAX-FREE",
                    'deadline':     'Before March 31'
                })

        # 3. Tax loss harvesting before year end
        if days_to_fy_end <= 60:
            loss_positions = [
                pos for pos in portfolio.open_positions
                if pos.unrealized_pnl < 0
            ]

            if loss_positions:
                for pos in loss_positions:
                    loss    = abs(pos.unrealized_pnl)
                    tax_saved = self.calculate_loss_harvest_saving(pos, portfolio, profile_id)
                    costs   = calculate_round_trip_charges(pos.ticker, pos.shares, pos.current_price)

                    if tax_saved > costs + 500:
                        suggestions.append({
                            'type':         'HARVEST_LOSS',
                            'priority':     'HIGH' if days_to_fy_end <= 30 else 'MEDIUM',
                            'ticker':       pos.ticker,
                            'action':       f"Sell at loss ₹{loss:,.0f} to offset gains",
                            'saving':       tax_saved - costs,
                            'deadline':     fy_end.isoformat(),
                            'description':  f"Booking loss on {pos.ticker} saves ₹{tax_saved-costs:,.0f} tax. India has no wash sale rule — can rebuy same day.",
                            'rebuy_note':   'No wash sale rule in India — can rebuy immediately to maintain position'
                        })

        # 4. Advance tax reminder
        adv_calc        = AdvanceTaxCalculator()
        estimated_tax   = get_estimated_annual_tax(profile_id)
        tds             = get_tds_ytd(profile_id)
        advance_paid    = get_advance_tax_paid(profile_id)
        schedule        = adv_calc.calculate_installments(estimated_tax, tds)
        next_inst       = schedule['next_installment']

        if next_inst and next_inst['days_away'] <= 15:
            suggestions.append({
                'type':         'ADVANCE_TAX_DUE',
                'priority':     'CRITICAL',
                'action':       f"Pay advance tax: ₹{next_inst['amount']:,.0f}",
                'deadline':     next_inst['due_date'].isoformat(),
                'description':  f"Advance tax installment due in {next_inst['days_away']} days. Late payment attracts 1% monthly penalty under Section 234C.",
                'payment_link': 'https://www.incometax.gov.in/iec/foportal/help/how-to-pay-taxes-online'
            })

        # 5. F&O audit threshold warning
        fo_turnover = get_fo_turnover_ytd(profile_id)
        if fo_turnover > 8_00_00_000:  # ₹8Cr — approaching ₹10Cr threshold
            suggestions.append({
                'type':         'FO_AUDIT_THRESHOLD',
                'priority':     'HIGH',
                'action':       'Prepare for tax audit',
                'description':  f"F&O turnover ₹{fo_turnover/1e7:.1f}Cr — approaching ₹10Cr mandatory audit threshold. Consult CA immediately.",
                'turnover':     fo_turnover
            })

        # 6. Crypto TDS reconciliation
        crypto_tds_deducted = get_crypto_tds_ytd(profile_id)
        if crypto_tds_deducted > 0:
            suggestions.append({
                'type':         'CRYPTO_TDS_RECONCILE',
                'priority':     'LOW',
                'action':       f"Verify crypto TDS of ₹{crypto_tds_deducted:,.0f} in Form 26AS",
                'description':  'TDS on crypto transactions should appear in Form 26AS. Verify and claim credit.',
                'form':         '26AS / AIS'
            })

        # Sort by priority
        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        suggestions.sort(key=lambda x: priority_order.get(x['priority'], 4))

        return {
            'suggestions':          suggestions,
            'total_savings':        sum(s.get('saving', 0) for s in suggestions if isinstance(s.get('saving'), (int, float))),
            'critical_count':       sum(1 for s in suggestions if s['priority'] == 'CRITICAL'),
            'high_count':           sum(1 for s in suggestions if s['priority'] == 'HIGH'),
            'generated_at':         datetime.now().isoformat()
        }
```

---

# SECTION H — COMPLETE CA EXPORT PACKAGE

## H.1 Year-End Package Generator

```python
def generate_ca_package(profile_id: int, financial_year: str) -> str:
    """
    Generate complete package for CA review.
    Exports to Excel with multiple sheets.
    One file, everything CA needs to file your ITR.
    """
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, numbers

    wb = openpyxl.Workbook()

    # === Sheet 1: SUMMARY ===
    ws1 = wb.active
    ws1.title = "TAX SUMMARY"

    cumulative = CumulativeTaxBillEngine()
    bill = cumulative.calculate_cumulative_bill(profile_id, financial_year)

    summary_data = [
        ["FINANCELAB TAX SUMMARY", f"FY {financial_year}", "", ""],
        ["Profile", get_profile(profile_id).name, "", ""],
        ["PAN", get_profile(profile_id).pan or "NOT PROVIDED", "", ""],
        ["Generated", date.today().isoformat(), "", ""],
        ["", "", "", ""],
        ["INCOME HEAD", "GROSS", "TAXABLE", "TAX"],
        ["STCG (Equity/ETF) @ 20%", bill['india']['stcg_equity'],
         bill['india']['stcg_equity'], bill['india']['tax_stcg']],
        ["LTCG (Equity/ETF) @ 12.5%", bill['india']['ltcg_equity'],
         max(0, bill['india']['ltcg_equity'] - 125000), bill['india']['tax_ltcg']],
        ["F&O Business Income", bill['india']['fo_income'],
         bill['india']['fo_income'], bill['india']['tax_fo']],
        ["Intraday Speculative", bill['india']['intraday_income'],
         bill['india']['intraday_income'], "At slab"],
        ["Dividend Income", bill['india']['dividend_income'],
         bill['india']['dividend_income'], "At slab"],
        ["Crypto/VDA @ 30%", bill['india']['crypto_income'],
         bill['india']['crypto_income'], bill['india']['tax_crypto']],
        ["US Source Income (after FTC)", bill['foreign_income']['us_gain_inr'],
         bill['foreign_income']['us_gain_inr'], bill['foreign_income']['net_india_tax_on_us']],
        ["UK Source Income (after FTC)", bill['foreign_income']['uk_gain_inr'],
         bill['foreign_income']['uk_gain_inr'], bill['foreign_income']['net_india_tax_on_uk']],
        ["", "", "", ""],
        ["TOTAL TAX LIABILITY", "", "", bill['summary']['total_tax_liability']],
        ["TDS Deducted", "", "", -bill['summary']['tds_deducted']],
        ["Advance Tax Paid", "", "", -bill['summary']['advance_tax_paid']],
        ["BALANCE PAYABLE", "", "", bill['summary']['balance_payable']],
        ["Refund Due", "", "", bill['summary']['refund_due']],
        ["Penalty u/s 234B (if any)", "", "", bill['summary']['penalty_234b']],
        ["", "", "", ""],
        ["ITR Form Required", bill['itr_form'], "", ""],
        ["Form 67 Required", "YES" if bill['form_67_required'] else "NO", "", ""],
        ["F&O Audit Required", "YES" if bill['india']['fo_income'] else "NO", "", ""],
    ]

    for row_data in summary_data:
        ws1.append(row_data)

    # === Sheet 2: ALL TRANSACTIONS ===
    ws2 = wb.create_sheet("ALL TRANSACTIONS")
    headers = [
        "Date", "Ticker", "Name", "Portfolio", "Exchange",
        "Instrument", "Action", "Qty", "Price", "Currency",
        "INR Rate", "Total Value INR", "Charges",
        "Holding Days", "Tax Treatment", "Cost Basis",
        "Gain/Loss", "Taxable Gain", "Tax Amount", "Notes"
    ]
    ws2.append(headers)

    all_txs = get_all_transactions(profile_id, financial_year)
    for tx in sorted(all_txs, key=lambda x: x.trade_date):
        ws2.append([
            tx.trade_date.isoformat(),
            tx.ticker,
            tx.name,
            get_portfolio(tx.portfolio_id).name,
            tx.exchange,
            tx.instrument_type.value,
            tx.action.value,
            float(tx.quantity),
            float(tx.price),
            tx.currency,
            float(tx.inr_rate) if tx.inr_rate else 1.0,
            float(tx.amount_inr) if tx.amount_inr else float(tx.price * tx.quantity),
            float(tx.total_charges),
            tx.holding_days or "",
            tx.tax_treatment.value if tx.tax_treatment else "",
            "",  # Cost basis from lot matching
            float(tx.taxable_gain) if tx.taxable_gain else "",
            float(tx.taxable_gain) if tx.taxable_gain else "",
            float(tx.tax_amount) if tx.tax_amount else "",
            tx.notes
        ])

    # === Sheet 3: SCHEDULE CG (Capital Gains) ===
    ws3 = wb.create_sheet("SCHEDULE CG")

    ws3.append(["SCHEDULE CG — CAPITAL GAINS", f"FY {financial_year}"])
    ws3.append([])
    ws3.append(["PART A: SHORT TERM CAPITAL GAINS (Section 111A) @ 20%"])
    stcg_headers = ["Sr", "Security Name", "ISIN", "Buy Date", "Sell Date",
                    "Quantity", "Full Value (₹)", "Cost of Acquisition (₹)",
                    "Charges (₹)", "Net Consideration (₹)", "STCG (₹)"]
    ws3.append(stcg_headers)

    stcg_txs = [tx for tx in all_txs if tx.tax_treatment == TaxTreatment.INDIA_STCG_EQUITY
                and tx.action == ActionType.SELL]
    for i, tx in enumerate(stcg_txs, 1):
        ws3.append([
            i, tx.name, tx.isin or "", "", tx.trade_date.isoformat(),
            float(tx.quantity), float(tx.price * tx.quantity),
            "", float(tx.total_charges), "",
            float(tx.taxable_gain) if tx.taxable_gain else ""
        ])

    ws3.append([])
    ws3.append(["TOTAL STCG", "", "", "", "", "", "", "", "", "",
                float(bill['india']['stcg_equity'])])
    ws3.append(["TAX @ 20% + 4% Cess", "", "", "", "", "", "", "", "", "",
                float(bill['india']['tax_stcg'])])

    ws3.append([])
    ws3.append(["PART B: LONG TERM CAPITAL GAINS (Section 112A) @ 12.5%"])
    ltcg_headers = ["Sr", "Security Name", "ISIN", "Buy Date", "Sell Date",
                    "Quantity", "Full Value (₹)", "Cost (₹)", "FMV 31 Jan 2018 (₹)",
                    "Net Consideration (₹)", "LTCG (₹)"]
    ws3.append(ltcg_headers)

    ltcg_txs = [tx for tx in all_txs if tx.tax_treatment == TaxTreatment.INDIA_LTCG_EQUITY
                and tx.action == ActionType.SELL]
    for i, tx in enumerate(ltcg_txs, 1):
        ws3.append([
            i, tx.name, tx.isin or "", "", tx.trade_date.isoformat(),
            float(tx.quantity), float(tx.price * tx.quantity),
            "", "", "", float(tx.taxable_gain) if tx.taxable_gain else ""
        ])

    ws3.append([])
    ws3.append(["GROSS LTCG", "", "", "", "", "", "", "", "", "",
                float(bill['india']['ltcg_equity'])])
    ws3.append(["Exemption u/s 112A", "", "", "", "", "", "", "", "", "", -125000])
    ws3.append(["TAXABLE LTCG", "", "", "", "", "", "", "", "", "",
                float(max(0, bill['india']['ltcg_equity'] - 125000))])
    ws3.append(["TAX @ 12.5% + 4% Cess", "", "", "", "", "", "", "", "", "",
                float(bill['india']['tax_ltcg'])])

    # === Sheet 4: F&O SCHEDULE (Business Profit) ===
    ws4 = wb.create_sheet("F&O BUSINESS INCOME")
    fo_txs = [tx for tx in all_txs
              if tx.instrument_type in [InstrumentType.FUTURES, InstrumentType.OPTIONS]]

    ws4.append(["F&O BUSINESS INCOME — SCHEDULE BP", f"FY {financial_year}"])
    ws4.append([])

    fo_summary = IndiaTaxEngine(get_profile(profile_id)).fo_turnover_calculation(fo_txs)

    ws4.append(["GROSS PROFIT FROM F&O", fo_summary['total_profit']])
    ws4.append(["GROSS LOSS FROM F&O", fo_summary['total_loss']])
    ws4.append(["NET F&O INCOME", fo_summary['net_fo_income']])
    ws4.append([])
    ws4.append(["DEDUCTIBLE EXPENSES"])
    expenses = ChargesDeductionTracker().calculate_deductible_expenses(fo_txs, {})
    for expense, amount in expenses['transaction_charges'].items():
        ws4.append([expense.replace('_', ' ').title(), amount])
    ws4.append(["TOTAL EXPENSES", expenses['total_deductible']])
    ws4.append([])
    ws4.append(["TAXABLE F&O INCOME", fo_summary['net_fo_income'] - expenses['total_deductible']])
    ws4.append([])
    ws4.append(["F&O TURNOVER", fo_summary['total_turnover']])
    ws4.append(["AUDIT REQUIRED", "YES" if fo_summary['audit_required'] else "NO"])

    # === Sheet 5: CARRY FORWARD LOSSES ===
    ws5 = wb.create_sheet("CARRY FORWARD LOSSES")
    ws5.append(["LOSSES TO CARRY FORWARD", f"FY {financial_year}"])
    ws5.append([])
    cf = bill['carry_forward']
    ws5.append(["STCG Losses (can offset STCG/LTCG — 8 years)", cf.get('stcg_loss', 0)])
    ws5.append(["LTCG Losses (can offset LTCG only — 8 years)", cf.get('ltcg_loss', 0)])
    ws5.append(["F&O Losses (can offset F&O/business — 8 years)", cf.get('fo_loss', 0)])
    ws5.append(["Intraday Losses (can offset intraday only — 4 years)", cf.get('intraday_loss', 0)])
    ws5.append([])
    ws5.append(["IMPORTANT: File ITR on time to carry forward losses"])
    ws5.append(["IMPORTANT: Crypto losses CANNOT be carried forward"])

    # === Sheet 6: FOREIGN INCOME (Schedule FSI) ===
    ws6 = wb.create_sheet("FOREIGN INCOME (Sch FSI)")
    ws6.append(["SCHEDULE FSI — FOREIGN SOURCE INCOME", f"FY {financial_year}"])
    ws6.append(["(India resident must disclose ALL foreign income)"])
    ws6.append([])

    headers_fsi = ["Country", "Nature of Income", "Amount (Foreign)", "Currency",
                   "FX Rate (RBI)", "Amount INR", "Foreign Tax Paid INR",
                   "FTC Available INR", "Net India Tax INR"]
    ws6.append(headers_fsi)

    # US income
    ws6.append([
        "USA", "Capital Gains from US Stocks",
        bill['foreign_income']['us_gain_inr'], "USD",
        "", bill['foreign_income']['us_gain_inr'],
        bill['foreign_income']['us_ftc_available'],
        bill['foreign_income']['us_ftc_available'],
        bill['foreign_income']['net_india_tax_on_us']
    ])

    ws6.append([
        "USA", "Dividend Income from US Stocks",
        bill['foreign_income']['us_dividend_inr'], "USD",
        "", bill['foreign_income']['us_dividend_inr'],
        "", "", ""
    ])

    # UK income
    ws6.append([
        "United Kingdom", "Capital Gains from UK Stocks",
        bill['foreign_income']['uk_gain_inr'], "GBP",
        "", bill['foreign_income']['uk_gain_inr'],
        bill['foreign_income']['uk_ftc_available'],
        bill['foreign_income']['uk_ftc_available'],
        bill['foreign_income']['net_india_tax_on_uk']
    ])

    # === Sheet 7: ADVANCE TAX ===
    ws7 = wb.create_sheet("ADVANCE TAX SCHEDULE")
    ws7.append(["ADVANCE TAX SCHEDULE", f"FY {financial_year}"])
    ws7.append([])
    ws7.append(["Total Estimated Tax Liability", bill['summary']['total_tax_liability']])
    ws7.append(["TDS Already Deducted", bill['summary']['tds_deducted']])
    ws7.append(["Net Advance Tax Required", bill['advance_tax']['net_advance_tax']])
    ws7.append([])
    ws7.append(["INSTALLMENT", "DUE DATE", "CUMULATIVE %", "AMOUNT DUE", "STATUS"])

    for q, inst in bill['advance_tax']['installments'].items():
        ws7.append([
            q,
            inst['due_date'].isoformat(),
            f"{int(inst['cumulative_required'] / bill['advance_tax']['net_advance_tax'] * 100)}%"
            if bill['advance_tax']['net_advance_tax'] > 0 else "N/A",
            inst['installment_amount'],
            inst['status']
        ])

    # Save file
    filename    = f"FinanceLab_Tax_FY{financial_year.replace('-','_')}_{date.today()}.xlsx"
    filepath    = f"/tmp/{filename}"
    wb.save(filepath)

    return filepath
```

---

# SECTION I — DASHBOARD DESIGN SPECIFICATION

## I.1 Transaction Entry Form

```
MANUAL TRANSACTION ENTRY FORM
═══════════════════════════════════════════════════════════

STEP 1: BASIC DETAILS
  Ticker / Symbol:      [_______________]  [Search]
  Instrument Type:      [Equity ▼]
  Exchange:             [NSE ▼]
  Portfolio:            [Zerodha Main ▼]
  Action:               [Buy ○] [Sell ○]
  Trade Date:           [dd/mm/yyyy]
  Quantity:             [_______]
  Price per unit:       ₹[_______]
  Currency:             [INR ▼]

STEP 2: CHARGES (auto-calculated, can override)
  Brokerage:            ₹[_______]  [Calculate]
  STT:                  ₹[_______]  [Calculate]
  Exchange charges:     ₹[_______]  [Calculate]
  GST on charges:       ₹[_______]  [Calculate]
  Stamp duty:           ₹[_______]  [Calculate]
  DP charges:           ₹[_______]  [Sell only]
  Total charges:        ₹[_______]  [AUTO]
  Net amount:           ₹[_______]  [AUTO]

STEP 3: CROSS-BORDER (if applicable)
  Foreign currency:     [USD ▼]
  INR rate on trade date: ₹[_______]
  Foreign tax withheld: [_______] [USD]
  Amount in INR:        ₹[_______]  [AUTO]

STEP 4: TAX PREVIEW (AUTO)
  ┌──────────────────────────────────┐
  │  TAX CLASSIFICATION              │
  │  Treatment: STCG (held 187 days) │
  │  Cost basis: ₹1,23,456           │
  │  Net gain:   ₹23,456             │
  │  Tax @ 20%:  ₹4,691              │
  │  After tax:  ₹18,765             │
  │                                  │
  │  ⚠️ HOLD 178 more days           │
  │  → Save ₹1,756 tax (LTCG 12.5%) │
  └──────────────────────────────────┘

NOTES:  [___________________________________]

[Save Transaction]  [Save & Add Another]  [Cancel]
```

## I.2 Cumulative Tax Bill Dashboard

```
FINANCELAB TAX CENTRE — FY 2024-25
═══════════════════════════════════════════════════════════

RUNNING TAX LIABILITY                      As of Jan 15, 2025

  ┌──────────────┬─────────────┬───────────┬──────────────┐
  │ INDIA STCG   │ INDIA LTCG  │ F&O       │ CRYPTO       │
  │ ₹12,450 tax  │ ₹8,320 tax  │ ₹34,200   │ ₹6,000       │
  │ (₹62,250 gain)│ (₹66,560 gain)│ (business)│ (30% flat)  │
  └──────────────┴─────────────┴───────────┴──────────────┘

  ┌──────────────┬─────────────┐
  │ DIVIDENDS    │ FOREIGN     │
  │ ₹3,200       │ ₹8,400      │
  │ (slab rate)  │ (US+UK-FTC) │
  └──────────────┴─────────────┘

  ════════════════════════════════
  TOTAL TAX LIABILITY:    ₹72,570
  TDS Already Deducted:   -₹8,400
  Advance Tax Paid:       -₹15,000
  ────────────────────────────────
  BALANCE PAYABLE:        ₹49,170
  ════════════════════════════════

ADVANCE TAX SCHEDULE:
  ✅ Q1 (Jun 15):  ₹10,886 — PAID
  ✅ Q2 (Sep 15):  ₹21,771 — PAID (₹15,000 paid — SHORT by ₹6,771)
  ⚠️ Q3 (Dec 15):  ₹21,771 — DUE IN 15 DAYS
  📅 Q4 (Mar 15):  ₹18,142 — UPCOMING

  ⚠️ PAY NOW: ₹21,771 at incometax.gov.in
     Late payment penalty: ₹218/month (234C)

PER-PORTFOLIO BREAKDOWN:
  Zerodha Main:    ₹34,500 liability  [View Details]
  HDFC Sky:        ₹18,200 liability  [View Details]
  IBKR (US):       ₹12,400 liability  [View Details]
  Upstox Options:  ₹7,470  liability  [View Details]

TAX OPTIMIZATION (₹18,340 potential saving):
  🟢 HIGH:  Hold INFY 23 more days → Save ₹4,200 (STCG→LTCG)
  🟡 MED:   Book ₹40,000 LTCG gain — still within ₹1.25L exemption
  🟡 MED:   Harvest PAYTM loss ₹28,000 → Save ₹5,600 in tax
  🔵 LOW:   Verify CDSL TDS ₹8,400 in Form 26AS

CARRY FORWARD LOSSES:
  LTCG Loss (FY23-24):   ₹45,000  (can offset LTCG gains)
  F&O Loss (FY23-24):    ₹1,20,000 (can offset business income)

[Export to Excel for CA]  [Generate Form 67]  [Pay Advance Tax]
```

---

# SECTION J — KEY TAX DATES CALENDAR

## India Tax Calendar
```
ADVANCE TAX:
  June 15        Q1 — Pay 15% of estimated annual tax
  September 15   Q2 — Pay 45% cumulative
  December 15    Q3 — Pay 75% cumulative
  March 15       Q4 — Pay 100%

ITR FILING:
  July 31        Due date for individuals (non-audit)
  October 31     Due date for audit cases
  December 31    Belated ITR last date
  March 31       Revised ITR last date

FORM 26AS:
  Available:     15th of month following quarter
  Download:      incometax.gov.in (login required)

FINANCIAL YEAR:
  April 1        Start of new FY
  March 31       End of FY (book losses before this!)

KEY TAX DEADLINES FOR TRADERS:
  March 31       Last day to book tax losses for the year
  March 31       Last day to pay 100% advance tax
  July 31        File ITR-3 (F&O traders)
  October 31     Audit report due (if turnover > ₹10Cr)
  Before ITR     File Form 67 to claim FTC

LTCG TAX COLLECTION:
  Budget date     New LTCG rates effective from announcement
  July 23, 2024   New rates: LTCG 12.5%, STCG 20%
                  (any sale AFTER July 23, 2024 at new rates)
```

## US Tax Calendar (for India residents)
```
No US tax filing required for India residents
Unless: US citizen/green card holder

DIVIDEND WITHHOLDING:
  Paid quarterly by most US companies
  Withheld at 25% (DTAA rate with W-8BEN)
  Without W-8BEN: 30% default withholding

FORM W-8BEN:
  File with US broker (IBKR, Schwab etc)
  Valid for 3 years
  Claims 25% DTAA rate on dividends
  Download: irs.gov/pub/irs-pdf/fw8ben.pdf

INDIA REPORTING:
  Schedule FSI: All foreign income
  Schedule FA: All foreign assets
  Form 67: Foreign tax credit claim
  All filed as part of India ITR
```

---

*FinanceLab Complete Tax Engine*
*India Resident · Global Investments · FY 2024-25 Rates*
*Covers: India (all instruments) · US (DTAA) · UK (DTAA) · Europe (DTAA)*
*Updated for: Budget July 2024 rates (STCG 20%, LTCG 12.5%, LTCG exemption ₹1.25L)*
*Inject into Ollama RAG for complete AI tax context*

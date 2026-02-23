"""
KrishiMind AI — Crop Price Prediction & Advisory Service
Uses weighted moving average + trend extrapolation on historical price data
to predict future crop prices and generate farmer advisory.
"""

import json
import math
import os
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

# Path to historical data
HISTORY_FILE = Path(__file__).parent.parent / 'data' / 'crop_price_history.json'


ORIGINAL_HISTORY_FILE = Path(__file__).parent.parent / 'data' / 'original_crop_history.json'


def _load_history():
    """Load crop price history configuration."""
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def _load_original_history():
    """Load original mandi history if exists."""
    if not ORIGINAL_HISTORY_FILE.exists():
        return None
    try:
        with open(ORIGINAL_HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None


def _get_original_history(crop_name, state=None):
    """
    Get original history for a crop and fill gaps using linear interpolation.
    If state is provided, attempts to find state-specific history.
    """
    data = _load_original_history()
    if not data or crop_name not in data.get('crops', {}):
        return None, None

    crop_data = data['crops'][crop_name]
    raw_history = []
    source_label = 'data.gov.in (National)'

    # Try state-specific history first
    if state and 'states' in crop_data and state in crop_data['states']:
        raw_history = crop_data['states'][state]
        source_label = f'data.gov.in ({state})'
    else:
        raw_history = crop_data.get('history', [])

    if not raw_history:
        return None, None

    # Parse dates and map prices
    history_map = {h['date']: h['price'] for h in raw_history}
    dates = sorted(history_map.keys())
    
    start_dt = datetime.strptime(dates[0], '%Y-%m-%d')
    end_dt = datetime.strptime(dates[-1], '%Y-%m-%d')
    total_days = (end_dt - start_dt).days + 1
    
    full_history = []
    for i in range(total_days):
        current_dt = start_dt + timedelta(days=i)
        iso_date = current_dt.strftime('%Y-%m-%d')
        
        if iso_date in history_map:
            full_history.append({'date': iso_date, 'price': history_map[iso_date]})
        else:
            prev_date = next((d for d in reversed(dates) if d < iso_date), None)
            next_date = next((d for d in dates if d > iso_date), None)
            
            if prev_date and next_date:
                p_dt, n_dt = datetime.strptime(prev_date, '%Y-%m-%d'), datetime.strptime(next_date, '%Y-%m-%d')
                p_val, n_val = history_map[prev_date], history_map[next_date]
                total_gap = (n_dt - p_dt).days
                since_prev = (current_dt - p_dt).days
                interpolated = p_val + (n_val - p_val) * (since_prev / total_gap)
                full_history.append({'date': iso_date, 'price': round(interpolated)})
            elif prev_date:
                full_history.append({'date': iso_date, 'price': history_map[prev_date]})
            elif next_date:
                full_history.append({'date': iso_date, 'price': history_map[next_date]})
    
    return full_history, source_label


def _generate_daily_prices(monthly_prices, volatility, days=365):
    """
    Generate synthetic daily prices from monthly averages.
    Uses deterministic seeding so results are consistent per day.
    """
    daily = []
    today = datetime.now()
    start = today - timedelta(days=days)

    for d in range(days):
        current_date = start + timedelta(days=d)
        month_idx = current_date.month - 1  # 0-indexed
        base = monthly_prices[month_idx]

        # Deterministic daily variation using date as seed
        seed_str = f"{current_date.strftime('%Y%m%d')}"
        seed_val = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
        noise = ((seed_val % 200) - 100) / 100.0  # -1 to +1
        variation = noise * volatility

        price = max(100, round(base + variation))
        daily.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'price': price
        })

    return daily


def _weighted_moving_average(prices, window=30):
    """Compute weighted moving average (recent prices weighted more)."""
    if len(prices) < window:
        window = len(prices)
    weights = list(range(1, window + 1))  # 1, 2, 3, ... window
    total_weight = sum(weights)
    recent = prices[-window:]
    wma = sum(p * w for p, w in zip(recent, weights)) / total_weight
    return round(wma)


def _compute_trend(prices, days=30):
    """
    Compute price trend using linear regression slope on recent data.
    Returns slope per day (positive = rising, negative = falling).
    """
    recent = prices[-days:]
    n = len(recent)
    if n < 2:
        return 0.0
    x_mean = (n - 1) / 2
    y_mean = sum(recent) / n
    numerator = sum((i - x_mean) * (y - y_mean) for i, y in enumerate(recent))
    denominator = sum((i - x_mean) ** 2 for i in range(n))
    if denominator == 0:
        return 0.0
    return numerator / denominator


def predict_prices(crop_name, forecast_days=30, state=None):
    """
    Generate price prediction for a specific crop.
    Prioritizes state-specific history if provided.
    """
    config = _load_history()
    crops_config = config.get('crops', {})

    if crop_name not in crops_config:
        return None

    crop_meta = crops_config[crop_name]
    msp = crop_meta['msp']
    volatility = crop_meta.get('daily_volatility', 50)
    monthly = crop_meta.get('monthly_prices', [2000]*12)

    # Try original history first (prioritizing state if provided)
    data = _load_original_history()
    last_updated = data.get('last_updated') if data else None
    
    history, source = _get_original_history(crop_name, state=state)

    if not history:
        # Fallback to 365 days of synthetic history
        history = _generate_daily_prices(monthly, volatility, days=365)
        source = 'Synthetic Model'
    
    price_values = [h['price'] for h in history]
    current_price = price_values[-1]

    # Moving averages
    ma_30 = _weighted_moving_average(price_values, 30)
    ma_90 = _weighted_moving_average(price_values, min(len(price_values), 90))

    # Trend slope
    slope_30 = _compute_trend(price_values, min(len(price_values), 30))
    slope_90 = _compute_trend(price_values, min(len(price_values), 90))

    # Determine trend direction
    if slope_30 > 0.5:
        trend = 'rising'
    elif slope_30 < -0.5:
        trend = 'falling'
    else:
        trend = 'stable'

    # Forecast: extrapolate from weighted average with trend
    forecast = []
    # Start from last date in history
    last_date_str = history[-1]['date']
    last_dt = datetime.strptime(last_date_str, '%Y-%m-%d')
    
    for d in range(1, forecast_days + 1):
        future_date = last_dt + timedelta(days=d)

        # Base prediction: weighted avg + trend * days
        predicted = ma_30 + slope_30 * d

        # Add seasonal influence from monthly context
        month_idx = future_date.month - 1
        seasonal_pull = (monthly[month_idx] - ma_30) * 0.2
        predicted += seasonal_pull

        # Dampen extreme predictions (no more than 20% change)
        max_change = current_price * 0.25
        predicted = max(current_price - max_change, min(current_price + max_change, predicted))

        # Add slight noise for realism
        seed_str = f"{crop_name}{future_date.strftime('%Y%m%d')}"
        seed_val = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
        noise = ((seed_val % 100) - 50) / 100.0 * (volatility * 0.3)

        final_price = max(100, round(predicted + noise))
        forecast.append({
            'date': future_date.strftime('%Y-%m-%d'),
            'price': final_price,
            'lower': max(100, round(final_price - volatility * 1.5)),
            'upper': round(final_price + volatility * 1.5)
        })

    # Predicted price at end of forecast
    predicted_price = forecast[-1]['price'] if forecast else current_price
    
    # Confidence (lower volatility = higher confidence, real data = higher confidence)
    base_conf = 100 - (volatility / 150 * 50) # 0 to 150 volatility mapping
    if history and source.startswith('data.gov.in'):
        base_conf += 5 # Bonus for real data
    confidence = max(40, min(98, round(base_conf)))

    return {
        'crop': crop_name,
        'icon': _get_icon(crop_name),
        'msp': msp,
        'current_price': current_price,
        'predicted_price': predicted_price,
        'history': history,
        'prediction': forecast,
        'moving_avg_30': ma_30,
        'moving_avg_90': ma_90,
        'trend': trend,
        'slope_per_day': round(slope_30, 2),
        'confidence': confidence,
        'forecast_days': forecast_days,
        'source': source,
        'last_updated': last_updated
    }


def generate_advisory(crop_name=None, state=None):
    """
    Generate farmer advisory for one or all crops.
    Returns buy/sell/hold recommendations based on state if provided.
    """
    data = _load_history()
    crops = data.get('crops', {})

    target_crops = [crop_name] if crop_name else list(crops.keys())
    advisories = []

    for name in target_crops:
        if name not in crops:
            continue

        pred = predict_prices(name, forecast_days=30, state=state)
        if not pred:
            continue

        current = pred['current_price']
        predicted = pred['predicted_price']
        msp = pred['msp']
        trend = pred['trend']
        change_pct = round((predicted - current) / max(current, 1) * 100, 1)

        # Generate verdict
        verdict, reason, action_color = _compute_verdict(
            current, predicted, msp, trend, change_pct, name
        )

        advisories.append({
            'crop': name,
            'icon': pred['icon'],
            'verdict': verdict,
            'reason': reason,
            'action_color': action_color,
            'current_price': current,
            'predicted_price': predicted,
            'change_pct': change_pct,
            'msp': msp,
            'trend': trend,
            'source': pred.get('source', 'AI Model'),
            'confidence': pred['confidence']
        })

    return advisories


def _compute_verdict(current, predicted, msp, trend, change_pct, crop):
    """Compute advisory verdict based on price analysis."""

    # Volatile crops (no MSP) — different logic
    if msp is None:
        if change_pct > 8:
            return 'HOLD', f'Prices expected to rise {change_pct}% — wait for better rates', 'green'
        elif change_pct < -8:
            return 'SELL NOW', f'Prices may drop {abs(change_pct)}% — sell current stock', 'red'
        else:
            return 'MONITOR', f'Prices relatively stable ({change_pct:+.1f}%) — watch market daily', 'amber'

    # MSP crops
    msp_ratio = current / msp if msp > 0 else 1.0

    if trend == 'rising' and change_pct > 5:
        return 'HOLD', f'Prices rising {change_pct}% above current. Wait for peak before selling', 'green'
    elif trend == 'falling' and change_pct < -5:
        if msp_ratio < 1.05:
            return 'SELL AT MSP', f'Market price falling. Sell at MSP (Rs {msp}/qt) for guaranteed income', 'blue'
        else:
            return 'SELL NOW', f'Prices dropping {abs(change_pct)}%. Current price Rs {current}/qt is above MSP', 'red'
    elif current > msp * 1.15:
        return 'SELL IN MANDI', f'Market price Rs {current}/qt is {round((msp_ratio-1)*100)}% above MSP. Good time to sell', 'green'
    elif current < msp * 0.95:
        return 'SELL AT MSP', f'Market below MSP. Use government procurement at Rs {msp}/qt', 'blue'
    else:
        return 'HOLD', f'Prices stable near MSP ({change_pct:+.1f}%). Monitor for better opportunity', 'amber'


def _get_icon(crop):
    """Get emoji icon for crop."""
    icons = {
        'Wheat': '🌾', 'Rice': '🍚', 'Mustard': '🌻',
        'Cotton': '🏵️', 'Soyabean': '🫘', 'Maize': '🌽',
        'Gram': '🫘', 'Onion': '🧅', 'Tomato': '🍅', 'Potato': '🥔'
    }
    return icons.get(crop, '🌱')


def get_available_crops():
    """Return list of crops available for prediction."""
    data = _load_history()
    return list(data.get('crops', {}).keys())

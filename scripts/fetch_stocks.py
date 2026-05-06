#!/usr/bin/env python3
# fetch_stocks.py
# yfinance で日本株データを取得し data/stocks.json を生成する
# GitHub Actions から平日3回実行される

import json
import os
import sys
from datetime import datetime, timezone, timedelta

import yfinance as yf
import pandas as pd

# 日本時間 (JST = UTC+9)
JST = timezone(timedelta(hours=9))

# scripts/ と同じ階層にある translate_names を import
sys.path.insert(0, os.path.dirname(__file__))
from translate_names import get_name_map

# -------------------------
# 設定
# -------------------------
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
OUTPUT_PATH = os.path.join(DATA_DIR, 'stocks.json')
CSV_PATH = os.path.join(DATA_DIR, 'stocks_list.csv')

# 移動平均の期間
MA_SHORT = 25
MA_LONG = 75

# 財務スコア重み（最大10点 × 4項目 = 40点満点）
SCORE_MAX = 40


def score_yield(div_yield):
    """配当利回り スコア (0-10)。4%以上で満点"""
    if div_yield is None:
        return 0
    if div_yield >= 4.0:
        return 10
    if div_yield <= 0:
        return 0
    return round(div_yield / 4.0 * 10, 1)


def score_pbr(pbr):
    """PBR スコア (0-10)。低いほど高スコア。0.5以下で満点"""
    if pbr is None or pbr <= 0:
        return 0
    if pbr <= 0.5:
        return 10
    if pbr >= 3.0:
        return 0
    return round((3.0 - pbr) / 2.5 * 10, 1)


def score_per(per):
    """PER スコア (0-10)。低いほど高スコア。10倍以下で満点"""
    if per is None or per <= 0:
        return 0
    if per <= 10:
        return 10
    if per >= 30:
        return 0
    return round((30 - per) / 20 * 10, 1)


def score_deviation(dev):
    """移動平均乖離率 スコア (0-10)。-10%以下で満点（割安）"""
    if dev is None:
        return 5  # データなし → 中立
    if dev <= -10:
        return 10
    if dev >= 20:
        return 0
    # -10% ~ +20% を線形マッピング
    return round((20 - dev) / 30 * 10, 1)


def fetch_market_info():
    """市場環境データ（VIX・日経VI）を取得"""
    market = {}
    try:
        vix = yf.Ticker("^VIX")
        vix_hist = vix.history(period="2d")
        if not vix_hist.empty:
            market['vix'] = round(float(vix_hist['Close'].iloc[-1]), 2)
        else:
            market['vix'] = None
    except Exception:
        market['vix'] = None

    try:
        nkvi = yf.Ticker("^JNIV")  # 日経VI
        nkvi_hist = nkvi.history(period="2d")
        if not nkvi_hist.empty:
            market['nikkei_vi'] = round(float(nkvi_hist['Close'].iloc[-1]), 2)
        else:
            market['nikkei_vi'] = None
    except Exception:
        market['nikkei_vi'] = None

    try:
        nk225 = yf.Ticker("^N225")
        nk_hist = nk225.history(period="2d")
        if not nk_hist.empty:
            market['nikkei225'] = round(float(nk_hist['Close'].iloc[-1]), 0)
            if len(nk_hist) >= 2:
                prev = float(nk_hist['Close'].iloc[-2])
                cur = float(nk_hist['Close'].iloc[-1])
                market['nikkei225_change_pct'] = round((cur - prev) / prev * 100, 2)
            else:
                market['nikkei225_change_pct'] = None
        else:
            market['nikkei225'] = None
            market['nikkei225_change_pct'] = None
    except Exception:
        market['nikkei225'] = None
        market['nikkei225_change_pct'] = None

    return market


def fetch_stock(code, name):
    """1銘柄のデータを取得して dict で返す"""
    ticker_symbol = f"{code}.T"
    result = {
        "code": code,
        "name": name,
        "price": None,
        "div_yield": None,
        "per": None,
        "pbr": None,
        "ma25": None,
        "ma75": None,
        "deviation_ma25": None,
        "score": None,
        "score_detail": {
            "yield": 0,
            "pbr": 0,
            "per": 0,
            "deviation": 0
        },
        "error": None
    }

    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info

        # 現在値
        price = info.get('currentPrice') or info.get('regularMarketPrice')
        result['price'] = round(float(price), 1) if price else None

        # 配当利回り (yfinance は 0.035 = 3.5% で返すことが多い)
        dy = info.get('dividendYield')
        if dy is not None:
            result['div_yield'] = round(float(dy) * 100, 2)

        # PER
        per = info.get('trailingPE') or info.get('forwardPE')
        result['per'] = round(float(per), 1) if per else None

        # PBR
        pbr = info.get('priceToBook')
        result['pbr'] = round(float(pbr), 2) if pbr else None

        # 移動平均
        hist = ticker.history(period="6mo")
        if not hist.empty and len(hist) >= MA_SHORT:
            closes = hist['Close']
            ma25 = closes.rolling(MA_SHORT).mean().iloc[-1]
            result['ma25'] = round(float(ma25), 1)
            if result['price'] and ma25:
                result['deviation_ma25'] = round((result['price'] - float(ma25)) / float(ma25) * 100, 2)
            if len(closes) >= MA_LONG:
                ma75 = closes.rolling(MA_LONG).mean().iloc[-1]
                result['ma75'] = round(float(ma75), 1)

        # 財務スコア計算
        s_yield = score_yield(result['div_yield'])
        s_pbr   = score_pbr(result['pbr'])
        s_per   = score_per(result['per'])
        s_dev   = score_deviation(result['deviation_ma25'])
        total   = s_yield + s_pbr + s_per + s_dev

        result['score'] = round(total, 1)
        result['score_detail'] = {
            "yield": s_yield,
            "pbr":   s_pbr,
            "per":   s_per,
            "deviation": s_dev
        }

    except Exception as e:
        result['error'] = str(e)

    return result


def main():
    name_map = get_name_map()
    codes = list(name_map.keys())

    print(f"[{datetime.now(JST).strftime('%Y-%m-%d %H:%M JST')}] 取得開始 — {len(codes)} 銘柄")

    stocks = []
    for i, code in enumerate(codes, 1):
        name = name_map[code]
        print(f"  [{i:02d}/{len(codes)}] {code} {name} ...", end=' ', flush=True)
        data = fetch_stock(code, name)
        stocks.append(data)
        status = f"¥{data['price']:,.0f}" if data['price'] else f"ERROR: {data['error']}"
        print(status)

    # 市場情報
    print("  市場情報 取得中 ...", end=' ', flush=True)
    market = fetch_market_info()
    print(f"VIX={market.get('vix')}, 日経225={market.get('nikkei225')}")

    # JSON 出力
    output = {
        "updated_at": datetime.now(JST).strftime('%Y-%m-%d %H:%M'),
        "updated_at_iso": datetime.now(JST).isoformat(),
        "market": market,
        "stocks": stocks
    }

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✅ 保存完了: {OUTPUT_PATH}")


if __name__ == '__main__':
    main()

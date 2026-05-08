"""
中证红利 vs 国证A股 对比分析 API
数据源: 新浪财经 CN_MarketData.getKLineData
- 中证红利 515180 (sh.515180)
- 国证A股 399317 (sz.399317)
"""

import math
import json
from datetime import datetime, timedelta

import pandas as pd
import numpy as np
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# ============ 指数配置 ============
INDEX_CONFIGS = {
    "hongli": {
        "symbol": "sh515180",
        "name": "中证红利",
    },
    "guozheng": {
        "symbol": "sz399317",
        "name": "国证A股",
    },
}

# ============ 新浪 API ==========

def fetch_kline_sina(symbol: str, datalen: int = 2500) -> pd.DataFrame:
    """
    从新浪财经获取K线数据（240分钟=日K）
    返回不复权数据
    """
    url = (
        f"https://money.finance.sina.com.cn/quotes_service/api/json_v2.php"
        f"/CN_MarketData.getKLineData?symbol={symbol}&scale=240&ma=5&datalen={datalen}"
    )
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    if not data:
        raise HTTPException(status_code=500, detail=f"获取 {symbol} 数据失败")

    records = []
    for line in data:
        records.append({
            "date": line["day"],
            "open": float(line["open"]),
            "close": float(line["close"]),
            "high": float(line["high"]),
            "low": float(line["low"]),
            "volume": float(line["volume"]),
        })

    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    # 日收益率
    df["return"] = df["close"].pct_change().fillna(0)

    # 全收益指数（模拟股息再投）
    df["total_return"] = (1 + df["return"]).cumprod() * 1000

    return df


# ============ 数据计算 ==========

def get_all_data() -> dict:
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=3000)).strftime("%Y-%m-%d")

    dfs = {}
    for key, config in INDEX_CONFIGS.items():
        df = fetch_kline_sina(config["symbol"])
        if df.empty:
            raise HTTPException(status_code=500, detail=f"获取 {config['name']} 数据失败")
        dfs[key] = df

    hongli = dfs["hongli"][["date", "close", "return", "total_return"]].copy()
    guozheng = dfs["guozheng"][["date", "close", "return", "total_return"]].copy()
    guozheng.columns = ["date", "guozheng_close", "guozheng_return", "guozheng_tr"]
    hongli.columns = ["date", "hongli_close", "hongli_return", "hongli_tr"]

    merged = hongli.merge(guozheng, on="date", how="inner")

    # ========== 工具函数 ==========
    def clean(v):
        if v is None or (isinstance(v, float) and math.isnan(v)):
            return None
        return v

    def clean_list(lst):
        return [clean(x) for x in lst]

    # ========== 图表1: 收益走势 ==========
    chart1 = {
        "dates": merged["date"].dt.strftime("%Y-%m-%d").tolist(),
        "hongli": clean_list(merged["hongli_tr"].round(4).tolist()),
        "guozheng": clean_list(merged["guozheng_tr"].round(4).tolist()),
    }

    # ========== 图表2: 布林线 ==========
    merged["ratio"] = merged["hongli_tr"] / merged["guozheng_tr"]
    window = 242
    merged["ratio_ma"] = merged["ratio"].rolling(window=window, min_periods=1).mean()
    merged["ratio_std"] = merged["ratio"].rolling(window=window, min_periods=1).std()
    merged["upper"] = merged["ratio_ma"] + 2 * merged["ratio_std"]
    merged["lower"] = merged["ratio_ma"] - 2 * merged["ratio_std"]

    latest = merged.iloc[-1]
    upper_val, lower_val, ma_val, ratio_val = latest["upper"], latest["lower"], latest["ratio_ma"], latest["ratio"]
    pct_b = (ratio_val - lower_val) / (upper_val - lower_val) if upper_val != lower_val else 0.5
    bandwidth = (upper_val - lower_val) / ma_val * 100 if ma_val != 0 else 0

    chart2 = {
        "dates": merged["date"].dt.strftime("%Y-%m-%d").tolist(),
        "ratio": clean_list(merged["ratio"].round(4).tolist()),
        "ma242": clean_list(merged["ratio_ma"].round(4).tolist()),
        "upper": clean_list(merged["upper"].round(4).tolist()),
        "lower": clean_list(merged["lower"].round(4).tolist()),
        "pctB": round(float(pct_b), 2),
        "bandwidth": round(float(bandwidth), 2),
    }

    # ========== 图表3: 收益差 ==========
    merged["hongli_40d"] = merged["hongli_return"].rolling(window=40, min_periods=1).sum()
    merged["guozheng_40d"] = merged["guozheng_return"].rolling(window=40, min_periods=1).sum()
    merged["profit_diff"] = merged["hongli_40d"] - merged["guozheng_40d"]
    merged["profit_diff_ma242"] = merged["profit_diff"].rolling(window=242, min_periods=1).mean()
    mean_diff = float(merged["profit_diff"].mean())

    chart3 = {
        "dates": merged["date"].dt.strftime("%Y-%m-%d").tolist(),
        "diff": clean_list((merged["profit_diff"] * 100).round(4).tolist()),
        "diff_ma242": clean_list((merged["profit_diff_ma242"] * 100).round(4).tolist()),
        "mean": round(mean_diff * 100, 2),
    }

    # ========== 图表4: RSI ==========
    delta = merged["ratio"].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=14, min_periods=1).mean()
    avg_loss = loss.rolling(window=14, min_periods=1).mean()
    rs = avg_gain / avg_loss
    rsi = (100 - (100 / (1 + rs))).fillna(50)
    merged["rsi14"] = rsi
    merged["rsi_ma242"] = rsi.rolling(window=242, min_periods=1).mean()
    latest_rsi = float(merged["rsi14"].iloc[-1])
    latest_rsi_ma = float(merged["rsi_ma242"].iloc[-1])

    chart4 = {
        "dates": merged["date"].dt.strftime("%Y-%m-%d").tolist(),
        "rsi": clean_list(merged["rsi14"].round(4).tolist()),
        "rsi_ma242": clean_list(merged["rsi_ma242"].round(4).tolist()),
        "latest_rsi": round(latest_rsi, 2),
        "latest_rsi_ma": round(latest_rsi_ma, 2),
    }

    return {
        "chart1": chart1,
        "chart2": chart2,
        "chart3": chart3,
        "chart4": chart4,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


# ============ FastAPI App ============
app = FastAPI(
    title="中证红利对比分析 API",
    version="1.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "time": datetime.now().isoformat()}


@app.get("/api/compare-data")
async def get_compare_data():
    try:
        data = get_all_data()
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=20005)

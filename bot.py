import yfinance as yf
import pandas as pd
from datetime import datetime

def run_bot():
    symbol = "BTC-USD"
    print(f"🚀 [启动] 正在连接市场获取 {symbol} 数据...")
    
    # 1. 获取数据
    try:
        data = yf.download(symbol, period="3mo", interval="1d", progress=False)
        if data.empty:
            print("❌ 错误：未获取到数据，可能是网络问题。")
            return
            
        # 清理多层索引问题 (兼容新版 yfinance)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            
        df = data.copy()

        # 2. 计算 MA12 和 MA20
        df['MA12'] = df['Close'].rolling(window=12).mean()
        df['MA20'] = df['Close'].rolling(window=20).mean()

        # 3. 计算 RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # 4. 获取最新数据
        today = df.iloc[-1]
        price = float(today['Close'])
        ma12 = float(today['MA12'])
        ma20 = float(today['MA20'])
        rsi = float(today['RSI'])
        date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        print("\n" + "="*40)
        print(f"📅 运行时间 (UTC): {date_str}")
        print(f"💰 比特币价格: ${price:,.2f}")
        print(f"📈 指标状况: MA12=${ma12:,.0f} | MA20=${ma20:,.0f} | RSI={rsi:.1f}")
        print("="*40 + "\n")

        # 5. 信号判断
        if ma12 > ma20 and rsi > 50:
            print("🟢 信号：【买入 / 持有】 (趋势向上且动能强)")
        elif ma12 < ma20:
            print("🔴 信号：【卖出 / 空仓】 (趋势向下)")
        else:
            print("🟡 信号：【观望】 (趋势不明或动能不足)")
            
    except Exception as e:
        print(f"❌ 发生未知错误: {e}")

if __name__ == "__main__":
    run_bot()

# 交易日历功能说明

## 功能概述

交易日历功能是缠论分析系统的重要组成部分，提供了与交易日期相关的各种操作，包括：

- 获取最近的交易日
- 判断指定日期是否为交易日
- 获取指定日期范围内的所有交易日
- 获取指定日期前N个交易日

这些功能可以帮助分析系统正确处理交易日期，避免在非交易日进行不必要的计算或信号生成，提高分析的准确性和效率。

## 主要功能

### 获取最近的交易日

```python
from chan_theory_v2.core import get_nearest_trading_date

# 获取当前日期最近的交易日（默认向前查找）
latest_trading_day = get_nearest_trading_date(datetime.now())

# 获取指定日期后的第一个交易日（向后查找）
next_trading_day = get_nearest_trading_date("2023-01-01", direction="forward")
```

### 判断是否为交易日

```python
from chan_theory_v2.core import is_trading_day

# 判断当前日期是否为交易日
is_today_trading = is_trading_day(datetime.now())

# 判断指定日期是否为交易日
is_date_trading = is_trading_day("2023-01-03")
```

### 获取交易日列表

```python
from chan_theory_v2.core import get_trading_dates

# 获取指定日期范围内的所有交易日
trading_days = get_trading_dates("2023-01-01", "2023-01-31")
```

### 获取前N个交易日

```python
from chan_theory_v2.core import get_previous_n_trading_days

# 获取当前日期前5个交易日
prev_days = get_previous_n_trading_days(datetime.now(), 5)
```

## 使用场景

### 1. 数据获取与预处理

在获取K线数据时，可以使用交易日历功能确保查询的日期范围是有效的交易日：

```python
# 获取最近30个交易日的数据
end_date = get_nearest_trading_date(datetime.now(), "backward")
prev_trading_days = get_previous_n_trading_days(end_date, 30)
start_date = prev_trading_days[0]

# 获取K线数据
kline_data = db_handler.get_kline_data(
    stock_code, 
    start_date=start_date.strftime("%Y%m%d"), 
    end_date=end_date.strftime("%Y%m%d")
)
```

### 2. 回测周期选择

在进行策略回测时，可以使用交易日历功能选择合适的回测周期：

```python
# 选择过去一年的交易日进行回测
end_date = get_nearest_trading_date(datetime.now(), "backward")
start_date = get_nearest_trading_date(datetime.now() - timedelta(days=365), "forward")
trading_days = get_trading_dates(start_date, end_date)

# 使用交易日列表进行回测
for day in trading_days:
    # 回测逻辑
    pass
```

### 3. 信号生成与验证

在生成交易信号时，可以使用交易日历功能确保信号生成在有效的交易日：

```python
# 检查当前是否为交易日
if is_trading_day(datetime.now()):
    # 生成交易信号
    pass
else:
    # 获取下一个交易日
    next_trading_day = get_nearest_trading_date(datetime.now(), "forward")
    # 设置定时任务在下一个交易日执行
    pass
```

## 注意事项

1. **数据依赖**：交易日历功能依赖于数据库中的 `infrastructure_trading_calendar` 集合，请确保该集合包含完整的交易日历数据。

2. **日期格式**：函数支持多种日期格式输入，包括 `datetime` 对象、`YYYYMMDD` 格式字符串和 `YYYY-MM-DD` 格式字符串。

3. **交易所选择**：当前实现默认使用上海证券交易所（SSE）的交易日历，如需支持其他交易所，可以修改 `TradingCalendar` 类中的相关代码。

4. **缓存机制**：为提高性能，可以考虑在 `TradingCalendar` 类中实现交易日历数据的缓存机制，减少数据库查询次数。

## 示例代码

完整的使用示例可以参考 `chan_theory_v2/examples/use_trading_calendar.py` 文件。

## 测试

可以运行 `chan_theory_v2/tests/test_trading_calendar.py` 文件测试交易日历功能是否正常工作。

```bash
python chan_theory_v2/tests/test_trading_calendar.py
```

## 未来改进

1. 支持多交易所交易日历
2. 实现交易日历数据的本地缓存
3. 添加更多交易日历相关功能，如获取交易时段、节假日信息等
4. 提供交易日历数据的更新机制
GZH：Mario量化
机器学习中小板增强，完整的数据获取、数据预处理、模型训练、模型回测一条龙框架
能完整跑出来回测的截图到评论区，方便大家互相学习。有问题可以在评论区问我。
**数据集制作：**

```
from jqdata import *
from jqlib.technical_analysis import *
from jqfactor import get_factor_values, winsorize_med, standardlize, neutralize
import datetime
import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
from statsmodels import regression
from six import StringIO
from sklearn.decomposition import PCA
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.grid_search import GridSearchCV
from sklearn import metrics
from tqdm import tqdm
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import warnings
import seaborn as sns
import pickle
warnings.filterwarnings("ignore")
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                            f1_score, roc_auc_score, confusion_matrix, 
                            roc_curve, precision_recall_curve, auc, classification_report)
import lightgbm as lgb
jqfactors_list=['asset_impairment_loss_ttm', 'cash_flow_to_price_ratio', 'market_cap', 'interest_free_current_liability', 'EBITDA', 'financial_assets', 'gross_profit_ttm', 'net_working_capital', 'non_recurring_gain_loss', 'EBIT', 'sales_to_price_ratio', 'AR', 'ARBR', 'ATR6', 'DAVOL10', 'MAWVAD', 'TVMA6', 'PSY', 'VOL10', 'VDIFF', 'VEMA26', 'VMACD', 'VOL120', 'VOSC', 'VR', 'WVAD', 'arron_down_25', 'arron_up_25', 'BBIC', 'MASS', 'Rank1M', 'single_day_VPT', 'single_day_VPT_12', 'single_day_VPT_6', 'Volume1M', 'capital_reserve_fund_per_share', 'net_asset_per_share', 'net_operate_cash_flow_per_share', 'operating_profit_per_share', 'total_operating_revenue_per_share', 'surplus_reserve_fund_per_share', 'ACCA', 'account_receivable_turnover_days', 'account_receivable_turnover_rate', 'adjusted_profit_to_total_profit', 'super_quick_ratio', 'MLEV', 'debt_to_equity_ratio', 'debt_to_tangible_equity_ratio', 'equity_to_fixed_asset_ratio', 'fixed_asset_ratio', 'intangible_asset_ratio', 'invest_income_associates_to_total_profit', 'long_debt_to_asset_ratio', 'long_debt_to_working_capital_ratio', 'net_operate_cash_flow_to_total_liability', 'net_operating_cash_flow_coverage', 'non_current_asset_ratio', 'operating_profit_to_total_profit', 'roa_ttm', 'roe_ttm', 'Kurtosis120', 'Kurtosis20', 'Kurtosis60', 'sharpe_ratio_20', 'sharpe_ratio_60', 'Skewness120', 'Skewness20', 'Skewness60', 'Variance120', 'Variance20', 'liquidity', 'beta', 'book_to_price_ratio', 'cash_earnings_to_price_ratio', 'cube_of_size', 'earnings_to_price_ratio', 'earnings_yield', 'growth', 'momentum', 'natural_log_of_market_cap', 'boll_down', 'MFI14', 'price_no_fq']
print(len(jqfactors_list))
def get_period_date(peroid, start_date, end_date):
    stock_data = get_price('000001.XSHE', start_date, end_date, 'daily', fields=['close'])
    stock_data['date'] = stock_data.index
    period_stock_data = stock_data.resample(peroid, how='last')
    period_stock_data = period_stock_data.set_index('date').dropna()
    date = period_stock_data.index
    pydate_array = date.to_pydatetime()
    date_only_array = np.vectorize(lambda s: s.strftime('%Y-%m-%d'))(pydate_array)
    date_only_series = pd.Series(date_only_array)
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    start_date = start_date - datetime.timedelta(days=1)
    start_date = start_date.strftime("%Y-%m-%d")
    date_list = date_only_series.values.tolist()
    date_list.insert(0, start_date)
    return date_list

peroid = 'M'
start_date = '2019-01-01'
end_date = '2024-01-01'
DAY = get_period_date(peroid, start_date, end_date)
print(len(DAY))

def delect_stop(stocks, beginDate, n=30 * 3):
    stockList = []
    beginDate = datetime.datetime.strptime(beginDate, "%Y-%m-%d")
    for stock in stocks:
        start_date = get_security_info(stock).start_date
        if start_date < (beginDate - datetime.timedelta(days=n)).date():
            stockList.append(stock)
    return stockList

def get_stock(stockPool, begin_date):
    if stockPool == 'HS300':
        stockList = get_index_stocks('000300.XSHG', begin_date)
    elif stockPool == 'ZZ500':
        stockList = get_index_stocks('399905.XSHE', begin_date)
    elif stockPool == 'ZZ800':
        stockList = get_index_stocks('399906.XSHE', begin_date)
    elif stockPool == 'CYBZ':
        stockList = get_index_stocks('399006.XSHE', begin_date)
    elif stockPool == 'ZXBZ':
        stockList = get_index_stocks('399101.XSHE', begin_date)
    elif stockPool == 'A':
        stockList = get_index_stocks('000002.XSHG', begin_date) + get_index_stocks('399107.XSHE', begin_date)
        stockList = [stock for stock in stockList if not stock.startswith(('68', '4', '8'))]
    elif stockPool == 'AA':
        stockList = get_index_stocks('000985.XSHG', begin_date)
        stockList = [stock for stock in stockList if not stock.startswith(('3', '68', '4', '8'))]
    st_data = get_extras('is_st', stockList, count=1, end_date=begin_date)
    stockList = [stock for stock in stockList if not st_data[stock][0]]
    stockList = delect_stop(stockList, begin_date)
    return stockList

def get_factor_data(securities_list, date):
    factor_data = get_factor_values(securities=securities_list, factors=jqfactors_list, count=1, end_date=date)
    df_jq_factor = pd.DataFrame(index=securities_list)
    for i in factor_data.keys():
        df_jq_factor[i] = factor_data[i].iloc[0, :]
    return df_jq_factor

dateList = get_period_date(peroid, start_date, end_date)
DF = pd.DataFrame()

for date in tqdm(dateList[:-1]):
    stockList = get_stock('ZXBZ', date)
    factor_origl_data = get_factor_data(stockList, date)
    data_close = get_price(stockList, date, dateList[dateList.index(date) + 1], '1d', 'close')['close']
    factor_origl_data['pchg'] = data_close.iloc[-1] / data_close.iloc[1] - 1
    factor_origl_data = factor_origl_data.dropna()
    median_pchg = factor_origl_data['pchg'].median()
    factor_origl_data['label'] = np.where(factor_origl_data['pchg'] >= median_pchg, 1, 0)
    factor_origl_data = factor_origl_data.drop(columns=['pchg'])
    DF = pd.concat([DF, factor_origl_data], ignore_index=True)

DF.to_csv(r'train_small.csv', index=False)
```

**数据分析**

```
df = pd.read_csv(r'train_small.csv')
plot_cols = jqfactors_list
print(len(plot_cols))
corr_matrix = df.corr()
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
label_corr = corr_matrix['label'].sort_values(ascending=False)
plt.figure(figsize=(12, 10))
corr = df[plot_cols].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=False, fmt=".2f", cmap='RdBu_r', vmin=-1, vmax=1)
plt.title('因子间相关性矩阵')
plt.show()

plt.figure(figsize=(14, 100))
for i, col in enumerate(plot_cols, 1):
    plt.subplot(42, 2, i)
    sns.distplot(df[col].dropna(), bins=30, color='skyblue', kde=True)
    stats_text = f"均值: {df[col].mean():.2f}\n中位数: {df[col].median():.2f}\n标准差: {df[col].std():.2f}"
    plt.gca().text(0.95, 0.95, stats_text, transform=plt.gca().transAxes, 
                  verticalalignment='top', horizontalalignment='right',
                  bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    plt.title(f'{col} 分布')
    plt.xlabel('')
plt.tight_layout()
plt.show()
```

**数据预处理**

```
from collections import defaultdict
# 计算每个特征的缺失值数量
missing_counts = df[plot_cols].isnull().sum().to_dict()

# 计算特征间的相关系数矩阵
corr_matrix = df[plot_cols].corr()

# 创建图结构存储高度相关的特征对
graph = defaultdict(list)
threshold = 0.6  # 相关性阈值

# 遍历上三角矩阵找到高度相关的特征对
n = len(plot_cols)
for i in range(n):
    for j in range(i + 1, n):
        col1, col2 = plot_cols[i], plot_cols[j]
        corr_value = corr_matrix.iloc[i, j]

        if not pd.isna(corr_value) and abs(corr_value) > threshold:
            graph[col1].append(col2)
            graph[col2].append(col1)

# 使用DFS找到连通分量（高度相关的特征组）
visited = set()
components = []

def dfs(node, comp):
    visited.add(node)
    comp.append(node)
    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs(neighbor, comp)

for col in plot_cols:
    if col not in visited:
        comp = []
        dfs(col, comp)
        components.append(comp)

# 处理每个连通分量：保留缺失值最少的特征
to_keep = []
to_remove = []

for comp in components:
    if len(comp) == 1:  # 独立特征直接保留
        to_keep.append(comp[0])
    else:
        # 按缺失值数量排序（升序），相同缺失值时按特征名字母顺序排序
        comp_sorted = sorted(comp, key=lambda x: (missing_counts[x], x))
        keep_feature = comp_sorted[0]  # 缺失值最少的特征
        to_keep.append(keep_feature)
        to_remove.extend(comp_sorted[1:])  # 组内其他特征移除



print(f"\n最终保留特征数量: {len(to_keep)}")
print(f"移除特征数量: {len(to_remove)}")
print("\n移除的特征列表:", to_remove)
print("\n保留的特征列表:", to_keep)
# 可视化保留特征的相关矩阵（可选）
plt.figure(figsize=(12, 10))
corr_kept = df[to_keep].corr()
mask = np.triu(np.ones_like(corr_kept, dtype=bool))
sns.heatmap(corr_kept, mask=mask, annot=True, fmt=".2f", cmap='RdBu_r', vmin=-1, vmax=1)
plt.title('保留特征间相关性矩阵')
plt.show()
```

训练模型

```
X = df[to_keep]
y = df['label']
lgb_train = lgb.Dataset(X, label=y)
params = {
    'objective': 'binary',
    'metric': 'binary_logloss',
    'boosting_type': 'gbdt',
    'verbose': -1
}
model = lgb.train(params, lgb_train, num_boost_round=200)
y_pred_proba = model.predict(X)
y_pred = (y_pred_proba > 0.5).astype(int)
precision, recall, _ = precision_recall_curve(y, y_pred_proba)
prauc = auc(recall, precision)
print("\n模型性能评估:")
print("准确率 (Accuracy):", accuracy_score(y, y_pred))
print("精确率 (Precision):", precision_score(y, y_pred))
print("召回率 (Recall):", recall_score(y, y_pred))
print("F1分数 (F1-score):", f1_score(y, y_pred))
print("AUC分数:", roc_auc_score(y, y_pred_proba))
print("PRAUC分数:", prauc)  # 新增PRAUC输出
plt.figure(figsize=(15, 12))
plt.subplot(2, 2, 1)
cm = confusion_matrix(y, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['预测0', '预测1'], 
            yticklabels=['实际0', '实际1'])
plt.title('混淆矩阵')
plt.ylabel('实际标签')
plt.xlabel('预测标签')
plt.subplot(2, 2, 2)
fpr, tpr, _ = roc_curve(y, y_pred_proba)
roc_auc = roc_auc_score(y, y_pred_proba)
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'AUC = {roc_auc:.3f}')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('假正率 (FPR)')
plt.ylabel('真正率 (TPR)')
plt.title('ROC曲线')
plt.legend(loc="lower right")
plt.subplot(2, 2, 3)
importance = pd.Series(model.feature_importance(), index=to_keep)
importance.sort_values().plot(kind='barh')
plt.title('特征重要性')
plt.xlabel('重要性分数')
plt.ylabel('特征')
plt.subplot(2, 2, 4)
for label in [0, 1]:
    sns.kdeplot(y_pred_proba[y == label], label=f'真实标签={label}', shade=True)
plt.title('预测概率分布')
plt.xlabel('预测为正类的概率')
plt.ylabel('密度')
plt.legend()
plt.axvline(0.5, color='red', linestyle='--')
plt.tight_layout()
plt.show()
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(recall, precision, color='darkblue', lw=2, label=f'PRAUC = {prauc:.3f}')
plt.fill_between(recall, precision, alpha=0.2, color='darkblue')
plt.xlabel('召回率 (Recall)')
plt.ylabel('精确率 (Precision)')
plt.title('PRAUC曲线')
plt.legend(loc='upper right')
plt.grid(True)
plt.tight_layout()
plt.show()
with open('model_small.pkl', 'wb') as model_file:
    pickle.dump(model, model_file)
```

**回测代码：**

```
from jqdata import *
from jqfactor import *
import numpy as np
import pandas as pd
import pickle



# 初始化函数
def initialize(context):
    # 设定基准
    set_benchmark('399101.XSHE')
    # 用真实价格交易
    set_option('use_real_price', True)
    # 打开防未来函数
    set_option("avoid_future_data", True)
    # 将滑点设置为0
    set_slippage(FixedSlippage(0))
    # 设置交易成本万分之三，不同滑点影响可在归因分析中查看
    set_order_cost(OrderCost(open_tax=0, close_tax=0.001, open_commission=0.0003, close_commission=0.0003,
                             close_today_commission=0, min_commission=5), type='stock')
    # 过滤order中低于error级别的日志
    log.set_level('order', 'error')
    # 初始化全局变量

    g.stock_num = 10
    g.hold_list = []  # 当前持仓的全部股票
    g.yesterday_HL_list = []  # 记录持仓中昨日涨停的股票


    g.model_small = pickle.loads(read_file('model_small.pkl'))

    # 因子列表
    g.factor_list =  ['asset_impairment_loss_ttm', 'cash_flow_to_price_ratio', 'EBIT', 'net_working_capital', 'non_recurring_gain_loss', 'sales_to_price_ratio', 'AR', 'ARBR', 'ATR6', 'DAVOL10', 'MAWVAD', 'TVMA6', 'PSY', 'VOL10', 'VDIFF', 'VEMA26', 'VMACD', 'VOL120', 'VOSC', 'VR', 'arron_down_25', 'arron_up_25', 'BBIC', 'MASS', 'Rank1M', 'single_day_VPT', 'single_day_VPT_12', 'Volume1M', 'capital_reserve_fund_per_share', 'net_operate_cash_flow_per_share', 'operating_profit_per_share', 'total_operating_revenue_per_share', 'surplus_reserve_fund_per_share', 'ACCA', 'account_receivable_turnover_days', 'account_receivable_turnover_rate', 'adjusted_profit_to_total_profit', 'super_quick_ratio', 'MLEV', 'debt_to_equity_ratio', 'debt_to_tangible_equity_ratio', 'equity_to_fixed_asset_ratio', 'fixed_asset_ratio', 'intangible_asset_ratio', 'invest_income_associates_to_total_profit', 'long_debt_to_asset_ratio', 'long_debt_to_working_capital_ratio', 'net_operate_cash_flow_to_total_liability', 'net_operating_cash_flow_coverage', 'non_current_asset_ratio', 'operating_profit_to_total_profit', 'roa_ttm', 'Kurtosis120', 'Kurtosis20', 'Kurtosis60', 'sharpe_ratio_20', 'sharpe_ratio_60', 'Skewness120', 'Skewness20', 'Skewness60', 'Variance120', 'Variance20', 'beta', 'book_to_price_ratio', 'cash_earnings_to_price_ratio', 'cube_of_size', 'earnings_to_price_ratio', 'earnings_yield', 'growth', 'momentum', 'natural_log_of_market_cap', 'boll_down', 'MFI14', 'price_no_fq']
    run_daily(prepare_stock_list, '9:05')
    run_monthly(weekly_adjustment, 1, '9:30')
    run_daily(check_limit_up, '14:00') 




# 1-1 准备股票池
def prepare_stock_list(context):
    # 获取已持有列表
    g.hold_list = []
    for position in list(context.portfolio.positions.values()):
        stock = position.security
        g.hold_list.append(stock)
    # 获取昨日涨停列表
    if g.hold_list != []:
        df = get_price(g.hold_list, end_date=context.previous_date, frequency='daily', fields=['close', 'high_limit'],
                       count=1, panel=False, fill_paused=False)
        df = df[df['close'] == df['high_limit']]
        g.yesterday_HL_list = list(df.code)
    else:
        g.yesterday_HL_list = []

# 1-2 选股模块
def get_stock_list(context):
    yesterday = context.previous_date
    today = context.current_dt
    stocks = get_index_stocks('399101.XSHE', yesterday)
    initial_list = filter_kcbj_stock(stocks)
    initial_list = filter_st_stock(initial_list)
    initial_list = filter_paused_stock(initial_list)
    initial_list = filter_new_stock(context, initial_list)
    initial_list = filter_limitup_stock(context,initial_list)
    initial_list = filter_limitdown_stock(context,initial_list)
    factor_data = get_factor_values(initial_list, g.factor_list, end_date=yesterday, count=1)
    df_jq_factor_value = pd.DataFrame(index=initial_list, columns=g.factor_list)
    for factor in g.factor_list:
        df_jq_factor_value[factor] = list(factor_data[factor].T.iloc[:, 0])
    tar = g.model_small.predict(df_jq_factor_value)
    df = df_jq_factor_value
    df['total_score'] = list(tar)
    df = df.sort_values(by=['total_score'], ascending=False)  
    lst = df.index.tolist()
    lst = lst[:min(g.stock_num, len(lst))]
    return lst


# 1-3 整体调整持仓
def weekly_adjustment(context):

        # 获取应买入列表
        target_list = get_stock_list(context)
        # 调仓卖出
        for stock in g.hold_list:
            if (stock not in target_list) and (stock not in g.yesterday_HL_list):
                log.info("卖出[%s]" % (stock))
                position = context.portfolio.positions[stock]
                close_position(position)
            else:
                log.info("已持有[%s]" % (stock))
        # 调仓买入
        position_count = len(context.portfolio.positions)
        target_num = len(target_list)
        if target_num > position_count:
            value = context.portfolio.cash / (target_num - position_count)
            for stock in target_list:
                if context.portfolio.positions[stock].total_amount == 0:
                    if open_position(stock, value):
                        if len(context.portfolio.positions) == target_num:
                            break



# 1-4 调整昨日涨停股票
def check_limit_up(context):
    now_time = context.current_dt
    if g.yesterday_HL_list != []:
        # 对昨日涨停股票观察到尾盘如不涨停则提前卖出，如果涨停即使不在应买入列表仍暂时持有
        for stock in g.yesterday_HL_list:
            current_data = get_price(stock, end_date=now_time, frequency='1m', fields=['close', 'high_limit'],
                                     skip_paused=False, fq='pre', count=1, panel=False, fill_paused=True)
            if current_data.iloc[0, 0] < current_data.iloc[0, 1]:
                log.info("[%s]涨停打开，卖出" % (stock))
                position = context.portfolio.positions[stock]
                close_position(position)
            else:
                log.info("[%s]涨停，继续持有" % (stock))

# 3-1 交易模块-自定义下单
def order_target_value_(security, value):
    if value == 0:
        log.debug("Selling out %s" % (security))
    else:
        log.debug("Order %s to value %f" % (security, value))
    return order_target_value(security, value)


# 3-2 交易模块-开仓
def open_position(security, value):
    order = order_target_value_(security, value)
    if order != None and order.filled > 0:
        return True
    return False


# 3-3 交易模块-平仓
def close_position(position):
    security = position.security
    order = order_target_value_(security, 0)  # 可能会因停牌失败
    if order != None:
        if order.status == OrderStatus.held and order.filled == order.amount:
            return True
    return False


# 2-1 过滤停牌股票
def filter_paused_stock(stock_list):
    current_data = get_current_data()
    return [stock for stock in stock_list if not current_data[stock].paused]


# 2-2 过滤ST及其他具有退市标签的股票
def filter_st_stock(stock_list):
    current_data = get_current_data()
    return [stock for stock in stock_list
            if not current_data[stock].is_st
            and 'ST' not in current_data[stock].name
            and '*' not in current_data[stock].name
            and '退' not in current_data[stock].name]


# 2-3 过滤科创北交股票
def filter_kcbj_stock(stock_list):
    for stock in stock_list[:]:
        if stock[0] == '4' or stock[0] == '8' or stock[:2] == '68' or stock[0] == '3':
            stock_list.remove(stock)
    return stock_list


# 2-4 过滤涨停的股票
def filter_limitup_stock(context, stock_list):
    last_prices = history(1, unit='1m', field='close', security_list=stock_list)
    current_data = get_current_data()
    return [stock for stock in stock_list if stock in context.portfolio.positions.keys()
            or last_prices[stock][-1] < current_data[stock].high_limit]


# 2-5 过滤跌停的股票
def filter_limitdown_stock(context, stock_list):
    last_prices = history(1, unit='1m', field='close', security_list=stock_list)
    current_data = get_current_data()
    return [stock for stock in stock_list if stock in context.portfolio.positions.keys()
            or last_prices[stock][-1] > current_data[stock].low_limit]


# 2-6 过滤次新股
def filter_new_stock(context, stock_list):
    yesterday = context.previous_date
    return [stock for stock in stock_list if
            not yesterday - get_security_info(stock).start_date < datetime.timedelta(days=375)]
```


from ctypes.wintypes import SIZE
import backtrader as bt
import backtrader.indicators as btind ## 导入策略分析模块

from datetime import datetime
from dateutil.relativedelta import relativedelta

class QQStrategy(bt.Strategy):
  # 先在 __init__ 中提前算好指标
    def __init__(self):
        self._next_buy_date = datetime(2020, 1, 1) ## 起始日
        # 保存收盘价的引用
        self.dataclose = self.datas[0].close
        self.one_share = 0 #股票数量
        self.start_cash = self.broker.get_cash()

        self.sma5 = btind.SimpleMovingAverage(period=5) # 5日均线
        self.sma10 = btind.SimpleMovingAverage(period=10) # 10日均线
        # bt.And 中所有条件都满足时返回 1；有一个条件不满足就返回 0
        self.And = bt.And(self.data>self.sma5, self.data>self.sma10, self.sma5>self.sma10)
        # bt.Or 中有一个条件满足时就返回 1；所有条件都不满足时返回 0
        self.Or = bt.Or(self.data>self.sma5, self.data>self.sma10, self.sma5>self.sma10)
        # bt.If(a, b, c) 如果满足条件 a，就返回 b，否则返回 c
        self.If = bt.If(self.data>self.sma5,1000, 5000)
        # bt.All,同 bt.And
        self.All = bt.All(self.data>self.sma5, self.data>self.sma10, self.sma5>self.sma10)
        # bt.Any，同 bt.Or
        self.Any = bt.Any(self.data>self.sma5, self.data>self.sma10, self.sma5>self.sma10)
        # bt.Max，返回同一时刻所有指标中的最大值
        self.Max = bt.Max(self.data, self.sma10, self.sma5)
        # bt.Min，返回同一时刻所有指标中的最小值
        self.Min = bt.Min(self.data, self.sma10, self.sma5)
        # bt.Sum，对同一时刻所有指标进行求和
        self.Sum = bt.Sum(self.data, self.sma10, self.sma5)
        # bt.Cmp(a,b), 如果 a>b ，返回 1；否则返回 -1
        self.Cmp = bt.Cmp(self.data, self.sma5)

        sma1 = btind.SimpleMovingAverage(self.data) ##簡單移動平均線
        ema1 = btind.ExponentialMovingAverage() ## 指數移動平均線
        close_over_sma = self.data.close > sma1
        close_over_ema = self.data.close > ema1
        sma_ema_diff = sma1 - ema1
        # 生成交易信号
        self.buy_sig = bt.And(close_over_sma, close_over_ema, sma_ema_diff > 0) ## 看起來就是字面意義
    # 在 next 中直接调用计算好的指标
    def next(self):
        if self.buy_sig:
            self.buy(size=100)
            

        if self.dataclose[0] < self.sma5 and self.one_share > 0:
            self.sell(size=100)
            

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # broker 提交/接受了，买/卖订单则什么都不做
            return

        # 检查一个订单是否完成
        # 注意: 当资金不足时，broker会拒绝订单
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    '已买入, 价格: %.2f, 張數: %.2f, 费用: %.2f, 佣金 %.2f' %
                    (order.executed.price,
                     order.executed.size,
                     order.executed.value,
                     order.executed.comm))
                self.one_share += 1
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log('已卖出, 价格: %.2f,, 張數: %.2f 费用: %.2f, 佣金 %.2f' %
                         (order.executed.price,
                          order.executed.size,
                          order.executed.value,
                          order.executed.comm))
                self.one_share -= 1
            # 记录当前交易数量
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单取消/保证金不足/拒绝')

        # 其他状态记录为：无挂起订单
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('交易利润, 毛利润 %.2f, 净利润 %.2f' %
                 (trade.pnl, trade.pnlcomm))
        self.log(f'目前現金 {int(self.broker.get_cash())}')
        
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def stop(self):
        self.roi = (self.broker.get_value() / self.start_cash) - 1.0
        print('ROI:        {:.2f}%'.format(100.0 * self.roi))
        print(self.one_share)

class DEMO(bt.Strategy): ## 新策略 copy 這邊過去 撰寫策略
    def __init__(self):
        self._next_buy_date = datetime(2020, 1, 1) ## 起始日
        # 保存收盘价的引用
        self.dataclose = self.datas[0].close
        self.one_share = 0 #股票数量
        self.start_cash = self.broker.get_cash()
        ## KDJ
        # 9个交易日内最高价
        self.high_nine = bt.indicators.Highest(self.data.high, period=9)
        # 9个交易日内最低价
        self.low_nine = bt.indicators.Lowest(self.data.low, period=9)
        # 计算rsv值
        self.rsv = 100 * bt.DivByZero(self.data_close - self.low_nine, self.high_nine - self.low_nine, zero=None)
        # 计算rsv的3周期加权平均值，即K值
        self.K = bt.indicators.EMA(self.rsv, period=3)
        # D值=K值的3周期加权平均值
        self.D = bt.indicators.EMA(self.K, period=3)
        # J=3*K-2*D
        self.J = 3 * self.K - 2 * self.D
        ## KDJ
        ## MACD
        me1 = bt.indicators.EMA(self.data, period=12)
        me2 = bt.indicators.EMA(self.data, period=26)
        self.macd = me1 - me2
        self.signal = bt.indicators.EMA(self.macd, period=9)
        bt.indicators.MACDHisto(self.data)
        ## MACD
        # 跟踪挂单
        self.order = None
        # 买入价格和手续费
        self.buyprice = None
        self.buycomm = None
  
    def next(self):
        if self.rsi <= 20:
            self.log('BUY, %.2f' % self.data.close[0])
            self.buy(size=100)
            
        elif self.rsi >= 80 and self.one_share > 0:
            self.log('SELL, %.2f' % self.data.close[0])
            self.sell(size=100)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # broker 提交/接受了，买/卖订单则什么都不做
            return

        # 检查一个订单是否完成
        # 注意: 当资金不足时，broker会拒绝订单
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    '已买入, 价格: %.2f, 張數: %.2f, 费用: %.2f, 佣金 %.2f' %
                    (order.executed.price,
                     order.executed.size,
                     order.executed.value,
                     order.executed.comm))
                self.one_share += 1
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log('已卖出, 价格: %.2f,, 張數: %.2f 费用: %.2f, 佣金 %.2f' %
                         (order.executed.price,
                          order.executed.size,
                          order.executed.value,
                          order.executed.comm))
                self.one_share -= 1
            # 记录当前交易数量
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单取消/保证金不足/拒绝')

        # 其他状态记录为：无挂起订单
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('交易利润, 毛利润 %.2f, 净利润 %.2f' %
                 (trade.pnl, trade.pnlcomm))
        self.log(f'目前現金 {int(self.broker.get_cash())}')
        
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def stop(self):
        self.roi = (self.broker.get_value() / self.start_cash) - 1.0
        print('ROI:        {:.2f}%'.format(100.0 * self.roi))
        print(self.one_share)

class TestStrategy(bt.Strategy): ## 策略
    params = (
        # 均线参数设置15天，15日均线
        ('maperiod', 15),
    )
    def __init__(self):
        self._next_buy_date = datetime(2020, 1, 1)
        # 保存收盘价的引用
        self.dataclose = self.datas[0].close
        self.one_share = 0 #股票数量
        self.start_cash = self.broker.get_cash()
        # 9个交易日内最高价
        self.high_nine = bt.indicators.Highest(self.data.high, period=9)
        # 9个交易日内最低价
        self.low_nine = bt.indicators.Lowest(self.data.low, period=9)
        # 计算rsv值
        self.rsv = 100 * bt.DivByZero(self.data_close - self.low_nine, self.high_nine - self.low_nine, zero=None)
        # 计算rsv的3周期加权平均值，即K值
        self.K = bt.indicators.EMA(self.rsv, period=3)
        # D值=K值的3周期加权平均值
        self.D = bt.indicators.EMA(self.K, period=3)
        # J=3*K-2*D
        self.J = 3 * self.K - 2 * self.D
        # 跟踪挂单
        self.order = None
        # 买入价格和手续费
        self.buyprice = None
        self.buycomm = None
        # 加入均线指标
        # self.sma1 = bt.indicators.SimpleMovingAverage(self.datas[0], period=5)
        # self.sma2 = bt.indicators.SimpleMovingAverage(self.datas[0], period=10)
        # self.sma3 = bt.indicators.SimpleMovingAverage(self.datas[0], period=15)

        # 绘制图形时候用到的指标
        self.rsi = bt.indicators.RSI(self.datas[0],period=self.params.maperiod) # K線的RSI指標
        # self.lrsi = bt.indicators.LRSI(self.datas[0],period=self.params.maperiod)

        # bt.indicators.MACDHisto(self.datas[0])
        # bt.indicators.WeightedMovingAverage(self.datas[0], period=self.params.maperiod,subplot=True)
    def next(self):
        if self.rsi <= 20:
            self.log('BUY, %.2f' % self.data.close[0])
            self.buy(size=100)
            
        elif self.rsi >= 80 and self.one_share > 0:
            self.log('SELL, %.2f' % self.data.close[0])
            self.sell(size=100)

        elif self.rsi >= 80 and self.one_share == 0:
            # print('好時機沒股票賣')
            pass

    # 订单状态通知，买入卖出都是下单
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # broker 提交/接受了，买/卖订单则什么都不做
            return

        # 检查一个订单是否完成
        # 注意: 当资金不足时，broker会拒绝订单
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    '已买入, 价格: %.2f, 费用: %.2f, 佣金 %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
                self.one_share += 1
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log('已卖出, 价格: %.2f, 费用: %.2f, 佣金 %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
                self.one_share -= 1
            # 记录当前交易数量
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单取消/保证金不足/拒绝')

        # 其他状态记录为：无挂起订单
        self.order = None

    # 交易状态通知，一买一卖算交易
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('交易利润, 毛利润 %.2f, 净利润 %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
    
    def stop(self):
        # calculate the actual returns
        self.roi = (self.broker.get_value() / self.start_cash) - 1.0
        print('ROI:        {:.2f}%'.format(100.0 * self.roi))
        print(self.one_share)

class SmaCross(bt.SignalStrategy): ## 均線交叉策略 怪怪
    def __init__(self):
        self._next_buy_date = datetime(2020, 1, 1) ##起始點
        self.one_share = 0
        self.start_cash = self.broker.get_cash()
        print(f"初始資金 {self.start_cash}")
    def next(self):
        '''必选，编写交易策略逻辑'''
        sma1, sma2 = bt.ind.SMA(period=10), bt.ind.SMA(period=30)
        crossover = bt.ind.CrossOver(sma1, sma2)
        self.signal_add(bt.SIGNAL_LONG, crossover)
    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # broker 提交/接受了，买/卖订单则什么都不做
            return

        # 检查一个订单是否完成
        # 注意: 当资金不足时，broker会拒绝订单
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    '已买入, 价格: %.2f, 張數: %.2f, 费用: %.2f, 佣金 %.2f' %
                    (order.executed.price,
                     order.executed.size,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log('已卖出, 价格: %.2f,, 張數: %.2f 费用: %.2f, 佣金 %.2f' %
                         (order.executed.price,
                          order.executed.size,
                          order.executed.value,
                          order.executed.comm))
            # 记录当前交易数量
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单取消/保证金不足/拒绝')

        # 其他状态记录为：无挂起订单
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('交易利润, 毛利润 %.2f, 净利润 %.2f' %
                 (trade.pnl, trade.pnlcomm))
        self.log(f'目前現金 {int(self.broker.get_cash())}')

    def stop(self):
        # calculate the actual returns
        self.roi = (self.broker.get_value() / self.start_cash) - 1.0
        print('ROI:        {:.2f}%'.format(100.0 * self.roi))
        print(f'{self.one_share}')

class every_mon_five_buy_Strategy(bt.Strategy): ## 策略 每月五號買入
    def __init__(self):
        '''必选，初始化属性、计算指标等'''
        self._next_buy_date = datetime(2020, 1, 5)
        self.one_share = 0
        self.start_cash = self.broker.get_cash()
  
    def next(self):
        '''必选，编写交易策略逻辑'''
        if self.data.datetime.date() >= self. _next_buy_date.date():
            self. _next_buy_date += relativedelta(months=1)
            self.buy(size=100) ## 台美股 單位 股 張  要注意
            

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # broker 提交/接受了，买/卖订单则什么都不做
            return

        # 检查一个订单是否完成
        # 注意: 当资金不足时，broker会拒绝订单
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    '已买入, 价格: %.2f, 張數: %.2f, 费用: %.2f, 佣金 %.2f' %
                    (order.executed.price,
                     order.executed.size,
                     order.executed.value,
                     order.executed.comm))
                self.one_share += 1
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log('已卖出, 价格: %.2f,, 張數: %.2f 费用: %.2f, 佣金 %.2f' %
                         (order.executed.price,
                          order.executed.size,
                          order.executed.value,
                          order.executed.comm))
                self.one_share -= 1
            # 记录当前交易数量
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单取消/保证金不足/拒绝')

        # 其他状态记录为：无挂起订单
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('交易利润, 毛利润 %.2f, 净利润 %.2f' %
                 (trade.pnl, trade.pnlcomm))
        self.log(f'目前現金 {int(self.broker.get_cash())}')

    def log(self, txt, dt=None):
        '''可选，构建策略打印日志的函数：可用于打印订单记录或交易记录等'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
    
    
    def stop(self):
        # calculate the actual returns
        self.roi = (self.broker.get_value() / self.start_cash) - 1.0
        print('ROI:        {:.2f}%'.format(100.0 * self.roi))
        print(f'{self.one_share}')

class Black_Triple_Start_Strategy(bt.Strategy): ## 策略 黑色三連星 連收三黑K
    def __init__(self):
        '''必选，初始化属性、计算指标等'''
        self._next_buy_date = datetime(2020, 1, 1)
        self.one_share = 0
    def next(self):
        '''必选，编写交易策略逻辑'''
        # 记录收盘价
        # self.log('Close, %.2f' % self.data.close[0])
        # 今天的收盘价 < 昨天收盘价
        # print(self.data.close[0])

        if self.data.close[0] < self.data.close[-1]:
            # 昨天收盘价 < 前天的收盘价
            if self.data.close[-1] < self.data.close[-2]:
                # 买入
                self.log('BUY, %.2f' % self.data.close[0])
                self.buy(size=1000)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # broker 提交/接受了，买/卖订单则什么都不做
            return

        # 检查一个订单是否完成
        # 注意: 当资金不足时，broker会拒绝订单
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    '已买入, 价格: %.2f, 張數: %.2f, 费用: %.2f, 佣金 %.2f' %
                    (order.executed.price,
                     order.executed.size,
                     order.executed.value,
                     order.executed.comm))
                self.one_share += 1
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log('已卖出, 价格: %.2f,, 張數: %.2f 费用: %.2f, 佣金 %.2f' %
                         (order.executed.price,
                          order.executed.size,
                          order.executed.value,
                          order.executed.comm))
                self.one_share -= 1
            # 记录当前交易数量
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单取消/保证金不足/拒绝')

        # 其他状态记录为：无挂起订单
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('交易利润, 毛利润 %.2f, 净利润 %.2f' %
                 (trade.pnl, trade.pnlcomm))
        self.log(f'目前現金 {int(self.broker.get_cash())}')

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
    
class buy_sell_demo_Strategy(bt.Strategy): ## 策略 買入後 五個單位後賣出
    
    def __init__(self):
        # 保存收盘价的引用
        self.dataclose = self.datas[0].close
        # 跟踪挂单
        self.order = None
        # 买入价格和手续费
        self.buyprice = None
        self.buycomm = None
        self.one_share = 0

    def next(self):
        # 记录收盘价
        self.log('Close, %.2f' % self.dataclose[0])

        # 如果有订单正在挂起，不操作
        if self.order:
            return

        # 如果没有持仓则买入
        if not self.position:
            # 今天的收盘价 < 昨天收盘价 
            if self.dataclose[0] < self.dataclose[-1]:
                # 昨天收盘价 < 前天的收盘价
                if self.dataclose[-1] < self.dataclose[-2]:
                    # 买入
                    self.log('买入单, %.2f' % self.dataclose[0])
                     # 跟踪订单避免重复
                    self.order = self.buy(size=1000)
        else:
            # 如果已经持仓，且当前交易数据量在买入后5个单位后
            if len(self) >= (self.bar_executed + 5):
                # 全部卖出
                self.log('卖出单, %.2f' % self.dataclose[0])
                # 跟踪订单避免重复
                self.order = self.sell(size=500)

    # 订单状态通知，买入卖出都是下单
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # broker 提交/接受了，买/卖订单则什么都不做
            return

        # 检查一个订单是否完成
        # 注意: 当资金不足时，broker会拒绝订单
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    '已买入, 价格: %.2f, 费用: %.2f, 佣金 %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
                self.one_share += 1
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log('已卖出, 价格: %.2f, 费用: %.2f, 佣金 %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
                self.one_share -= 0.5
            # 记录当前交易数量
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单取消/保证金不足/拒绝')

        # 其他状态记录为：无挂起订单
        self.order = None

    # 交易状态通知，一买一卖算交易
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('交易利润, 毛利润 %.2f, 净利润 %.2f' %
                 (trade.pnl, trade.pnlcomm))

    
    def log(self, txt, dt=None):
        # 记录策略的执行日志
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def stop(self):
        self.roi = (self.broker.get_value() / self.start_cash) - 1.0
        print('ROI:        {:.2f}%'.format(100.0 * self.roi))
        # print(self.one_share)

class fifteenStrategy(bt.Strategy): ## 策略 15日均线交易
    params = (
        # 均线参数设置15天，15日均线
        ('maperiod', 15),
    )

    def log(self, txt, dt=None):
        # 记录策略的执行日志
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # 保存收盘价的引用
        self.dataclose = self.datas[0].close
        # 跟踪挂单
        self.order = None
        # 买入价格和手续费
        self.buyprice = None
        self.buycomm = None

        self.one_share = 0
        # 加入均线指标
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maperiod)

        # 绘制图形时候用到的指标
        self.rsi = bt.indicators.RSI(self.datas[0])
        self.lrsi = bt.indicators.LRSI(self.datas[0])

        bt.indicators.ExponentialMovingAverage(self.datas[0], period=15)
        bt.indicators.WeightedMovingAverage(self.datas[0], period=15,subplot=True)
        bt.indicators.StochasticSlow(self.datas[0])
        bt.indicators.MACDHisto(self.datas[0])
        bt.indicators.SmoothedMovingAverage(self.rsi, period=10)
        bt.indicators.ATR(self.datas[0], plot=False)
        # 绘制图形时候用到的指标
        
    # 订单状态通知，买入卖出都是下单
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # broker 提交/接受了，买/卖订单则什么都不做
            return

        # 检查一个订单是否完成
        # 注意: 当资金不足时，broker会拒绝订单
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    '已买入, 价格: %.2f, 费用: %.2f, 佣金 %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
                self.one_share += 0.5
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log('已卖出, 价格: %.2f, 费用: %.2f, 佣金 %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
                self.one_share -= 0.5
            # 记录当前交易数量
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单取消/保证金不足/拒绝')

        # 其他状态记录为：无挂起订单
        self.order = None

    # 交易状态通知，一买一卖算交易
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('交易利润, 毛利润 %.2f, 净利润 %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # 记录收盘价
        self.log('Close, %.2f' % self.dataclose[0])

        # 如果有订单正在挂起，不操作
        if self.order:
            return

        # 如果没有持仓则买入
        if not self.position:
            # 今天的收盘价在均线价格之上 
            if self.dataclose[0] > self.sma[0]: 
                # 买入
                self.log('买入单, %.2f' % self.dataclose[0])
                    # 跟踪订单避免重复
                self.order = self.buy(size=500)
        else:
            # 如果已经持仓，收盘价在均线价格之下
            if self.dataclose[0] < self.sma[0]:
                # 全部卖出
                self.log('卖出单, %.2f' % self.dataclose[0])
                # 跟踪订单避免重复
                self.order = self.sell(size=500)

    def stop(self):
        self.roi = (self.broker.get_value() / self.start_cash) - 1.0
        print('ROI:        {:.2f}%'.format(100.0 * self.roi))
        # print(self.one_share)
    
class MACD_buy_KDJ_sell(bt.Strategy): ## 策略 
    def __init__(self):
        self._next_buy_date = datetime(2020, 4, 5)
        # 保存收盘价的引用
        self.dataclose = self.datas[0].close
        self.one_share = 0 #股票数量
        self.start_cash = self.broker.get_cash()
        ## KDJ
        # 9个交易日内最高价
        self.high_nine = bt.indicators.Highest(self.data.high, period=9)
        # 9个交易日内最低价
        self.low_nine = bt.indicators.Lowest(self.data.low, period=9)
        # 计算rsv值
        self.rsv = 100 * bt.DivByZero(self.data_close - self.low_nine, self.high_nine - self.low_nine, zero=None)
        # 计算rsv的3周期加权平均值，即K值
        self.K = bt.indicators.EMA(self.rsv, period=3)
        # D值=K值的3周期加权平均值
        self.D = bt.indicators.EMA(self.K, period=3)
        # J=3*K-2*D
        self.J = 3 * self.K - 2 * self.D
        ## KDJ
        ## MACD
        me1 = bt.indicators.EMA(self.data, period=12)
        me2 = bt.indicators.EMA(self.data, period=26)
        self.macd = me1 - me2
        self.signal = bt.indicators.EMA(self.macd, period=9)
        bt.indicators.MACDHisto(self.data)
        ## MACD
        # 跟踪挂单
        self.order = None
        # 买入价格和手续费
        self.buyprice = None
        self.buycomm = None
  
    def next(self):
        # if self.order:
        #     return
        
        # 帳戶沒有部位
        # if not self.position:
            # 买入：基于MACD策略
            condition1 = self.macd[-1] - self.signal[-1]
            condition2 = self.macd[0] - self.signal[0]
            if condition1 < 0 and condition2 > 0:
                self.order = self.buy(size=1000)

        # else:
            # 卖出：基于KDJ策略
            condition1 = self.J[-1] - self.D[-1]
            condition2 = self.J[0] - self.D[0]
            if (condition1 > 0 and self.one_share > 0) or (condition2 < 0 and self.one_share > 0):
                self.order = self.sell(size=500)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # broker 提交/接受了，买/卖订单则什么都不做
            return

        # 检查一个订单是否完成
        # 注意: 当资金不足时，broker会拒绝订单
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    '已买入, 价格: %.2f, 费用: %.2f, 佣金 %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
                self.one_share += 1
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log('已卖出, 价格: %.2f, 费用: %.2f, 佣金 %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
                self.one_share -= 1

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单取消/保证金不足/拒绝')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('交易利润, 毛利润 %.2f, 净利润 %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def stop(self):
        self.roi = (self.broker.get_value() / self.start_cash) - 1.0
        print('ROI:        {:.2f}%'.format(100.0 * self.roi))
        # print(self.one_share)

class MACD_glod_cross(bt.Strategy): ## MACD 黃金交叉

    def __init__(self):
        self._next_buy_date = datetime(2020, 4, 5)
        # 保存收盘价的引用
        self.dataclose = self.datas[0].close
        self.one_share = 0 #股票数量
        self.start_cash = self.broker.get_cash()
        ## KDJ
        # 9个交易日内最高价
        self.high_nine = bt.indicators.Highest(self.data.high, period=9)
        # 9个交易日内最低价
        self.low_nine = bt.indicators.Lowest(self.data.low, period=9)
        # 计算rsv值
        self.rsv = 100 * bt.DivByZero(self.data_close - self.low_nine, self.high_nine - self.low_nine, zero=None)
        # 计算rsv的3周期加权平均值，即K值
        self.K = bt.indicators.EMA(self.rsv, period=9)
        # D值=K值的3周期加权平均值
        self.D = bt.indicators.EMA(self.K, period=9)
        # J=3*K-2*D
        self.J = 3 * self.K - 2 * self.D
        ## KDJ
        ## MACD
        me1 = bt.indicators.EMA(self.data, period=12)
        me2 = bt.indicators.EMA(self.data, period=26)
        self.macd = me1 - me2 ## DIF
        self.signal = bt.indicators.EMA(self.macd, period=9) ## MACD 
        
        self.histo = bt.indicators.MACDHisto(self.data)
        ## MACD
        # 跟踪挂单
        self.order = None
        # 买入价格和手续费
        self.buyprice = None
        self.buycomm = None
  
    def next(self):
        if self.macd[0] > self.signal[0] and self.macd[-1] <= self.signal[-1]:
            self.log('BUY, %.2f' % self.data.close[0])
            self.buy(size=1000)
        elif self.K >= 80 and self.one_share > 0:
            self.log('SELL, %.2f' % self.data.close[0])
            self.sell(size=1000)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # broker 提交/接受了，买/卖订单则什么都不做
            return

        # 检查一个订单是否完成
        # 注意: 当资金不足时，broker会拒绝订单
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    '已买入, 价格: %.2f, 張數: %.2f, 费用: %.2f, 佣金 %.2f' %
                    (order.executed.price,
                     order.executed.size,
                     order.executed.value,
                     order.executed.comm))
                self.one_share += 1
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log('已卖出, 价格: %.2f,, 張數: %.2f 费用: %.2f, 佣金 %.2f' %
                         (order.executed.price,
                          order.executed.size,
                          order.executed.value,
                          order.executed.comm))
                self.one_share -= 1
            # 记录当前交易数量
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单取消/保证金不足/拒绝')

        # 其他状态记录为：无挂起订单
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('交易利润, 毛利润 %.2f, 净利润 %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def stop(self):
        self.roi = (self.broker.get_value() / self.start_cash) - 1.0
        print('ROI:        {:.2f}%'.format(100.0 * self.roi))
        print(self.one_share)

class KD_glod_cross(bt.Strategy): ## KD 黃金交叉
    def __init__(self):
        self._next_buy_date = datetime(2020, 4, 5)
        # 保存收盘价的引用
        self.dataclose = self.datas[0].close
        self.one_share = 0 #股票数量
        self.start_cash = self.broker.get_cash()
        ## KDJ
        # 9个交易日内最高价
        self.high_nine = bt.indicators.Highest(self.data.high, period=9)
        # 9个交易日内最低价
        self.low_nine = bt.indicators.Lowest(self.data.low, period=9)
        # 计算rsi值
        self.rsi = bt.indicators.RSI(self.datas[0], period=14)

        self.rsv = self.rsv = 100 * bt.DivByZero(self.data_close - self.low_nine, self.high_nine - self.low_nine, zero=None)
        # 计算rsv的3周期加权平均值，即K值
        self.K = bt.indicators.EMA(self.rsv, period=3)
        # D值=K值的3周期加权平均值
        self.D = bt.indicators.EMA(self.K, period=3)
        # J=3*K-2*D
        self.J = 3 * self.K - 2 * self.D
        ## KDJ
        ## MACD
        me1 = bt.indicators.EMA(self.data, period=12)
        me2 = bt.indicators.EMA(self.data, period=26)
        self.macd = me1 - me2
        self.signal = bt.indicators.EMA(self.macd, period=9)
        bt.indicators.MACDHisto(self.data)
        ## MACD
        # 跟踪挂单
        # self.order = None
        # 记录交易
        # self.trade = None
        # 买入价格和手续费
        self.buyprice = None
        self.buycomm = None
  
    def next(self):
        if self.K[0] > self.D[0] and self.K[-1] <= self.D[-1] and self.K[0] <= 35:
            self.log('BUY, %.2f' % self.data.close[0])
            se = int((int(self.broker.get_cash()) / self.data.close[0]) / 2)
            # nornum = 1000
            self.buy(size=se)
        elif self.rsi >= 80 and self.one_share > 0:
            self.log('SELL, %.2f' % self.data.close[0])
            self.sell(size=1000)
        else:
            pass

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # broker 提交/接受了，买/卖订单则什么都不做
            return

        # 检查一个订单是否完成
        # 注意: 当资金不足时，broker会拒绝订单
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    '已买入, 价格: %.2f, 張數: %.2f, 费用: %.2f, 佣金 %.2f' %
                    (order.executed.price,
                     order.executed.size,
                     order.executed.value,
                     order.executed.comm))
                self.one_share += 1
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log('已卖出, 价格: %.2f,, 張數: %.2f 费用: %.2f, 佣金 %.2f' %
                         (order.executed.price,
                          order.executed.size,
                          order.executed.value,
                          order.executed.comm))
                self.one_share -= 1
            # 记录当前交易数量
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单取消/保证金不足/拒绝')

        # 其他状态记录为：无挂起订单
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('交易利润, 毛利润 %.2f, 净利润 %.2f' %
                 (trade.pnl, trade.pnlcomm))
        self.log(f'目前現金 {int(self.broker.get_cash())}')
        
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def stop(self):
        self.roi = (self.broker.get_value() / self.start_cash) - 1.0
        print('ROI:    {:.2f}%'.format(100.0 * self.roi))
        # print(f'股票價值 {(self.one_share) * self.data.close[0]}')
        print(f'剩餘現金 {int(self.broker.get_cash())}')

class RSI_glod_cross(bt.Strategy): ## RSI 黃金交叉
    def __init__(self):
        self._next_buy_date = datetime(2020, 4, 5)
        # 保存收盘价的引用
        self.dataclose = self.datas[0].close
        self.one_share = 0 #股票数量
        self.start_cash = self.broker.get_cash()
        ## KDJ
        # 9个交易日内最高价
        # self.high_nine = bt.indicators.Highest(self.data.high, period=9)
        # 9个交易日内最低价
        # self.low_nine = bt.indicators.Lowest(self.data.low, period=9)
        # 计算rsv值
        # self.rsv = 100 * bt.DivByZero(self.data_close - self.low_nine, self.high_nine - self.low_nine, zero=None)
        # 计算rsv的3周期加权平均值，即K值
        # self.K = bt.indicators.EMA(self.rsv, period=3)
        # D值=K值的3周期加权平均值
        # self.D = bt.indicators.EMA(self.K, period=3)
        # J=3*K-2*D
        # self.J = 3 * self.K - 2 * self.D
        ## KDJ
        ## MACD
        # me1 = bt.indicators.EMA(self.data, period=12)
        # me2 = bt.indicators.EMA(self.data, period=26)
        # self.macd = me1 - me2
        # self.signal = bt.indicators.EMA(self.macd, period=9)
        # bt.indicators.MACDHisto(self.data)
        ## MACD
        ## RSI
        self.rsi5 = bt.indicators.RSI(self.datas[0], period=5)
        self.rsi10 = bt.indicators.RSI(self.datas[0], period=10)
        ## RSI
        # 跟踪挂单
        # self.order = None
        # 买入价格和手续费
        self.buyprice = None
        self.buycomm = None
  
    def next(self):
        if self.rsi5 > self.rsi10 and self.rsi5[-1] <= self.rsi10[-1] and self.rsi5 < 40:
            self.log('BUY, %.2f' % self.data.close[0])
            self.buy(size=1000)
            
        elif self.rsi5 < self.rsi10 and self.rsi5[-1] >= self.rsi10[-1] and self.rsi5 > 60:
            self.log('SELL, %.2f' % self.data.close[0])
            self.sell(size=1000)
            

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # broker 提交/接受了，买/卖订单则什么都不做
            return

        # 检查一个订单是否完成
        # 注意: 当资金不足时，broker会拒绝订单
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    '已买入, 价格: %.2f, 張數: %.2f, 费用: %.2f, 佣金 %.2f' %
                    (order.executed.price,
                     order.executed.size,
                     order.executed.value,
                     order.executed.comm))
                self.one_share += 1000
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log('已卖出, 价格: %.2f,, 張數: %.2f 费用: %.2f, 佣金 %.2f' %
                         (order.executed.price,
                          order.executed.size,
                          order.executed.value,
                          order.executed.comm))
                self.one_share -= 1000
            # 记录当前交易数量
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单取消/保证金不足/拒绝')

        # 其他状态记录为：无挂起订单
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('交易利润, 毛利润 %.2f, 净利润 %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def stop(self):
        self.roi = (self.broker.get_value() / self.start_cash) - 1.0
        print('ROI:        {:.2f}%'.format(100.0 * self.roi))
        print('Cash: {:.2f}, Stock Value:{:.2f}'.format(self.broker.get_cash() ,self.broker.get_value()))

class K_80_20_buy_sell(bt.Strategy): ## 策略 K>80 sell K< 20 buy
    def __init__(self):
        self._next_buy_date = datetime(2020, 4, 5)
        # 保存收盘价的引用
        self.dataclose = self.datas[0].close
        self.one_share = 0 #股票数量
        self.start_cash = self.broker.get_cash()

        self.sma5 = btind.SimpleMovingAverage(period=5) # 5日均线
        self.sma10 = btind.SimpleMovingAverage(period=10) # 10日均线
        self.sma10 = btind.SimpleMovingAverage(period=15) # 15日均线

        # 9个交易日内最高价
        self.high_nine = bt.indicators.Highest(self.data.high, period=9)
        # 9个交易日内最低价
        self.low_nine = bt.indicators.Lowest(self.data.low, period=9)
        # 计算rsv值
        self.rsv = 100 * bt.DivByZero(self.data_close - self.low_nine, self.high_nine - self.low_nine, zero=None)
        # 计算rsv的3周期加权平均值，即K值
        self.K = bt.indicators.EMA(self.rsv, period=3)
        # D值=K值的3周期加权平均值
        self.D = bt.indicators.EMA(self.K, period=3)
        # J=3*K-2*D
        self.J = 3 * self.K - 2 * self.D
        # 跟踪挂单
        self.order = None
        # 买入价格和手续费
        self.buyprice = None
        self.buycomm = None
  
    def next(self):
        if self.rsv <= 20:
            self.log('BUY, %.2f' % self.data.close[0])
            self.buy(size=1000) ## 台股
            
        elif self.rsv >= 80 and self.one_share > 0:
            self.log('SELL, %.2f' % self.data.close[0])
            self.sell(size=1000) ## 台股
            
        elif self.rsv >= 80 and self.one_share == 0:
            print(' ')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # broker 提交/接受了，买/卖订单则什么都不做
            return

        # 检查一个订单是否完成
        # 注意: 当资金不足时，broker会拒绝订单
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    '已买入, 价格: %.2f, 费用: %.2f, 佣金 %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
                self.one_share += 1
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log('已卖出, 价格: %.2f, 费用: %.2f, 佣金 %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
                self.one_share -= 1
            # 记录当前交易数量
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单取消/保证金不足/拒绝')

        # 其他状态记录为：无挂起订单
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('交易利润, 毛利润 %.2f, 净利润 %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def stop(self):
        self.roi = (self.broker.get_value() / self.start_cash) - 1.0
        print('ROI:        {:.2f}%'.format(100.0 * self.roi))
        print('Cash: {:.2f}, Stock Value:{:.2f}'.format(self.broker.get_cash() ,self.broker.get_value()))
        # print(self.one_share)
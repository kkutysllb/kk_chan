"""
Mario机器学习模型训练脚本
基于Mario量化文章，训练和验证LightGBM模型
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from quantitative.strategies.mario_ml_strategy import MarioMLStrategy, MarioMLStrategyConfig
from quantitative.adapters.jq_data_adapter import JQDataAdapter

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mario_ml_training.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class MarioMLModelTrainer:
    """Mario机器学习模型训练器"""
    
    def __init__(self):
        self.strategy = None
        self.training_data = None
        self.results_dir = Path(__file__).parent.parent / 'training_results'
        self.results_dir.mkdir(exist_ok=True)
        
    def create_strategy(self) -> MarioMLStrategy:
        """创建策略实例"""
        
        config = MarioMLStrategyConfig(
            strategy_name="Mario_ML_SmallCap_Enhanced",
            position_size=0.1,
            params={
                'stock_num': 20,  # 持仓股票数量
                'rebalance_freq': 'monthly',  # 月度调仓
                'correlation_threshold': 0.6,  # 恢复原始阈值
                'model_params': {
                    'objective': 'binary',
                    'metric': 'binary_logloss',
                    'boosting_type': 'gbdt',
                    'verbose': -1,
                    'num_boost_round': 100,  # 大幅减少训练轮数防止过拟合
                    'learning_rate': 0.1,    # 提高学习率
                    'num_leaves': 31,        # 恢复原始叶子数
                    'feature_fraction': 0.8, # 恢复原始特征采样
                    'bagging_fraction': 0.8, # 恢复原始样本采样
                    'bagging_freq': 5,
                    'min_child_samples': 20  # 恢复原始最小样本数
                },
                'feature_selection': True,
                'lookback_months': 24,  # 2年训练数据
                'min_samples': 500,
            }
        )
        
        self.strategy = MarioMLStrategy(config)
        return self.strategy
    
    def prepare_and_analyze_data(self, end_date: datetime) -> pd.DataFrame:
        """准备和分析训练数据"""
        
        logger.info("开始准备训练数据...")
        
        # 准备训练数据
        self.training_data = self.strategy.prepare_training_data(end_date)
        
        if self.training_data.empty:
            logger.error("训练数据为空")
            return pd.DataFrame()
        
        logger.info(f"训练数据形状: {self.training_data.shape}")
        
        # 数据质量分析
        self._analyze_data_quality()
        
        # 特征分析
        self._analyze_features()
        
        return self.training_data
    
    def _analyze_data_quality(self):
        """分析数据质量"""
        
        logger.info("开始数据质量分析...")
        
        df = self.training_data
        
        # 基本统计信息
        logger.info(f"样本总数: {len(df)}")
        logger.info(f"特征总数: {len(df.columns) - 1}")  # 减去label列
        
        # 标签分布
        if 'label' in df.columns:
            label_dist = df['label'].value_counts()
            logger.info("标签分布:")
            logger.info(f"  正类 (1): {label_dist.get(1, 0)} ({label_dist.get(1, 0)/len(df)*100:.1f}%)")
            logger.info(f"  负类 (0): {label_dist.get(0, 0)} ({label_dist.get(0, 0)/len(df)*100:.1f}%)")
        
        # 缺失值分析
        missing_info = df.isnull().sum()
        missing_features = missing_info[missing_info > 0]
        
        if len(missing_features) > 0:
            logger.info(f"存在缺失值的特征数: {len(missing_features)}")
            logger.info("缺失值最多的前10个特征:")
            for feature, count in missing_features.nlargest(10).items():
                ratio = count / len(df) * 100
                logger.info(f"  {feature}: {count} ({ratio:.1f}%)")
        else:
            logger.info("所有特征均无缺失值")
        
        # 保存数据质量报告
        self._save_data_quality_report(df)
    
    def _save_data_quality_report(self, df: pd.DataFrame):
        """保存数据质量报告"""
        
        try:
            # 创建数据质量报告
            report = {
                'basic_info': {
                    'total_samples': len(df),
                    'total_features': len(df.columns) - 1,
                    'memory_usage': df.memory_usage(deep=True).sum() / 1024 / 1024  # MB
                },
                'label_distribution': df['label'].value_counts().to_dict() if 'label' in df.columns else {},
                'missing_values': df.isnull().sum().to_dict(),
                'feature_stats': df.describe().to_dict()
            }
            
            # 保存为JSON
            import json
            report_file = self.results_dir / 'data_quality_report.json'
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"数据质量报告已保存: {report_file}")
            
        except Exception as e:
            logger.error(f"保存数据质量报告失败: {e}")
    
    def _analyze_features(self):
        """特征分析"""
        
        logger.info("开始特征分析...")
        
        df = self.training_data
        features = [col for col in df.columns if col != 'label']
        
        if len(features) == 0:
            return
        
        # 相关性分析
        corr_matrix = df[features].corr()
        
        # 找出高相关性特征对
        high_corr_pairs = []
        threshold = 0.8
        
        for i in range(len(features)):
            for j in range(i+1, len(features)):
                corr_val = corr_matrix.iloc[i, j]
                if not pd.isna(corr_val) and abs(corr_val) > threshold:
                    high_corr_pairs.append((features[i], features[j], corr_val))
        
        logger.info(f"高相关性特征对数量 (|r| > {threshold}): {len(high_corr_pairs)}")
        
        if len(high_corr_pairs) > 0:
            logger.info("高相关性特征对 (前10个):")
            for feat1, feat2, corr in high_corr_pairs[:10]:
                logger.info(f"  {feat1} <-> {feat2}: {corr:.3f}")
        
        # 生成相关性热力图
        self._plot_correlation_heatmap(corr_matrix)
        
        # 特征重要性分析（与标签的相关性）
        if 'label' in df.columns:
            self._analyze_feature_importance(df)
    
    def _plot_correlation_heatmap(self, corr_matrix: pd.DataFrame):
        """绘制相关性热力图"""
        
        try:
            # 由于特征太多，只显示部分特征
            n_features = min(30, len(corr_matrix))
            corr_subset = corr_matrix.iloc[:n_features, :n_features]
            
            plt.figure(figsize=(15, 12))
            mask = np.triu(np.ones_like(corr_subset, dtype=bool))
            sns.heatmap(corr_subset, mask=mask, annot=False, fmt=".2f", 
                       cmap='RdBu_r', vmin=-1, vmax=1, center=0)
            plt.title(f'因子间相关性矩阵 (前{n_features}个特征)')
            plt.tight_layout()
            
            plot_file = self.results_dir / 'correlation_heatmap.png'
            plt.savefig(plot_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"相关性热力图已保存: {plot_file}")
            
        except Exception as e:
            logger.error(f"绘制相关性热力图失败: {e}")
    
    def _analyze_feature_importance(self, df: pd.DataFrame):
        """分析特征重要性"""
        
        try:
            features = [col for col in df.columns if col != 'label']
            
            # 计算与标签的相关性
            label_corr = df[features + ['label']].corr()['label'].drop('label')
            
            # 按绝对值排序
            feature_importance = label_corr.abs().sort_values(ascending=False)
            
            logger.info("特征重要性 Top 20 (与标签的相关性):")
            for feature, corr in feature_importance.head(20).items():
                direction = "正相关" if label_corr[feature] > 0 else "负相关"
                logger.info(f"  {feature}: {corr:.4f} ({direction})")
            
            # 绘制特征重要性图
            self._plot_feature_importance(feature_importance)
            
        except Exception as e:
            logger.error(f"分析特征重要性失败: {e}")
    
    def _plot_feature_importance(self, importance: pd.Series):
        """绘制特征重要性图"""
        
        try:
            plt.figure(figsize=(12, 8))
            
            # 显示前20个最重要的特征
            top_features = importance.head(20)
            
            bars = plt.barh(range(len(top_features)), top_features.values)
            plt.yticks(range(len(top_features)), top_features.index)
            plt.xlabel('与标签的相关性 (绝对值)')
            plt.title('特征重要性 Top 20')
            plt.gca().invert_yaxis()
            
            # 添加数值标签
            for i, bar in enumerate(bars):
                width = bar.get_width()
                plt.text(width + 0.001, bar.get_y() + bar.get_height()/2, 
                        f'{width:.3f}', ha='left', va='center', fontsize=8)
            
            plt.tight_layout()
            
            plot_file = self.results_dir / 'feature_importance.png'
            plt.savefig(plot_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"特征重要性图已保存: {plot_file}")
            
        except Exception as e:
            logger.error(f"绘制特征重要性图失败: {e}")
    
    def train_and_validate_model(self) -> bool:
        """训练和验证模型"""
        
        if self.training_data.empty:
            logger.error("训练数据为空")
            return False
        
        logger.info("开始训练模型...")
        
        # 训练模型
        success = self.strategy.train_model(self.training_data)
        
        if not success:
            logger.error("模型训练失败")
            return False
        
        # 模型验证（训练集）
        self._validate_model()
        
        # 验证集评估（2025年数据）
        self._evaluate_on_validation_set()
        
        return True
    
    def _validate_model(self):
        """模型验证"""
        
        logger.info("开始模型验证...")
        
        try:
            df = self.training_data
            features = self.strategy.selected_features
            
            if not features:
                logger.error("没有选择的特征")
                return
            
            X = df[features]
            y = df['label']
            
            # 转换数据类型 - LightGBM需要数值类型
            for col in X.columns:
                X[col] = pd.to_numeric(X[col], errors='coerce')
            
            # 删除包含NaN的行
            valid_idx = ~(X.isnull().any(axis=1) | y.isnull())
            X_valid = X[valid_idx]
            y_valid = y[valid_idx]
            
            # 模型预测
            predictions = self.strategy.model.predict(X_valid)
            pred_binary = (predictions > 0.5).astype(int)
            
            # 生成验证报告
            self._generate_validation_report(y_valid, predictions, pred_binary)
            
            # 特征重要性分析
            self._analyze_model_feature_importance()
            
        except Exception as e:
            logger.error(f"模型验证失败: {e}")
    
    def _generate_validation_report(self, y_true, y_pred_proba, y_pred_binary):
        """生成验证报告"""
        
        try:
            from sklearn.metrics import (classification_report, confusion_matrix, 
                                       roc_curve, precision_recall_curve, auc)
            
            # 性能指标
            report = classification_report(y_true, y_pred_binary, output_dict=True)
            cm = confusion_matrix(y_true, y_pred_binary)
            
            # ROC曲线
            fpr, tpr, _ = roc_curve(y_true, y_pred_proba)
            roc_auc = auc(fpr, tpr)
            
            # PR曲线
            precision, recall, _ = precision_recall_curve(y_true, y_pred_proba)
            pr_auc = auc(recall, precision)
            
            # 打印报告
            logger.info("模型验证报告:")
            logger.info(f"  准确率: {report['accuracy']:.4f}")
            logger.info(f"  精确率: {report['1']['precision']:.4f}")
            logger.info(f"  召回率: {report['1']['recall']:.4f}")
            logger.info(f"  F1分数: {report['1']['f1-score']:.4f}")
            logger.info(f"  ROC AUC: {roc_auc:.4f}")
            logger.info(f"  PR AUC: {pr_auc:.4f}")
            
            # 绘制性能图表
            self._plot_model_performance(y_true, y_pred_proba, y_pred_binary, 
                                       fpr, tpr, roc_auc, precision, recall, pr_auc, cm)
            
            # 保存验证报告
            validation_report = {
                'classification_report': report,
                'confusion_matrix': cm.tolist(),
                'roc_auc': roc_auc,
                'pr_auc': pr_auc,
                'model_config': self.strategy.config.params
            }
            
            import json
            report_file = self.results_dir / 'validation_report.json'
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(validation_report, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"验证报告已保存: {report_file}")
            
        except Exception as e:
            logger.error(f"生成验证报告失败: {e}")
    
    def _plot_model_performance(self, y_true, y_pred_proba, y_pred_binary,
                               fpr, tpr, roc_auc, precision, recall, pr_auc, cm):
        """绘制模型性能图表"""
        
        try:
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            
            # 1. 混淆矩阵
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                       xticklabels=['预测0', '预测1'],
                       yticklabels=['实际0', '实际1'], ax=axes[0,0])
            axes[0,0].set_title('混淆矩阵')
            axes[0,0].set_ylabel('实际标签')
            axes[0,0].set_xlabel('预测标签')
            
            # 2. ROC曲线
            axes[0,1].plot(fpr, tpr, color='darkorange', lw=2, 
                          label=f'ROC曲线 (AUC = {roc_auc:.3f})')
            axes[0,1].plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
            axes[0,1].set_xlim([0.0, 1.0])
            axes[0,1].set_ylim([0.0, 1.05])
            axes[0,1].set_xlabel('假正率 (FPR)')
            axes[0,1].set_ylabel('真正率 (TPR)')
            axes[0,1].set_title('ROC曲线')
            axes[0,1].legend(loc="lower right")
            axes[0,1].grid(True)
            
            # 3. PR曲线
            axes[1,0].plot(recall, precision, color='darkblue', lw=2,
                          label=f'PR曲线 (AUC = {pr_auc:.3f})')
            axes[1,0].fill_between(recall, precision, alpha=0.2, color='darkblue')
            axes[1,0].set_xlabel('召回率 (Recall)')
            axes[1,0].set_ylabel('精确率 (Precision)')
            axes[1,0].set_title('Precision-Recall曲线')
            axes[1,0].legend(loc='upper right')
            axes[1,0].grid(True)
            
            # 4. 预测概率分布
            for label in [0, 1]:
                mask = y_true == label
                if mask.sum() > 0:
                    axes[1,1].hist(y_pred_proba[mask], bins=30, alpha=0.7, 
                                  label=f'真实标签={label}', density=True)
            axes[1,1].axvline(0.5, color='red', linestyle='--', label='阈值=0.5')
            axes[1,1].set_xlabel('预测为正类的概率')
            axes[1,1].set_ylabel('密度')
            axes[1,1].set_title('预测概率分布')
            axes[1,1].legend()
            axes[1,1].grid(True)
            
            plt.tight_layout()
            
            plot_file = self.results_dir / 'model_performance.png'
            plt.savefig(plot_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"模型性能图表已保存: {plot_file}")
            
            # 生成训练指标汇总图
            self._plot_training_metrics_summary(y_true, y_pred_proba, y_pred_binary, roc_auc, pr_auc)
            
        except Exception as e:
            logger.error(f"绘制模型性能图表失败: {e}")
    
    def _plot_training_metrics_summary(self, y_true, y_pred_proba, y_pred_binary, roc_auc, pr_auc):
        """绘制训练指标汇总图"""
        
        try:
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
            
            # 计算关键指标
            accuracy = accuracy_score(y_true, y_pred_binary)
            precision = precision_score(y_true, y_pred_binary)
            recall = recall_score(y_true, y_pred_binary)
            f1 = f1_score(y_true, y_pred_binary)
            
            # 创建指标汇总图
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # 左图：关键指标柱状图
            metrics = ['准确率', '精确率', '召回率', 'F1分数', 'ROC AUC', 'PR AUC']
            values = [accuracy, precision, recall, f1, roc_auc, pr_auc]
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
            
            bars = ax1.bar(metrics, values, color=colors, alpha=0.8)
            ax1.set_ylim(0, 1)
            ax1.set_ylabel('分数')
            ax1.set_title('Mario ML模型训练指标汇总', fontsize=14, fontweight='bold')
            ax1.grid(True, axis='y', alpha=0.3)
            
            # 在柱状图上添加数值标签
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                        f'{value:.3f}', ha='center', va='bottom', fontweight='bold')
            
            # 右图：样本分布饼图
            pos_samples = (y_true == 1).sum()
            neg_samples = (y_true == 0).sum()
            
            labels = [f'负样本\n({neg_samples}个)', f'正样本\n({pos_samples}个)']
            sizes = [neg_samples, pos_samples]
            colors_pie = ['#ff9999', '#66b3ff']
            
            ax2.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%',
                   startangle=90, textprops={'fontsize': 12})
            ax2.set_title('训练样本分布', fontsize=14, fontweight='bold')
            
            plt.tight_layout()
            
            plot_file = self.results_dir / 'training_metrics_summary.png'
            plt.savefig(plot_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"训练指标汇总图已保存: {plot_file}")
            
        except Exception as e:
            logger.error(f"绘制训练指标汇总图失败: {e}")
    
    def _evaluate_on_validation_set(self):
        """在验证集（2025年数据）上评估模型"""
        
        logger.info("开始在验证集上评估模型...")
        
        try:
            from datetime import datetime
            
            # 使用2024年下半年作为验证集，减少验证集规模
            validation_start = datetime(2024, 7, 1)
            validation_end = datetime(2024, 12, 31)
            
            logger.info(f"验证集时间范围: {validation_start.strftime('%Y-%m-%d')} 到 {validation_end.strftime('%Y-%m-%d')}")
            
            # 临时修改策略的训练数据生成逻辑为验证集
            original_prepare = self.strategy.prepare_training_data
            
            def prepare_validation_data(end_date):
                # 使用验证集时间范围生成数据
                date_list = self.strategy._generate_month_end_dates(validation_start, validation_end)
                
                all_validation_data = []
                import random
                
                for i, date in enumerate(date_list[:-1]):
                    try:
                        logger.info(f"验证集处理日期: {date.strftime('%Y-%m-%d')} ({i+1}/{len(date_list)-1})")
                        
                        # 获取股票池并随机采样
                        stock_list = self.strategy.jq_adapter.get_index_stocks('399101.XSHE', date)
                        stock_list = self.strategy.jq_adapter.filter_st_stock(stock_list)
                        stock_list = self.strategy.jq_adapter.filter_new_stock(stock_list, date)
                        stock_list = self.strategy.jq_adapter.filter_paused_stock(stock_list, date)
                        
                        if len(stock_list) < 100:
                            continue
                        
                        # 随机采样200只股票用于验证
                        if len(stock_list) > 200:
                            stock_list = random.sample(stock_list, 200)
                        
                        # 获取因子数据
                        factor_data = self.strategy.jq_adapter.get_factor_values(
                            stock_list, self.strategy.factor_names, date, count=1
                        )
                        
                        # 构建因子DataFrame
                        df_factors = self.strategy._build_factor_dataframe(factor_data, stock_list)
                        
                        if df_factors.empty:
                            continue
                        
                        # 计算收益率
                        next_date = date_list[i + 1]
                        returns = self.strategy._calculate_monthly_returns(stock_list, date, next_date)
                        
                        if returns.empty:
                            continue
                        
                        # 合并数据
                        df_combined = df_factors.merge(returns, left_index=True, right_index=True, how='inner')
                        median_return = df_combined['monthly_return'].median()
                        df_combined['label'] = (df_combined['monthly_return'] >= median_return).astype(int)
                        df_combined = df_combined.drop(columns=['monthly_return'])
                        
                        all_validation_data.append(df_combined)
                        
                    except Exception as e:
                        logger.error(f"验证集处理日期 {date} 时出错: {e}")
                        continue
                
                if not all_validation_data:
                    return pd.DataFrame()
                
                validation_df = pd.concat(all_validation_data, ignore_index=True)
                logger.info(f"验证集数据生成完成，样本数: {len(validation_df)}")
                return validation_df
            
            validation_data = prepare_validation_data(validation_end)
            
            if validation_data.empty:
                logger.warning("验证集数据为空")
                return
            
            logger.info(f"验证集样本数: {len(validation_data)}")
            
            # 准备验证特征和标签
            features = self.strategy.selected_features
            X_val = validation_data[features]
            y_val = validation_data['label']
            
            # 转换数据类型
            for col in X_val.columns:
                X_val[col] = pd.to_numeric(X_val[col], errors='coerce')
            
            # 删除包含NaN的行
            valid_idx = ~(X_val.isnull().any(axis=1) | y_val.isnull())
            X_val_clean = X_val[valid_idx]
            y_val_clean = y_val[valid_idx]
            
            if len(X_val_clean) == 0:
                logger.warning("验证集清洗后数据为空")
                return
            
            logger.info(f"验证集有效样本数: {len(X_val_clean)}")
            
            # 模型预测
            val_predictions = self.strategy.model.predict(X_val_clean)
            val_pred_binary = (val_predictions > 0.5).astype(int)
            
            # 生成验证集报告和图表
            self._generate_validation_set_report(y_val_clean, val_predictions, val_pred_binary)
            
        except Exception as e:
            logger.error(f"验证集评估失败: {e}")
            import traceback
            traceback.print_exc()
    
    def _generate_validation_set_report(self, y_true, y_pred_proba, y_pred_binary):
        """生成验证集评估报告和图表"""
        
        try:
            from sklearn.metrics import (classification_report, confusion_matrix, 
                                       roc_curve, precision_recall_curve, auc,
                                       accuracy_score, precision_score, recall_score, f1_score)
            
            # 性能指标
            accuracy = accuracy_score(y_true, y_pred_binary)
            precision = precision_score(y_true, y_pred_binary)
            recall = recall_score(y_true, y_pred_binary)
            f1 = f1_score(y_true, y_pred_binary)
            
            report = classification_report(y_true, y_pred_binary, output_dict=True)
            cm = confusion_matrix(y_true, y_pred_binary)
            
            # ROC和PR曲线
            fpr, tpr, _ = roc_curve(y_true, y_pred_proba)
            roc_auc = auc(fpr, tpr)
            
            precision_curve, recall_curve, _ = precision_recall_curve(y_true, y_pred_proba)
            pr_auc = auc(recall_curve, precision_curve)
            
            # 打印验证集报告
            logger.info("验证集评估报告:")
            logger.info(f"  准确率: {accuracy:.4f}")
            logger.info(f"  精确率: {precision:.4f}")
            logger.info(f"  召回率: {recall:.4f}")
            logger.info(f"  F1分数: {f1:.4f}")
            logger.info(f"  ROC AUC: {roc_auc:.4f}")
            logger.info(f"  PR AUC: {pr_auc:.4f}")
            
            # 绘制验证集性能图表
            self._plot_validation_performance(y_true, y_pred_proba, y_pred_binary,
                                            fpr, tpr, roc_auc, precision_curve, recall_curve, pr_auc, cm)
            
            # 绘制验证集指标汇总图
            self._plot_validation_metrics_summary(y_true, y_pred_proba, y_pred_binary, roc_auc, pr_auc)
            
            # 保存验证集报告
            validation_report = {
                'validation_metrics': {
                    'accuracy': accuracy,
                    'precision': precision,
                    'recall': recall,
                    'f1_score': f1,
                    'roc_auc': roc_auc,
                    'pr_auc': pr_auc
                },
                'classification_report': report,
                'confusion_matrix': cm.tolist(),
                'sample_count': len(y_true)
            }
            
            import json
            report_file = self.results_dir / 'validation_set_report.json'
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(validation_report, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"验证集报告已保存: {report_file}")
            
        except Exception as e:
            logger.error(f"生成验证集报告失败: {e}")
    
    def _plot_validation_performance(self, y_true, y_pred_proba, y_pred_binary,
                                   fpr, tpr, roc_auc, precision, recall, pr_auc, cm):
        """绘制验证集性能图表"""
        
        try:
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            
            # 1. 混淆矩阵
            sns.heatmap(cm, annot=True, fmt='d', cmap='Greens',
                       xticklabels=['预测0', '预测1'],
                       yticklabels=['实际0', '实际1'], ax=axes[0,0])
            axes[0,0].set_title('验证集混淆矩阵')
            axes[0,0].set_ylabel('实际标签')
            axes[0,0].set_xlabel('预测标签')
            
            # 2. ROC曲线
            axes[0,1].plot(fpr, tpr, color='darkgreen', lw=2, 
                          label=f'验证集ROC曲线 (AUC = {roc_auc:.3f})')
            axes[0,1].plot([0, 1], [0, 1], color='gray', lw=2, linestyle='--')
            axes[0,1].set_xlim([0.0, 1.0])
            axes[0,1].set_ylim([0.0, 1.05])
            axes[0,1].set_xlabel('假正率 (FPR)')
            axes[0,1].set_ylabel('真正率 (TPR)')
            axes[0,1].set_title('验证集ROC曲线')
            axes[0,1].legend(loc="lower right")
            axes[0,1].grid(True)
            
            # 3. PR曲线
            axes[1,0].plot(recall, precision, color='darkred', lw=2,
                          label=f'验证集PR曲线 (AUC = {pr_auc:.3f})')
            axes[1,0].fill_between(recall, precision, alpha=0.2, color='darkred')
            axes[1,0].set_xlabel('召回率 (Recall)')
            axes[1,0].set_ylabel('精确率 (Precision)')
            axes[1,0].set_title('验证集Precision-Recall曲线')
            axes[1,0].legend(loc='upper right')
            axes[1,0].grid(True)
            
            # 4. 预测概率分布
            for label in [0, 1]:
                mask = y_true == label
                if mask.sum() > 0:
                    axes[1,1].hist(y_pred_proba[mask], bins=20, alpha=0.7, 
                                  label=f'真实标签={label}', density=True)
            axes[1,1].axvline(0.5, color='red', linestyle='--', label='阈值=0.5')
            axes[1,1].set_xlabel('预测为正类的概率')
            axes[1,1].set_ylabel('密度')
            axes[1,1].set_title('验证集预测概率分布')
            axes[1,1].legend()
            axes[1,1].grid(True)
            
            plt.suptitle('验证集模型性能评估', fontsize=16, fontweight='bold')
            plt.tight_layout()
            
            plot_file = self.results_dir / 'validation_set_performance.png'
            plt.savefig(plot_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"验证集性能图表已保存: {plot_file}")
            
        except Exception as e:
            logger.error(f"绘制验证集性能图表失败: {e}")
    
    def _plot_validation_metrics_summary(self, y_true, y_pred_proba, y_pred_binary, roc_auc, pr_auc):
        """绘制验证集指标汇总图"""
        
        try:
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
            
            # 计算关键指标
            accuracy = accuracy_score(y_true, y_pred_binary)
            precision = precision_score(y_true, y_pred_binary)
            recall = recall_score(y_true, y_pred_binary)
            f1 = f1_score(y_true, y_pred_binary)
            
            # 创建指标汇总图
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # 左图：关键指标柱状图
            metrics = ['准确率', '精确率', '召回率', 'F1分数', 'ROC AUC', 'PR AUC']
            values = [accuracy, precision, recall, f1, roc_auc, pr_auc]
            colors = ['#2ca02c', '#ff7f0e', '#1f77b4', '#d62728', '#9467bd', '#8c564b']
            
            bars = ax1.bar(metrics, values, color=colors, alpha=0.8)
            ax1.set_ylim(0, 1)
            ax1.set_ylabel('分数')
            ax1.set_title('验证集性能指标汇总', fontsize=14, fontweight='bold')
            ax1.grid(True, axis='y', alpha=0.3)
            
            # 在柱状图上添加数值标签
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                        f'{value:.3f}', ha='center', va='bottom', fontweight='bold')
            
            # 右图：样本分布饼图
            pos_samples = (y_true == 1).sum()
            neg_samples = (y_true == 0).sum()
            
            labels = [f'负样本\n({neg_samples}个)', f'正样本\n({pos_samples}个)']
            sizes = [neg_samples, pos_samples]
            colors_pie = ['#ffcc99', '#99ccff']
            
            ax2.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%',
                   startangle=90, textprops={'fontsize': 12})
            ax2.set_title('验证集样本分布', fontsize=14, fontweight='bold')
            
            plt.tight_layout()
            
            plot_file = self.results_dir / 'validation_set_metrics_summary.png'
            plt.savefig(plot_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"验证集指标汇总图已保存: {plot_file}")
            
        except Exception as e:
            logger.error(f"绘制验证集指标汇总图失败: {e}")
    
    def _analyze_model_feature_importance(self):
        """分析模型特征重要性"""
        
        try:
            if not hasattr(self.strategy.model, 'feature_importance'):
                return
            
            importance = self.strategy.model.feature_importance()
            feature_names = self.strategy.selected_features
            
            # 创建特征重要性DataFrame
            importance_df = pd.DataFrame({
                'feature': feature_names,
                'importance': importance
            }).sort_values('importance', ascending=False)
            
            logger.info("模型特征重要性 Top 20:")
            for _, row in importance_df.head(20).iterrows():
                logger.info(f"  {row['feature']}: {row['importance']}")
            
            # 绘制特征重要性图
            plt.figure(figsize=(12, 8))
            
            top_features = importance_df.head(20)
            bars = plt.barh(range(len(top_features)), top_features['importance'])
            plt.yticks(range(len(top_features)), top_features['feature'])
            plt.xlabel('特征重要性')
            plt.title('LightGBM模型特征重要性 Top 20')
            plt.gca().invert_yaxis()
            
            # 添加数值标签
            for i, bar in enumerate(bars):
                width = bar.get_width()
                plt.text(width + max(importance) * 0.01, bar.get_y() + bar.get_height()/2,
                        f'{width:.0f}', ha='left', va='center', fontsize=8)
            
            plt.tight_layout()
            
            plot_file = self.results_dir / 'model_feature_importance.png'
            plt.savefig(plot_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"模型特征重要性图已保存: {plot_file}")
            
            # 保存特征重要性数据
            importance_file = self.results_dir / 'feature_importance.csv'
            importance_df.to_csv(importance_file, index=False, encoding='utf-8')
            
        except Exception as e:
            logger.error(f"分析模型特征重要性失败: {e}")
    
    def test_stock_selection(self, test_date: datetime):
        """测试选股功能"""
        
        logger.info(f"测试选股功能，日期: {test_date}")
        
        try:
            selected_stocks = self.strategy.get_stock_selection(test_date)
            
            if selected_stocks:
                logger.info(f"选中股票数量: {len(selected_stocks)}")
                logger.info("选中的股票:")
                for i, stock in enumerate(selected_stocks, 1):
                    logger.info(f"  {i}. {stock}")
            else:
                logger.warning("未选中任何股票")
            
            return selected_stocks
            
        except Exception as e:
            logger.error(f"测试选股功能失败: {e}")
            return []
    
    def run_full_training_pipeline(self):
        """运行完整的训练流程"""
        
        logger.info("=" * 60)
        logger.info("开始Mario机器学习模型训练流程")
        logger.info("=" * 60)
        
        try:
            # 1. 创建策略
            logger.info("步骤 1: 创建策略实例")
            self.create_strategy()
            
            # 2. 准备和分析数据
            logger.info("步骤 2: 准备和分析训练数据")
            end_date = datetime(2024, 6, 30)  # 训练数据截止到2024年中
            training_data = self.prepare_and_analyze_data(end_date)
            
            if training_data.empty:
                logger.error("训练数据准备失败")
                return False
            
            # 3. 训练和验证模型
            logger.info("步骤 3: 训练和验证模型")
            success = self.train_and_validate_model()
            
            if not success:
                logger.error("模型训练失败")
                return False
            
            # 4. 测试选股功能
            logger.info("步骤 4: 测试选股功能")
            test_date = datetime(2024, 6, 30)  # 在验证集期间测试选股
            selected_stocks = self.test_stock_selection(test_date)
            
            logger.info("=" * 60)
            logger.info("Mario机器学习模型训练流程完成")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"训练流程失败: {e}")
            return False


def main():
    """主函数"""
    
    # 创建训练器
    trainer = MarioMLModelTrainer()
    
    # 运行完整训练流程
    success = trainer.run_full_training_pipeline()
    
    if success:
        logger.info("训练完成，可以使用模型进行策略回测")
    else:
        logger.error("训练失败，请检查日志")


if __name__ == "__main__":
    main()
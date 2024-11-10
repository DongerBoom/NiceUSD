from bank_transfer import get_bank_transfer_results, sort_transfer_results
import json

def get_available_banks():
    """从配置文件中获取可用的银行列表"""
    try:
        with open('bank_transfer_fees.json', 'r', encoding='utf-8') as f:
            fees_data = json.load(f)
            return sorted([fee['bank_name'] for fee in fees_data['fees']])
    except Exception:
        return []

def main():
    # 配置参数
    amount_rmb = 50000  # 汇款金额（人民币）
    top_num = 0  # 显示前几名（0表示显示全部）
    
    # 指定要查询的银行列表
    # 可选值包括：
    # - [] 空列表表示查询所有银行
    # - ['工商银行', '建设银行'] 只查询指定的银行
    # 支持的银行名称：
    available_banks = get_available_banks()
    print("支持的银行列表：")
    for bank in available_banks:
        print(f"- {bank}")
    print("\n使用示例：banks_available = ['工商银行', '建设银行']\n")
    
    banks_available = ['中国银行', '华夏银行', '工商银行', '建设银行', '招商银行']
    debug = False  # 是否显示调试信息
    
    all_results = get_bank_transfer_results(amount_rmb, debug)
    if not all_results:
        print("获取汇率数据失败")
        return
    
    sorted_all = sort_transfer_results(all_results, len(all_results))
    best_amount = sorted_all[0]['usd_amount']
    
    if banks_available:
        available_results = [result for result in sorted_all 
                           if result['bank_name'] in banks_available]
        if not available_results:
            print(f"未找到指定银行的汇率数据。可用银行: {banks_available}")
            return
    else:
        available_results = sorted_all if top_num == 0 else sorted_all[:top_num]
    
    print(f"\n汇款金额: {amount_rmb} 元人民币")
    print("\n===== 最优选择排名 =====")
    
    for result in available_results:
        global_rank = sorted_all.index(result) + 1
        print(f"\n第{global_rank}名: {result['bank_name']}")
        print(f"卖出汇率: {result['exchange_rate']:.4f}")
        print(f"手续费: {result['handling_fee']:.2f} 元")
        print(f"电报费: {result['wire_fee']:.2f} 元")
        print(f"总费用: {result['total_fees_rmb']:.2f} 元")
        print(f"可兑换: {result['usd_amount']:.2f} 美元")
        print(f"较最优方案少: {best_amount - result['usd_amount']:.2f} 美元")
        print("-" * 30)

if __name__ == "__main__":
    main() 
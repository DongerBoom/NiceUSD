from exchange_rate import get_currency_rate
from config import BANK_NAME_MAPPING
import json

def get_bank_transfer_results(amount_rmb=50000, currency='usd', debug=False):
    """获取所有银行的汇款计算结果
    Args:
        amount_rmb: 人民币金额，默认50000
        currency: 目标货币类型，默认usd
        debug: 是否输出调试信息，默认False
    Returns:
        list: 包含所有银行计算结果的列表
    """
    rates = get_currency_rate(currency)
    if not rates:
        return None
        
    try:
        with open('bank_transfer_fees.json', 'r', encoding='utf-8') as f:
            fees_data = json.load(f)
    except Exception as e:
        if debug:
            print(f"读取手续费数据失败: {str(e)}")
        return None
    
    all_results = []
    skipped_banks = []
    fee_banks = [fee['bank_name'] for fee in fees_data['fees']]
    
    for rate_data in rates:
        bank_name = rate_data['bank_name']
        search_name = BANK_NAME_MAPPING.get(bank_name, bank_name)
        exchange_rate = rate_data['sell_forex']
        
        bank_fee = next((fee for fee in fees_data['fees'] 
                        if fee['bank_name'] == search_name), None)
        
        if not bank_fee:
            if debug:
                reason = "未找到手续费信息"
                if search_name != bank_name:
                    reason += f"（原名: {bank_name} -> 映射名: {search_name}）"
                if search_name not in fee_banks:
                    reason += f"\n可用的银行名称: {', '.join(fee_banks)}"
                skipped_banks.append(f"{bank_name}: {reason}")
            continue
            
        result = calculate_transfer_result(bank_name, exchange_rate, bank_fee, amount_rmb)
        all_results.append(result)
    
    if debug:
        print(f"\n成功处理的银行数量: {len(all_results)}")
        if skipped_banks:
            print("\n以下银行被跳过:")
            for skip_info in skipped_banks:
                print(f"- {skip_info}")
    
    return all_results

def calculate_transfer_result(bank_name, exchange_rate, bank_fee, amount_rmb):
    """计算单个银行的汇款结果"""
    handling_fee_rate = float(bank_fee['handling_fee']['rate']) / 100
    handling_fee = amount_rmb * handling_fee_rate
    handling_fee = max(float(bank_fee['handling_fee']['min']), 
                      min(handling_fee, float(bank_fee['handling_fee']['max'])))
    
    wire_fee = float(bank_fee['wire_fee']['overseas'])
    if isinstance(wire_fee, str) and ";" in wire_fee:
        wire_fee = float(wire_fee.split(";")[1].split(":")[1].strip())
        
    total_fees_rmb = handling_fee + wire_fee
    exchangeable_rmb = amount_rmb - total_fees_rmb
    usd_amount = exchangeable_rmb / exchange_rate
    
    return {
        'bank_name': bank_name,
        'exchange_rate': exchange_rate,
        'handling_fee': handling_fee,
        'wire_fee': wire_fee,
        'total_fees_rmb': total_fees_rmb,
        'usd_amount': usd_amount
    }

def sort_transfer_results(results, top_n=5):
    """对汇款结果进行排序"""
    if not results:
        return None
        
    sorted_results = sorted(results, key=lambda x: x['usd_amount'], reverse=True)
    return sorted_results[:top_n] if top_n > 0 else sorted_results
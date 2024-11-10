import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def get_currency_rate(currency_code='usd'):
    """获取指定货币的汇率数据
    Args:
        currency_code: 货币代码，默认为'usd'
    """
    url = f"https://www.kylc.com/huilv?ccy={currency_code.lower()}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 找到汇率表格
        table = soup.find('table', {'id': f'bank_huilvtable_{currency_code.lower()}'})
        if not table:
            return None
            
        rates_data = []
        
        # 遍历表格行
        rows = table.find('tbody').find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 8:  # 确保有足够的列
                try:
                    rate_data = {
                        'bank_name': cols[0].text.split('\n')[0].strip(),  # 只取银行名称
                        'sell_forex': float(cols[4].text.strip()),  # 现汇卖出价
                        'update_time': cols[7].text.strip().split('\n')[0]  # 保留完整时间
                    }
                    rates_data.append(rate_data)
                except (ValueError, IndexError) as e:
                    continue
        
        # 打印获取到的数据条数
        print(f"成功获取了 {len(rates_data)} 条汇率数据")
                
        return rates_data
        
    except Exception as e:
        print(f"获取{currency_code}汇率数据失败: {str(e)}")
        return None 
    
def save_rates_to_json(rates_data, currency_code='usd', filename=None):
    """保存汇率数据到JSON文件
    Args:
        rates_data: 汇率数据列表
        currency_code: 货币代码
        filename: 文件名，默认为 currency_rates_YYYYMMDD.json
    """
    if not rates_data:
        return False
        
    if not filename:
        today = datetime.now().strftime('%Y%m%d')
        filename = f'currency_rates_{today}.json'
    
    data = {
        'currency': currency_code.upper(),
        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'rates': rates_data
    }
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"汇率数据已保存到 {filename}")
        return True
    except Exception as e:
        print(f"保存数据失败: {str(e)}")
        return False

if __name__ == "__main__":
    currency_code = 'usd'
    rates = get_currency_rate(currency_code)
    if rates:
        print("\n获取到汇率信息的银行列表:")
        for i, rate in enumerate(rates, 1):
            print(f"{i}. {rate['bank_name']}")
            
        # 保存到JSON文件
        save_rates_to_json(rates, currency_code)
    else:
        print(f"获取{currency_code}汇率数据失败")

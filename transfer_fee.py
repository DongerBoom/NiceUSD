import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def get_transfer_fees():
    """获取各大银行的境外汇款手续费"""
    fees_data = {
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "fees": []
    }
    
    # Add URL and fetch content
    url = "https://www.kylc.com/bank/fees/tt.html"
    html_content = requests.get(url).text
    
    # 解析HTML提取费率信息
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table', id='table')
    
    # 定义普通客户的可能描述
    normal_client_keywords = ["普通", "个人理财", "个人客户"]
    
    current_bank = None
    for row in table.find_all('tr')[1:]:  # 跳过表头
        cells = row.find_all('td')
        if len(cells) < 4:  # 确保至少有银行、客户级别、手续费和电报费这几列
            continue
            
        # 获取银行名称和客户级别
        bank_name = cells[0].text.strip() if not cells[0].get('style') else current_bank
        client_level = cells[1].text.strip()
        current_bank = bank_name if bank_name else current_bank
        
        # 检查是否为普通客户渠道
        if not any(keyword in client_level for keyword in normal_client_keywords):
            continue
            
        # 解析手续费
        handling_fee_text = cells[2].text.strip()
        handling_fee = {}
        
        if "免费" in handling_fee_text:
            handling_fee = {
                "rate": "0",
                "min": "0",
                "max": "0"
            }
        elif "汇款金额的" in handling_fee_text:
            try:
                parts = handling_fee_text.split(",")
                rate = parts[0].split("的")[1].replace("%", "")
                min_fee = parts[1].split("最低")[1].replace("元/笔", "")
                max_fee = parts[2].split("最高")[1].replace("元/笔", "")
                handling_fee = {
                    "rate": rate,
                    "min": min_fee,
                    "max": max_fee
                }
            except Exception as e:
                print(f"解析手续费失败: {handling_fee_text}, 错误: {str(e)}")
                continue
        
        # 解析电报费
        wire_fee_text = cells[3].text.strip()
        wire_fee = {}
        
        if "免费" in wire_fee_text:
            wire_fee = {
                "overseas": "0",
                "hk_mo_tw": "0"
            }
        else:
            try:
                if "港澳:" in wire_fee_text or "港:" in wire_fee_text:
                    parts = wire_fee_text.split(";")
                    # 处理港澳/港的费用
                    if "港澳:" in parts[0]:
                        hk_fee = parts[0].split("港澳:")[1].replace("元/笔", "").strip()
                    else:
                        hk_fee = parts[0].split("港:")[1].replace("元/笔", "").strip()
                    
                    # 处理其他地区费用
                    if "其余:" in parts[1]:
                        overseas_fee = parts[1].split("其余:")[1].replace("元/笔", "").strip()
                    else:
                        overseas_fee = parts[1].split(":")[1].replace("元/笔", "").strip()
                    
                    wire_fee = {
                        "overseas": overseas_fee,
                        "hk_mo_tw": hk_fee
                    }
                elif "港澳台:" in wire_fee_text:
                    parts = wire_fee_text.split(";")
                    hk_fee = parts[0].split(":")[1].replace("元/笔", "").strip()
                    overseas_fee = parts[1].split(":")[1].replace("元/笔", "").strip()
                    wire_fee = {
                        "overseas": overseas_fee,
                        "hk_mo_tw": hk_fee
                    }
                else:
                    fee = wire_fee_text.replace("元/笔", "").strip()
                    wire_fee = {
                        "overseas": fee,
                        "hk_mo_tw": fee
                    }
            except Exception as e:
                print(f"解析电报费失败: {wire_fee_text}, 错误: {str(e)}")
                continue
        
        # 添加到结果中
        fees_data["fees"].append({
            "bank_name": current_bank,
            "client_level": client_level,
            "handling_fee": handling_fee,
            "wire_fee": wire_fee
        })
    
    return fees_data

def save_to_json(data, filename='bank_transfer_fees.json'):
    """保存数据到JSON文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存数据失败: {str(e)}")
        return False

def get_available_banks():
    """从配置文件中获取可用的银行列表
    Returns:
        list: 已排序的可用银行列表
    """
    try:
        with open('bank_transfer_fees.json', 'r', encoding='utf-8') as f:
            fees_data = json.load(f)
            return sorted([fee['bank_name'] for fee in fees_data['fees']])
    except Exception:
        return []

if __name__ == "__main__":
    fees = get_transfer_fees()
    if fees:
        print(f"成功获取并保存了 {len(fees['fees'])} 条银行手续费数据")
        if save_to_json(fees):
            print("手续费数据已成功保存到 bank_transfer_fees.json")
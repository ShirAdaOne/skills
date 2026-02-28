#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化测试用例脚本：将文言信号替换为具体文言文字
"""

import json
import re
import os

def load_text_mappings():
    """加载文言映射表"""
    with open('/tmp/havp_text_mapping.json', 'r', encoding='utf-8') as f:
        havp_mapping = json.load(f)
    
    with open('/tmp/popup_mapping.json', 'r', encoding='utf-8') as f:
        popup_mapping = json.load(f)
    
    # 补充0xC4映射（从需求文档中得知）
    havp_mapping["0xC4"] = "车辆漫游中，请注意周围环境"
    havp_mapping["HAVPFunctTextDisp=0xC4"] = "车辆漫游中，请注意周围环境"
    havp_mapping["HAVPFunctTextDisp=0xC4: HAVP Roaming"] = "车辆漫游中，请注意周围环境"
    
    return havp_mapping, popup_mapping

def optimize_test_case_text(md_content, havp_mapping, popup_mapping):
    """优化测试用例中的文言信号"""
    
    optimized_content = md_content
    replacements = []
    
    # 1. 优化HAVPFunctTextDisp信号（在"预期结果"列）
    # 查找模式：显示文言"XXX" 或 中控屏显示文言"XXX"
    
    # 匹配HAVPFunctTextDisp=0xXX格式
    havp_pattern = r'(HAVPFunctTextDisp\s*=\s*0[xX]([0-9A-Fa-f]+))(?::[\w\s\-/]+)?'
    
    def replace_havp_signal(match):
        full_signal = match.group(0)
        hex_value = match.group(2).upper()
        
        # 在映射表中查找
        text = None
        for key, value in havp_mapping.items():
            if f"0x{hex_value}" in key.upper() or f"0X{hex_value}" in key.upper():
                text = value
                break
        
        if text and text != "系统退出" and text != "N.A.":
            # 返回信号+文言
            replacements.append((full_signal, hex_value, text))
            return f'HAVPFunctTextDisp=0x{hex_value}（文言："{text}"）'
        else:
            return full_signal
    
    optimized_content = re.sub(havp_pattern, replace_havp_signal, optimized_content)
    
    # 2. 在预期结果中添加具体文言文字
    # 查找"显示文言"但没有具体内容的地方，根据信号描述列补充
    lines = optimized_content.split('\n')
    optimized_lines = []
    
    for i, line in enumerate(lines):
        if '|' in line and '预期结果' in lines[max(0, i-3):i+1]:
            # 这是表格行，检查是否有文言信号但没有具体文言
            if 'HAVPFunctTextDisp' in line:
                # 提取信号值
                matches = re.findall(r'0[xX]([0-9A-Fa-f]+)', line)
                for hex_val in matches:
                    hex_upper = hex_val.upper()
                    text = None
                    for key, value in havp_mapping.items():
                        if f"0x{hex_upper}" in key.upper() or f"0X{hex_upper}" in key.upper():
                            text = value
                            break
                    
                    if text and '显示文言' in line and text not in line:
                        # 尝试补充具体文言到预期结果列
                        # 注意：这里需要谨慎处理，避免重复添加
                        pass
        
        optimized_lines.append(line)
    
    optimized_content = '\n'.join(optimized_lines)
    
    print(f"\n✅ 优化完成，共替换了{len(replacements)}处文言信号")
    if replacements:
        print(f"\n替换示例（前10条）：")
        for i, (signal, hex_val, text) in enumerate(replacements[:10]):
            print(f"  {i+1}. 0x{hex_val} → \"{text}\"")
    
    return optimized_content, replacements

def main():
    """主函数"""
    print("="*80)
    print("测试用例文言信号优化工具")
    print("="*80)
    
    # 加载映射表
    print("\n1. 加载文言映射表...")
    havp_mapping, popup_mapping = load_text_mappings()
    print(f"✅ 加载{len(havp_mapping)}条HAVPFunctTextDisp映射")
    print(f"✅ 加载{len(popup_mapping)}条PopupDisp映射")
    
    # 读取测试用例文档
    input_file = "新增用例/VLA泊车HMI交互测试用例_完整版.md"
    print(f"\n2. 读取测试用例文档...")
    with open(input_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    print(f"✅ 文档大小：{len(md_content)}字符，{len(md_content.split(chr(10)))}行")
    
    # 优化内容
    print(f"\n3. 优化文言信号...")
    optimized_content, replacements = optimize_test_case_text(md_content, havp_mapping, popup_mapping)
    
    # 写入优化后的文档
    output_file = "新增用例/VLA泊车HMI交互测试用例_完整优化版.md"
    print(f"\n4. 保存优化后的文档...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(optimized_content)
    
    print(f"\n{'='*80}")
    print(f"✅ 优化完成！")
    print(f"{'='*80}")
    print(f"输出文件：{output_file}")
    print(f"优化后大小：{len(optimized_content)}字符")
    print(f"替换信号数：{len(replacements)}处")
    
    return output_file

if __name__ == "__main__":
    os.chdir("/home/wangqian/Documents/hmi-testcase-auto-generation")
    main()

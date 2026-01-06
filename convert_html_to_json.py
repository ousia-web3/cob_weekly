import json
import os
import sys

def extract_dashboard_data(html_path, output_json_path):
    print(f"Reading HTML file: {html_path}")
    if not os.path.exists(html_path):
        print(f"Error: File not found: {html_path}")
        return

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    start_marker = 'const dashboardData ='
    start_idx = content.find(start_marker)
    if start_idx == -1:
        print("Error: Could not find dashboardData start")
        return

    # Find the start of the JSON object
    start_brace = content.find('{', start_idx)
    if start_brace == -1:
        print("Error: Could not find start brace")
        return

    # Use brace counting to find the matching end brace
    balance = 0
    end_brace = -1
    for i in range(start_brace, len(content)):
        char = content[i]
        if char == '{':
            balance += 1
        elif char == '}':
            balance -= 1
            if balance == 0:
                end_brace = i
                break

    if end_brace == -1:
        print("Error: Could not find matching end brace")
        return

    json_str = content[start_brace:end_brace+1]
    
    try:
        data = json.loads(json_str)
        print("Successfully parsed JSON data.")
        
        # Save to JSON file
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Successfully saved JSON to: {output_json_path}")
        
        # Verification: Print keys to show what was extracted
        print("Extracted keys:", list(data.keys()))
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")

if __name__ == "__main__":
    html_file = r"c:\Users\HANA\Desktop\cob_weekly\data\html\2025년 12월 3주차 주간 UV 레포트현황_20251223_162836.html"
    json_filename = os.path.basename(html_file).replace('.html', '.json')
    output_dir = r"c:\Users\HANA\Desktop\cob_weekly\data\json"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_file = os.path.join(output_dir, json_filename)
    
    extract_dashboard_data(html_file, output_file)

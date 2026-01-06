import os
import json
import re
from datetime import datetime

def migrate_history():
    email_dir = os.path.join(os.getcwd(), 'data', 'email')
    history_file = os.path.join(os.getcwd(), 'data', 'email_history.json')
    
    if not os.path.exists(email_dir):
        print("이메일 데이터 폴더가 없습니다.")
        return

    # 기존 히스토리 로드
    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
    else:
        history = []
        
    existing_paths = {item.get('html_path') for item in history}
    
    files = [f for f in os.listdir(email_dir) if f.endswith('.html')]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(email_dir, x)), reverse=True)
    
    added_count = 0
    
    for filename in files:
        filepath = os.path.join(email_dir, filename)
        
        # 이미 히스토리에 있으면 건너뜀
        if filepath in existing_paths:
            continue
            
        stat = os.stat(filepath)
        sent_at = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        
        # 파일명 파싱
        # 예: email_2025년 12월 1주차 트래픽 현황 보고_20251209_142211.html
        name_parts = filename.replace('email_', '').replace('.html', '').split('_')
        
        if len(name_parts) >= 3:
            # 마지막 두 부분은 날짜/시간이라고 가정
            title = "_".join(name_parts[:-2])
        else:
            title = filename.replace('.html', '')
            
        # ID 생성 (타임스탬프 + 인덱스)
        file_timestamp = datetime.fromtimestamp(stat.st_mtime).strftime('%Y%m%d%H%M%S')
        entry_id = f"{file_timestamp}{added_count:03d}"
        
        entry = {
            "id": entry_id,
            "date": sent_at,
            "subject": title,
            "recipients": ["(기존 발송 내역)"],
            "status": "success",
            "message": "기존 파일에서 복원됨",
            "html_path": filepath
        }
        
        history.append(entry)
        added_count += 1
        
    # 날짜순 정렬 (최신순)
    history.sort(key=lambda x: x['date'], reverse=True)
    
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
        
    print(f"✅ {added_count}개의 기존 이메일 내역을 복원했습니다.")

if __name__ == "__main__":
    migrate_history()

import os
import sys
import logging
from datetime import datetime
from email_service import EmailService

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    service = EmailService()
    
    # 1. HTML 리포트 파일 경로 확인
    # generate_email_report.py가 생성하는 경로 확인
    # 우선 순위: 1. 현재 디렉토리의 email_report_sample.html 2. 하드코딩된 경로 (레거시 지원)
    
    report_filename = 'email_report_sample.html'
    candidates = [
        os.path.join(os.getcwd(), report_filename), # 현재 프로젝트 루트
        r"c:\Users\HANA\Desktop\cob_weekly\email_report_sample.html", # 기존 스크립트 경로
        os.path.join(os.getcwd(), 'data', 'email', report_filename) # data/email 경로
    ]
    
    html_path = None
    for path in candidates:
        if os.path.exists(path):
            html_path = path
            break
            
    if not html_path:
        logger.error("❌ 이메일 리포트 파일을 찾을 수 없습니다. (email_report_sample.html)")
        print("Tip: generate_email_report.py를 먼저 실행하여 리포트를 생성해주세요.")
        return

    logger.info(f"📄 리포트 파일 확인됨: {html_path}")

    # 2. HTML 내용 읽기
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        logger.error(f"❌ 파일 읽기 실패: {e}")
        return

    # 3. 제목 추출 (HTML 타이틀 태그 또는 기본값)
    import re
    title_match = re.search(r'<title>(.*?)</title>', html_content)
    if title_match:
        subject = title_match.group(1)
    else:
        # 날짜 기반 제목 생성
        now = datetime.now()
        subject = f"{now.year}년 {now.month}월 {now.day}일 주간 트래픽 현황 보고"

    logger.info(f"📧 메일 제목: {subject}")

    # 4. 수신자 확인 및 발송
    # .env 또는 저장된 수신자 목록 사용
    recipients = service.get_recipients()
    active_recipients = [r['email'] for r in recipients if r.get('active', True)]
    
    if not active_recipients:
        logger.warning("⚠️ 저장된 수신자가 없습니다. .env 파일에서 가져오기를 시도합니다.")
        service.import_from_env()
        recipients = service.get_recipients()
        active_recipients = [r['email'] for r in recipients if r.get('active', True)]
        
    if not active_recipients:
        logger.error("❌ 발송할 수신자가 없습니다. .env 파일의 EMAIL_RECIPIENTS를 확인하거나 수신자를 추가해주세요.")
        return

    print(f"📨 발송 대상: {len(active_recipients)}명 ({', '.join(active_recipients)})")
    
    # 발송 확인
    # confirm = input("정말로 발송하시겠습니까? (y/n): ")
    # if confirm.lower() != 'y':
    #     print("취소되었습니다.")
    #     return

    # 5. 이메일 발송 
    # (주의: 실제 발송됨)
    success, message = service.send_email(subject, html_content, active_recipients, html_path)
    
    if success:
        logger.info(f"✅ {message}")
    else:
        logger.error(f"❌ {message}")

if __name__ == "__main__":
    main()

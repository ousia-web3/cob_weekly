import os
import re
import json
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        load_dotenv()
        self.sender_email = os.getenv('EMAIL_SENDER')
        self.sender_password = os.getenv('EMAIL_PASSWORD')
        self.smtp_server = os.getenv('SMTP_SERVER')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.recipients_file = os.path.join(os.getcwd(), 'data', 'recipients.json')
        self.history_file = os.path.join(os.getcwd(), 'data', 'email_history.json')
        
        # Microsoft 계정 자동 감지
        if self.sender_email and ('@outlook.com' in self.sender_email or '@hotmail.com' in self.sender_email or '@hanatour.com' in self.sender_email):
            self.smtp_server = 'smtp-mail.outlook.com'
            self.smtp_port = 587
            logger.info("Microsoft 계정 SMTP 설정 사용")

        self._ensure_data_dir()

    def _ensure_data_dir(self):
        """데이터 디렉토리 및 파일 확인"""
        os.makedirs(os.path.dirname(self.recipients_file), exist_ok=True)
        if not os.path.exists(self.recipients_file):
            self.save_recipients([])
        if not os.path.exists(self.history_file):
            self.save_history([])

    def get_recipients(self):
        """수신자 목록 조회"""
        try:
            with open(self.recipients_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"수신자 목록 로드 실패: {e}")
            return []

    def save_recipients(self, recipients):
        """수신자 목록 저장"""
        try:
            with open(self.recipients_file, 'w', encoding='utf-8') as f:
                json.dump(recipients, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"수신자 목록 저장 실패: {e}")
            return False

    def get_history(self):
        """발송 이력 조회"""
        try:
            if not os.path.exists(self.history_file):
                return []
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"발송 이력 로드 실패: {e}")
            return []

    def save_history(self, history):
        """발송 이력 저장"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"발송 이력 저장 실패: {e}")
            return False

    def add_history_entry(self, subject, recipients, status, message, html_path=None):
        """이력 추가"""
        history = self.get_history()
        entry = {
            "id": datetime.now().strftime('%Y%m%d%H%M%S%f'),
            "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "subject": subject,
            "recipients": recipients,
            "status": status, # 'success' or 'fail'
            "message": message,
            "html_path": html_path
        }
        history.insert(0, entry) # 최신순 정렬
        self.save_history(history)
        return entry

    def add_recipient(self, email):
        """수신자 추가"""
        recipients = self.get_recipients()
        # 중복 확인
        if any(r['email'] == email for r in recipients):
            return False, "이미 존재하는 이메일입니다."
        
        recipients.append({
            "email": email,
            "added_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "active": True
        })
        
        if self.save_recipients(recipients):
            return True, "수신자가 추가되었습니다."
        return False, "저장 중 오류가 발생했습니다."

    def remove_recipient(self, email):
        """수신자 삭제"""
        recipients = self.get_recipients()
        initial_len = len(recipients)
        recipients = [r for r in recipients if r['email'] != email]
        
        if len(recipients) < initial_len:
            if self.save_recipients(recipients):
                return True, "수신자가 삭제되었습니다."
            return False, "저장 중 오류가 발생했습니다."
        return False, "해당 이메일을 찾을 수 없습니다."

    def send_email(self, subject, html_content, recipients=None, html_path=None):
        """이메일 발송"""
        if not self.sender_email or not self.sender_password:
            return False, "SMTP 설정이 누락되었습니다 (.env 확인 필요)"

        if recipients is None:
            # 활성 수신자만 필터링
            all_recipients = self.get_recipients()
            recipients = [r['email'] for r in all_recipients if r.get('active', True)]

        if not recipients:
            return False, "발송할 수신자가 없습니다."

        try:
            # SMTP 서버 연결
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)

            success_count = 0
            fail_count = 0

            # 개별 발송 (또는 숨은참조 사용 가능, 여기서는 개별 발송 처리)
            for recipient in recipients:
                try:
                    msg = MIMEMultipart()
                    msg['From'] = self.sender_email
                    msg['To'] = recipient
                    msg['Subject'] = subject
                    
                    msg.attach(MIMEText(html_content, 'html'))
                    
                    server.send_message(msg)
                    success_count += 1
                except Exception as e:
                    logger.error(f"이메일 발송 실패 ({recipient}): {e}")
                    fail_count += 1

            server.quit()
            
            result_message = f"발송 완료: 성공 {success_count}건, 실패 {fail_count}건"
            status = 'success' if success_count > 0 else 'fail'
            
            # 이력 저장
            self.add_history_entry(subject, recipients, status, result_message, html_path)
            
            return True, result_message

        except Exception as e:
            logger.error(f"SMTP 연결/발송 오류: {e}")
            error_msg = f"이메일 발송 중 오류 발생: {str(e)}"
            self.add_history_entry(subject, recipients, 'fail', error_msg, html_path)
            return False, error_msg

    def resend_email(self, history_id):
        """이메일 재발송"""
        history = self.get_history()
        entry = next((item for item in history if item['id'] == history_id), None)
        
        if not entry:
            return False, "해당 발송 이력을 찾을 수 없습니다."
            
        if not entry.get('html_path') or not os.path.exists(entry['html_path']):
            return False, "원본 HTML 파일을 찾을 수 없습니다."
            
        try:
            with open(entry['html_path'], 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # 수신자 확인 및 폴백 로직
            recipients = entry.get('recipients', [])
            
            # 수신자가 없거나, 유효하지 않은 형식(마이그레이션 데이터 등)인 경우
            use_current_recipients = False
            if not recipients:
                use_current_recipients = True
            elif isinstance(recipients, list) and len(recipients) > 0:
                # 첫 번째 수신자가 이메일 형식이 아니면 (예: "(기존 발송 내역)")
                if '@' not in recipients[0]:
                    use_current_recipients = True
            
            if use_current_recipients:
                logger.info(f"재발송: 저장된 수신자 정보가 유효하지 않아 현재 활성 수신자 목록을 사용합니다. (ID: {history_id})")
                all_recipients = self.get_recipients()
                recipients = [r['email'] for r in all_recipients if r.get('active', True)]
                
                if not recipients:
                    return False, "발송할 수신자가 없습니다. (저장된 수신자 없음 & 현재 수신자 없음)"
            
            return self.send_email(
                subject=f"[재발송] {entry['subject']}",
                html_content=html_content,
                recipients=recipients,
                html_path=entry['html_path'] # 원본 경로 유지
            )
        except Exception as e:
            return False, f"재발송 중 오류 발생: {str(e)}"

    def save_email_html(self, html_content, title):
        """생성된 HTML을 data/email 폴더에 저장"""
        try:
            email_dir = os.path.join(os.getcwd(), 'data', 'email')
            os.makedirs(email_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # 제목을 파일명에 안전하게 변환
            safe_title = re.sub(r'[\\/*?:"<>|]', "", title)
            filename = f"email_{safe_title}_{timestamp}.html"
            
            filepath = os.path.join(email_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            return filepath
        except Exception as e:
            logger.error(f"HTML 저장 실패: {e}")
            return None

    def get_env_recipients(self):
        """ENV 파일에서 수신자 목록 읽기"""
        try:
            env_path = os.path.join(os.getcwd(), '.env')
            if not os.path.exists(env_path):
                return []
            
            recipients = []
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # EMAIL_RECIPIENTS= 로 시작하는 줄 찾기
                    if line.startswith('EMAIL_RECIPIENTS='):
                        # = 이후의 값 추출
                        value = line.split('=', 1)[1].strip()
                        # 쉼표로 구분된 이메일 추출
                        if value:
                            emails = [e.strip() for e in value.split(',') if e.strip()]
                            recipients.extend(emails)
                        break
            
            return recipients
        except Exception as e:
            logger.error(f"ENV 파일 읽기 실패: {e}")
            return []

    def sync_to_env(self):
        """현재 수신자 목록을 .env 파일에 동기화"""
        try:
            env_path = os.path.join(os.getcwd(), '.env')
            recipients = self.get_recipients()
            
            # 활성 수신자만 추출
            active_emails = [r['email'] for r in recipients if r.get('active', True)]
            recipients_str = ','.join(active_emails)
            
            # .env 파일 읽기
            if os.path.exists(env_path):
                with open(env_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            else:
                lines = []
            
            # EMAIL_RECIPIENTS 라인 찾아서 업데이트
            found = False
            for i, line in enumerate(lines):
                if line.strip().startswith('EMAIL_RECIPIENTS='):
                    lines[i] = f'EMAIL_RECIPIENTS={recipients_str}\n'
                    found = True
                    break
            
            # 없으면 추가
            if not found:
                lines.append(f'\nEMAIL_RECIPIENTS={recipients_str}\n')
            
            # .env 파일 쓰기
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            return True, f"{len(active_emails)}명의 수신자가 .env 파일에 동기화되었습니다."
        except Exception as e:
            logger.error(f".env 동기화 실패: {e}")
            return False, f"동기화 실패: {str(e)}"

    def import_from_env(self, overwrite=False):
        """ENV 파일에서 수신자 가져오기"""
        try:
            env_emails = self.get_env_recipients()
            
            if not env_emails:
                return False, ".env 파일에 수신자 정보가 없습니다."
            
            if overwrite:
                # 기존 목록 삭제하고 새로 추가
                new_recipients = []
                for email in env_emails:
                    new_recipients.append({
                        "email": email,
                        "added_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "active": True
                    })
                self.save_recipients(new_recipients)
                return True, f"{len(env_emails)}명의 수신자를 가져왔습니다. (기존 목록 삭제됨)"
            else:
                # 기존 목록에 추가 (중복 제외)
                current_recipients = self.get_recipients()
                current_emails = {r['email'] for r in current_recipients}
                
                added_count = 0
                for email in env_emails:
                    if email not in current_emails:
                        current_recipients.append({
                            "email": email,
                            "added_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            "active": True
                        })
                        added_count += 1
                
                self.save_recipients(current_recipients)
                return True, f"{added_count}명의 새로운 수신자를 추가했습니다. (중복 {len(env_emails) - added_count}명 제외)"
                
        except Exception as e:
            logger.error(f"ENV 가져오기 실패: {e}")
            return False, f"가져오기 실패: {str(e)}"


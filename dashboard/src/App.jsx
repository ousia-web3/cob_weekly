import React, { useState, useCallback } from 'react';
import GeneratorControls from './components/GeneratorControls';
import DashboardPreview from './components/DashboardPreview';
import { ErrorBoundary } from './components/ErrorBoundary';
import EmailBodyEditor from './components/EmailBodyEditor';
import EmailHistory from './components/EmailHistory';
import { parseExcel } from './utils/excelParser';
import { downloadJSON, generateDashboardHTML } from './utils/exportUtils';
import { Download, Save, Mail, Users, FileText } from 'lucide-react';

function App() {
  // API URL을 현재 호스트네임에 맞춰 동적으로 설정 (localhost 또는 IP)
  const API_BASE_URL = `http://${window.location.hostname}:8001`;

  const [dashboardData, setDashboardData] = useState(null);
  const [status, setStatus] = useState(null); // { type: 'success' | 'error' | 'loading', message: string }
  const [titleConfig, setTitleConfig] = useState({ year: 2025, month: 12, week: 1, title: '', dateRange: '' });
  
  // 메일 본문 에디터 상태
  const [emailBodyEnabled, setEmailBodyEnabled] = useState(false);
  const [emailBodyContent, setEmailBodyContent] = useState('');

  const handleTitleChange = useCallback((config) => {
    setTitleConfig(config);
    setDashboardData(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        meta: {
          ...prev.meta,
          year: config.year,
          month: config.month,
          weekNumber: config.week,
          title: config.title,
          range: config.dateRange
        }
      };
    });
  }, []);

  const handleDataUpload = async (file) => {
    // 진행률 시뮬레이션
    let progress = 0;
    setStatus({ type: 'loading', message: '데이터 분석 및 AI 요약 생성 중입니다...', progress: 0 });
    
    // 진행률 업데이트 (시뮬레이션)
    const progressInterval = setInterval(() => {
      progress += Math.random() * 15;
      if (progress > 90) progress = 90; // 90%까지만 자동 증가
      setStatus({ type: 'loading', message: '데이터 분석 및 AI 요약 생성 중입니다...', progress: Math.floor(progress) });
    }, 500);
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server Error: ${response.statusText}`);
      }

      const data = await response.json();
      
      // 완료 시 100%
      clearInterval(progressInterval);
      setStatus({ type: 'loading', message: '데이터 분석 및 AI 요약 생성 중입니다...', progress: 100 });
      
      // Merge with current title config
      data.meta = {
        ...data.meta,
        year: titleConfig.year,
        month: titleConfig.month,
        weekNumber: titleConfig.week,
        title: titleConfig.title,
        range: titleConfig.dateRange
      };
      
      setDashboardData(data);
      
      // 잠시 후 성공 메시지
      setTimeout(() => {
        setStatus({ type: 'success', message: '분석 및 요약 생성이 완료되었습니다.' });
      }, 300);
    } catch (error) {
      clearInterval(progressInterval);
      console.error(error);
      setStatus({ type: 'error', message: `오류 발생: ${error.message}` });
    }
  };

  const handleExportHTML = async () => {
    if (!dashboardData) return;
    
    try {
      const htmlContent = generateDashboardHTML(dashboardData);
      
      // 1. 서버에 HTML 저장
      try {
        const response = await fetch(`${API_BASE_URL}/save-html`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            title: dashboardData.meta.title,
            html: htmlContent
          })
        });
        
        const result = await response.json();
        if (result.success) {
          console.log(`✓ 서버 저장 완료: ${result.filepath}`);
        }
      } catch (serverError) {
        console.error('서버 저장 실패:', serverError);
        // 서버 저장 실패해도 클라이언트 다운로드는 진행
      }
      
      // 2. 브라우저 다운로드 제공
      const blob = new Blob([htmlContent], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${dashboardData.meta.title}.html`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      alert('파일이 저장되었습니다. (서버 저장 + 로컬 다운로드)');
      
    } catch (error) {
      console.error('HTML 생성 오류:', error);
      alert('HTML 생성 중 오류가 발생했습니다.');
    }
  };

  const handleSaveJSON = async () => {
    if (!dashboardData) return;
    
    try {
      // 1. 서버에 JSON 저장
      try {
        const response = await fetch(`${API_BASE_URL}/save-json`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(dashboardData)
        });
        
        const result = await response.json();
        if (result.success) {
          console.log(`✓ 서버 저장 완료: ${result.filepath}`);
        }
      } catch (serverError) {
        console.error('서버 저장 실패:', serverError);
        // 서버 저장 실패해도 클라이언트 다운로드는 진행
      }
      
      // 2. 브라우저 다운로드 제공
      downloadJSON(dashboardData, `${dashboardData.meta.title}.json`);
      
      alert('파일이 저장되었습니다. (서버 저장 + 로컬 다운로드)');
      
    } catch (error) {
      console.error('JSON 저장 오류:', error);
      alert('JSON 저장 중 오류가 발생했습니다.');
    }
  };

  const handleSendEmail = async () => {
    if (!dashboardData) return;
    if (!confirm('현재 대시보드 내용으로 이메일을 발송하시겠습니까?\n(수신자 관리 메뉴에서 수신자를 먼저 확인해주세요)')) return;

    try {
      setStatus({ type: 'loading', message: '이메일 발송 중입니다...' });
      
      // emailBody가 활성화된 경우 데이터에 포함
      const dataToSend = {
        ...dashboardData,
        emailBody: emailBodyEnabled && emailBodyContent ? emailBodyContent : null
      };
      
      const response = await fetch(`${API_BASE_URL}/send-email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(dataToSend)
      });
      
      const result = await response.json();
      
      if (result.status === 'success') {
        alert(result.message);
        setStatus({ type: 'success', message: '이메일 발송이 완료되었습니다.' });
      } else {
        alert(`발송 실패: ${result.message}`);
        setStatus({ type: 'error', message: `이메일 발송 실패: ${result.message}` });
      }
    } catch (error) {
      console.error('이메일 발송 오류:', error);
      alert('이메일 발송 중 오류가 발생했습니다.');
      setStatus({ type: 'error', message: `이메일 발송 오류: ${error.message}` });
    }
  };

  const handleInsightsChange = (newInsights) => {
    setDashboardData(prev => ({
      ...prev,
      aiInsight: newInsights
    }));
  };

  const handleRegenerateInsights = async () => {
    if (!dashboardData || !dashboardData.aiContext) {
      alert('재생성에 필요한 데이터 컨텍스트가 없습니다. 파일을 다시 업로드해주세요.');
      return;
    }

    if (!confirm('핵심 요약을 다시 생성하시겠습니까? 기존 내용은 덮어씌워집니다.')) return;

    setStatus({ type: 'loading', message: '핵심 요약을 재생성 중입니다...' });

    try {
      const response = await fetch(`${API_BASE_URL}/regenerate-summary`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(dashboardData.aiContext)
      });

      if (!response.ok) {
        throw new Error(`Server Error: ${response.statusText}`);
      }

      const result = await response.json();
      
      setDashboardData(prev => ({
        ...prev,
        aiInsight: result.insights
      }));
      
      setStatus({ type: 'success', message: '핵심 요약이 재생성되었습니다.' });
    } catch (error) {
      console.error('Regeneration Error:', error);
      setStatus({ type: 'error', message: `재생성 오류: ${error.message}` });
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="w-full px-4 py-8">
        <header className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">코브랜드 주간 현황 대시보드 생성기</h1>
            <p className="text-slate-500 mt-2">엑셀 데이터를 업로드하여 주간 보고서를 생성하세요.</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => window.open(`${API_BASE_URL}/recipients`, '_blank')}
              className="flex items-center gap-2 px-4 py-2 bg-white text-indigo-600 border border-indigo-200 rounded-lg hover:bg-indigo-50 font-medium transition-colors shadow-sm"
            >
              <Users className="w-4 h-4" />
              수신자 관리
            </button>
            <button
              onClick={() => window.open(`${API_BASE_URL}/prompt-manager`, '_blank')}
              className="flex items-center gap-2 px-4 py-2 bg-white text-indigo-600 border border-indigo-200 rounded-lg hover:bg-indigo-50 font-medium transition-colors shadow-sm"
            >
              <FileText className="w-4 h-4" />
              프롬프트 관리
            </button>
          </div>
        </header>

        <GeneratorControls 
          onDataUpload={handleDataUpload}
          onTitleChange={handleTitleChange}
          status={status}
        />

        {dashboardData && (
          <div className="flex justify-end gap-3 mb-4">
            <button 
              onClick={handleSaveJSON}
              className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-300 rounded-lg text-slate-700 hover:bg-slate-50 font-medium transition-colors shadow-sm"
            >
              <Save className="w-4 h-4" />
              JSON 저장
            </button>
            <button 
              onClick={handleExportHTML}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium transition-colors shadow-sm"
            >
              <Download className="w-4 h-4" />
              대시보드 생성
            </button>
            <button 
              onClick={handleSendEmail}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium transition-colors shadow-sm"
            >
              <Mail className="w-4 h-4" />
              이메일 발송
            </button>
          </div>
        )}

        {/* 메일 본문 에디터 섹션 */}
        {dashboardData && (
          <div className="mt-6 mb-6">
            <div className="flex items-center gap-3 mb-3 px-4">
              <input
                type="checkbox"
                id="emailBodyToggle"
                checked={emailBodyEnabled}
                onChange={(e) => setEmailBodyEnabled(e.target.checked)}
                className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
              />
              <label htmlFor="emailBodyToggle" className="text-sm font-medium text-slate-700 cursor-pointer">
                메일 본문 추가 (선택 사항)
              </label>
            </div>
            <EmailBodyEditor
              value={emailBodyContent}
              onChange={setEmailBodyContent}
              enabled={emailBodyEnabled}
            />
          </div>
        )}

        <div className="mt-8 border-t border-slate-200 pt-8">
          <h2 className="text-xl font-bold mb-4 text-slate-800 px-4">미리보기</h2>
          <div className="border border-slate-200 rounded-xl overflow-hidden shadow-lg bg-white">
            <ErrorBoundary>
              <DashboardPreview 
                data={dashboardData} 
                onInsightsChange={handleInsightsChange}
                onRegenerateInsights={handleRegenerateInsights}
              />
            </ErrorBoundary>
          </div>
        </div>

        {/* 이메일 발송 이력 섹션 */}
        <div className="mt-8 mb-8">
          <EmailHistory />
        </div>
      </div>
    </div>
  );
}

export default App;

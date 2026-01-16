import React, { useState, useCallback } from 'react';
import GeneratorControls from './components/GeneratorControls';
import DashboardPreview from './components/DashboardPreview';
import { parseExcel } from './utils/excelParser';
import { downloadJSON, generateDashboardHTML } from './utils/exportUtils';
import { Download, Save } from 'lucide-react';

function App() {
  // API URL을 현재 호스트네임에 맞춰 동적으로 설정 (localhost 또는 IP)
  // API URL을 Proxy를 통해 처리하므로 상대 경로 사용
  const API_BASE_URL = '';

  const [dashboardData, setDashboardData] = useState(null);
  const [status, setStatus] = useState(null); // { type: 'success' | 'error' | 'loading', message: string }
  const [titleConfig, setTitleConfig] = useState({ year: 2025, month: 12, week: 1, title: '' });

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
          title: config.title
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
        title: titleConfig.title
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
      
      // 서버에 HTML 저장
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
        alert(`✓ HTML 파일이 저장되었습니다!\n위치: ${result.filepath}`);
      }
      
      // 브라우저 다운로드도 함께 제공
      const blob = new Blob([htmlContent], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${dashboardData.meta.title}.html`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
    } catch (error) {
      console.error('HTML 저장 오류:', error);
      alert('HTML 저장 중 오류가 발생했습니다.');
    }
  };

  const handleSaveJSON = async () => {
    if (!dashboardData) return;
    
    try {
      // 서버에 JSON 저장
      const response = await fetch(`${API_BASE_URL}/save-json`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(dashboardData)
      });
      
      const result = await response.json();
      
      if (result.success) {
        alert(`✓ JSON 파일이 저장되었습니다!\n위치: ${result.filepath}`);
      }
      
      // 브라우저 다운로드도 함께 제공
      downloadJSON(dashboardData, `${dashboardData.meta.title}.json`);
      
    } catch (error) {
      console.error('JSON 저장 오류:', error);
      alert('JSON 저장 중 오류가 발생했습니다.');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="w-full px-4 py-8">
        <header className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-slate-900">코브랜드 주간 현황 대시보드 생성기</h1>
          <p className="text-slate-500 mt-2">엑셀 데이터를 업로드하여 주간 보고서를 생성하세요.</p>
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
              대시보드 생성 (HTML)
            </button>
          </div>
        )}

        <div className="mt-8 border-t border-slate-200 pt-8">
          <h2 className="text-xl font-bold mb-4 text-slate-800 px-4">미리보기</h2>
          <div className="border border-slate-200 rounded-xl overflow-hidden shadow-lg bg-white">
            <DashboardPreview data={dashboardData} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;

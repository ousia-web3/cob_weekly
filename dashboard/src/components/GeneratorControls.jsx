import React, { useState, useEffect } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react';

const GeneratorControls = ({ onDataUpload, onSummaryUpload, onTitleChange, status }) => {
  const [year, setYear] = useState(new Date().getFullYear());
  const [month, setMonth] = useState(new Date().getMonth() + 1);
  const [week, setWeek] = useState(1);
  const [autoTitle, setAutoTitle] = useState('');

  useEffect(() => {
    const title = `${year}년 ${month}월 ${week}주차 주간 UV 레포트현황`;
    setAutoTitle(title);
    onTitleChange({ year, month, week, title });
  }, [year, month, week, onTitleChange]);

  const handleDataUpload = (e) => {
    const file = e.target.files[0];
    if (file) onDataUpload(file);
  };

  const handleSummaryUpload = (e) => {
    const file = e.target.files[0];
    if (file) onSummaryUpload(file);
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md mb-6">
      <h2 className="text-xl font-bold mb-4 text-gray-800">대시보드 생성 설정</h2>
      
      {/* Title Configuration */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">연도</label>
          <select 
            value={year} 
            onChange={(e) => setYear(Number(e.target.value))}
            className="w-full border border-gray-300 rounded-md p-2 focus:ring-indigo-500 focus:border-indigo-500"
          >
            {[2025, 2026, 2027, 2028, 2029, 2030].map(y => (
              <option key={y} value={y}>{y}년</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">월</label>
          <select 
            value={month} 
            onChange={(e) => setMonth(Number(e.target.value))}
            className="w-full border border-gray-300 rounded-md p-2 focus:ring-indigo-500 focus:border-indigo-500"
          >
            {Array.from({ length: 12 }, (_, i) => i + 1).map(m => (
              <option key={m} value={m}>{m}월</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">주차</label>
          <select 
            value={week} 
            onChange={(e) => setWeek(Number(e.target.value))}
            className="w-full border border-gray-300 rounded-md p-2 focus:ring-indigo-500 focus:border-indigo-500"
          >
            {[1, 2, 3, 4, 5].map(w => (
              <option key={w} value={w}>{w}주차</option>
            ))}
          </select>
        </div>
      </div>

      <div className="mb-6 p-3 bg-gray-50 rounded-md border border-gray-200">
        <span className="text-sm text-gray-500 mr-2">자동 생성 타이틀:</span>
        <span className="font-bold text-indigo-600">{autoTitle}</span>
      </div>

      {/* File Uploads */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">주간 데이터 파일 업로드 (.xlsx)</label>
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:bg-gray-50 transition-colors relative">
          <input 
            type="file" 
            accept=".xlsx, .csv"
            onChange={handleDataUpload}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          <div className="flex flex-col items-center pointer-events-none">
            <Upload className="w-12 h-12 text-indigo-400 mb-3" />
            <p className="text-gray-600 font-medium">클릭하거나 파일을 드래그하여 업로드하세요</p>
            <p className="text-gray-400 text-sm mt-1">자동으로 분석 및 AI 요약이 생성됩니다.</p>
          </div>
        </div>
      </div>

      {/* Status Display */}
      {status && (
        <div className={`mt-4 p-4 rounded-md ${
          status.type === 'success' ? 'bg-green-50 border border-green-200' : 
          status.type === 'error' ? 'bg-red-50 border border-red-200' : 
          'bg-blue-50 border border-blue-200'
        }`}>
          <div className="flex items-center mb-2">
            {status.type === 'success' ? <CheckCircle className="w-5 h-5 mr-2 text-green-600" /> : 
             status.type === 'error' ? <AlertCircle className="w-5 h-5 mr-2 text-red-600" /> : 
             <div className="w-5 h-5 mr-2 animate-spin rounded-full border-2 border-blue-600 border-t-transparent"></div>}
            <span className={`text-sm font-medium ${
              status.type === 'success' ? 'text-green-700' : 
              status.type === 'error' ? 'text-red-700' : 
              'text-blue-700'
            }`}>{status.message}</span>
          </div>
          
          {/* Progress Bar */}
          {status.type === 'loading' && status.progress !== undefined && (
            <div className="mt-3">
              <div className="flex justify-between items-center mb-1">
                <span className="text-xs text-blue-600 font-medium">진행률</span>
                <span className="text-xs text-blue-600 font-bold">{status.progress}%</span>
              </div>
              <div className="w-full bg-blue-100 rounded-full h-2.5 overflow-hidden">
                <div 
                  className="bg-blue-600 h-2.5 rounded-full transition-all duration-300 ease-out"
                  style={{ width: `${status.progress}%` }}
                ></div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default GeneratorControls;

import React, { useState, useEffect } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle, Calendar } from 'lucide-react';

const GeneratorControls = ({ onDataUpload, onSummaryUpload, onTitleChange, status }) => {
  const [year, setYear] = useState(new Date().getFullYear());
  const [month, setMonth] = useState(new Date().getMonth() + 1);
  const [week, setWeek] = useState(1);
  const [autoTitle, setAutoTitle] = useState('');
  
  // Date Range State
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [dateRangeText, setDateRangeText] = useState('');

  // Helper to format date as YYYY.MM.DD
  const formatDate = (date) => {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}.${m}.${d}`;
  };

  // Helper to format date as YYYY-MM-DD for input type="date"
  const formatDateForInput = (date) => {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  };

  useEffect(() => {
    // Calculate Date Range based on Year, Month, Week
    // Logic: Find the 1st day of the month. Find the Monday of that week. Add (Week-1)*7 days.
    const firstDayOfMonth = new Date(year, month - 1, 1);
    const dayOfWeek = firstDayOfMonth.getDay(); // 0=Sun, 1=Mon, ...
    
    // Calculate offset to get to the Monday of the week containing the 1st
    // If 1st is Mon(1), offset 0. If Tue(2), offset -1. ... If Sun(0), offset -6.
    const diffToMon = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
    
    const week1Mon = new Date(firstDayOfMonth);
    week1Mon.setDate(firstDayOfMonth.getDate() + diffToMon);
    
    const start = new Date(week1Mon);
    start.setDate(week1Mon.getDate() + (week - 1) * 7);
    
    const end = new Date(start);
    end.setDate(start.getDate() + 6); // Sunday
    
    const startStr = formatDate(start);
    const endStr = formatDate(end);
    const rangeText = `${startStr} ~ ${endStr}`;
    
    setStartDate(formatDateForInput(start));
    setEndDate(formatDateForInput(end));
    setDateRangeText(rangeText);

    const title = `[${year}년 ${month}월 ${week}주차] 코브랜드채널 주요 영역별 UV 레포트 공유`;
    setAutoTitle(title);
    
    // Pass dateRangeText to parent
    onTitleChange({ year, month, week, title, dateRange: rangeText });
  }, [year, month, week, onTitleChange]);

  const handleDateRangeTextChange = (e) => {
    setDateRangeText(e.target.value);
    onTitleChange({ year, month, week, title: autoTitle, dateRange: e.target.value });
  };

  const handleStartDateChange = (e) => {
    const newStart = e.target.value;
    setStartDate(newStart);
    if (newStart && endDate) {
      const startObj = new Date(newStart);
      const endObj = new Date(endDate);
      const rangeText = `${formatDate(startObj)} ~ ${formatDate(endObj)}`;
      setDateRangeText(rangeText);
      onTitleChange({ year, month, week, title: autoTitle, dateRange: rangeText });
    }
  };

  const handleEndDateChange = (e) => {
    const newEnd = e.target.value;
    setEndDate(newEnd);
    if (startDate && newEnd) {
      const startObj = new Date(startDate);
      const endObj = new Date(newEnd);
      const rangeText = `${formatDate(startObj)} ~ ${formatDate(endObj)}`;
      setDateRangeText(rangeText);
      onTitleChange({ year, month, week, title: autoTitle, dateRange: rangeText });
    }
  };

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

      {/* Date Range Configuration */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-1">기간 설정 (자동 생성 및 수정 가능)</label>
        <div className="flex items-center gap-2">
          <div className="relative flex-grow">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Calendar className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              value={dateRangeText}
              onChange={handleDateRangeTextChange}
              className="pl-10 block w-full border border-gray-300 rounded-md p-2 focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="YYYY.MM.DD ~ YYYY.MM.DD"
            />
          </div>
          
          {/* Hidden/Small Date Pickers for Selection */}
          <div className="flex items-center gap-1 bg-gray-50 p-1 rounded border border-gray-200">
            <input 
              type="date" 
              value={startDate}
              onChange={handleStartDateChange}
              className="text-xs border-none bg-transparent focus:ring-0 p-1"
              title="시작일 선택"
            />
            <span className="text-gray-400">~</span>
            <input 
              type="date" 
              value={endDate}
              onChange={handleEndDateChange}
              className="text-xs border-none bg-transparent focus:ring-0 p-1"
              title="종료일 선택"
            />
          </div>
        </div>
      </div>

      <div className="mb-6 p-3 bg-gray-50 rounded-md border border-gray-200">
        <span className="text-sm text-gray-500 mr-2">자동 생성 타이틀:</span>
        <span className="font-bold text-indigo-600">{autoTitle}</span>
      </div>

      {/* File Uploads */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-1">주간 데이터 파일 업로드 (.xlsx)</label>
        <p className="text-xs text-slate-500 mb-2">파일명형식 : 2025_COB_01.xlsx, 작업연도_코브랜드채널구분_주차</p>
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

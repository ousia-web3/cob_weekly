import React, { useState, useEffect } from 'react';
import { RefreshCw, Send, Clock, FileText } from 'lucide-react';

const EmailHistory = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [resending, setResending] = useState(null); // id being resent
  const API_BASE_URL = `http://${window.location.hostname}:8001`;

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/api/email/history`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      if (data.status === 'success') {
        setHistory(data.history);
      } else {
        throw new Error(data.message || 'Failed to load history');
      }
    } catch (error) {
      console.error('Failed to fetch email history:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleResend = async (id, title) => {
    if (!confirm(`"${title}" 메일을 재발송하시겠습니까?`)) return;

    setResending(id);
    try {
      const response = await fetch(`${API_BASE_URL}/api/email/resend/${id}`, {
        method: 'POST'
      });
      const result = await response.json();
      
      if (result.status === 'success') {
        alert('재발송 완료: ' + result.message);
        fetchHistory(); // Refresh history to show new entry
      } else {
        alert('재발송 실패: ' + result.message);
      }
    } catch (error) {
      console.error('Resend error:', error);
      alert('재발송 중 오류가 발생했습니다.');
    } finally {
      setResending(null);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
      <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50">
        <h3 className="font-bold text-slate-800 flex items-center gap-2">
          발송 이력
        </h3>
        <button 
          onClick={fetchHistory} 
          className="p-2 hover:bg-slate-200 rounded-full transition-colors"
          title="새로고침"
        >
          <RefreshCw className={`w-4 h-4 text-slate-600 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>
      
      <div className="max-h-60 overflow-y-auto">
        {loading ? (
          <div className="p-8 text-center text-slate-500">로딩 중...</div>
        ) : error ? (
          <div className="p-8 text-center text-red-500">
            데이터를 불러오지 못했습니다.<br/>
            ({error})
          </div>
        ) : history.length === 0 ? (
          <div className="p-8 text-center text-slate-500">
            발송된 이메일 내역이 없습니다.
          </div>
        ) : (
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-slate-500 uppercase bg-slate-50 sticky top-0">
              <tr>
                <th className="px-6 py-3">상태</th>
                <th className="px-6 py-3">제목</th>
                <th className="px-6 py-3">수신자</th>
                <th className="px-6 py-3">발송 일시</th>
                <th className="px-6 py-3 text-right">작업</th>
              </tr>
            </thead>
            <tbody>
              {history.map((item) => (
                <tr key={item.id} className="border-b border-slate-100 hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-3">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                      item.status === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {item.status === 'success' ? '성공' : '실패'}
                    </span>
                  </td>
                  <td className="px-6 py-3 font-medium text-slate-900">
                    <div className="flex items-center gap-2">
                      <span className="truncate max-w-xs" title={item.subject}>{item.subject}</span>
                    </div>
                  </td>
                  <td className="px-6 py-3 text-slate-500">
                    <span title={item.recipients.join(', ')}>
                      {item.recipients.length}명
                    </span>
                  </td>
                  <td className="px-6 py-3 text-slate-500 text-xs">
                    {item.date}
                  </td>
                  <td className="px-6 py-3 text-right">
                    <button
                      onClick={() => handleResend(item.id, item.subject)}
                      disabled={resending === item.id}
                      className={`inline-flex items-center gap-1 px-3 py-1.5 rounded-md text-xs font-medium transition-colors
                        ${resending === item.id 
                          ? 'bg-slate-100 text-slate-400 cursor-not-allowed' 
                          : 'bg-indigo-50 text-indigo-600 hover:bg-indigo-100 border border-indigo-200'
                        }`}
                    >
                      <Send className="w-3 h-3" />
                      {resending === item.id ? '발송중...' : '재발송'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default EmailHistory;

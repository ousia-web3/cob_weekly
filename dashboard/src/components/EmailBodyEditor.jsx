import React, { useEffect, useRef } from 'react';
import Quill from 'quill';
import 'quill/dist/quill.snow.css';

const EmailBodyEditor = ({ value, onChange, enabled }) => {
  const containerRef = useRef(null);
  const quillRef = useRef(null);
  const isInitializedRef = useRef(false);

  useEffect(() => {
    // 이미 초기화되었으면 중단
    if (isInitializedRef.current || !containerRef.current) return;

    // 기존 에디터 영역 정리
    const editorContainer = containerRef.current;
    editorContainer.innerHTML = '';
    
    // 에디터 div 생성
    const editorDiv = document.createElement('div');
    editorContainer.appendChild(editorDiv);

    // Quill 에디터 초기화
    const quill = new Quill(editorDiv, {
      theme: 'snow',
      placeholder: '메일 본문 내용을 입력하세요... (선택 사항)',
      modules: {
        toolbar: [
          [{ 'header': [1, 2, 3, false] }],
          ['bold', 'italic', 'underline', 'strike'],
          [{ 'color': [] }, { 'background': [] }],
          [{ 'list': 'ordered'}, { 'list': 'bullet' }],
          [{ 'align': [] }],
          ['link'],
          ['clean']
        ]
      }
    });

    // 초기값 설정
    if (value) {
      quill.root.innerHTML = value;
    }

    // 변경 이벤트 리스너
    quill.on('text-change', () => {
      onChange(quill.root.innerHTML);
    });

    quillRef.current = quill;
    isInitializedRef.current = true;

    // 클린업
    return () => {
      if (quillRef.current) {
        quillRef.current.off('text-change');
        quillRef.current = null;
      }
      isInitializedRef.current = false;
    };
  }, []);

  // enabled 상태 변경 시 에디터 활성화/비활성화
  useEffect(() => {
    if (quillRef.current) {
      quillRef.current.enable(enabled);
    }
  }, [enabled]);

  // value prop이 외부에서 변경될 때 에디터 내용 업데이트 (무한 루프 방지)
  useEffect(() => {
    if (quillRef.current && value !== quillRef.current.root.innerHTML) {
      const currentSelection = quillRef.current.getSelection();
      quillRef.current.root.innerHTML = value || '';
      if (currentSelection) {
        quillRef.current.setSelection(currentSelection);
      }
    }
  }, [value]);

  return (
    <div className="bg-white rounded-lg border border-slate-200 shadow-sm">
      <div className="px-4 py-3 border-b border-slate-200 bg-slate-50">
        <h3 className="text-sm font-semibold text-slate-700">메일 본문 (선택 사항)</h3>
        <p className="text-xs text-slate-500 mt-1">
          {enabled 
            ? "내용을 입력하면 리포트 상단에 포함됩니다." 
            : "체크박스를 활성화하여 메일 본문을 추가할 수 있습니다."}
        </p>
      </div>
      <div 
        ref={containerRef} 
        className={`min-h-[150px] ${!enabled ? 'opacity-50' : ''}`}
        style={{ backgroundColor: enabled ? 'white' : '#f8f9fa' }}
      />
    </div>
  );
};

export default EmailBodyEditor;

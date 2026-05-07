import React from 'react';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError && this.state.error) {
      return (
        <div style={{ padding: 20, background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 8, margin: 16 }}>
          <h3 style={{ color: '#b91c1c', marginBottom: 8 }}>오류 발생</h3>
          <pre style={{ fontSize: 12, overflow: 'auto', color: '#991b1b' }}>
            {this.state.error.toString()}
          </pre>
          {this.state.error.stack && (
            <details style={{ marginTop: 8 }}>
              <summary>스택 트레이스</summary>
              <pre style={{ fontSize: 11, overflow: 'auto', marginTop: 4 }}>{this.state.error.stack}</pre>
            </details>
          )}
        </div>
      );
    }
    return this.props.children;
  }
}

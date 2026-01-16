export const downloadJSON = (data, filename = "dashboard_data.json") => {
  const jsonStr = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonStr], { type: "application/json" });
  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

export const generateDashboardHTML = (data) => {
  // This function generates a standalone HTML file that embeds the data
  // and a script to render it.
  // Since we are in a React environment, the "easiest" way to make a standalone file
  // that looks exactly like the preview is to use a template that includes
  // the React runtime and our component code.
  // However, bundling the entire React app into a single string client-side is complex.

  // A simpler approach for this specific requirement (generating a report)
  // is to use a pre-built HTML template (like the one we started with)
  // and inject the JSON data into a script tag.

  // We will use a template string that mimics the original HTML structure
  // but with the data variable populated with our `data` object.

  const jsonStr = JSON.stringify(data);

  return `<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${data.meta.title}</title>
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- React & ReactDOM (Ver 18) -->
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    
    <!-- Prop-types -->
    <script src="https://unpkg.com/prop-types/prop-types.min.js"></script>
    
    <!-- Recharts -->
    <script src="https://unpkg.com/recharts@2.12.7/umd/Recharts.js"></script>
    
    <!-- Babel -->
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
        body { font-family: 'Noto Sans KR', sans-serif; }
    </style>
</head>
<body class="bg-slate-100">
    <div id="root"></div>

    <script type="text/babel">
        // Inject Data
        const dashboardData = ${jsonStr};

        // --- Recharts Components ---
        const { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, AreaChart, Area } = window.Recharts;

        // --- Components ---
        // (We need to duplicate the component logic here or include it in the template)
        // For simplicity, we'll inline the DashboardPreview logic adapted for standalone use.
        
        const formatNumber = (num) => new Intl.NumberFormat('ko-KR').format(num);

        const Top10Table = ({ title, dataInfo, headerColor = "indigo" }) => {
            const headerColors = { indigo: "bg-indigo-600", emerald: "bg-emerald-600", rose: "bg-rose-600" };
            const headerBg = headerColors[headerColor] || "bg-slate-600";
            if (!dataInfo) return null;
            return (
                <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden h-full">
                    <div className={\`p-4 \${headerBg} text-white\`}>
                        <div className="flex justify-between items-center mb-1">
                            <h4 className="font-bold text-sm">{title}</h4>
                            <span className="text-xs bg-white/20 px-2 py-0.5 rounded text-white font-medium">TOP 10</span>
                        </div>
                        <div className="flex justify-between items-end">
                            <div><span className="text-xs opacity-80 block">Total UV</span><span className="font-bold text-lg">{formatNumber(dataInfo.totalUV)}</span></div>
                            <div className="text-right"><span className="text-xs opacity-80 block">전주대비</span><span className="font-bold text-sm flex items-center justify-end text-white">{dataInfo.growth > 0 ? '▲' : '▼'} {Math.abs(dataInfo.growth)}%</span></div>
                        </div>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-xs text-left">
                            <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200">
                                <tr><th className="px-3 py-2 text-center w-10 whitespace-nowrap">순위</th><th className="px-3 py-2 whitespace-nowrap">업체명</th><th className="px-3 py-2 text-right whitespace-nowrap">UV</th></tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                                {dataInfo.data.map((item) => (
                                    <tr key={item.rank} className="hover:bg-slate-50">
                                        <td className="px-3 py-2 text-center font-medium text-slate-500 whitespace-nowrap">{item.rank}</td>
                                        <td className="px-3 py-2 text-slate-700 truncate max-w-[100px] whitespace-nowrap" title={item.name}>{item.name}</td>
                                        <td className="px-3 py-2 text-right font-medium text-slate-800 whitespace-nowrap">{formatNumber(item.uv)}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            );
        };

        const Dashboard = ({ data }) => {
            const [isDetailedTableVisible, setIsDetailedTableVisible] = React.useState(true);
            const { meta, summary, trend, device, categories, coBrandTop20, detailedTop10, aiInsight } = data;
            
            // Channel Type Data
            const channelTypeData = coBrandTop20.reduce((acc, item) => {
                const existing = acc.find(d => d.name === item.type);
                if (existing) existing.value += 1;
                else acc.push({ name: item.type, value: 1 });
                return acc;
            }, []);
            channelTypeData.sort((a, b) => b.value - a.value);
            const top20SumUV = coBrandTop20.reduce((acc, item) => acc + item.uv, 0);

            return (
                <div className="min-h-screen bg-slate-100 p-8 font-sans text-slate-800">
                    {/* Header */}
                    <div className="bg-white rounded-t-xl shadow-sm border-b border-slate-200 p-6 flex flex-col md:flex-row justify-between items-center gap-4">
                        <div>
                            <div className="flex items-center gap-2 mb-1"><span className="text-xs font-bold text-indigo-600 tracking-wider uppercase">Weekly Executive Summary</span></div>
                            <h1 className="text-2xl font-bold text-slate-900">{meta.title}</h1>
                            <p className="text-slate-500 text-sm mt-1">기간: {meta.range} | 작성: 공통서비스기획팀</p>
                        </div>
                    </div>

                    {/* AI Summary */}
                    <div className="bg-white p-6 shadow-sm border-b border-slate-200 mb-6">
                        <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">핵심 요약</h3>
                        <div className="bg-indigo-50 border-l-4 border-indigo-500 p-5 rounded-r-md">
                            {aiInsight ? aiInsight.map((insight, idx) => (
                                <div key={idx} className="mb-4 last:mb-0">
                                    <h4 className="font-bold text-indigo-700 text-base mb-1">{insight.title}</h4>
                                    <p className="text-slate-700 text-sm leading-relaxed whitespace-pre-line">{insight.content}</p>
                                </div>
                            )) : <p className="text-slate-500 italic">AI 요약이 없습니다.</p>}
                        </div>
                    </div>

                    {/* KPIs */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                        <div className="bg-white p-5 rounded-lg shadow-sm border border-slate-200 flex flex-col justify-between">
                            <div><p className="text-xs font-bold text-slate-400 uppercase tracking-wide">Total UV</p><div className="flex items-baseline mt-1 gap-2"><h2 className="text-3xl font-extrabold text-slate-800">{formatNumber(summary.totalUV)}</h2><span className="text-xs text-slate-400">명</span></div></div>
                            <div className="mt-4 flex items-center"><span className={\`flex items-center text-sm font-bold \${summary.growth >= 0 ? 'text-red-500' : 'text-blue-600'}\`}>{summary.growth >= 0 ? '+' : ''}{summary.growth}%</span><span className="text-xs text-slate-400 ml-2">vs 전주</span></div>
                        </div>
                        <div className="bg-white p-5 rounded-lg shadow-sm border border-slate-200 flex flex-col justify-between">
                            <div><p className="text-xs font-bold text-slate-400 uppercase tracking-wide">Mobile Share</p><div className="flex items-baseline mt-1 gap-2"><h2 className="text-3xl font-extrabold text-slate-800">{summary.mobileShare}%</h2></div></div>
                            <div className="mt-4 w-full bg-slate-100 rounded-full h-2 overflow-hidden"><div className="bg-orange-500 h-2 rounded-full" style={{ width: \`\${summary.mobileShare}%\` }}></div></div>
                            <p className="text-xs text-slate-400 mt-2">모바일 중심 유입 지속</p>
                        </div>
                        <div className="bg-white p-5 rounded-lg shadow-sm border border-slate-200 border-l-4 border-l-red-500 flex flex-col justify-between">
                            <div><p className="text-xs font-bold text-red-500 uppercase tracking-wide flex items-center gap-1">Best Growth</p><h2 className="text-xl font-bold text-slate-800 mt-2">{summary.bestGrowth?.name || '-'}</h2></div>
                            <div className="mt-2"><span className="text-2xl font-bold text-red-500">{summary.bestGrowth?.rate > 0 ? '+' : ''}{summary.bestGrowth?.rate}%</span><span className="text-xs text-slate-400 ml-1">증가</span></div>
                        </div>
                        <div className="bg-white p-5 rounded-lg shadow-sm border border-slate-200 border-l-4 border-l-blue-500 flex flex-col justify-between">
                            <div><p className="text-xs font-bold text-blue-500 uppercase tracking-wide flex items-center gap-1">Worst Drop</p><h2 className="text-xl font-bold text-slate-800 mt-2">{summary.worstDrop?.name || '-'}</h2></div>
                            <div className="mt-2"><span className="text-2xl font-bold text-blue-500">{summary.worstDrop?.rate}%</span><span className="text-xs text-slate-400 ml-1">감소</span></div>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6">
                        {/* Trend Chart */}
                        <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200 lg:col-span-2">
                            <div className="flex justify-between items-end mb-6"><h3 className="text-lg font-bold text-slate-800">주간 트래픽 추이</h3></div>
                            <div className="h-72">
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={trend} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                                        <defs><linearGradient id="colorUv" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#6366f1" stopOpacity={0.1}/><stop offset="95%" stopColor="#6366f1" stopOpacity={0}/></linearGradient></defs>
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                        <XAxis dataKey="name" tick={{fill: '#94a3b8', fontSize: 12}} axisLine={false} tickLine={false} dy={10} />
                                        <YAxis tickFormatter={(value) => \`\${value/1000}k\`} tick={{fill: '#94a3b8', fontSize: 12}} axisLine={false} tickLine={false} />
                                        <Tooltip contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}} formatter={(value) => [formatNumber(value), 'UV']} />
                                        <Area type="monotone" dataKey="uv" stroke="#6366f1" strokeWidth={3} fillOpacity={1} fill="url(#colorUv)" />
                                    </AreaChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                        
                        {/* Device Pie */}
                        <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200 lg:col-span-1">
                            <h3 className="text-sm font-bold text-slate-800 mb-6 uppercase tracking-wide">디바이스 점유율</h3>
                            <div className="relative h-64 flex justify-center items-center">
                                <ResponsiveContainer width="100%" height="100%">
                                    <PieChart><Pie data={device} innerRadius={60} outerRadius={80} paddingAngle={2} dataKey="value" startAngle={90} endAngle={-270}><Cell fill="#f97316" /><Cell fill="#334155" /></Pie></PieChart>
                                </ResponsiveContainer>
                                <div className="absolute inset-0 flex flex-col justify-center items-center pointer-events-none"><span className="text-3xl font-bold text-slate-800">{summary.mobileShare}%</span><span className="text-xs font-medium text-slate-400">Mobile</span></div>
                            </div>
                            <div className="flex justify-center gap-4 mt-2 text-xs"><div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-orange-500"></div><span className="text-slate-600">Mobile</span></div><div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-slate-700"></div><span className="text-slate-600">PC</span></div></div>
                        </div>

                        {/* Channel Pie */}
                        <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200 lg:col-span-1">
                            <h3 className="text-sm font-bold text-slate-800 mb-6 uppercase tracking-wide">채널 유형 점유율 (TOP 20)</h3>
                            <div className="relative h-64 flex justify-center items-center">
                                <ResponsiveContainer width="100%" height="100%">
                                    <PieChart><Pie data={channelTypeData} innerRadius={60} outerRadius={80} paddingAngle={2} dataKey="value" startAngle={90} endAngle={-270}>{channelTypeData.map((entry, index) => (<Cell key={\`cell-\${index}\`} fill={entry.name === '브랜드몰' ? '#6366f1' : '#10b981'} />))}</Pie></PieChart>
                                </ResponsiveContainer>
                                <div className="absolute inset-0 flex flex-col justify-center items-center pointer-events-none"><span className="text-2xl font-bold text-slate-800">{channelTypeData.length > 0 ? Math.round((channelTypeData[0].value / (channelTypeData.reduce((a,b)=>a+b.value,0))) * 100) : 0}%</span><span className="text-xs font-medium text-slate-400">{channelTypeData[0]?.name}</span></div>
                            </div>
                            <div className="flex justify-center gap-4 mt-2 text-xs"><div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-indigo-500"></div><span className="text-slate-600">브랜드몰</span></div><div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-emerald-500"></div><span className="text-slate-600">제휴채널</span></div></div>
                        </div>
                    </div>

                    {/* Top 20 Table */}
                    <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden mb-6">
                        <div className="p-6 border-b border-slate-100 flex justify-between items-center">
                            <div className="flex flex-col"><h3 className="text-lg font-bold text-slate-800">코브랜드 도메인 UV TOP 20</h3><p className="text-xs text-slate-500 mt-1">* 비중(%)은 TOP 20 합계 ({formatNumber(top20SumUV)}) 대비 비율입니다.</p></div>
                            <span className="text-xs text-slate-500 font-medium bg-slate-100 px-3 py-1 rounded-full">Top 20 UV: {formatNumber(top20SumUV)}</span>
                        </div>
                        <div className="overflow-x-auto max-h-96">
                            <table className="w-full text-sm text-left">
                                <thead className="bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider sticky top-0">
                                    <tr><th className="px-6 py-3 text-center w-24 whitespace-nowrap">순위</th><th className="px-6 py-3">제휴사명</th><th className="px-6 py-3 text-center">채널유형</th><th className="px-6 py-3 text-right">UV</th><th className="px-6 py-3 text-right">비중(%)</th><th className="px-6 py-3 text-right">증감율</th></tr>
                                </thead>
                                <tbody className="divide-y divide-slate-100">
                                    {coBrandTop20.map((item) => (
                                        <tr key={item.rank} className="hover:bg-slate-50 transition-colors">
                                            <td className="px-6 py-3 text-center font-bold text-slate-600">{item.rank}</td>
                                            <td className="px-6 py-3 font-medium text-slate-800">{item.name}</td>
                                            <td className="px-6 py-3 text-center"><span className={\`px-2 py-1 rounded-full text-xs font-medium \${item.type === '브랜드몰' ? 'bg-indigo-50 text-indigo-600' : 'bg-green-50 text-green-600'}\`}>{item.type}</span></td>
                                            <td className="px-6 py-3 text-right text-slate-700 font-mono">{formatNumber(item.uv)}</td>
                                            <td className="px-6 py-3 text-right text-slate-500">{((item.uv / top20SumUV) * 100).toFixed(2)}%</td>
                                            <td className="px-6 py-3 text-right font-medium">{item.growth === 'new' ? <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-600">신규진입</span> : <span className={item.growth > 0 ? 'text-red-500' : item.growth < 0 ? 'text-blue-500' : 'text-slate-500'}>{item.growth > 0 ? '▲' : '▼'} {Math.abs(item.growth)}%</span>}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {/* Detailed Top 10s */}
                    {detailedTop10 && (
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                            <Top10Table title="브랜드몰 TOP 10" dataInfo={detailedTop10.brandMall} headerColor="indigo" />
                            <Top10Table title="제휴사 TOP 10" dataInfo={detailedTop10.affiliate} headerColor="emerald" />
                            <Top10Table title="공식인증예약센터 TOP 10" dataInfo={detailedTop10.officialCenter} headerColor="rose" />
                        </div>
                    )}

                    {/* Categories */}
                    <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
                        <div className="p-6 border-b border-slate-100 flex justify-between items-center">
                            <h3 className="text-lg font-bold text-slate-800">카테고리별 상세 실적</h3>
                            <button
                                onClick={() => setIsDetailedTableVisible(!isDetailedTableVisible)}
                                className="text-sm text-slate-500 hover:text-indigo-600 font-medium transition-colors bg-white border border-slate-200 px-3 py-1.5 rounded-md hover:bg-slate-50 shadow-sm"
                            >
                                {isDetailedTableVisible ? "테이블 숨기기 (-)" : "테이블 전체보기 (+)"}
                            </button>
                        </div>
                        {isDetailedTableVisible && (
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm text-left">
                                <thead className="bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider">
                                    <tr><th className="px-6 py-4 text-center whitespace-nowrap">구분</th><th className="px-6 py-4 text-center whitespace-nowrap">상세 구분</th><th className="px-6 py-4 text-center whitespace-nowrap">이번주 UV</th><th className="px-6 py-4 text-center whitespace-nowrap">지난주 UV</th><th className="px-6 py-4 text-center whitespace-nowrap">변동률</th></tr>
                                </thead>
                                <tbody className="divide-y divide-slate-100">
                                    {categories.map((group, groupIdx) => (
                                        <React.Fragment key={groupIdx}>
                                            <tr className="bg-slate-50"><td colSpan={5} className="px-6 py-2 font-bold text-slate-700 border-t border-b border-slate-200 text-sm">{group.group}</td></tr>
                                            {group.items.map((row, idx) => (
                                                <tr key={\`\${groupIdx}-\${idx}\`} className="hover:bg-slate-50 transition-colors">
                                                    <td className="px-6 py-3 font-medium text-slate-500 text-center whitespace-nowrap hidden md:table-cell">{group.group.split(' ')[0]}</td>
                                                    <td className="px-6 py-3 font-medium text-slate-700 text-center whitespace-nowrap">{row.name}</td>
                                                    <td className="px-6 py-3 text-right font-medium text-slate-900 whitespace-nowrap">{formatNumber(row.current)}</td>
                                                    <td className="px-6 py-3 text-right text-slate-400 whitespace-nowrap">{formatNumber(row.prev)}</td>
                                                    <td className="px-6 py-3 text-right whitespace-nowrap"><span className={\`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold \${row.rate > 0 ? 'bg-red-50 text-red-600' : 'bg-blue-50 text-blue-600'}\`}>{row.rate > 0 ? '▲' : '▼'} {Math.abs(row.rate)}%</span></td>
                                                </tr>
                                            ))}
                                        </React.Fragment>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                        )}
                    </div>
                </div>
            );
        };

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<Dashboard data={dashboardData} />);
    </script>
</body>
</html>`;
};

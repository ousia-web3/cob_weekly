import * as XLSX from 'xlsx';

export const parseExcel = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, { type: 'array' });
        const firstSheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[firstSheetName];
        
        // Convert to JSON (array of arrays)
        const rawData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });

        // Helper to safely get cell value
        const getVal = (row, col) => {
            if (!rawData[row] || rawData[row][col] === undefined) return 0;
            return rawData[row][col];
        };
        const getStr = (row, col) => {
             if (!rawData[row] || rawData[row][col] === undefined) return '';
             return String(rawData[row][col]).trim();
        };

        // --- Parsing Logic ---
        // Excel row numbers are 1-based. Array indices are 0-based.
        // Row 1 = Index 0

        // 1. Device Share (Found at Row 100 in sample)
        // Row 100 (Index 99): Col 3(Total), Col 4(Mobile), Col 5(PC)
        const deviceRowIndex = 99;
        const mobileUV = getVal(deviceRowIndex, 4);
        const pcUV = getVal(deviceRowIndex, 5);
        const totalDeviceUV = mobileUV + pcUV; // Or use Col 3
        
        // Calculate percentages
        const mobileShare = totalDeviceUV ? Math.round((mobileUV / totalDeviceUV) * 100) : 0;
        const pcShare = totalDeviceUV ? Math.round((pcUV / totalDeviceUV) * 100) : 0;

        const deviceData = [
            { name: 'Mobile', value: mobileShare },
            { name: 'PC', value: pcShare }
        ];

        // 2. Detailed Top 10 Lists (Found at Rows 84-93 in sample)
        // Brand Mall: Col 3 (Name), Col 4 (UV)
        // Affiliate: Col 8 (Name), Col 9 (UV)
        // Official Center: Col 14 (Name), Col 15 (UV) - Assumed based on pattern
        
        const parseTop10 = (startColName, startColUV) => {
            const list = [];
            for (let i = 83; i < 93; i++) { // Rows 84-93
                const rank = i - 82;
                const name = getStr(i, startColName);
                const uv = getVal(i, startColUV);
                if (name && name !== '0') {
                    list.push({ rank, name, uv: Number(uv) || 0 });
                }
            }
            return list;
        };

        const brandMallData = parseTop10(3, 4);
        const affiliateData = parseTop10(8, 9);
        const officialCenterData = parseTop10(13, 14); // Assuming Col 14/15

        // Calculate totals and growth (mock growth for now as it's not clearly in the same block)
        const calculateMeta = (data) => ({
            totalUV: data.reduce((acc, item) => acc + item.uv, 0),
            growth: 0, // Placeholder
            data: data
        });

        const detailedTop10 = {
            brandMall: calculateMeta(brandMallData),
            affiliate: calculateMeta(affiliateData),
            officialCenter: calculateMeta(officialCenterData)
        };

        // 3. Co-Brand Top 20
        // Since the sample file doesn't have a dedicated Top 20 list at Rows 98-124 (it has Device Share there),
        // we will construct a "Top 20" by combining Brand Mall and Affiliate lists and sorting them.
        // This is a reasonable fallback.
        
        let combinedTop20 = [
            ...brandMallData.map(d => ({ ...d, type: '브랜드몰' })),
            ...affiliateData.map(d => ({ ...d, type: '제휴채널' }))
        ];
        
        // Sort by UV desc
        combinedTop20.sort((a, b) => b.uv - a.uv);
        
        // Take top 20 and re-rank
        combinedTop20 = combinedTop20.slice(0, 20).map((item, index) => ({
            rank: index + 1,
            name: item.name,
            uv: item.uv,
            type: item.type,
            growth: 0 // Placeholder
        }));

        // If parsing failed (empty), use mock data
        const useMock = combinedTop20.length === 0;
        const mockData = getMockData();

        const finalData = {
            meta: mockData.meta, // TODO: Parse from header
            summary: {
                ...mockData.summary,
                mobileShare: mobileShare || mockData.summary.mobileShare
            },
            trend: mockData.trend, // TODO: Parse from trend block
            device: deviceData.length > 0 ? deviceData : mockData.device,
            categories: mockData.categories, // TODO: Parse from category block
            coBrandTop20: useMock ? mockData.coBrandTop20 : combinedTop20,
            detailedTop10: detailedTop10.brandMall.data.length > 0 ? detailedTop10 : mockData.detailedTop10
        };
        
        resolve(finalData);
      } catch (error) {
        reject(error);
      }
    };
    reader.onerror = (error) => reject(error);
    reader.readAsArrayBuffer(file);
  });
};

const getMockData = () => {
    return {
        meta: {
          year: 2025, month: 12, weekNumber: 1,
          range: "2025.12.01 ~ 12.07",
          title: "2025년 12월 1주차 트래픽 현황 보고"
        },
        summary: {
          totalUV: 450710, prevTotalUV: 465920, growth: -3.3, mobileShare: 77,
          bestGrowth: { name: "해외항공 (예약완료)", rate: 45.5 },
          worstDrop: { name: "해외호텔 (예약)", rate: -37.5 }
        },
        trend: [
          { name: '10월 5주', uv: 418163 },
          { name: '11월 1주', uv: 468304 },
          { name: '11월 2주', uv: 434859 },
          { name: '11월 3주', uv: 480351 },
          { name: '11월 4주', uv: 465920 },
          { name: '12월 1주', uv: 450710 },
        ],
        device: [
          { name: 'Mobile', value: 77 },
          { name: 'PC', value: 23 },
        ],
        categories: [
           {
              group: '공통',
              items: [
                  { name: '전체', current: 450710, prev: 465920, rate: -3.3 },
                  { name: '메인', current: 42280, prev: 34480, rate: 22.6 },
                  { name: '검색', current: 103240, prev: 101790, rate: 1.4 },
              ]
          },
          {
              group: '패키지',
              items: [
                  { name: '대표상품', current: 137430, prev: 130260, rate: 5.5 },
                  { name: '상품상세', current: 119580, prev: 115680, rate: 3.4 },
                  { name: '예약하기', current: 2850, prev: 2530, rate: 12.6 },
                  { name: '예약완료', current: 1120, prev: 930, rate: 20.4 },
              ]
          },
          {
              group: '항공(해외)',
              items: [
                  { name: '서브메인', current: 6740, prev: 5270, rate: 27.9 },
                  { name: '검색(해외)', current: 5140, prev: 4180, rate: 23.0 },
                  { name: '약관동의', current: 20970, prev: 18120, rate: 15.7 },
                  { name: '예약정보입력', current: 18530, prev: 16000, rate: 15.8 },
                  { name: '예약완료', current: 8480, prev: 5830, rate: 45.5 },
              ]
          },
          {
              group: '호텔(해외)',
              items: [
                  { name: '서브메인', current: 3690, prev: 3910, rate: -5.6 },
                  { name: '상품리스팅', current: 2120, prev: 2290, rate: -7.4 },
                  { name: '상품상세', current: 100680, prev: 151610, rate: -33.6 },
                  { name: '예약하기', current: 72320, prev: 115730, rate: -37.5 },
                  { name: '결제완료', current: 1470, prev: 2400, rate: -38.8 },
              ]
          },
          {
              group: '마이페이지',
              items: [
                  { name: '메인', current: 3880, prev: 2590, rate: 49.8 },
                  { name: '패키지', current: 2000, prev: 2200, rate: -9.1 },
                  { name: '해외항공', current: 1800, prev: 920, rate: 95.7 },
                  { name: '국내항공', current: 3530, prev: 3350, rate: 5.4 },
                  { name: '호텔', current: 1480, prev: 1120, rate: 32.1 },
              ]
          }
        ],
        coBrandTop20: [
          { rank: 1, name: '호텔스컴바인', uv: 87615, type: '제휴채널', growth: -60.2 },
          { rank: 2, name: '세주여행사', uv: 45534, type: '브랜드몰', growth: 5.3 },
          { rank: 3, name: '스카이스캐너', uv: 40806, type: '제휴채널', growth: 35.0 },
          { rank: 4, name: '새서울여행사', uv: 21313, type: '브랜드몰', growth: 4.2 },
          { rank: 5, name: '드림패키지', uv: 20716, type: '브랜드몰', growth: 21.7 },
          { rank: 6, name: '네이버', uv: 20587, type: '제휴채널', growth: 30.4 },
          { rank: 7, name: '트립페이지', uv: 18813, type: '브랜드몰', growth: -3.0 },
          { rank: 8, name: '하나이앤비티', uv: 11657, type: '브랜드몰', growth: 1.7 },
          { rank: 9, name: '남강트레블서비스', uv: 10113, type: '브랜드몰', growth: 10.3 },
          { rank: 10, name: '나이스하나', uv: 9489, type: '브랜드몰', growth: -9.3 },
          { rank: 11, name: '컨텐츠월드', uv: 8964, type: '브랜드몰', growth: -10.3 },
          { rank: 12, name: '윙메이트', uv: 8763, type: '브랜드몰', growth: 11.6 },
          { rank: 13, name: '도도투어', uv: 8310, type: '브랜드몰', growth: 20.8 },
          { rank: 14, name: '다운투어', uv: 8300, type: '브랜드몰', growth: 10.5 },
          { rank: 15, name: '황금여행사', uv: 8253, type: '브랜드몰', growth: 1.5 },
          { rank: 16, name: '리컴퍼니', uv: 8016, type: '브랜드몰', growth: 2.6 },
          { rank: 17, name: '트립나우', uv: 7847, type: '브랜드몰', growth: -5.2 },
          { rank: 18, name: '한국교육여행사', uv: 7644, type: '브랜드몰', growth: -3.4 },
          { rank: 19, name: '구글코리아', uv: 7215, type: '제휴채널', growth: -7.1 },
          { rank: 20, name: '케이에이피투어', uv: 7149, type: '브랜드몰', growth: 'new' },
        ],
        detailedTop10: {
            brandMall: {
                totalUV: 151256, growth: -3.2,
                data: [
                    { rank: 1, name: '세주여행사', uv: 45534 },
                    { rank: 2, name: '새서울여행사', uv: 21313 },
                    { rank: 3, name: '트립페이지', uv: 18813 },
                    { rank: 4, name: '하나이앤비티', uv: 11657 },
                    { rank: 5, name: '남강트레블서비스', uv: 10113 },
                    { rank: 6, name: '나이스하나', uv: 9489 },
                    { rank: 7, name: '컨텐츠월드', uv: 8964 },
                    { rank: 8, name: '윙메이트', uv: 8763 },
                    { rank: 9, name: '도도투어', uv: 8310 },
                    { rank: 10, name: '다운투어', uv: 8300 },
                ]
            },
            affiliate: {
                totalUV: 165160, growth: -17.0,
                data: [
                    { rank: 1, name: '호텔스컴바인', uv: 87615 },
                    { rank: 2, name: '스카이스캐너', uv: 40806 },
                    { rank: 3, name: '네이버', uv: 20587 },
                    { rank: 4, name: '구글코리아', uv: 7215 },
                    { rank: 5, name: '롯데카드[해외]', uv: 2363 },
                    { rank: 6, name: '하나투어[카약]', uv: 1488 },
                    { rank: 7, name: '골프존카운티', uv: 1362 },
                    { rank: 8, name: '삼성카드[임직원몰]', uv: 1326 },
                    { rank: 9, name: '하나카드[VIP]', uv: 1246 },
                    { rank: 10, name: '더케이교직원나라', uv: 1152 },
                ]
            },
            officialCenter: {
                totalUV: 16558, growth: 43.2,
                data: [
                    { rank: 1, name: '여행의달인', uv: 4327 },
                    { rank: 2, name: '순이엔티', uv: 2810 },
                    { rank: 3, name: '홈쇼핑모아', uv: 2782 },
                    { rank: 4, name: 'H.브릿지', uv: 1865 },
                    { rank: 5, name: '하나투어리스트[온라인]', uv: 1456 },
                    { rank: 6, name: '부산은성관광', uv: 874 },
                    { rank: 7, name: '모먼트 스튜디오', uv: 840 },
                    { rank: 8, name: '엠에스투어', uv: 555 },
                    { rank: 9, name: '하나이앤비티', uv: 536 },
                    { rank: 10, name: '나침반여행사', uv: 513 },
                ]
            }
        }
    };
};

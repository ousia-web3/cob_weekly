import re
import json
import base64
import io
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib
import os

# Set font for Korean support
try:
    matplotlib.rc('font', family='Malgun Gothic')
except:
    pass
matplotlib.rcParams['axes.unicode_minus'] = False
matplotlib.rcParams['figure.dpi'] = 100

# Color Palette
PRIMARY_COLOR = "#5E35AA" # Hana Bank/Group Blue-ish -> Updated to Purple
SECONDARY_COLOR = "#008485" # Teal
ACCENT_COLOR = "#e60028" # Red for negative/important
BG_COLOR = "#f4f6f9"
CARD_BG = "#ffffff"
TEXT_COLOR = "#333333"
BORDER_COLOR = "#e1e4e8"

def extract_data_from_json(json_path):
    print(f"Reading JSON file: {json_path}")
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_data_robust(html_path):
    print(f"Reading HTML file: {html_path}")
    if not os.path.exists(html_path):
        raise FileNotFoundError(f"File not found: {html_path}")
        
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    start_marker = 'const dashboardData ='
    start_idx = content.find(start_marker)
    if start_idx == -1:
        raise ValueError("Could not find dashboardData start")
    
    start_brace = content.find('{', start_idx)
    if start_brace == -1:
        raise ValueError("Could not find start brace")
    
    balance = 0
    end_brace = -1
    for i in range(start_brace, len(content)):
        char = content[i]
        if char == '{':
            balance += 1
        elif char == '}':
            balance -= 1
            if balance == 0:
                end_brace = i
                break
    
    if end_brace == -1:
        raise ValueError("Could not find matching end brace")
    
    json_str = content[start_brace:end_brace+1]
    return json.loads(json_str)

def plot_to_base64():
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    return img_str

def create_trend_chart(trend_data):
    if not trend_data:
        return ""
    
    names = [item['name'] for item in trend_data]
    uvs = [item['uv'] for item in trend_data]
    
    fig, ax = plt.subplots(figsize=(10, 4))
    
    # Style
    ax.set_facecolor('white')
    fig.patch.set_facecolor('white')
    
    # Plot line
    ax.plot(names, uvs, marker='o', markersize=6, linestyle='-', linewidth=2, color=PRIMARY_COLOR, label='UV')
    
    # Fill area under line
    ax.fill_between(names, uvs, alpha=0.1, color=PRIMARY_COLOR)
    
    # Grid
    ax.grid(True, axis='y', linestyle='--', alpha=0.5, color='#cccccc')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cccccc')
    ax.spines['bottom'].set_color('#cccccc')
    
    # Labels
    ax.set_title('주간 UV 추이', fontsize=14, pad=15, fontweight='bold', color=TEXT_COLOR)
    
    # Format Y axis with commas
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
    
    # Annotate points
    for i, v in enumerate(uvs):
        ax.text(i, v + (max(uvs)*0.03), f"{v:,}", ha='center', fontsize=9, fontweight='bold', color=TEXT_COLOR)
        
    plt.tight_layout()
    return plot_to_base64()

def generate_html(data, charts):
    title = data.get('meta', {}).get('title', 'Weekly Report')
    date_range = data.get('meta', {}).get('range', '')

    summary = data.get('summary', {})
    total_uv = summary.get('totalUV', 0)
    prev_total_uv = summary.get('prevTotalUV', 0)
    growth = summary.get('growth', 0)
    mobile_share = summary.get('mobileShare', 0)
    best_growth = summary.get('bestGrowth', {})
    worst_drop = summary.get('worstDrop', {})

    growth_color = ACCENT_COLOR if growth < 0 else PRIMARY_COLOR
    growth_icon = "▼" if growth < 0 else "▲"

    # Prepare data for tables
    co_brand_data = data.get('coBrandTop20', [])
    detailed = data.get('detailedTop10', {})

    # Get all three detailed sections
    brand_mall_data = detailed.get('brandMall', {})
    affiliate_data = detailed.get('affiliate', {})
    official_data = detailed.get('officialCenter', {})

    # Calculate total UV for TOP 20
    top20_sum_uv = sum(item.get('uv', 0) for item in co_brand_data)

    # Device data
    device_data = data.get('device', [])
    mobile_pct = 0
    pc_pct = 0
    for d in device_data:
        if d.get('name') == 'Mobile':
            mobile_pct = d.get('value', 0)
        elif d.get('name') == 'PC':
            pc_pct = d.get('value', 0)

    # AI Insights
    ai_insights = data.get('aiInsight', [])
    
    # Email Body (선택 사항)
    email_body = data.get('emailBody', None)

    # Calculate channel type distribution for TOP 20
    channel_type_counts = {}
    for item in co_brand_data:
        channel_type = item.get('type', '기타')
        channel_type_counts[channel_type] = channel_type_counts.get(channel_type, 0) + 1

    # Sort by count
    sorted_channel_types = sorted(channel_type_counts.items(), key=lambda x: x[1], reverse=True)

    # Categories data
    categories = data.get('categories', [])

    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
    </head>
    <body style="margin: 0; padding: 0; background-color: {BG_COLOR}; font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif; color: {TEXT_COLOR}; -webkit-font-smoothing: antialiased;">

        <!-- Main Container -->
        <div style="max-width: 850px; margin: 0 auto; background-color: {CARD_BG}; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">

            <!-- Email Body (선택 사항) - 배너 위에 텍스트로만 표시 -->
            {generate_email_body_html(email_body) if email_body else ''}

            <!-- Header -->
            <div style="background-color: {PRIMARY_COLOR}; padding: 30px 40px; text-align: left;">
                <div style="font-size: 11px; font-weight: bold; color: rgba(255,255,255,0.9); letter-spacing: 1px; margin-bottom: 8px;">WEEKLY EXECUTIVE SUMMARY</div>
                <h1 style="margin: 0; font-size: 24px; color: #ffffff; font-weight: bold;">{title}</h1>
                <p style="margin: 10px 0 0 0; font-size: 13px; color: rgba(255,255,255,0.8);">기간: {date_range}</p>
            </div>

            <!-- Content Padding -->
            <div style="padding: 40px;">

                <!-- AI Insights (핵심 요약) -->
                {generate_ai_insights_html(ai_insights)}

                <!-- KPIs (4 Cards) - Table-based for email compatibility -->
                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom: 20px;">
                    <tr>
                        <!-- Total UV -->
                        <td width="25%" valign="top" style="padding: 0 5px 0 0;">
                            <div style="background-color: #ffffff; border: 1px solid {BORDER_COLOR}; border-radius: 8px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.03); height: 90px;">
                                <div style="font-size: 10px; font-weight: bold; color: #999; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px;">Total UV</div>
                                <div style="font-size: 24px; font-weight: bold; color: {TEXT_COLOR}; margin-bottom: 8px;">{total_uv:,}</div>
                                <div style="font-size: 13px; font-weight: bold; color: {growth_color};">
                                    {growth:+.1f}% <span style="font-size: 10px; color: #999; font-weight: normal;">vs 전주</span>
                                </div>
                            </div>
                        </td>

                        <!-- Mobile Share -->
                        <td width="25%" valign="top" style="padding: 0 5px;">
                            <div style="background-color: #ffffff; border: 1px solid {BORDER_COLOR}; border-radius: 8px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.03); height: 90px;">
                                <div style="font-size: 10px; font-weight: bold; color: #999; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px;">Mobile Share</div>
                                <div style="font-size: 24px; font-weight: bold; color: {TEXT_COLOR}; margin-bottom: 8px;">{mobile_share}%</div>
                                <div style="background-color: #f4f6f9; height: 6px; border-radius: 3px; overflow: hidden;">
                                    <div style="background-color: #f97316; height: 100%; width: {mobile_share}%;"></div>
                                </div>
                            </div>
                        </td>

                        <!-- Best Growth -->
                        <td width="25%" valign="top" style="padding: 0 5px;">
                            <div style="background-color: #ffffff; border: 1px solid {BORDER_COLOR}; border-left: 4px solid #ef4444; border-radius: 8px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.03); height: 90px;">
                                <div style="font-size: 10px; font-weight: bold; color: #ef4444; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px;">Best Growth</div>
                                <div style="font-size: 13px; font-weight: bold; color: {TEXT_COLOR}; margin-bottom: 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{best_growth.get('name', '-')}</div>
                                <div style="font-size: 18px; font-weight: bold; color: #ef4444;">
                                    {best_growth.get('rate', 0):+.1f}% <span style="font-size: 10px; color: #999; font-weight: normal;">증가</span>
                                </div>
                            </div>
                        </td>

                        <!-- Worst Drop -->
                        <td width="25%" valign="top" style="padding: 0 0 0 5px;">
                            <div style="background-color: #ffffff; border: 1px solid {BORDER_COLOR}; border-left: 4px solid #3b82f6; border-radius: 8px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.03); height: 90px;">
                                <div style="font-size: 10px; font-weight: bold; color: #3b82f6; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px;">Worst Drop</div>
                                <div style="font-size: 13px; font-weight: bold; color: {TEXT_COLOR}; margin-bottom: 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{worst_drop.get('name', '-')}</div>
                                <div style="font-size: 18px; font-weight: bold; color: #3b82f6;">
                                    {worst_drop.get('rate', 0):.1f}% <span style="font-size: 10px; color: #999; font-weight: normal;">감소</span>
                                </div>
                            </div>
                        </td>
                    </tr>
                </table>

                <!-- Chart Section -->
                <div style="margin-bottom: 20px;">
                    <div style="background-color: #ffffff; border: 1px solid {BORDER_COLOR}; border-radius: 8px; padding: 25px; margin-bottom: 20px;">
                        <h3 style="font-size: 16px; font-weight: bold; color: {TEXT_COLOR}; margin: 0 0 20px 0;">주간 트래픽 추이</h3>
                        <img src="data:image/png;base64,{charts.get('trend', '')}" style="max-width: 100%; height: auto; display: block; margin: 0 auto;" alt="Weekly Trend Chart">
                    </div>

                    <!-- Device & Channel Type Cards - Table-based for email compatibility -->
                    <table width="100%" cellpadding="0" cellspacing="0" border="0">
                        <tr>
                            <!-- Device Distribution -->
                            <td width="50%" valign="top" style="padding: 0 10px 0 0;">
                                <div style="background-color: #ffffff; border: 1px solid {BORDER_COLOR}; border-radius: 8px; padding: 25px;">
                                    <h3 style="font-size: 14px; font-weight: bold; color: {TEXT_COLOR}; margin: 0 0 20px 0; text-transform: uppercase; letter-spacing: 0.5px;">디바이스 점유율</h3>

                                    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom: 20px;">
                                        <tr>
                                            <td style="padding-bottom: 10px;">
                                                <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                                    <tr>
                                                        <td valign="middle">
                                                            <span style="display: inline-block; width: 12px; height: 12px; border-radius: 2px; background-color: #f97316; vertical-align: middle;"></span>
                                                            <span style="font-size: 13px; font-weight: 600; color: {TEXT_COLOR}; vertical-align: middle; margin-left: 8px;">Mobile</span>
                                                        </td>
                                                        <td align="right">
                                                            <span style="font-size: 18px; font-weight: bold; color: {TEXT_COLOR};">{mobile_pct}%</span>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>
                                                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f1f5f9; height: 24px; border-radius: 6px;">
                                                    <tr>
                                                        <td width="{mobile_pct}%" style="background-color: #f97316; border-radius: 6px; text-align: center; color: white; font-size: 11px; font-weight: bold;">{mobile_pct}%</td>
                                                        <td></td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                    </table>

                                    <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                        <tr>
                                            <td style="padding-bottom: 10px;">
                                                <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                                    <tr>
                                                        <td valign="middle">
                                                            <span style="display: inline-block; width: 12px; height: 12px; border-radius: 2px; background-color: #334155; vertical-align: middle;"></span>
                                                            <span style="font-size: 13px; font-weight: 600; color: {TEXT_COLOR}; vertical-align: middle; margin-left: 8px;">PC</span>
                                                        </td>
                                                        <td align="right">
                                                            <span style="font-size: 18px; font-weight: bold; color: {TEXT_COLOR};">{pc_pct}%</span>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>
                                                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f1f5f9; height: 24px; border-radius: 6px;">
                                                    <tr>
                                                        <td width="{pc_pct}%" style="background-color: #334155; border-radius: 6px; text-align: center; color: white; font-size: 11px; font-weight: bold;">{pc_pct}%</td>
                                                        <td></td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                    </table>

                                    <div style="margin-top: 20px; text-align: center; font-size: 11px; color: #999;">
                                        모바일 중심 유입 지속
                                    </div>
                                </div>
                            </td>

                            <!-- Channel Type Distribution -->
                            <td width="50%" valign="top" style="padding: 0 0 0 10px;">
                                <div style="background-color: #ffffff; border: 1px solid {BORDER_COLOR}; border-radius: 8px; padding: 25px;">
                                    <h3 style="font-size: 14px; font-weight: bold; color: {TEXT_COLOR}; margin: 0 0 20px 0; text-transform: uppercase; letter-spacing: 0.5px;">채널 유형 점유율 (TOP 20)</h3>

                                    {generate_channel_type_bars(sorted_channel_types)}

                                    <div style="margin-top: 20px; text-align: center; font-size: 11px; color: #999;">
                                        기준: 코브랜드 TOP 20
                                    </div>
                                </div>
                            </td>
                        </tr>
                    </table>
                </div>

                <!-- Co-Brand TOP 20 Table -->
                <div style="background-color: #ffffff; border: 1px solid {BORDER_COLOR}; border-radius: 8px; overflow: hidden; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.03);">
                    <div style="padding: 15px; border-bottom: 1px solid {BORDER_COLOR};">
                        <h3 style="font-size: 15px; font-weight: bold; color: {TEXT_COLOR}; margin: 0 0 5px 0;">코브랜드 도메인 UV TOP 20</h3>
                        <p style="font-size: 11px; color: #999; margin: 0;">* 비중(%)은 TOP 20 합계 ({top20_sum_uv:,}) 대비 비율입니다.</p>
                    </div>
                    {create_cobrand_table_html(co_brand_data, top20_sum_uv)}
                </div>

                <!-- Detailed Top 10 Tables (Three Columns) - Table-based for email compatibility -->
                <div style="margin-bottom: 20px;">
                    <h3 style="font-size: 15px; color: {PRIMARY_COLOR}; margin-bottom: 15px; font-weight: bold;">채널별 상세 순위 (Top 10)</h3>

                    <table width="100%" cellpadding="0" cellspacing="0" border="0">
                        <tr>
                            <!-- Brand Mall -->
                            <td width="33%" valign="top" style="padding: 0 10px 0 0; height: 100%;">
                                {create_detailed_top10_card(brand_mall_data, '브랜드몰 TOP 10', '#6366f1')}
                            </td>

                            <!-- Affiliate -->
                            <td width="34%" valign="top" style="padding: 0 5px; height: 100%;">
                                {create_detailed_top10_card(affiliate_data, '제휴사 TOP 10', '#10b981')}
                            </td>

                            <!-- Official Center -->
                            <td width="33%" valign="top" style="padding: 0 0 0 10px; height: 100%;">
                                {create_detailed_top10_card(official_data, '공식인증예약센터 TOP 10', '#f97316')}
                            </td>
                        </tr>
                    </table>
                </div>

                <!-- Categories Section -->
                {generate_categories_html(categories)}

                <!-- Footer -->
                <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; font-size: 12px; color: #999;">
                    <p style="margin: 0;">본 메일은 주간 리포트 자동 발송 시스템에 의해 생성되었습니다.</p>
                </div>

            </div>
        </div>
    </body>
    </html>
    """
    return html

def generate_categories_html(categories):
    """Generate HTML for categories detailed performance table"""
    if not categories:
        return ""

    html = f"""
    <div style="background-color: #ffffff; border: 1px solid {BORDER_COLOR}; border-radius: 8px; overflow: hidden; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.03);">
        <div style="padding: 20px; border-bottom: 1px solid {BORDER_COLOR};">
            <h3 style="font-size: 16px; font-weight: bold; color: {TEXT_COLOR}; margin: 0;">카테고리별 상세 실적</h3>
        </div>
        <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                <thead style="background-color: {BG_COLOR}; font-weight: 600; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px;">
                    <tr>
                        <th style="padding: 12px 20px; text-align: center; color: #999; border-bottom: 2px solid {BORDER_COLOR};">구분</th>
                        <th style="padding: 12px 20px; text-align: center; color: #999; border-bottom: 2px solid {BORDER_COLOR};">상세 구분</th>
                        <th style="padding: 12px 20px; text-align: center; color: #999; border-bottom: 2px solid {BORDER_COLOR};">이번주 UV</th>
                        <th style="padding: 12px 20px; text-align: center; color: #999; border-bottom: 2px solid {BORDER_COLOR};">지난주 UV</th>
                        <th style="padding: 12px 20px; text-align: center; color: #999; border-bottom: 2px solid {BORDER_COLOR};">변동률</th>
                    </tr>
                </thead>
                <tbody>
    """

    for group in categories:
        group_name = group.get('group', '')
        items = group.get('items', [])

        if not items:
            continue

        # Group header row
        html += f"""
            <tr style="background-color: {BG_COLOR};">
                <td colspan="5" style="padding: 10px 20px; font-weight: bold; color: {TEXT_COLOR}; border-top: 2px solid {BORDER_COLOR}; border-bottom: 1px solid {BORDER_COLOR}; font-size: 13px;">
                    {group_name}
                </td>
            </tr>
        """

        # Group items
        for item in items:
            name = item.get('name', '')
            current_uv = item.get('current', 0)
            prev_uv = item.get('prev', 0)
            rate = item.get('rate', 0)

            # Rate color and icon
            if rate > 0:
                rate_color = '#ef4444'
                rate_icon = '▲'
                rate_bg = 'rgba(239, 68, 68, 0.1)'
            elif rate < 0:
                rate_color = '#3b82f6'
                rate_icon = '▼'
                rate_bg = 'rgba(59, 130, 246, 0.1)'
            else:
                rate_color = '#999'
                rate_icon = ''
                rate_bg = 'rgba(153, 153, 153, 0.1)'

            html += f"""
                <tr style="border-bottom: 1px solid #f1f5f9;">
                    <td style="padding: 10px 20px; font-weight: 500; color: #999; text-align: center;">{group_name.split()[0]}</td>
                    <td style="padding: 10px 20px; font-weight: 500; color: {TEXT_COLOR}; text-align: center;">{name}</td>
                    <td style="padding: 10px 20px; text-align: right; font-weight: 600; color: {TEXT_COLOR};">{current_uv:,}</td>
                    <td style="padding: 10px 20px; text-align: right; color: #999;">{prev_uv:,}</td>
                    <td style="padding: 10px 20px; text-align: right;">
                        <span style="display: inline-flex; align-items: center; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: bold; background-color: {rate_bg}; color: {rate_color};">
                            {rate_icon} {abs(rate)}%
                        </span>
                    </td>
                </tr>
            """

    html += """
                </tbody>
            </table>
        </div>
    </div>
    """

    return html

def generate_channel_type_bars(sorted_channel_types):
    """Generate HTML for channel type distribution bars"""
    if not sorted_channel_types:
        return "<p style='text-align: center; color: #999;'>데이터 없음</p>"

    total_count = sum(count for _, count in sorted_channel_types)
    html = ""

    # Color mapping
    color_map = {
        '브랜드몰': '#6366f1',
        '제휴채널': '#10b981',
        '공식인증예약센터': '#f97316'
    }

    for channel_type, count in sorted_channel_types:
        percentage = (count / total_count * 100) if total_count > 0 else 0
        color = color_map.get(channel_type, '#999')

        html += f"""
            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom: 20px;">
                <tr>
                    <td style="padding-bottom: 8px;">
                        <table width="100%" cellpadding="0" cellspacing="0" border="0">
                            <tr>
                                <td valign="middle">
                                    <span style="display: inline-block; width: 12px; height: 12px; border-radius: 2px; background-color: {color}; vertical-align: middle;"></span>
                                    <span style="font-size: 13px; font-weight: 600; color: {TEXT_COLOR}; vertical-align: middle; margin-left: 8px;">{channel_type}</span>
                                </td>
                                <td align="right">
                                    <span style="font-size: 14px; font-weight: bold; color: {TEXT_COLOR};">{count}개 ({percentage:.0f}%)</span>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
                <tr>
                    <td>
                        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f1f5f9; height: 20px; border-radius: 6px;">
                            <tr>
                                <td width="{percentage}%" style="background-color: {color}; border-radius: 6px;"></td>
                                <td></td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        """

    return html

def generate_email_body_html(email_body):
    """Generate HTML for custom email body section (메일 본문) - 배너 위에 텍스트로만"""
    if not email_body or not email_body.strip():
        return ""
    
    # 줄바꿈 처리
    formatted_body = email_body.replace('\n', '<br>')
    
    html = f"""
    <div style="padding: 10px 10px; background-color: #ffffff;">
        <div style="font-size: 14px; line-height: 0.5; color: {TEXT_COLOR};">
            {formatted_body}
        </div>
    </div>
    """
    
    return html

def generate_ai_insights_html(insights):
    """Generate HTML for AI insights section (핵심 요약)"""
    if not insights:
        return ""

    html = f"""
    <div style="background-color: #ffffff; border: 1px solid {BORDER_COLOR}; border-radius: 8px; padding: 25px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.03);">
        <h3 style="font-size: 16px; font-weight: bold; color: {TEXT_COLOR}; margin: 0 0 20px 0;">핵심 요약</h3>
        <div style="background: linear-gradient(to right, rgba(99, 102, 241, 0.05), rgba(99, 102, 241, 0.02)); border-left: 4px solid {PRIMARY_COLOR}; padding: 20px; border-radius: 0 8px 8px 0;">
    """

    for idx, insight in enumerate(insights):
        title = insight.get('title', '')
        content = insight.get('content', '')
        
        # 모든 줄바꿈 형식을 <br> 태그로 변환
        # Windows (\r\n), Unix (\n), Old Mac (\r) 모두 처리
        content = content.replace('\r\n', '<br>')
        content = content.replace('\n', '<br>')
        content = content.replace('\r', '<br>')
        
        # 추가: 문장 단위로 분리하여 줄바꿈 추가 (마침표 + 공백 또는 끝 패턴)
        # 예: "문장1. 문장2" -> "문장1.<br>문장2"
        import re
        # 마침표 뒤에 숫자가 아닌 문자가 오는 경우에만 줄바꿈 추가
        content = re.sub(r'\. (?=[가-힣A-Za-z])', '.<br>', content)
        
        margin_bottom = '0' if idx == len(insights) - 1 else '20px'

        html += f"""
            <div style="margin-bottom: {margin_bottom};">
                <h4 style="margin: 0 0 8px 0; font-size: 14px; font-weight: bold; color: {PRIMARY_COLOR};">{title}</h4>
                <p style="margin: 0; font-size: 13px; line-height: 1.7; color: {TEXT_COLOR};">{content}</p>
            </div>
        """

    html += """
        </div>
    </div>
    """

    return html

def create_cobrand_table_html(co_brand_data, top20_sum_uv):
    """Create HTML for Co-Brand TOP 20 table with all columns"""
    html = f"""
    <div style="overflow-x: auto;">
        <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
            <thead style="background-color: {BG_COLOR}; font-weight: 600; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px;">
                <tr>
                    <th style="padding: 12px 20px; text-align: center; color: #999; border-bottom: 2px solid {BORDER_COLOR};">순위</th>
                    <th style="padding: 12px 20px; text-align: left; color: #999; border-bottom: 2px solid {BORDER_COLOR};">제휴사명</th>
                    <th style="padding: 12px 20px; text-align: center; color: #999; border-bottom: 2px solid {BORDER_COLOR};">채널유형</th>
                    <th style="padding: 12px 20px; text-align: right; color: #999; border-bottom: 2px solid {BORDER_COLOR};">UV</th>
                    <th style="padding: 12px 20px; text-align: right; color: #999; border-bottom: 2px solid {BORDER_COLOR};">비중(%)</th>
                    <th style="padding: 12px 20px; text-align: right; color: #999; border-bottom: 2px solid {BORDER_COLOR};">증감율</th>
                </tr>
            </thead>
            <tbody>
    """

    for item in co_brand_data:
        rank = item.get('rank', '')
        name = item.get('name', '')
        channel_type = item.get('type', '')
        uv = item.get('uv', 0)
        growth_val = item.get('growth', 0)

        # Calculate percentage
        percentage = (uv / top20_sum_uv * 100) if top20_sum_uv > 0 else 0

        # Channel type badge color
        if '브랜드몰' in channel_type:
            badge_bg = 'rgba(99, 102, 241, 0.1)'
            badge_color = '#6366f1'
        elif '제휴채널' in channel_type:
            badge_bg = 'rgba(16, 185, 129, 0.1)'
            badge_color = '#10b981'
        else:
            badge_bg = 'rgba(249, 115, 22, 0.1)'
            badge_color = '#f97316'

        # Growth color
        if growth_val > 0:
            growth_color = '#ef4444'
            growth_icon = '▲'
        elif growth_val < 0:
            growth_color = '#3b82f6'
            growth_icon = '▼'
        else:
            growth_color = '#999'
            growth_icon = ''

        html += f"""
            <tr style="border-bottom: 1px solid #f1f5f9;">
                <td style="padding: 12px 20px; text-align: center; font-weight: bold; color: #666;">{rank}</td>
                <td style="padding: 12px 20px; font-weight: 500; color: {TEXT_COLOR};">{name}</td>
                <td style="padding: 12px 20px; text-align: center;">
                    <span style="display: inline-block; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; background-color: {badge_bg}; color: {badge_color};">{channel_type}</span>
                </td>
                <td style="padding: 12px 20px; text-align: right; font-family: 'Courier New', monospace; color: {TEXT_COLOR};">{uv:,}</td>
                <td style="padding: 12px 20px; text-align: right; color: #666;">{percentage:.2f}%</td>
                <td style="padding: 12px 20px; text-align: right; font-weight: 600; color: {growth_color};">{growth_icon} {abs(growth_val)}%</td>
            </tr>
        """

    html += """
            </tbody>
        </table>
    </div>
    """

    return html

def create_detailed_top10_card(data_info, title, header_color):
    """Create HTML for Detailed TOP 10 card matching original style"""
    if not data_info or not data_info.get('data'):
        return ""

    total_uv = data_info.get('totalUV', 0)
    growth = data_info.get('growth', 0)
    items = data_info.get('data', [])

    growth_icon = '▲' if growth > 0 else '▼'
    growth_display = f"{growth_icon} {abs(growth)}%" if growth != 0 else "0%"

    html = f"""
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #ffffff; border: 1px solid {BORDER_COLOR}; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.03);">
        <tr>
            <td style="background-color: {header_color}; padding: 16px; color: #ffffff;">
                <table width="100%" cellpadding="0" cellspacing="0" border="0">
                    <tr>
                        <td>
                            <h4 style="margin: 0; font-size: 13px; font-weight: bold;">{title}</h4>
                        </td>
                        <td align="right">
                            <span style="background-color: rgba(255,255,255,0.2); padding: 3px 8px; border-radius: 10px; font-size: 10px; font-weight: 600;">TOP 10</span>
                        </td>
                    </tr>
                </table>
                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top: 8px;">
                    <tr>
                        <td valign="bottom">
                            <div style="font-size: 10px; opacity: 0.8; margin-bottom: 2px;">Total UV</div>
                            <div style="font-size: 18px; font-weight: bold;">{total_uv:,}</div>
                        </td>
                        <td align="right" valign="bottom">
                            <div style="font-size: 10px; opacity: 0.8; margin-bottom: 2px;">전주대비</div>
                            <div style="font-size: 13px; font-weight: bold;">{growth_display}</div>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        <tr>
            <td>
                <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
                    <thead style="background-color: {BG_COLOR}; font-weight: 600; font-size: 11px;">
                        <tr>
                            <th style="padding: 8px 10px; text-align: center; color: #999; width: 35px; height: 32px;">순위</th>
                            <th style="padding: 8px 10px; text-align: left; color: #999; height: 32px;">업체명</th>
                            <th style="padding: 8px 10px; text-align: right; color: #999; height: 32px;">UV</th>
                        </tr>
                    </thead>
                    <tbody>
    """

    for item in items:
        rank = item.get('rank', '')
        name = item.get('name', '')
        uv = item.get('uv', 0)

        html += f"""
                        <tr style="border-bottom: 1px solid #f1f5f9;">
                            <td style="padding: 8px 10px; text-align: center; font-weight: 600; color: #999; height: 34px;">{rank}</td>
                            <td style="padding: 8px 10px; color: {TEXT_COLOR}; max-width: 120px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; height: 34px;" title="{name}">{name}</td>
                            <td style="padding: 8px 10px; text-align: right; font-weight: 600; color: {TEXT_COLOR}; height: 34px;">{uv:,}</td>
                        </tr>
        """

    html += """
                    </tbody>
                </table>
            </td>
        </tr>
    </table>
    """

    return html

def create_table_html(data_source, keys, headers):
    # Handle data source variations
    items = []
    if isinstance(data_source, dict) and 'data' in data_source:
        items = data_source['data']
    elif isinstance(data_source, list):
        items = data_source
        
    html = f"""
    <table style="width: 100%; border-collapse: collapse; font-size: 13px; background-color: white;">
        <thead>
            <tr style="background-color: {BG_COLOR}; border-bottom: 2px solid {BORDER_COLOR};">
    """
    
    for h in headers:
        align = "right" if h == 'UV' else "center"
        html += f'<th style="padding: 10px; text-align: {align}; font-weight: bold; color: {TEXT_COLOR};">{h}</th>'
    
    html += """
            </tr>
        </thead>
        <tbody>
    """
    
    if not items:
        html += f'<tr><td colspan="{len(keys)}" style="padding: 20px; text-align: center; color: #999;">데이터가 없습니다.</td></tr>'
    
    for i, item in enumerate(items):
        if not isinstance(item, dict): continue
        
        bg_style = f'background-color: {BG_COLOR};' if i % 2 != 0 else ''
        border_style = f'border-bottom: 1px solid {BORDER_COLOR};'
        
        html += f'<tr style="{bg_style} {border_style}">'
        
        for key in keys:
            val = item.get(key, '-')
            align = "center"
            weight = "normal"
            
            if key == 'uv':
                try:
                    val = f"{int(val):,}"
                except:
                    pass
                align = "right"
                weight = "bold"
            elif key == 'rank':
                weight = "bold"
                
            html += f'<td style="padding: 8px 10px; text-align: {align}; font-weight: {weight}; color: {TEXT_COLOR};">{val}</td>'
            
        html += "</tr>"
        
    html += """
        </tbody>
    </table>
    """
    return html

def main():
    # 우선순위: 1) Target JSON (2025), 2) Fallback
    json_path_target = r"c:\Users\HANA\Desktop\cob_weekly\data\json\2025년 12월 3주차 주간 UV 레포트현황_20260105_175711.json"
    json_path_fallback = r"c:\Users\HANA\Desktop\cob_weekly\data\html\extracted_data.json"
    data = None

    # Try Target JSON first
    if os.path.exists(json_path_target):
        try:
            data = extract_data_from_json(json_path_target)
            print(f"[OK] Successfully loaded data from: {os.path.basename(json_path_target)}")
        except Exception as e:
            print(f"[ERROR] Error reading Target JSON: {e}")

    # Fallback to extracted_data.json
    if not data and os.path.exists(json_path_fallback):
        try:
            data = extract_data_from_json(json_path_fallback)
            print("[OK] Successfully loaded data from extracted_data.json")
        except Exception as e:
            print(f"[ERROR] Error reading JSON: {e}")

    # If no data, try HTML (with robust search)
    if not data:
        dir_path = r"c:\Users\HANA\Desktop\cob_weekly\data\html"
        file_path = None
        try:
            for f in os.listdir(dir_path):
                if f.endswith(".html") and "2026" in f:
                    file_path = os.path.join(dir_path, f)
                    break
        except:
            pass

        if file_path:
            try:
                data = extract_data_robust(file_path)
                print(f"[OK] Successfully loaded data from HTML: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"[ERROR] Error extracting from HTML: {e}")
                return
        else:
            print("[ERROR] No data source found.")
            return

    output_path = r"c:\Users\HANA\Desktop\cob_weekly\email_report_sample.html"
    
    charts = {}
    
    print("Generating charts...")
    trend_data = data.get('trend', [])
    charts['trend'] = create_trend_chart(trend_data)
        
    print("Generating HTML...")
    html_content = generate_html(data, charts)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"Successfully created: {output_path}")

if __name__ == "__main__":
    main()

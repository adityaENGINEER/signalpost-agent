import http.server
import socketserver
import json
import urllib.parse
import os

from agent.core import SignalpostAgent
from agent.validator import normalize_org_number, format_org_number
from agent.intelligence import calculate_data_quality, answer_company_question
from agent.analytics import get_analytics_metrics

agent = SignalpostAgent()

# Pre-load analytics summary
cached_analytics = get_analytics_metrics()

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NordIntel — AI-Powered Norwegian Company Intelligence Platform</title>
    <!-- Modern Typography: Inter & JetBrains Mono -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --bg-primary: #F7F9FC;
            --surface-main: #FFFFFF;
            --surface-subtle: #F8FAFC;
            --primary-navy: #101828;
            --brand-blue: #3157D5;
            --brand-blue-hover: #2646b3;
            --light-blue: #EAF0FF;
            --primary-text: #172033;
            --secondary-text: #667085;
            --border-color: #E6EAF0;
            --border-hover: #CBD5E1;
            --success: #16805D;
            --success-bg: #ECFDF3;
            --warning: #B7791F;
            --warning-bg: #FEF3C7;
            --error: #D92D20;
            --error-bg: #FEF3F2;
            --shadow-subtle: 0 1px 3px rgba(16, 24, 40, 0.05);
            --shadow-card: 0 4px 12px -2px rgba(16, 24, 40, 0.06);
            --shadow-hover: 0 12px 24px -4px rgba(16, 24, 40, 0.08);
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --sidebar-width: 250px;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            -webkit-font-smoothing: antialiased;
        }

        body {
            background-color: var(--bg-primary);
            color: var(--primary-text);
            min-height: 100vh;
            display: flex;
            overflow-x: hidden;
        }

        /* Sidebar Navigation */
        .sidebar {
            width: var(--sidebar-width);
            background: var(--surface-main);
            border-right: 1px solid var(--border-color);
            position: fixed;
            top: 0;
            bottom: 0;
            left: 0;
            display: flex;
            flex-direction: column;
            z-index: 100;
            transition: transform 0.25s ease;
        }

        .sidebar-brand {
            padding: 1.5rem 1.4rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            border-bottom: 1px solid var(--border-color);
            text-decoration: none;
        }

        .sidebar-logo {
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, var(--brand-blue) 0%, #1a3cb0 100%);
            border-radius: var(--radius-sm);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            font-size: 1.15rem;
            box-shadow: 0 2px 8px rgba(49, 87, 213, 0.28);
        }

        .sidebar-title {
            font-size: 1.15rem;
            font-weight: 800;
            color: var(--primary-navy);
            letter-spacing: -0.02em;
        }

        .sidebar-title span { color: var(--brand-blue); }

        .nav-menu {
            padding: 1.25rem 0.8rem;
            display: flex;
            flex-direction: column;
            gap: 0.35rem;
            flex: 1;
            overflow-y: auto;
        }

        .nav-item {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.65rem 0.95rem;
            border-radius: var(--radius-sm);
            color: var(--secondary-text);
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.15s ease;
        }

        .nav-item:hover {
            color: var(--primary-navy);
            background: var(--bg-primary);
        }

        .nav-item.active {
            color: var(--brand-blue);
            background: var(--light-blue);
            font-weight: 600;
        }

        .nav-item .icon { font-size: 1.1rem; width: 20px; }

        .sidebar-footer {
            padding: 1.2rem;
            border-top: 1px solid var(--border-color);
            font-size: 0.78rem;
            color: var(--secondary-text);
            background: var(--surface-subtle);
        }

        /* Main Workspace Container */
        .workspace {
            margin-left: var(--sidebar-width);
            flex: 1;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            width: calc(100% - var(--sidebar-width));
        }

        /* Top Header Navigation */
        .topbar {
            height: 68px;
            background: var(--surface-main);
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 2.25rem;
            position: sticky;
            top: 0;
            z-index: 90;
        }

        .topbar-left {
            display: flex;
            align-items: center;
            gap: 1.5rem;
        }

        .breadcrumb {
            font-size: 0.9rem;
            color: var(--secondary-text);
            font-weight: 500;
        }

        .breadcrumb strong { color: var(--primary-navy); }

        .quick-top-search {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            background: var(--bg-primary);
            border: 1px solid var(--border-color);
            padding: 0.45rem 0.9rem;
            border-radius: var(--radius-sm);
            width: 280px;
        }

        .quick-top-search input {
            border: none;
            background: transparent;
            outline: none;
            width: 100%;
            font-size: 0.88rem;
            color: var(--primary-navy);
        }

        .topbar-right {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .country-indicator {
            display: flex;
            align-items: center;
            gap: 0.45rem;
            background: var(--light-blue);
            color: var(--brand-blue);
            padding: 0.35rem 0.85rem;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 600;
            border: 1px solid rgba(49, 87, 213, 0.2);
        }

        .live-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: var(--success);
            box-shadow: 0 0 6px rgba(22, 128, 93, 0.5);
        }

        /* Content Views */
        .view-content {
            padding: 2.25rem;
            flex: 1;
            display: none;
            animation: fadeIn 0.25s ease-out;
        }

        .view-content.active { display: block; }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(4px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Search Screen Hero Box */
        .search-hero {
            background: var(--surface-main);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 2.5rem;
            margin-bottom: 2rem;
            box-shadow: var(--shadow-subtle);
        }

        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: var(--brand-blue);
            background: var(--light-blue);
            padding: 0.3rem 0.8rem;
            border-radius: 9999px;
            margin-bottom: 0.75rem;
        }

        .hero-title {
            font-size: 2.25rem;
            font-weight: 800;
            color: var(--primary-navy);
            letter-spacing: -0.03em;
            line-height: 1.2;
            margin-bottom: 0.5rem;
        }

        .hero-subtitle {
            font-size: 1.05rem;
            color: var(--secondary-text);
            max-width: 820px;
            line-height: 1.6;
            margin-bottom: 1.75rem;
        }

        /* Big Search Input */
        .search-bar-row {
            display: flex;
            gap: 0.75rem;
            margin-bottom: 1.25rem;
        }

        .search-field-box {
            flex: 1;
            display: flex;
            align-items: center;
            gap: 0.85rem;
            background: var(--surface-subtle);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 0.8rem 1.25rem;
            transition: all 0.2s ease;
        }

        .search-field-box:focus-within {
            background: #ffffff;
            border-color: var(--brand-blue);
            box-shadow: 0 0 0 4px rgba(49, 87, 213, 0.12);
        }

        .input-org {
            width: 100%;
            border: none;
            outline: none;
            font-size: 1.2rem;
            font-weight: 600;
            color: var(--primary-navy);
            background: transparent;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: 0.04em;
        }

        .input-org::placeholder {
            font-family: 'Inter', sans-serif;
            font-weight: 400;
            color: #98A2B3;
            font-size: 1rem;
            letter-spacing: normal;
        }

        .btn-primary {
            background: var(--brand-blue);
            color: #ffffff;
            border: none;
            border-radius: var(--radius-md);
            padding: 0 2.2rem;
            font-size: 1rem;
            font-weight: 700;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            transition: all 0.15s ease;
            box-shadow: 0 2px 6px rgba(49, 87, 213, 0.25);
            white-space: nowrap;
        }

        .btn-primary:hover { background: var(--brand-blue-hover); }
        .btn-primary:active { transform: scale(0.98); }

        .chips-line {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            flex-wrap: wrap;
            font-size: 0.85rem;
        }

        .chip-tag {
            background: var(--surface-subtle);
            border: 1px solid var(--border-color);
            color: var(--primary-text);
            padding: 0.35rem 0.75rem;
            border-radius: var(--radius-sm);
            font-size: 0.82rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.15s;
        }

        .chip-tag:hover {
            border-color: var(--brand-blue);
            color: var(--brand-blue);
            background: var(--light-blue);
        }

        .error-banner {
            display: none;
            background: var(--error-bg);
            border: 1px solid rgba(217, 45, 32, 0.25);
            color: var(--error);
            padding: 0.9rem 1.25rem;
            border-radius: var(--radius-md);
            font-size: 0.92rem;
            font-weight: 500;
            margin-top: 1.25rem;
            align-items: center;
            gap: 0.6rem;
        }

        /* Profile Container Cards */
        .profile-hero-card {
            background: var(--surface-main);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 2.25rem;
            margin-bottom: 1.75rem;
            box-shadow: var(--shadow-card);
        }

        .profile-hero-top {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 1.5rem;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
        }

        .profile-brand-box {
            display: flex;
            align-items: center;
            gap: 1.25rem;
        }

        .avatar-box {
            width: 60px;
            height: 60px;
            background: var(--light-blue);
            border: 1px solid rgba(49, 87, 213, 0.25);
            color: var(--brand-blue);
            border-radius: var(--radius-md);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            font-weight: 800;
        }

        .comp-title {
            font-size: 2rem;
            font-weight: 800;
            color: var(--primary-navy);
            letter-spacing: -0.025em;
            margin-bottom: 0.4rem;
        }

        .comp-sub-row {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            flex-wrap: wrap;
        }

        .badge-id {
            font-family: 'JetBrains Mono', monospace;
            background: var(--bg-primary);
            border: 1px solid var(--border-color);
            color: var(--primary-navy);
            padding: 0.25rem 0.65rem;
            border-radius: 6px;
            font-size: 0.9rem;
            font-weight: 700;
        }

        .badge-status {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.4rem 0.95rem;
            border-radius: 9999px;
            font-size: 0.82rem;
            font-weight: 700;
            text-transform: uppercase;
        }

        .badge-status.active {
            background: var(--success-bg);
            color: var(--success);
            border: 1px solid rgba(22, 128, 93, 0.3);
        }

        .badge-status.inactive {
            background: var(--error-bg);
            color: var(--error);
            border: 1px solid rgba(217, 45, 32, 0.3);
        }

        /* 4 KPI Grid */
        .kpi-row {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1.25rem;
            margin-bottom: 1.5rem;
        }

        @media (max-width: 1024px) { .kpi-row { grid-template-columns: repeat(2, 1fr); } }
        @media (max-width: 640px) { .kpi-row { grid-template-columns: 1fr; } }

        .kpi-card {
            background: var(--surface-subtle);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 1.1rem 1.25rem;
        }

        .kpi-lbl {
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--secondary-text);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.35rem;
        }

        .kpi-num {
            font-size: 1.35rem;
            font-weight: 800;
            color: var(--primary-navy);
        }

        /* Summary Box */
        .summary-callout {
            background: var(--surface-subtle);
            border-left: 4px solid var(--brand-blue);
            padding: 1.1rem 1.4rem;
            border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
            font-size: 0.95rem;
            line-height: 1.6;
            margin-bottom: 1.5rem;
            color: #334155;
        }

        /* Action Toolbar */
        .action-tray {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            border-top: 1px solid var(--border-color);
            padding-top: 1.25rem;
            flex-wrap: wrap;
        }

        .btn-tool {
            background: var(--surface-main);
            border: 1px solid var(--border-color);
            color: var(--primary-text);
            padding: 0.5rem 0.95rem;
            border-radius: var(--radius-sm);
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            transition: all 0.15s ease;
        }

        .btn-tool:hover {
            background: var(--bg-primary);
            border-color: var(--border-hover);
        }

        /* 3-Column Profile Grid */
        .profile-3col {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 1.5rem;
            align-items: start;
        }

        @media (max-width: 1200px) { .profile-3col { grid-template-columns: 1fr 1fr; } }
        @media (max-width: 800px) { .profile-3col { grid-template-columns: 1fr; } }

        .dash-box {
            background: var(--surface-main);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 1.5rem;
            box-shadow: var(--shadow-card);
            margin-bottom: 1.5rem;
        }

        .dash-box-head {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.1rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid var(--border-color);
        }

        .dash-box-title {
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--primary-navy);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .prop-item-box {
            margin-bottom: 0.85rem;
        }

        .prop-k {
            font-size: 0.76rem;
            font-weight: 600;
            color: var(--secondary-text);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 0.2rem;
        }

        .prop-v {
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--primary-navy);
            word-break: break-word;
        }

        .prop-v a { color: var(--brand-blue); text-decoration: none; }
        .prop-v a:hover { text-decoration: underline; }

        /* AI Interactive Chat Assistant Box */
        .chat-container {
            background: var(--surface-subtle);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 1.1rem;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }

        .chat-history {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            max-height: 280px;
            overflow-y: auto;
        }

        .chat-bubble {
            padding: 0.75rem 1rem;
            border-radius: var(--radius-sm);
            font-size: 0.88rem;
            line-height: 1.5;
        }

        .chat-bubble.user {
            background: var(--light-blue);
            color: var(--brand-blue);
            align-self: flex-end;
            font-weight: 600;
        }

        .chat-bubble.agent {
            background: #ffffff;
            border: 1px solid var(--border-color);
            color: var(--primary-text);
            align-self: flex-start;
        }

        .chat-suggested {
            display: flex;
            gap: 0.4rem;
            flex-wrap: wrap;
        }

        .suggested-btn {
            background: #ffffff;
            border: 1px solid var(--border-color);
            padding: 0.3rem 0.65rem;
            border-radius: 999px;
            font-size: 0.76rem;
            font-weight: 500;
            cursor: pointer;
            color: var(--secondary-text);
            transition: all 0.15s;
        }

        .suggested-btn:hover {
            color: var(--brand-blue);
            border-color: var(--brand-blue);
        }

        .chat-input-row {
            display: flex;
            gap: 0.5rem;
        }

        .chat-input {
            flex: 1;
            padding: 0.55rem 0.85rem;
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            outline: none;
            font-size: 0.88rem;
        }

        .chat-input:focus { border-color: var(--brand-blue); }

        .btn-ask {
            background: var(--brand-blue);
            color: #ffffff;
            border: none;
            border-radius: var(--radius-sm);
            padding: 0 1rem;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
        }

        /* Quality Score Circle / Gauge */
        .quality-header-gauge {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1rem 1.25rem;
            background: var(--surface-subtle);
            border-radius: var(--radius-md);
            margin-bottom: 1.25rem;
        }

        .quality-score-large {
            font-size: 2.2rem;
            font-weight: 800;
            color: var(--brand-blue);
            font-family: 'JetBrains Mono', monospace;
        }

        .check-item {
            display: flex;
            align-items: flex-start;
            gap: 0.6rem;
            padding: 0.6rem 0;
            border-bottom: 1px solid var(--border-color);
            font-size: 0.85rem;
        }

        .check-icon { font-size: 1rem; line-height: 1; }
        .check-icon.pass { color: var(--success); }
        .check-icon.fail { color: var(--error); }

        /* Comparison Table View */
        .comparison-table-wrapper {
            background: var(--surface-main);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            overflow-x: auto;
            box-shadow: var(--shadow-card);
            margin-top: 1.5rem;
        }

        .comparison-table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 0.9rem;
        }

        .comparison-table th, .comparison-table td {
            padding: 1rem 1.25rem;
            border-bottom: 1px solid var(--border-color);
        }

        .comparison-table th {
            background: var(--surface-subtle);
            color: var(--secondary-text);
            font-size: 0.82rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        /* Analytics Grid */
        .analytics-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
        }

        @media (max-width: 900px) { .analytics-grid { grid-template-columns: 1fr; } }

        .stat-bar-row {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 0.75rem;
            font-size: 0.86rem;
        }

        .stat-bar-label { width: 180px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .stat-bar-track { flex: 1; background: var(--bg-primary); height: 10px; border-radius: 999px; overflow: hidden; }
        .stat-bar-fill { background: var(--brand-blue); height: 100%; border-radius: 999px; }
        .stat-bar-count { width: 40px; text-align: right; font-weight: 700; font-family: 'JetBrains Mono', monospace; }

        /* Toast Popup */
        .toast-box {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            background: var(--primary-navy);
            color: #ffffff;
            padding: 0.85rem 1.4rem;
            border-radius: var(--radius-md);
            font-size: 0.9rem;
            font-weight: 600;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            display: none;
            align-items: center;
            gap: 0.6rem;
            z-index: 1000;
            animation: slideUp 0.25s ease-out;
        }

        @keyframes slideUp {
            from { transform: translateY(15px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
    </style>
</head>
<body>

    <!-- Sidebar Navigation -->
    <aside class="sidebar" id="sidebar">
        <a href="javascript:void(0)" onclick="switchTab('search')" class="sidebar-brand">
            <div class="sidebar-logo">⚡</div>
            <div class="sidebar-title">Nord<span>Intel</span></div>
        </a>

        <nav class="nav-menu">
            <a href="javascript:void(0)" onclick="switchTab('overview')" class="nav-item" id="nav-overview">
                <span class="icon">📊</span> Overview
            </a>
            <a href="javascript:void(0)" onclick="switchTab('search')" class="nav-item active" id="nav-search">
                <span class="icon">🔍</span> Company Search
            </a>
            <a href="javascript:void(0)" onclick="switchTab('comparison')" class="nav-item" id="nav-comparison">
                <span class="icon">⚖️</span> Comparison
            </a>
            <a href="javascript:void(0)" onclick="switchTab('quality')" class="nav-item" id="nav-quality">
                <span class="icon">🛡️</span> Data Quality
            </a>
            <a href="javascript:void(0)" onclick="switchTab('analytics')" class="nav-item" id="nav-analytics">
                <span class="icon">📈</span> Analytics
            </a>
            <a href="javascript:void(0)" onclick="switchTab('history')" class="nav-item" id="nav-history">
                <span class="icon">🕒</span> Search History
            </a>
            <a href="javascript:void(0)" onclick="switchTab('sources')" class="nav-item" id="nav-sources">
                <span class="icon">🌐</span> Data Sources
            </a>
        </nav>

        <div class="sidebar-footer">
            <div>Data: <strong>Brønnøysundregistrene</strong></div>
            <div style="margin-top: 0.25rem;">Signalpost Agentic Platform</div>
        </div>
    </aside>

    <!-- Main Workspace Container -->
    <div class="workspace">
        
        <!-- Top Navigation Bar -->
        <header class="topbar">
            <div class="topbar-left">
                <div class="breadcrumb" id="currentSectionTitle">
                    Section / <strong>Company Search</strong>
                </div>
            </div>

            <div class="topbar-right">
                <div class="quick-top-search">
                    <span>🔍</span>
                    <input 
                        type="text" 
                        placeholder="Quick 9-digit Org lookup..." 
                        maxlength="14"
                        onkeydown="if(event.key==='Enter'){ quickTopLookup(this.value); this.value=''; }"
                    >
                </div>
                <div class="country-indicator">
                    <span class="live-dot"></span>
                    <span>🇳🇴</span> Norway Live Registry
                </div>
            </div>
        </header>

        <!-- 1. TAB: COMPANY SEARCH (PRIMARY) -->
        <section class="view-content active" id="view-search">
            
            <!-- Hero Search Component -->
            <div class="search-hero">
                <div class="hero-badge">
                    <span>🇳🇴</span> NORWAY BUSINESS INTELLIGENCE
                </div>
                <h1 class="hero-title">Know Every Company Behind the Number.</h1>
                <p class="hero-subtitle">
                    Search a Norwegian organization's 9-digit number to explore its company profile, registration details, business information, and available public records.
                </p>

                <!-- Search Input Row -->
                <div class="search-bar-row">
                    <div class="search-field-box">
                        <span style="font-size: 1.35rem;">🇳🇴</span>
                        <input 
                            type="text" 
                            id="orgInput" 
                            class="input-org" 
                            placeholder="Enter 9-digit organization number (e.g. 923 609 016)" 
                            maxlength="14"
                            autocomplete="off"
                        >
                    </div>
                    <button class="btn-primary" onclick="handleSearchClick()">
                        <span>🔍</span> Find Company
                    </button>
                </div>

                <!-- Chips -->
                <div class="chips-line">
                    <span style="color:var(--secondary-text); font-weight:600;">Verified Samples:</span>
                    <button class="chip-tag" onclick="quickFill('923 609 016')">Equinor ASA (923 609 016)</button>
                    <button class="chip-tag" onclick="quickFill('916 627 939')">Palmera (916 627 939)</button>
                    <button class="chip-tag" onclick="quickFill('989 061 593')">G-Group AS (989 061 593)</button>
                    <button class="chip-tag" onclick="quickFill('988 539 473')">EBE-Data (988 539 473)</button>
                </div>

                <!-- Inline Error Banner -->
                <div class="error-banner" id="searchError">
                    <span style="font-size: 1.15rem;">⚠️</span>
                    <span id="searchErrorText">Please enter a valid 9-digit Norwegian organization number.</span>
                </div>
            </div>

            <!-- Loading State -->
            <div class="dash-box" id="searchLoader" style="display:none; text-align:center; padding: 3rem 1rem;">
                <div style="width:36px; height:36px; border:3px solid #E2E8F0; border-top:3px solid var(--brand-blue); border-radius:50%; animation:spin 0.75s linear infinite; margin:0 auto 1rem;"></div>
                <div style="font-size:1.1rem; font-weight:700; color:var(--primary-navy);">Looking up company information...</div>
                <div style="font-size:0.88rem; color:var(--secondary-text); margin-top:0.25rem;">Querying Brønnøysundregistrene & extracting verified registry facts</div>
            </div>

            <!-- Profile Dashboard View -->
            <div id="companyProfileView" style="display:none;">
                
                <!-- Profile Hero Card -->
                <div class="profile-hero-card">
                    <div class="profile-hero-top">
                        <div class="profile-brand-box">
                            <div class="avatar-box" id="profAvatar">EQ</div>
                            <div>
                                <h2 class="comp-title" id="profName">-</h2>
                                <div class="comp-sub-row">
                                    <span class="badge-id" id="profOrg">ORG: -</span>
                                    <span class="badge-id" id="profType" style="color:var(--brand-blue);">-</span>
                                </div>
                            </div>
                        </div>
                        <div class="badge-status active" id="profStatusBadge">
                            <span class="live-dot"></span>
                            <span id="profStatusText">ACTIVE & REGISTERED</span>
                        </div>
                    </div>

                    <!-- 4 KPIs -->
                    <div class="kpi-row">
                        <div class="kpi-card">
                            <div class="kpi-lbl">Registered Headcount</div>
                            <div class="kpi-num" id="kpiStaff">-</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-lbl">Registration Date</div>
                            <div class="kpi-num" id="kpiDate">-</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-lbl">Registered City</div>
                            <div class="kpi-num" id="kpiCity">-</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-lbl">Data Quality Score</div>
                            <div class="kpi-num" id="kpiQuality" style="color:var(--brand-blue);">-</div>
                        </div>
                    </div>

                    <!-- Executive Briefing -->
                    <div class="summary-callout" id="profSummary">-</div>

                    <!-- Actions Toolbar -->
                    <div class="action-tray">
                        <button class="btn-tool" onclick="copyCurrentOrg()">
                            <span>📋</span> Copy Org Number
                        </button>
                        <button class="btn-tool" onclick="copyCurrentName()">
                            <span>📋</span> Copy Company Name
                        </button>
                        <button class="btn-tool" onclick="addToComparison()">
                            <span>⚖️</span> Add to Comparison
                        </button>
                        <button class="btn-tool" onclick="shareProfile()">
                            <span>🔗</span> Share Profile
                        </button>
                        <button class="btn-tool" onclick="exportJSON()">
                            <span>📥</span> Export JSON
                        </button>
                        <button class="btn-tool" onclick="exportCSV()">
                            <span>📊</span> Export CSV
                        </button>
                        <button class="btn-tool" onclick="window.print()">
                            <span>🖨️</span> Print / Save PDF
                        </button>
                    </div>
                </div>

                <!-- 3 Columns Details -->
                <div class="profile-3col">
                    
                    <!-- Col 1: Registration Details -->
                    <div class="dash-box">
                        <div class="dash-box-head">
                            <h3 class="dash-box-title"><span>📋</span> Registration & Legal</h3>
                        </div>
                        <div class="prop-item-box">
                            <div class="prop-k">Legal Registered Name</div>
                            <div class="prop-v" id="detailLegalName">-</div>
                        </div>
                        <div class="prop-item-box">
                            <div class="prop-k">Organization Number</div>
                            <div class="prop-v" id="detailOrgNr" style="font-family:'JetBrains Mono';">-</div>
                        </div>
                        <div class="prop-item-box">
                            <div class="prop-k">Legal Entity Form</div>
                            <div class="prop-v" id="detailOrgForm">-</div>
                        </div>
                        <div class="prop-item-box">
                            <div class="prop-k">Registration Date</div>
                            <div class="prop-v" id="detailRegDate">-</div>
                        </div>
                        <div class="prop-item-box">
                            <div class="prop-k">Solvency / Bankruptcy Status</div>
                            <div class="prop-v" id="detailSolvency">-</div>
                        </div>
                    </div>

                    <!-- Col 2: Operations & Location -->
                    <div class="dash-box">
                        <div class="dash-box-head">
                            <h3 class="dash-box-title"><span>📍</span> Industry & Location</h3>
                        </div>
                        <div class="prop-item-box">
                            <div class="prop-k">NACE Classification</div>
                            <div class="prop-v" id="detailNace">-</div>
                        </div>
                        <div class="prop-item-box">
                            <div class="prop-k">Industry Activity</div>
                            <div class="prop-v" id="detailIndustry">-</div>
                        </div>
                        <div class="prop-item-box">
                            <div class="prop-k">Headquarters Address</div>
                            <div class="prop-v" id="detailAddress">-</div>
                        </div>
                        <div class="prop-item-box">
                            <div class="prop-k">Official Website</div>
                            <div class="prop-v" id="detailWebsite">-</div>
                        </div>
                    </div>

                    <!-- Col 3: AI Contextual Assistant & Verified Source Evidence -->
                    <div class="dash-box">
                        <div class="dash-box-head">
                            <h3 class="dash-box-title"><span>🤖</span> AI Company Assistant</h3>
                            <span style="font-size:0.75rem; font-weight:700; color:var(--brand-blue); background:var(--light-blue); padding:0.2rem 0.5rem; border-radius:4px;">Grounded</span>
                        </div>
                        
                        <div class="chat-container">
                            <div class="chat-history" id="chatHistory">
                                <div class="chat-bubble agent">
                                    Hello! Ask me any specific question about this company's registration, employees, or verified facts.
                                </div>
                            </div>
                            
                            <div class="chat-suggested">
                                <button class="suggested-btn" onclick="askQuestion('What does this company do?')">What does it do?</button>
                                <button class="suggested-btn" onclick="askQuestion('How many employees are registered?')">Employee count?</button>
                                <button class="suggested-btn" onclick="askQuestion('Is this company active or bankrupt?')">Operating status?</button>
                                <button class="suggested-btn" onclick="askQuestion('Which company details are missing?')">Missing info?</button>
                            </div>

                            <div class="chat-input-row">
                                <input type="text" id="chatInput" class="chat-input" placeholder="Ask about this company..." onkeydown="if(event.key==='Enter') submitChatQuestion();">
                                <button class="btn-ask" onclick="submitChatQuestion()">Ask</button>
                            </div>
                        </div>

                    </div>

                </div>

            </div>

        </section>

        <!-- 2. TAB: OVERVIEW -->
        <section class="view-content" id="view-overview">
            <div class="search-hero">
                <div class="hero-badge">PLATFORM SUMMARY</div>
                <h1 class="hero-title">Company Intelligence Overview</h1>
                <p class="hero-subtitle">
                    Search, understand, compare, and analyze Norwegian company information from official registries.
                </p>
                <div style="display:flex; gap:1rem;">
                    <button class="btn-primary" onclick="switchTab('search')"><span>🔍</span> Search a Company</button>
                    <button class="btn-tool" onclick="switchTab('analytics')"><span>📊</span> View Dataset Analytics</button>
                </div>
            </div>

            <div class="kpi-row">
                <div class="kpi-card">
                    <div class="kpi-lbl">Dataset Records Stored</div>
                    <div class="kpi-num" id="ovTotalRecords">1,001</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-lbl">Active Entities</div>
                    <div class="kpi-num" id="ovActiveRecords" style="color:var(--success);">1,001</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-lbl">Average Data Quality</div>
                    <div class="kpi-num" id="ovQuality">93.8%</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-lbl">Source Authority</div>
                    <div class="kpi-num" style="font-size:1.1rem; color:var(--brand-blue);">Brønnøysundregistrene</div>
                </div>
            </div>

            <div class="dash-box">
                <div class="dash-box-head">
                    <h3 class="dash-box-title"><span>⚡</span> Platform Highlights</h3>
                </div>
                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:1.25rem;">
                    <div style="background:var(--surface-subtle); padding:1.25rem; border-radius:var(--radius-md); border:1px solid var(--border-color);">
                        <div style="font-weight:700; color:var(--primary-navy); margin-bottom:0.4rem;">Zero Hallucination</div>
                        <div style="font-size:0.88rem; color:var(--secondary-text);">Every fact is directly linked with public authority URLs and verified ISO timestamps.</div>
                    </div>
                    <div style="background:var(--surface-subtle); padding:1.25rem; border-radius:var(--radius-md); border:1px solid var(--border-color);">
                        <div style="font-weight:700; color:var(--primary-navy); margin-bottom:0.4rem;">Deterministic Quality Engine</div>
                        <div style="font-size:0.88rem; color:var(--secondary-text);">Mathematical rule-based scoring (60% required, 40% informational) for enterprise compliance.</div>
                    </div>
                    <div style="background:var(--surface-subtle); padding:1.25rem; border-radius:var(--radius-md); border:1px solid var(--border-color);">
                        <div style="font-weight:700; color:var(--primary-navy); margin-bottom:0.4rem;">AI Contextual Assistant</div>
                        <div style="font-size:0.88rem; color:var(--secondary-text);">Answers natural-language corporate questions grounded strictly on live registry payloads.</div>
                    </div>
                </div>
            </div>
        </section>

        <!-- 3. TAB: COMPARISON -->
        <section class="view-content" id="view-comparison">
            <div class="dash-box">
                <div class="dash-box-head">
                    <h3 class="dash-box-title"><span>⚖️</span> Norwegian Company Comparison</h3>
                    <button class="btn-tool" onclick="clearComparison()">Clear Comparison</button>
                </div>
                <p style="font-size:0.9rem; color:var(--secondary-text); margin-bottom:1.25rem;">
                    Compare multiple Norwegian companies side-by-side across legal structure, employee headcount, industry activity, and data completeness.
                </p>

                <div class="comparison-table-wrapper">
                    <table class="comparison-table" id="comparisonTable">
                        <thead>
                            <tr>
                                <th>Attribute</th>
                                <th id="compHead1">Company A</th>
                                <th id="compHead2">Company B</th>
                                <th id="compHead3">Company C</th>
                            </tr>
                        </thead>
                        <tbody id="comparisonBody">
                            <tr><td colspan="4" style="text-align:center; color:var(--secondary-text); padding:2.5rem;">No companies added to comparison yet. Search a company and click "Add to Comparison".</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- 4. TAB: DATA QUALITY -->
        <section class="view-content" id="view-quality">
            <div class="dash-box">
                <div class="dash-box-head">
                    <h3 class="dash-box-title"><span>🛡️</span> Corporate Data Quality Engine</h3>
                </div>
                <p style="font-size:0.9rem; color:var(--secondary-text); margin-bottom:1.5rem;">
                    Deterministic compliance validation formula: 4 Required Fields (60% total weight) + 4 Informational Fields (40% total weight).
                </p>

                <div class="quality-header-gauge">
                    <div>
                        <div style="font-size:0.82rem; font-weight:700; color:var(--secondary-text); text-transform:uppercase;">Evaluated Record Score</div>
                        <div style="font-size:1.05rem; font-weight:700; color:var(--primary-navy);" id="qualitySubjectName">Current Company</div>
                    </div>
                    <div class="quality-score-large" id="qualityScoreVal">--%</div>
                </div>

                <div id="qualityChecksList">
                    <div style="color:var(--secondary-text); font-size:0.9rem;">Perform a company search to inspect its granular rule-by-rule data quality audit report.</div>
                </div>
            </div>
        </section>

        <!-- 5. TAB: ANALYTICS -->
        <section class="view-content" id="view-analytics">
            <div class="dash-box">
                <div class="dash-box-head">
                    <h3 class="dash-box-title"><span>📈</span> Dataset Analytics & Distribution</h3>
                    <span style="font-size:0.82rem; font-weight:600; color:var(--brand-blue); background:var(--light-blue); padding:0.25rem 0.65rem; border-radius:4px;">1,001 Verified Entities</span>
                </div>
                <p style="font-size:0.9rem; color:var(--secondary-text); margin-bottom:1.5rem;">
                    Real distributions derived from the official 1,000+ Norwegian company dataset stored in this platform.
                </p>

                <div class="analytics-grid">
                    <!-- Top Industries -->
                    <div style="background:var(--surface-subtle); padding:1.4rem; border-radius:var(--radius-md); border:1px solid var(--border-color);">
                        <div style="font-size:0.95rem; font-weight:700; color:var(--primary-navy); margin-bottom:1rem;">Top NACE Industries</div>
                        <div id="analyticsIndustryBars"></div>
                    </div>

                    <!-- Top Entity Types -->
                    <div style="background:var(--surface-subtle); padding:1.4rem; border-radius:var(--radius-md); border:1px solid var(--border-color);">
                        <div style="font-size:0.95rem; font-weight:700; color:var(--primary-navy); margin-bottom:1rem;">Corporate Legal Forms</div>
                        <div id="analyticsTypeBars"></div>
                    </div>
                </div>
            </div>
        </section>

        <!-- 6. TAB: SEARCH HISTORY -->
        <section class="view-content" id="view-history">
            <div class="dash-box">
                <div class="dash-box-head">
                    <h3 class="dash-box-title"><span>🕒</span> Search History & Audits</h3>
                    <button class="btn-tool" onclick="clearSearchHistory()">Clear All History</button>
                </div>
                <p style="font-size:0.9rem; color:var(--secondary-text); margin-bottom:1.25rem;">
                    Locally stored session searches for fast instant re-opening without redundant network calls.
                </p>
                <div id="fullHistoryList" style="display:flex; flex-direction:column; gap:0.65rem;"></div>
            </div>
        </section>

        <!-- 7. TAB: DATA SOURCES -->
        <section class="view-content" id="view-sources">
            <div class="dash-box">
                <div class="dash-box-head">
                    <h3 class="dash-box-title"><span>🌐</span> Authoritative Public Data Sources</h3>
                </div>
                <p style="font-size:0.92rem; color:var(--secondary-text); margin-bottom:1.5rem;">
                    NordIntel adheres to zero-hallucination standards. All records originate directly from Norway's official statutory registers.
                </p>

                <div style="display:flex; flex-direction:column; gap:1.2rem;">
                    <div style="background:var(--surface-subtle); padding:1.25rem; border-radius:var(--radius-md); border:1px solid var(--border-color);">
                        <div style="font-size:1.05rem; font-weight:700; color:var(--primary-navy); margin-bottom:0.3rem;">1. Brønnøysundregistrene (Enhetsregisteret)</div>
                        <div style="font-size:0.88rem; color:var(--secondary-text); margin-bottom:0.6rem;">Provides legal names, 9-digit org numbers, registration dates, corporate forms, and registered business locations.</div>
                        <a href="https://data.brreg.no/enhetsregisteret/api" target="_blank" style="color:var(--brand-blue); font-size:0.85rem; font-weight:600; text-decoration:none;">🔗 Open Government API: data.brreg.no/enhetsregisteret/api</a>
                    </div>

                    <div style="background:var(--surface-subtle); padding:1.25rem; border-radius:var(--radius-md); border:1px solid var(--border-color);">
                        <div style="font-size:1.05rem; font-weight:700; color:var(--primary-navy); margin-bottom:0.3rem;">2. NAV & Aa-registeret (Employee Registry)</div>
                        <div style="font-size:0.88rem; color:var(--secondary-text); margin-bottom:0.6rem;">Official public counts of registered salaried personnel and staff headcounts.</div>
                        <a href="https://virksomhet.brreg.no" target="_blank" style="color:var(--brand-blue); font-size:0.85rem; font-weight:600; text-decoration:none;">🔗 Official Portal Reference: virksomhet.brreg.no</a>
                    </div>

                    <div style="background:var(--surface-subtle); padding:1.25rem; border-radius:var(--radius-md); border:1px solid var(--border-color);">
                        <div style="font-size:1.05rem; font-weight:700; color:var(--primary-navy); margin-bottom:0.3rem;">3. Konkursregisteret (Insolvency Register)</div>
                        <div style="font-size:0.88rem; color:var(--secondary-text); margin-bottom:0.6rem;">National bankruptcy and liquidation status tracking for operational solvency confirmation.</div>
                        <a href="https://www.brreg.no/om-oss/registrene-vare/konkursregisteret/" target="_blank" style="color:var(--brand-blue); font-size:0.85rem; font-weight:600; text-decoration:none;">🔗 Official Authority Registry: Konkursregisteret</a>
                    </div>
                </div>
            </div>
        </section>

    </div>

    <!-- Notification Toast -->
    <div class="toast-box" id="toast">
        <span id="toastIcon">✓</span>
        <span id="toastText">Action completed successfully</span>
    </div>

    <script>
        const ERROR_MESSAGE = "Please enter a valid 9-digit Norwegian organization number.";
        const inputElem = document.getElementById('orgInput');
        let currentProfileData = null;
        let comparisonList = [];

        // Tab Navigation Switcher
        function switchTab(tabId) {
            document.querySelectorAll('.view-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            
            const targetView = document.getElementById(`view-${tabId}`);
            const targetNav = document.getElementById(`nav-${tabId}`);
            if (targetView) targetView.classList.add('active');
            if (targetNav) targetNav.classList.add('active');

            const titleMap = {
                'overview': 'Platform Overview',
                'search': 'Company Search',
                'comparison': 'Company Comparison',
                'quality': 'Data Quality Checker',
                'analytics': 'Dataset Analytics',
                'history': 'Search History',
                'sources': 'Authoritative Data Sources'
            };
            document.getElementById('currentSectionTitle').innerHTML = `Section / <strong>${titleMap[tabId] || 'Dashboard'}</strong>`;

            if (tabId === 'history') renderFullHistory();
            if (tabId === 'analytics') renderAnalyticsUI();
        }

        // Validation & Normalization
        function validateAndNormalizeOrg(raw) {
            if (!raw) return { isValid: false, normalized: null, error: ERROR_MESSAGE };
            const stripped = raw.replace(/\\s+/g, '');
            if (!/^\\d+$/.test(stripped)) {
                return { isValid: false, normalized: null, error: ERROR_MESSAGE };
            }
            if (stripped.length !== 9) {
                return { isValid: false, normalized: null, error: ERROR_MESSAGE };
            }
            return { isValid: true, normalized: stripped, error: null };
        }

        function formatOrgDisplay(raw) {
            if (!raw) return '';
            const digits = raw.toString().replace(/\\D/g, '').substring(0, 9);
            const parts = [];
            if (digits.length > 0) parts.push(digits.substring(0, 3));
            if (digits.length > 3) parts.push(digits.substring(3, 6));
            if (digits.length > 6) parts.push(digits.substring(6, 9));
            return parts.join(' ');
        }

        // Intelligent auto-spacing while typing
        inputElem.addEventListener('input', function(e) {
            const cursorStart = this.selectionStart;
            const prevVal = this.value;
            const digitsOnly = prevVal.replace(/\\s+/g, '');
            if (/^\\d*$/.test(digitsOnly)) {
                const formatted = formatOrgDisplay(digitsOnly);
                if (formatted !== prevVal) {
                    this.value = formatted;
                    let newCursor = cursorStart;
                    if (e.inputType === 'insertText' || e.inputType === 'insertFromPaste') {
                        if (newCursor === 4 || newCursor === 8) newCursor += 1;
                    }
                    this.setSelectionRange(newCursor, newCursor);
                }
            }
        });

        // Paste support
        inputElem.addEventListener('paste', function(e) {
            e.preventDefault();
            const text = (e.clipboardData || window.clipboardData).getData('text');
            const clean = text.replace(/\\s+/g, '');
            if (/^\\d+$/.test(clean)) {
                this.value = formatOrgDisplay(clean);
            } else {
                this.value = text.trim();
            }
        });

        inputElem.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') handleSearchClick();
        });

        function showSearchError(msg) {
            const b = document.getElementById('searchError');
            document.getElementById('searchErrorText').innerText = msg;
            b.style.display = 'flex';
        }

        function hideSearchError() {
            document.getElementById('searchError').style.display = 'none';
        }

        function showToast(msg) {
            const t = document.getElementById('toast');
            document.getElementById('toastText').innerText = msg;
            t.style.display = 'flex';
            setTimeout(() => { t.style.display = 'none'; }, 2600);
        }

        function quickFill(org) {
            inputElem.value = formatOrgDisplay(org);
            handleSearchClick();
        }

        function quickTopLookup(val) {
            switchTab('search');
            inputElem.value = val;
            handleSearchClick();
        }

        // Local Storage for Recent Searches
        function getHistory() {
            try { return JSON.parse(localStorage.getItem('nordintel_history') || '[]'); }
            catch(e) { return []; }
        }

        function saveHistory(org, name) {
            try {
                let h = getHistory();
                h = h.filter(x => x.org !== org);
                h.unshift({ org, name, timestamp: Date.now() });
                if (h.length > 20) h = h.slice(0, 20);
                localStorage.setItem('nordintel_history', JSON.stringify(h));
            } catch(e) {}
        }

        function clearSearchHistory() {
            localStorage.removeItem('nordintel_history');
            renderFullHistory();
            showToast("Search history cleared");
        }

        function renderFullHistory() {
            const list = getHistory();
            const container = document.getElementById('fullHistoryList');
            container.innerHTML = '';
            if (list.length === 0) {
                container.innerHTML = '<div style="color:var(--secondary-text); padding:1rem;">No recent searches recorded yet.</div>';
                return;
            }
            list.forEach(item => {
                const row = document.createElement('div');
                row.style = 'background:var(--surface-subtle); padding:0.9rem 1.2rem; border-radius:var(--radius-sm); border:1px solid var(--border-color); display:flex; justify-content:space-between; align-items:center; cursor:pointer;';
                row.innerHTML = `
                    <div>
                        <div style="font-weight:700; color:var(--primary-navy);">${item.name || 'Company'}</div>
                        <div style="font-family:'JetBrains Mono'; font-size:0.85rem; color:var(--brand-blue);">ORG: ${formatOrgDisplay(item.org)}</div>
                    </div>
                    <button class="btn-tool" style="font-size:0.8rem;">Open Profile ➔</button>
                `;
                row.onclick = () => {
                    switchTab('search');
                    quickFill(item.org);
                };
                container.appendChild(row);
            });
        }

        async function handleSearchClick() {
            hideSearchError();
            const raw = inputElem.value;
            const validation = validateAndNormalizeOrg(raw);
            if (!validation.isValid) {
                showSearchError(validation.error);
                return;
            }
            inputElem.value = formatOrgDisplay(validation.normalized);
            await executeSearch(validation.normalized);
        }

        async function executeSearch(normalizedOrg) {
            const loader = document.getElementById('searchLoader');
            const profileView = document.getElementById('companyProfileView');
            
            loader.style.display = 'block';
            profileView.style.display = 'none';
            hideSearchError();

            try {
                const res = await fetch(`/api/search?org=${encodeURIComponent(normalizedOrg)}`);
                const data = await res.json();
                loader.style.display = 'none';

                if (data.error) {
                    showSearchError(data.error);
                    return;
                }

                currentProfileData = data;
                saveHistory(normalizedOrg, data.company_name);

                // Populate Profile
                const name = data.company_name || 'Unnamed Company';
                document.getElementById('profName').innerText = name;
                
                const initials = name.split(' ').map(w => w[0]).filter(Boolean).slice(0, 2).join('').toUpperCase() || 'NO';
                document.getElementById('profAvatar').innerText = initials;

                const formattedOrg = formatOrgDisplay(data.org_number);
                document.getElementById('profOrg').innerText = `ORG: ${formattedOrg}`;
                document.getElementById('profType').innerText = data.org_type_description || data.org_type || 'Commercial Entity';

                // Status
                const badge = document.getElementById('profStatusBadge');
                const badgeTxt = document.getElementById('profStatusText');
                if (data.is_bankrupt) {
                    badge.className = 'badge-status inactive';
                    badgeTxt.innerText = 'BANKRUPT';
                } else if (!data.is_active) {
                    badge.className = 'badge-status inactive';
                    badgeTxt.innerText = 'IN LIQUIDATION / INACTIVE';
                } else {
                    badge.className = 'badge-status active';
                    badgeTxt.innerText = 'ACTIVE & REGISTERED';
                }

                // KPIs
                document.getElementById('kpiStaff').innerText = (data.employee_count !== null && data.employee_count !== undefined) 
                    ? Number(data.employee_count).toLocaleString() + ' Personnel' 
                    : 'Unlisted';
                document.getElementById('kpiDate').innerText = data.registration_date || 'N/A';
                
                let city = 'Norway';
                if (data.business_address && data.business_address.poststed) {
                    city = data.business_address.poststed;
                } else if (data.facts) {
                    const factAddr = data.facts.find(f => f.key === 'business_address');
                    if (factAddr && factAddr.value) {
                        const parts = factAddr.value.split(',');
                        if (parts.length >= 3) city = parts[parts.length - 3].trim();
                    }
                }
                document.getElementById('kpiCity').innerText = city;

                // Summary
                document.getElementById('profSummary').innerText = data.agent_summary || 'Verified profile extracted from official Norwegian records.';

                // Column 1
                document.getElementById('detailLegalName').innerText = name;
                document.getElementById('detailOrgNr').innerText = formattedOrg;
                document.getElementById('detailOrgForm').innerText = data.org_type_description ? `${data.org_type_description} (${data.org_type || ''})` : 'Not available';
                document.getElementById('detailRegDate').innerText = data.registration_date || 'Not available';
                document.getElementById('detailSolvency').innerText = data.is_bankrupt ? 'Bankrupt' : (data.is_active ? 'Active & In Good Standing' : 'In Liquidation');

                // Column 2
                document.getElementById('detailNace').innerText = data.industry_code || 'Not available';
                document.getElementById('detailIndustry').innerText = data.industry_description || 'General Corporate Sector';
                
                let fullAddr = 'Not available in current data source';
                const bAddr = data.business_address || {};
                if (bAddr && (bAddr.adresse || bAddr.poststed)) {
                    const street = Array.isArray(bAddr.adresse) ? bAddr.adresse.join(', ') : (bAddr.adresse || '');
                    fullAddr = [street, bAddr.postnummer, bAddr.poststed].filter(Boolean).join(', ');
                } else if (data.facts) {
                    const factAddr = data.facts.find(f => f.key === 'business_address');
                    if (factAddr && factAddr.value) fullAddr = factAddr.value;
                }
                document.getElementById('detailAddress').innerText = fullAddr;

                const webElem = document.getElementById('detailWebsite');
                if (data.website) {
                    const url = data.website.startsWith('http') ? data.website : `https://${data.website}`;
                    webElem.innerHTML = `<a href="${url}" target="_blank">${data.website}</a>`;
                } else {
                    webElem.innerHTML = '<span style="color:var(--secondary-text); font-style:italic;">Not registered with authority</span>';
                }

                // Run Quality check on this entity
                fetchQualityReport(normalizedOrg);

                profileView.style.display = 'block';
                profileView.scrollIntoView({ behavior: 'smooth' });

            } catch(e) {
                loader.style.display = 'none';
                showSearchError("We couldn't retrieve company information right now. Please try again.");
            }
        }

        // Data Quality Checker Function
        async function fetchQualityReport(org) {
            try {
                const res = await fetch(`/api/quality?org=${org}`);
                const q = await res.json();
                document.getElementById('kpiQuality').innerText = `${q.score}% (${q.rating})`;
                document.getElementById('qualitySubjectName').innerText = `${currentProfileData.company_name} (${formatOrgDisplay(org)})`;
                document.getElementById('qualityScoreVal').innerText = `${q.score}%`;

                const container = document.getElementById('qualityChecksList');
                container.innerHTML = '';
                q.checks.forEach(c => {
                    const div = document.createElement('div');
                    div.className = 'check-item';
                    div.innerHTML = `
                        <span class="check-icon ${c.passed ? 'pass' : 'fail'}">${c.passed ? '✓' : '✗'}</span>
                        <div style="flex:1;">
                            <div style="font-weight:700; color:var(--primary-navy);">${c.rule} <span style="font-size:0.75rem; color:var(--secondary-text); font-weight:500;">(${c.impact})</span></div>
                            <div style="font-size:0.82rem; color:var(--secondary-text);">${c.description}</div>
                        </div>
                    `;
                    container.appendChild(div);
                });
            } catch(e) {}
        }

        // AI Chat Assistant
        async function askQuestion(qText) {
            if (!currentProfileData) {
                showToast("Please search a company first");
                return;
            }
            appendChat('user', qText);
            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ org: currentProfileData.org_number, question: qText })
                });
                const data = await res.json();
                appendChat('agent', `${data.answer} <br><span style="font-size:0.75rem; color:var(--secondary-text); margin-top:4px; display:inline-block;">Source: ${data.source}</span>`);
            } catch(e) {
                appendChat('agent', "AI insights are currently unavailable. You can still explore the retrieved company information.");
            }
        }

        function submitChatQuestion() {
            const input = document.getElementById('chatInput');
            const q = input.value.trim();
            if (!q) return;
            input.value = '';
            askQuestion(q);
        }

        function appendChat(role, htmlContent) {
            const hist = document.getElementById('chatHistory');
            const bubble = document.createElement('div');
            bubble.className = `chat-bubble ${role}`;
            bubble.innerHTML = htmlContent;
            hist.appendChild(bubble);
            hist.scrollTop = hist.scrollHeight;
        }

        // Comparison Functionality
        function addToComparison() {
            if (!currentProfileData) return;
            if (comparisonList.some(x => x.org_number === currentProfileData.org_number)) {
                showToast("Company is already in comparison");
                switchTab('comparison');
                return;
            }
            if (comparisonList.length >= 3) {
                comparisonList.shift(); // keep max 3 companies
            }
            comparisonList.push(currentProfileData);
            renderComparisonTable();
            showToast(`Added ${currentProfileData.company_name} to comparison`);
            switchTab('comparison');
        }

        function clearComparison() {
            comparisonList = [];
            renderComparisonTable();
            showToast("Comparison cleared");
        }

        function renderComparisonTable() {
            const tbody = document.getElementById('comparisonBody');
            if (comparisonList.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:var(--secondary-text); padding:2.5rem;">No companies added to comparison yet. Search a company and click "Add to Comparison".</td></tr>';
                return;
            }

            // Update headers
            for (let i = 0; i < 3; i++) {
                const th = document.getElementById(`compHead${i+1}`);
                if (comparisonList[i]) {
                    th.innerHTML = `<strong>${comparisonList[i].company_name}</strong><br><span style="font-family:'JetBrains Mono'; font-size:0.75rem;">${formatOrgDisplay(comparisonList[i].org_number)}</span>`;
                } else {
                    th.innerText = `Company ${String.fromCharCode(65+i)}`;
                }
            }

            const rows = [
                { label: 'Organization Number', fn: c => formatOrgDisplay(c.org_number) },
                { label: 'Legal Form', fn: c => c.org_type_description || c.org_type || 'N/A' },
                { label: 'Operating Status', fn: c => c.is_bankrupt ? 'Bankrupt' : (c.is_active ? 'Active' : 'Inactive') },
                { label: 'Registration Date', fn: c => c.registration_date || 'N/A' },
                { label: 'Registered Headcount', fn: c => c.employee_count !== null ? `${c.employee_count.toLocaleString()} Staff` : 'Unlisted' },
                { label: 'Industry Sector', fn: c => c.industry_description || 'N/A' },
                { label: 'Location / City', fn: c => (c.business_address && c.business_address.poststed) ? c.business_address.poststed : 'Norway' }
            ];

            tbody.innerHTML = '';
            rows.forEach(r => {
                const tr = document.createElement('tr');
                let colsHtml = `<td style="font-weight:600; color:var(--secondary-text);">${r.label}</td>`;
                for (let i = 0; i < 3; i++) {
                    const c = comparisonList[i];
                    colsHtml += `<td style="font-weight:600; color:var(--primary-navy);">${c ? r.fn(c) : '-'}</td>`;
                }
                tr.innerHTML = colsHtml;
                tbody.appendChild(tr);
            });
        }

        // Analytics UI
        async function renderAnalyticsUI() {
            try {
                const res = await fetch('/api/analytics');
                const data = await res.json();
                
                // Industries
                const indBox = document.getElementById('analyticsIndustryBars');
                indBox.innerHTML = '';
                const indEntries = Object.entries(data.top_industries);
                const maxInd = Math.max(...indEntries.map(x => x[1]), 1);
                indEntries.forEach(([name, count]) => {
                    const pct = Math.round((count / maxInd) * 100);
                    indBox.innerHTML += `
                        <div class="stat-bar-row">
                            <span class="stat-bar-label" title="${name}">${name}</span>
                            <div class="stat-bar-track"><div class="stat-bar-fill" style="width:${pct}%;"></div></div>
                            <span class="stat-bar-count">${count}</span>
                        </div>
                    `;
                });

                // Types
                const typeBox = document.getElementById('analyticsTypeBars');
                typeBox.innerHTML = '';
                const typeEntries = Object.entries(data.top_types);
                const maxType = Math.max(...typeEntries.map(x => x[1]), 1);
                typeEntries.forEach(([name, count]) => {
                    const pct = Math.round((count / maxType) * 100);
                    typeBox.innerHTML += `
                        <div class="stat-bar-row">
                            <span class="stat-bar-label" title="${name}">${name}</span>
                            <div class="stat-bar-track"><div class="stat-bar-fill" style="width:${pct}%; background:#059669;"></div></div>
                            <span class="stat-bar-count">${count}</span>
                        </div>
                    `;
                });
            } catch(e) {}
        }

        // Action Toolbar Functions
        function copyCurrentOrg() {
            if (!currentProfileData) return;
            const f = formatOrgDisplay(currentProfileData.org_number);
            navigator.clipboard.writeText(f).then(() => showToast(`Copied ${f} to clipboard`));
        }

        function copyCurrentName() {
            if (!currentProfileData) return;
            navigator.clipboard.writeText(currentProfileData.company_name).then(() => showToast(`Copied "${currentProfileData.company_name}"`));
        }

        function shareProfile() {
            if (!currentProfileData) return;
            const data = {
                title: `${currentProfileData.company_name} — Intelligence Profile`,
                text: `Verified profile for ${currentProfileData.company_name} (${formatOrgDisplay(currentProfileData.org_number)})`,
                url: window.location.href
            };
            if (navigator.share) {
                navigator.share(data).catch(() => {});
            } else {
                navigator.clipboard.writeText(window.location.href).then(() => showToast("Profile URL copied to clipboard"));
            }
        }

        function exportJSON() {
            if (!currentProfileData) return;
            const str = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(currentProfileData, null, 2));
            const a = document.createElement('a');
            a.href = str;
            a.download = `NordIntel_${currentProfileData.org_number}.json`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            showToast("JSON company record exported");
        }

        function exportCSV() {
            if (!currentProfileData) return;
            const p = currentProfileData;
            const csvRows = [
                ["Field", "Value"],
                ["Company Name", `"${(p.company_name||'').replace(/"/g, '""')}"`],
                ["Organization Number", `"${p.org_number}"`],
                ["Organization Form", `"${(p.org_type_description||'').replace(/"/g, '""')}"`],
                ["Registration Date", `"${p.registration_date||''}"`],
                ["Active Status", p.is_active ? "Active" : "Inactive"],
                ["Bankrupt", p.is_bankrupt ? "Yes" : "No"],
                ["Employee Headcount", p.employee_count !== null ? p.employee_count : ""],
                ["Industry Code", `"${p.industry_code||''}"`],
                ["Industry Description", `"${(p.industry_description||'').replace(/"/g, '""')}"`],
                ["Official Website", `"${p.website||''}"`],
                ["Data Source", "Brønnøysundregistrene (Norway)"]
            ];
            const csvContent = "data:text/csv;charset=utf-8," + csvRows.map(e => e.join(",")).join("\\n");
            const a = document.createElement('a');
            a.href = encodeURI(csvContent);
            a.download = `NordIntel_${p.org_number}.csv`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            showToast("CSV company record exported");
        }

        // Initialize on load
        window.addEventListener('DOMContentLoaded', () => {
            renderAnalyticsUI();
        });
    </script>
</body>
</html>
"""

class AgentServerHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        elif parsed.path == "/api/search":
            query = urllib.parse.parse_qs(parsed.query)
            raw_org = query.get("org", [None])[0]
            
            is_valid, clean_org, err_msg = normalize_org_number(raw_org)
            if not is_valid:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": err_msg}).encode("utf-8"))
                return

            profile = agent.process_company(clean_org)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            if profile:
                self.wfile.write(profile.model_dump_json().encode("utf-8"))
            else:
                self.wfile.write(json.dumps({"error": "No company was found for this organization number."}).encode("utf-8"))
        elif parsed.path == "/api/quality":
            query = urllib.parse.parse_qs(parsed.query)
            raw_org = query.get("org", [None])[0]
            is_valid, clean_org, _ = normalize_org_number(raw_org)
            if is_valid:
                p = agent.get_existing_profile(clean_org)
                if p:
                    q = calculate_data_quality(p.model_dump())
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(q).encode("utf-8"))
                    return
            self.send_response(404)
            self.end_headers()
        elif parsed.path == "/api/analytics":
            metrics = get_analytics_metrics()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(metrics).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/chat":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(body)
                raw_org = data.get("org")
                question = data.get("question", "")
                is_valid, clean_org, _ = normalize_org_number(raw_org)
                if is_valid:
                    p = agent.get_existing_profile(clean_org)
                    if p:
                        ans = answer_company_question(p.model_dump(), question)
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps(ans).encode("utf-8"))
                        return
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Profile not found"}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    PORT = 8000
    server_address = ('127.0.0.1', PORT)
    httpd = socketserver.TCPServer(server_address, AgentServerHandler)
    print(f"[*] NordIntel SaaS Platform running at http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")

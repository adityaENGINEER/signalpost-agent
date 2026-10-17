import http.server
import socketserver
import json
import urllib.parse
from agent.core import SignalpostAgent
from agent.validator import normalize_org_number, format_org_number

agent = SignalpostAgent()

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Signalpost (NordIntel) — Norwegian Company Intelligence Platform</title>
    <!-- Modern Typography: Inter & JetBrains Mono -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --bg-body: #F4F6FA;
            --surface-main: #FFFFFF;
            --surface-subtle: #F8FAFC;
            --primary-navy: #0F172A;
            --brand-blue: #2563EB;
            --brand-blue-hover: #1D4ED8;
            --brand-blue-light: #EFF6FF;
            --brand-blue-border: #BFDBFE;
            --success-green: #059669;
            --success-bg: #ECFDF5;
            --text-heading: #0F172A;
            --text-body: #334155;
            --text-muted: #64748B;
            --border-color: #E2E8F0;
            --border-hover: #CBD5E1;
            --danger-red: #DC2626;
            --danger-bg: #FEF2F2;
            --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(15, 23, 42, 0.07), 0 2px 4px -2px rgba(15, 23, 42, 0.04);
            --shadow-lg: 0 10px 15px -3px rgba(15, 23, 42, 0.08), 0 4px 6px -4px rgba(15, 23, 42, 0.03);
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            -webkit-font-smoothing: antialiased;
        }

        body {
            background-color: var(--bg-body);
            color: var(--text-body);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            width: 100%;
            overflow-x: hidden;
        }

        /* Full Width App Header / Navigation */
        .topbar {
            background: var(--surface-main);
            border-bottom: 1px solid var(--border-color);
            position: sticky;
            top: 0;
            z-index: 100;
            width: 100%;
        }

        .topbar-content {
            width: 100%;
            max-width: 1680px;
            margin: 0 auto;
            padding: 0 2rem;
            height: 68px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .brand-zone {
            display: flex;
            align-items: center;
            gap: 1.5rem;
        }

        .brand-link {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            text-decoration: none;
        }

        .brand-symbol {
            width: 38px;
            height: 38px;
            background: linear-gradient(135deg, var(--brand-blue) 0%, #1E40AF 100%);
            border-radius: var(--radius-sm);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            font-size: 1.2rem;
            box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
        }

        .brand-title {
            font-size: 1.2rem;
            font-weight: 800;
            color: var(--primary-navy);
            letter-spacing: -0.02em;
        }

        .brand-title span {
            color: var(--brand-blue);
        }

        .brand-tagline {
            display: none;
            font-size: 0.82rem;
            color: var(--text-muted);
            border-left: 1px solid var(--border-color);
            padding-left: 1rem;
            margin-left: 0.5rem;
        }

        @media (min-width: 900px) {
            .brand-tagline { display: block; }
        }

        .topbar-actions {
            display: flex;
            align-items: center;
            gap: 1.25rem;
        }

        .country-pill {
            display: flex;
            align-items: center;
            gap: 0.45rem;
            background: var(--brand-blue-light);
            color: var(--brand-blue);
            padding: 0.4rem 0.9rem;
            border-radius: 9999px;
            font-size: 0.82rem;
            font-weight: 600;
            border: 1px solid var(--brand-blue-border);
        }

        .live-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: var(--success-green);
            box-shadow: 0 0 6px rgba(5, 150, 105, 0.6);
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(0.95); opacity: 0.8; }
            50% { transform: scale(1.3); opacity: 1; }
            100% { transform: scale(0.95); opacity: 0.8; }
        }

        /* Full Screen Dashboard Container */
        .dashboard-container {
            width: 100%;
            max-width: 1680px;
            margin: 0 auto;
            padding: 1.75rem 2rem 3rem;
            flex: 1;
        }

        /* Hero / Search Panel */
        .search-panel {
            background: var(--surface-main);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 2.25rem 2.5rem;
            margin-bottom: 2rem;
            box-shadow: var(--shadow-sm);
        }

        .search-panel-top {
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
            gap: 1rem;
        }

        .hero-text h1 {
            font-size: 1.95rem;
            font-weight: 800;
            color: var(--primary-navy);
            letter-spacing: -0.025em;
            margin-bottom: 0.35rem;
        }

        .hero-text p {
            font-size: 0.98rem;
            color: var(--text-muted);
            max-width: 800px;
        }

        .badge-mini {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: var(--brand-blue);
            background: var(--brand-blue-light);
            border: 1px solid var(--brand-blue-border);
            padding: 0.3rem 0.75rem;
            border-radius: 9999px;
            margin-bottom: 0.6rem;
        }

        /* Search Input Row */
        .search-row {
            display: flex;
            gap: 0.75rem;
            margin-bottom: 1.25rem;
        }

        .input-box {
            flex: 1;
            display: flex;
            align-items: center;
            gap: 0.85rem;
            background: var(--surface-subtle);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 0.75rem 1.25rem;
            transition: all 0.2s ease;
        }

        .input-box:focus-within {
            background: #ffffff;
            border-color: var(--brand-blue);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
        }

        .input-flag {
            font-size: 1.4rem;
            line-height: 1;
        }

        .org-input {
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

        .org-input::placeholder {
            font-family: 'Inter', sans-serif;
            font-weight: 400;
            color: #94A3B8;
            font-size: 1.05rem;
            letter-spacing: normal;
        }

        .btn-search {
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
            box-shadow: 0 2px 6px rgba(37, 99, 235, 0.25);
            white-space: nowrap;
        }

        .btn-search:hover {
            background: var(--brand-blue-hover);
        }

        .btn-search:active {
            transform: scale(0.98);
        }

        /* Chips & Filter Bar */
        .quick-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 1rem;
            font-size: 0.85rem;
        }

        .chips-list {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            flex-wrap: wrap;
        }

        .chip-label {
            font-weight: 600;
            color: var(--text-muted);
            margin-right: 0.25rem;
        }

        .chip-button {
            background: var(--surface-subtle);
            border: 1px solid var(--border-color);
            color: var(--text-body);
            padding: 0.4rem 0.85rem;
            border-radius: var(--radius-sm);
            font-size: 0.84rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.15s;
        }

        .chip-button:hover {
            background: var(--brand-blue-light);
            border-color: var(--brand-blue-border);
            color: var(--brand-blue);
        }

        .history-trigger {
            color: var(--brand-blue);
            background: none;
            border: none;
            font-weight: 600;
            font-size: 0.85rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.35rem;
        }

        .history-trigger:hover {
            text-decoration: underline;
        }

        /* Feedback / Error Message */
        .feedback-banner {
            display: none;
            background: var(--danger-bg);
            border: 1px solid rgba(220, 38, 38, 0.25);
            color: var(--danger-red);
            padding: 0.9rem 1.25rem;
            border-radius: var(--radius-md);
            font-size: 0.92rem;
            font-weight: 500;
            margin-top: 1.25rem;
            align-items: center;
            gap: 0.6rem;
        }

        /* Search History Dropdown / Panel */
        .history-panel {
            display: none;
            margin-top: 1.25rem;
            padding: 1.1rem 1.25rem;
            background: var(--surface-subtle);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
        }

        .history-panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.75rem;
            font-size: 0.82rem;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .history-items-row {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }

        .history-tag {
            background: var(--surface-main);
            border: 1px solid var(--border-color);
            padding: 0.35rem 0.75rem;
            border-radius: var(--radius-sm);
            font-size: 0.82rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }

        .history-tag:hover {
            border-color: var(--brand-blue);
            color: var(--brand-blue);
        }

        /* Loading Skeleton State */
        .loader-card {
            display: none;
            background: var(--surface-main);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 3.5rem 2rem;
            text-align: center;
            margin-bottom: 2rem;
        }

        .loader-spinner {
            width: 40px;
            height: 40px;
            border: 3px solid rgba(37, 99, 235, 0.15);
            border-top: 3px solid var(--brand-blue);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin: 0 auto 1.1rem;
        }

        @keyframes spin { 100% { transform: rotate(360deg); } }

        .loader-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: var(--primary-navy);
            margin-bottom: 0.3rem;
        }

        .loader-sub {
            font-size: 0.9rem;
            color: var(--text-muted);
        }

        /* Company Profile Full Screen Dashboard */
        .profile-dashboard {
            display: none;
            animation: fadeIn 0.3s ease-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Header Identity Card */
        .profile-header-card {
            background: var(--surface-main);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 2.25rem;
            margin-bottom: 1.75rem;
            box-shadow: var(--shadow-sm);
        }

        .profile-header-flex {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 2rem;
            margin-bottom: 1.75rem;
            flex-wrap: wrap;
        }

        .profile-identity-main {
            display: flex;
            align-items: center;
            gap: 1.5rem;
        }

        .avatar-initials {
            width: 64px;
            height: 64px;
            background: linear-gradient(135deg, var(--brand-blue-light) 0%, #DBEAFE 100%);
            border: 1.5px solid var(--brand-blue-border);
            color: var(--brand-blue);
            border-radius: var(--radius-md);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.6rem;
            font-weight: 800;
            flex-shrink: 0;
            box-shadow: var(--shadow-sm);
        }

        .company-heading-title {
            font-size: 2.15rem;
            font-weight: 800;
            color: var(--primary-navy);
            letter-spacing: -0.03em;
            line-height: 1.2;
            margin-bottom: 0.5rem;
        }

        .company-badges-line {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            flex-wrap: wrap;
        }

        .badge-mono-org {
            font-family: 'JetBrains Mono', monospace;
            background: var(--surface-subtle);
            border: 1px solid var(--border-color);
            color: var(--primary-navy);
            padding: 0.3rem 0.75rem;
            border-radius: var(--radius-sm);
            font-size: 0.95rem;
            font-weight: 700;
            letter-spacing: 0.03em;
        }

        .badge-type-tag {
            background: var(--brand-blue-light);
            border: 1px solid var(--brand-blue-border);
            color: var(--brand-blue);
            padding: 0.3rem 0.75rem;
            border-radius: var(--radius-sm);
            font-size: 0.85rem;
            font-weight: 600;
        }

        .status-pill-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1.2rem;
            border-radius: 9999px;
            font-size: 0.88rem;
            font-weight: 700;
            letter-spacing: 0.03em;
            text-transform: uppercase;
        }

        .status-pill-badge.active {
            background: var(--success-bg);
            color: var(--success-green);
            border: 1px solid rgba(5, 150, 105, 0.3);
        }

        .status-pill-badge.inactive {
            background: var(--danger-bg);
            color: var(--danger-red);
            border: 1px solid rgba(220, 38, 38, 0.3);
        }

        /* 4 Key KPI Metric Boxes */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1.25rem;
            margin-bottom: 1.75rem;
        }

        @media (max-width: 1024px) {
            .kpi-grid { grid-template-columns: repeat(2, 1fr); }
        }

        @media (max-width: 640px) {
            .kpi-grid { grid-template-columns: 1fr; }
        }

        .kpi-box {
            background: var(--surface-subtle);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 1.2rem 1.4rem;
        }

        .kpi-title {
            font-size: 0.78rem;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.4rem;
        }

        .kpi-value {
            font-size: 1.45rem;
            font-weight: 800;
            color: var(--primary-navy);
            letter-spacing: -0.02em;
        }

        /* Executive Briefing Callout */
        .executive-briefing {
            background: #F8FAFC;
            border-left: 4px solid var(--brand-blue);
            padding: 1.25rem 1.5rem;
            border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
            font-size: 1rem;
            line-height: 1.6;
            color: var(--text-body);
            margin-bottom: 1.75rem;
        }

        .briefing-label {
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            color: var(--brand-blue);
            margin-bottom: 0.35rem;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }

        /* Actions Toolbar */
        .toolbar-row {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            border-top: 1px solid var(--border-color);
            padding-top: 1.4rem;
            flex-wrap: wrap;
        }

        .tool-btn {
            background: var(--surface-main);
            border: 1px solid var(--border-color);
            color: var(--text-body);
            padding: 0.55rem 1.1rem;
            border-radius: var(--radius-sm);
            font-size: 0.88rem;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            transition: all 0.15s ease;
        }

        .tool-btn:hover {
            background: var(--surface-subtle);
            border-color: var(--border-hover);
            color: var(--primary-navy);
        }

        /* Full Screen 3-Column Enterprise Dashboard Layout */
        .dashboard-grid-3col {
            display: grid;
            grid-template-columns: 1fr 1fr 1.25fr;
            gap: 1.75rem;
            align-items: start;
        }

        @media (max-width: 1280px) {
            .dashboard-grid-3col {
                grid-template-columns: 1fr 1fr;
            }
            .dashboard-grid-3col > div:nth-child(3) {
                grid-column: span 2;
            }
        }

        @media (max-width: 860px) {
            .dashboard-grid-3col {
                grid-template-columns: 1fr;
            }
            .dashboard-grid-3col > div:nth-child(3) {
                grid-column: span 1;
            }
        }

        /* Standard Dashboard Card */
        .dash-card {
            background: var(--surface-main);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 1.75rem;
            box-shadow: var(--shadow-sm);
            margin-bottom: 1.75rem;
        }

        .dash-card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.25rem;
            padding-bottom: 0.85rem;
            border-bottom: 1px solid var(--border-color);
        }

        .dash-card-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--primary-navy);
            display: flex;
            align-items: center;
            gap: 0.6rem;
        }

        .dash-card-title span.icon {
            font-size: 1.2rem;
        }

        /* Key-Value Attribute Rows */
        .prop-list {
            display: flex;
            flex-direction: column;
            gap: 1.1rem;
        }

        .prop-item {
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }

        .prop-label {
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .prop-value {
            font-size: 1rem;
            font-weight: 600;
            color: var(--primary-navy);
            word-break: break-word;
        }

        .prop-value.mono {
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: 0.03em;
        }

        .prop-value a {
            color: var(--brand-blue);
            text-decoration: none;
        }

        .prop-value a:hover {
            text-decoration: underline;
        }

        .prop-value.empty-val {
            color: #94A3B8;
            font-weight: 400;
            font-style: italic;
        }

        /* Verified Evidence Feed Cards */
        .evidence-feed {
            display: flex;
            flex-direction: column;
            gap: 0.85rem;
        }

        .evidence-card {
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 1rem 1.2rem;
            background: var(--surface-subtle);
            transition: all 0.15s ease;
        }

        .evidence-card:hover {
            background: #ffffff;
            border-color: var(--brand-blue-border);
            box-shadow: var(--shadow-sm);
        }

        .evidence-card-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.4rem;
        }

        .evidence-tag-key {
            font-size: 0.78rem;
            text-transform: uppercase;
            font-weight: 700;
            letter-spacing: 0.05em;
            color: var(--brand-blue);
        }

        .evidence-score-badge {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--success-green);
            background: var(--success-bg);
            border: 1px solid rgba(5, 150, 105, 0.2);
            padding: 0.15rem 0.55rem;
            border-radius: 4px;
        }

        .evidence-content-val {
            font-size: 1rem;
            font-weight: 700;
            color: var(--primary-navy);
            margin-bottom: 0.35rem;
        }

        .evidence-desc {
            font-size: 0.84rem;
            color: var(--text-muted);
            line-height: 1.45;
            margin-bottom: 0.65rem;
        }

        .evidence-link-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.78rem;
            border-top: 1px dashed var(--border-color);
            padding-top: 0.55rem;
        }

        .evidence-link-footer a {
            color: var(--brand-blue);
            text-decoration: none;
            font-weight: 600;
        }

        .evidence-link-footer a:hover {
            text-decoration: underline;
        }

        .evidence-timestamp {
            color: var(--text-muted);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.74rem;
        }

        /* Toast Popup */
        .toast-msg-box {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            background: var(--primary-navy);
            color: #ffffff;
            padding: 0.85rem 1.4rem;
            border-radius: var(--radius-md);
            font-size: 0.92rem;
            font-weight: 600;
            box-shadow: var(--shadow-lg);
            display: none;
            align-items: center;
            gap: 0.6rem;
            z-index: 1000;
            animation: slideIn 0.25s ease-out;
        }

        @keyframes slideIn {
            from { transform: translateY(20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        /* Clean SaaS Footer */
        .footer-bar {
            background: var(--surface-main);
            border-top: 1px solid var(--border-color);
            padding: 2rem 2rem;
            margin-top: auto;
            width: 100%;
        }

        .footer-inner {
            max-width: 1680px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.88rem;
            color: var(--text-muted);
            flex-wrap: wrap;
            gap: 1rem;
        }

        .footer-inner strong {
            color: var(--primary-navy);
        }
    </style>
</head>
<body>

    <!-- Top Navigation Bar -->
    <header class="topbar">
        <div class="topbar-content">
            <div class="brand-zone">
                <a href="/" class="brand-link">
                    <div class="brand-symbol">⚡</div>
                    <div class="brand-title">Signalpost <span>NordIntel</span></div>
                </a>
                <div class="brand-tagline">Autonomous Enterprise Intelligence</div>
            </div>

            <div class="topbar-actions">
                <div class="country-pill">
                    <span class="live-dot"></span>
                    <span>🇳🇴</span> Brønnøysundregistrene Live API
                </div>
            </div>
        </div>
    </header>

    <!-- Main Full-Width Dashboard -->
    <main class="dashboard-container">

        <!-- Search & Control Panel -->
        <section class="search-panel">
            <div class="search-panel-top">
                <div class="hero-text">
                    <div class="badge-mini">
                        <span>🇳🇴</span> NORWAY BUSINESS INTELLIGENCE
                    </div>
                    <h1>Know Every Company Behind the Number.</h1>
                    <p>Enter any Norwegian organization's 9-digit number to instantly retrieve verified corporate profiles, legal status, NACE classifications, employee headcounts, and registered public records.</p>
                </div>
            </div>

            <!-- Search Row -->
            <div class="search-row">
                <div class="input-box">
                    <span class="input-flag">🇳🇴</span>
                    <input 
                        type="text" 
                        id="orgInput" 
                        class="org-input" 
                        placeholder="Enter 9-digit organization number (e.g. 923 609 016)" 
                        maxlength="14"
                        autocomplete="off"
                    >
                </div>
                <button class="btn-search" id="btnSearch" onclick="handleSearchClick()">
                    <span>🔍</span> Find Company
                </button>
            </div>

            <!-- Chips & Options Bar -->
            <div class="quick-bar">
                <div class="chips-list">
                    <span class="chip-label">Verified Enterprises:</span>
                    <button class="chip-button" onclick="quickFill('923 609 016')">Equinor ASA (923 609 016)</button>
                    <button class="chip-button" onclick="quickFill('916 627 939')">Palmera (916 627 939)</button>
                    <button class="chip-button" onclick="quickFill('989 061 593')">G-Group AS (989 061 593)</button>
                    <button class="chip-button" onclick="quickFill('988 539 473')">EBE-Data (988 539 473)</button>
                </div>
                <button class="history-trigger" onclick="toggleHistoryView()">
                    <span>🕒</span> Recent Searches
                </button>
            </div>

            <!-- Error Banner -->
            <div class="feedback-banner" id="errorBanner">
                <span style="font-size: 1.2rem;">⚠️</span>
                <span id="errorBannerText">Please enter a valid 9-digit Norwegian organization number.</span>
            </div>

            <!-- Recent Searches History Tray -->
            <div class="history-panel" id="historyPanel">
                <div class="history-panel-header">
                    <span>Recent Searches</span>
                    <button style="background:none; border:none; color:var(--danger-red); cursor:pointer; font-size:0.8rem; font-weight:600;" onclick="clearSearchHistory()">Clear All</button>
                </div>
                <div class="history-items-row" id="historyItems"></div>
            </div>
        </section>

        <!-- Loading State -->
        <div class="loader-card" id="loaderBox">
            <div class="loader-spinner"></div>
            <div class="loader-title">Looking up company information...</div>
            <div class="loader-sub">Querying Brønnøysundregistrene & extracting verified registry facts</div>
        </div>

        <!-- 3-Column Enterprise Dashboard Profile View -->
        <div class="profile-dashboard" id="profileDashboard">
            
            <!-- Company Identity Header Card -->
            <div class="profile-header-card">
                <div class="profile-header-flex">
                    <div class="profile-identity-main">
                        <div class="avatar-initials" id="compInitials">EQ</div>
                        <div>
                            <h2 class="company-heading-title" id="compName">-</h2>
                            <div class="company-badges-line">
                                <span class="badge-mono-org" id="compOrgBadge">ORG: -</span>
                                <span class="badge-type-tag" id="compTypeTag">-</span>
                            </div>
                        </div>
                    </div>
                    <div class="status-pill-badge active" id="compStatusPill">
                        <span class="live-dot"></span>
                        <span id="compStatusText">ACTIVE & REGISTERED</span>
                    </div>
                </div>

                <!-- 4 KPI Metrics -->
                <div class="kpi-grid">
                    <div class="kpi-box">
                        <div class="kpi-title">Registered Headcount</div>
                        <div class="kpi-value" id="kpiEmployees">-</div>
                    </div>
                    <div class="kpi-box">
                        <div class="kpi-title">Registration Date</div>
                        <div class="kpi-value" id="kpiFounded">-</div>
                    </div>
                    <div class="kpi-box">
                        <div class="kpi-title">Headquarters Location</div>
                        <div class="kpi-value" id="kpiCity">-</div>
                    </div>
                    <div class="kpi-box">
                        <div class="kpi-title">Registry Verification</div>
                        <div class="kpi-value" style="color: var(--brand-blue);">100% Proven</div>
                    </div>
                </div>

                <!-- Executive Briefing -->
                <div class="executive-briefing">
                    <div class="briefing-label">
                        <span>🧠</span> Agent Executive Summary & Explanation
                    </div>
                    <p id="compSummaryText">-</p>
                </div>

                <!-- Quick Action Toolbar -->
                <div class="toolbar-row">
                    <button class="tool-btn" onclick="copyOrgNumber()">
                        <span>📋</span> Copy Org Number
                    </button>
                    <button class="tool-btn" onclick="copyCompanyName()">
                        <span>📋</span> Copy Company Name
                    </button>
                    <button class="tool-btn" onclick="shareProfile()">
                        <span>🔗</span> Share Profile
                    </button>
                    <button class="tool-btn" onclick="exportJSON()">
                        <span>📥</span> Export JSON Data
                    </button>
                    <button class="tool-btn" onclick="window.print()">
                        <span>🖨️</span> Print / Save PDF
                    </button>
                </div>
            </div>

            <!-- 3-Column Balanced Dashboard Details -->
            <div class="dashboard-grid-3col">
                
                <!-- Column 1: Legal & Registration Details -->
                <div class="dash-card">
                    <div class="dash-card-header">
                        <h3 class="dash-card-title">
                            <span class="icon">📋</span> Registration & Legal
                        </h3>
                    </div>
                    <div class="prop-list">
                        <div class="prop-item">
                            <span class="prop-label">Full Legal Name</span>
                            <span class="prop-value" id="rowLegalName">-</span>
                        </div>
                        <div class="prop-item">
                            <span class="prop-label">Organization Number</span>
                            <span class="prop-value mono" id="rowOrgNr">-</span>
                        </div>
                        <div class="prop-item">
                            <span class="prop-label">Corporate Form</span>
                            <span class="prop-value" id="rowOrgForm">-</span>
                        </div>
                        <div class="prop-item">
                            <span class="prop-label">Official Registration Date</span>
                            <span class="prop-value" id="rowRegDate">-</span>
                        </div>
                        <div class="prop-item">
                            <span class="prop-label">Operational Solvency</span>
                            <span class="prop-value" id="rowSolvency">-</span>
                        </div>
                    </div>
                </div>

                <!-- Column 2: Industry, Headcount & Location -->
                <div class="dash-card">
                    <div class="dash-card-header">
                        <h3 class="dash-card-title">
                            <span class="icon">📍</span> Operations & Location
                        </h3>
                    </div>
                    <div class="prop-list">
                        <div class="prop-item">
                            <span class="prop-label">NACE Classification</span>
                            <span class="prop-value" id="rowNaceCode">-</span>
                        </div>
                        <div class="prop-item">
                            <span class="prop-label">Industry Activity</span>
                            <span class="prop-value" id="rowNaceDesc">-</span>
                        </div>
                        <div class="prop-item">
                            <span class="prop-label">Registered Office Address</span>
                            <span class="prop-value" id="rowBusinessAddr">-</span>
                        </div>
                        <div class="prop-item">
                            <span class="prop-label">Municipality (Kommune)</span>
                            <span class="prop-value" id="rowMunicipality">-</span>
                        </div>
                        <div class="prop-item">
                            <span class="prop-label">Official Website</span>
                            <span class="prop-value" id="rowWebsite">-</span>
                        </div>
                    </div>
                </div>

                <!-- Column 3: Verified Registry Evidence Stream -->
                <div class="dash-card">
                    <div class="dash-card-header">
                        <h3 class="dash-card-title">
                            <span class="icon">🛡️</span> Verified Public Evidence
                        </h3>
                        <span style="font-size:0.75rem; font-weight:700; color:var(--success-green); background:var(--success-bg); padding:0.2rem 0.5rem; border-radius:4px;">100% Attributed</span>
                    </div>
                    <div class="evidence-feed" id="evidenceFeed"></div>
                </div>

            </div>

        </div>

    </main>

    <!-- Toast Notification -->
    <div class="toast-msg-box" id="toastBox">
        <span id="toastIcon">✓</span>
        <span id="toastText">Copied to clipboard!</span>
    </div>

    <!-- Full-Width Footer -->
    <footer class="footer-bar">
        <div class="footer-inner">
            <div>
                Data Source: <strong>Brønnøysundregistrene (Enhetsregisteret)</strong> • Official Open Government API
            </div>
            <div>
                Signalpost <strong>NordIntel</strong> • Enterprise Company Intelligence Platform
            </div>
        </div>
    </footer>

    <script>
        const ERROR_MESSAGE = "Please enter a valid 9-digit Norwegian organization number.";
        const inputElem = document.getElementById('orgInput');
        let currentProfileData = null;

        // Normalization and validation
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

        // Auto-spacing while typing
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
            const pastedText = (e.clipboardData || window.clipboardData).getData('text');
            const cleanDigits = pastedText.replace(/\\s+/g, '');
            if (/^\\d+$/.test(cleanDigits)) {
                this.value = formatOrgDisplay(cleanDigits);
            } else {
                this.value = pastedText.trim();
            }
        });

        inputElem.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') handleSearchClick();
        });

        function showError(msg) {
            const banner = document.getElementById('errorBanner');
            document.getElementById('errorBannerText').innerText = msg;
            banner.style.display = 'flex';
        }

        function hideError() {
            document.getElementById('errorBanner').style.display = 'none';
        }

        function showToast(msg) {
            const toast = document.getElementById('toastBox');
            document.getElementById('toastText').innerText = msg;
            toast.style.display = 'flex';
            setTimeout(() => { toast.style.display = 'none'; }, 2800);
        }

        function quickFill(org) {
            inputElem.value = formatOrgDisplay(org);
            handleSearchClick();
        }

        // Local Search History
        function getHistory() {
            try {
                return JSON.parse(localStorage.getItem('nordintel_searches') || '[]');
            } catch (e) { return []; }
        }

        function saveHistory(org, name) {
            try {
                let h = getHistory();
                h = h.filter(x => x.org !== org);
                h.unshift({ org, name });
                if (h.length > 8) h = h.slice(0, 8);
                localStorage.setItem('nordintel_searches', JSON.stringify(h));
                renderHistory();
            } catch (e) {}
        }

        function clearSearchHistory() {
            localStorage.removeItem('nordintel_searches');
            renderHistory();
            document.getElementById('historyPanel').style.display = 'none';
            showToast("Search history cleared");
        }

        function renderHistory() {
            const list = getHistory();
            const container = document.getElementById('historyItems');
            container.innerHTML = '';
            if (list.length === 0) {
                container.innerHTML = '<span style="color:var(--text-muted); font-size:0.85rem;">No recent searches yet.</span>';
                return;
            }
            list.forEach(item => {
                const tag = document.createElement('div');
                tag.className = 'history-tag';
                tag.innerHTML = `<span>🏢</span> <strong>${item.name || 'Company'}</strong> (${formatOrgDisplay(item.org)})`;
                tag.onclick = () => quickFill(item.org);
                container.appendChild(tag);
            });
        }

        function toggleHistoryView() {
            const panel = document.getElementById('historyPanel');
            if (panel.style.display === 'block') {
                panel.style.display = 'none';
            } else {
                renderHistory();
                panel.style.display = 'block';
            }
        }

        async function handleSearchClick() {
            hideError();
            const raw = inputElem.value;
            const validation = validateAndNormalizeOrg(raw);
            if (!validation.isValid) {
                showError(validation.error);
                return;
            }
            inputElem.value = formatOrgDisplay(validation.normalized);
            await searchCompany(validation.normalized);
        }

        async function searchCompany(normalizedOrg) {
            const loader = document.getElementById('loaderBox');
            const dashboard = document.getElementById('profileDashboard');

            loader.style.display = 'block';
            dashboard.style.display = 'none';
            hideError();

            try {
                const res = await fetch(`/api/search?org=${encodeURIComponent(normalizedOrg)}`);
                const data = await res.json();
                loader.style.display = 'none';

                if (data.error) {
                    showError(data.error);
                    return;
                }

                currentProfileData = data;
                saveHistory(normalizedOrg, data.company_name);

                // Populate Header
                const name = data.company_name || 'Unnamed Enterprise';
                document.getElementById('compName').innerText = name;
                
                const initials = name.split(' ').map(w => w[0]).filter(Boolean).slice(0, 2).join('').toUpperCase() || 'NO';
                document.getElementById('compInitials').innerText = initials;

                const formattedOrg = formatOrgDisplay(data.org_number);
                document.getElementById('compOrgBadge').innerText = `ORG: ${formattedOrg}`;
                document.getElementById('compTypeTag').innerText = data.org_type_description || data.org_type || 'Commercial Entity';

                // Status Pill
                const pill = document.getElementById('compStatusPill');
                const pillTxt = document.getElementById('compStatusText');
                if (data.is_bankrupt) {
                    pill.className = 'status-pill-badge inactive';
                    pillTxt.innerText = 'BANKRUPT';
                } else if (!data.is_active) {
                    pill.className = 'status-pill-badge inactive';
                    pillTxt.innerText = 'IN LIQUIDATION / INACTIVE';
                } else {
                    pill.className = 'status-pill-badge active';
                    pillTxt.innerText = 'ACTIVE & REGISTERED';
                }

                // 4 KPIs
                document.getElementById('kpiEmployees').innerText = (data.employee_count !== null && data.employee_count !== undefined)
                    ? Number(data.employee_count).toLocaleString() + ' Personnel'
                    : 'Unlisted';
                document.getElementById('kpiFounded').innerText = data.registration_date || 'N/A';
                
                let city = 'Norway';
                if (data.business_address && data.business_address.poststed) {
                    city = data.business_address.poststed;
                } else if (data.facts) {
                    const addrFact = data.facts.find(f => f.key === 'business_address');
                    if (addrFact && addrFact.value) {
                        const parts = addrFact.value.split(',');
                        if (parts.length >= 3) city = parts[parts.length - 3].trim();
                    }
                }
                document.getElementById('kpiCity').innerText = city;

                // Briefing
                document.getElementById('compSummaryText').innerText = data.agent_summary || 'Verified corporate profile extracted from official registers.';

                // Column 1: Legal & Registration
                document.getElementById('rowLegalName').innerText = name;
                document.getElementById('rowOrgNr').innerText = formattedOrg;
                document.getElementById('rowOrgForm').innerText = data.org_type_description ? `${data.org_type_description} (${data.org_type || ''})` : 'Not available';
                document.getElementById('rowRegDate').innerText = data.registration_date || 'Not available';
                document.getElementById('rowSolvency').innerText = data.is_bankrupt ? 'Bankrupt' : (data.is_active ? 'Active / In Good Standing' : 'In Liquidation');

                // Column 2: Operations & Location
                document.getElementById('rowNaceCode').innerText = data.industry_code || 'Not available in data source';
                document.getElementById('rowNaceDesc').innerText = data.industry_description || 'General Corporate Sector';
                
                const bAddr = data.business_address || {};
                let fullAddr = 'Not available in current data source';
                let kommune = 'Not available';
                if (bAddr && (bAddr.adresse || bAddr.poststed)) {
                    const street = Array.isArray(bAddr.adresse) ? bAddr.adresse.join(', ') : (bAddr.adresse || '');
                    fullAddr = [street, bAddr.postnummer, bAddr.poststed].filter(Boolean).join(', ');
                    kommune = [bAddr.poststed, bAddr.kommune].filter(Boolean).join(', ');
                } else if (data.facts) {
                    const factAddr = data.facts.find(f => f.key === 'business_address');
                    if (factAddr && factAddr.value) fullAddr = factAddr.value;
                }
                document.getElementById('rowBusinessAddr').innerText = fullAddr;
                document.getElementById('rowMunicipality').innerText = kommune;

                const websiteBox = document.getElementById('rowWebsite');
                if (data.website) {
                    const cleanUrl = data.website.startsWith('http') ? data.website : `https://${data.website}`;
                    websiteBox.innerHTML = `<a href="${cleanUrl}" target="_blank" rel="noopener noreferrer">${data.website}</a>`;
                } else {
                    websiteBox.innerHTML = `<span class="empty-val">Not registered with authority</span>`;
                }

                // Column 3: Evidence Feed
                const feed = document.getElementById('evidenceFeed');
                feed.innerHTML = '';
                const facts = data.facts || [];
                facts.forEach(fact => {
                    const card = document.createElement('div');
                    card.className = 'evidence-card';
                    const dateFormatted = fact.retrieved_at ? fact.retrieved_at.replace('T', ' ').substring(0, 16) + ' UTC' : 'Live';
                    let val = fact.value;
                    if (fact.key === 'org_number') val = formatOrgDisplay(val);

                    card.innerHTML = `
                        <div class="evidence-card-top">
                            <span class="evidence-tag-key">${fact.key.replace(/_/g, ' ')}</span>
                            <span class="evidence-score-badge">${Math.round((fact.confidence || 1.0) * 100)}% Proven</span>
                        </div>
                        <div class="evidence-content-val">${val}</div>
                        ${fact.explanation ? `<div class="evidence-desc">${fact.explanation}</div>` : ''}
                        <div class="evidence-link-footer">
                            <a href="${fact.source_url}" target="_blank" rel="noopener noreferrer">
                                🔗 ${fact.source_name}
                            </a>
                            <span class="evidence-timestamp">${dateFormatted}</span>
                        </div>
                    `;
                    feed.appendChild(card);
                });

                dashboard.style.display = 'block';
                dashboard.scrollIntoView({ behavior: 'smooth' });

            } catch (err) {
                loader.style.display = 'none';
                showError("We couldn't retrieve company information right now. Please try again.");
            }
        }

        // Actions
        function copyOrgNumber() {
            if (!currentProfileData) return;
            const formatted = formatOrgDisplay(currentProfileData.org_number);
            navigator.clipboard.writeText(formatted).then(() => {
                showToast(`Copied ${formatted} to clipboard`);
            });
        }

        function copyCompanyName() {
            if (!currentProfileData) return;
            navigator.clipboard.writeText(currentProfileData.company_name).then(() => {
                showToast(`Copied "${currentProfileData.company_name}" to clipboard`);
            });
        }

        function shareProfile() {
            if (!currentProfileData) return;
            const shareData = {
                title: `${currentProfileData.company_name} — Intelligence Profile`,
                text: `Verified corporate profile for ${currentProfileData.company_name} (Org Nr: ${formatOrgDisplay(currentProfileData.org_number)})`,
                url: window.location.href
            };
            if (navigator.share) {
                navigator.share(shareData).catch(() => {});
            } else {
                navigator.clipboard.writeText(window.location.href).then(() => {
                    showToast("Profile URL copied to clipboard");
                });
            }
        }

        function exportJSON() {
            if (!currentProfileData) return;
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(currentProfileData, null, 2));
            const dlAnchor = document.createElement('a');
            dlAnchor.setAttribute("href", dataStr);
            dlAnchor.setAttribute("download", `${currentProfileData.org_number}_profile.json`);
            document.body.appendChild(dlAnchor);
            dlAnchor.click();
            dlAnchor.remove();
            showToast("JSON company record exported");
        }

        window.addEventListener('DOMContentLoaded', () => {
            renderHistory();
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
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    PORT = 8000
    server_address = ('127.0.0.1', PORT)
    httpd = socketserver.TCPServer(server_address, AgentServerHandler)
    print(f"[*] Signalpost NordIntel Full-Screen Platform running at http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")

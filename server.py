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
    <!-- Google Fonts: Inter & JetBrains Mono for pristine SaaS aesthetics -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    
    <style>
        :root {
            /* Palette as specified in design brief */
            --bg-primary: #F7F9FC;
            --surface-main: #FFFFFF;
            --primary-navy: #101828;
            --brand-blue: #3157D5;
            --secondary-blue: #EAF0FF;
            --brand-blue-hover: #2646b3;
            --success-green: #16805D;
            --success-green-bg: #ECFDF3;
            --text-heading: #101828;
            --text-body: #344054;
            --text-muted: #667085;
            --border-color: #E6EAF0;
            --border-focus: #3157D5;
            --danger-red: #D92D20;
            --danger-bg: #FEF3F2;
            --shadow-subtle: 0 1px 3px rgba(16, 24, 40, 0.05), 0 1px 2px rgba(16, 24, 40, 0.03);
            --shadow-card: 0 4px 20px -2px rgba(16, 24, 40, 0.06), 0 2px 6px -1px rgba(16, 24, 40, 0.03);
            --shadow-elevated: 0 12px 32px -4px rgba(16, 24, 40, 0.08), 0 4px 12px -2px rgba(16, 24, 40, 0.04);
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --radius-pill: 9999px;
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
            color: var(--text-body);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            line-height: 1.5;
        }

        /* Top Navigation Bar */
        .navbar {
            background: var(--surface-main);
            border-bottom: 1px solid var(--border-color);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .nav-inner {
            max-width: 1160px;
            margin: 0 auto;
            padding: 0 1.5rem;
            height: 68px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .brand-block {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            text-decoration: none;
        }

        .brand-icon-box {
            width: 38px;
            height: 38px;
            background: linear-gradient(135deg, var(--brand-blue) 0%, #1a3cb0 100%);
            border-radius: var(--radius-sm);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            font-size: 1.15rem;
            box-shadow: 0 2px 8px rgba(49, 87, 213, 0.28);
        }

        .brand-name {
            font-size: 1.15rem;
            font-weight: 700;
            color: var(--primary-navy);
            letter-spacing: -0.02em;
        }

        .brand-name span {
            color: var(--brand-blue);
        }

        .nav-links {
            display: flex;
            align-items: center;
            gap: 1.75rem;
        }

        .nav-link {
            color: var(--text-muted);
            text-decoration: none;
            font-size: 0.92rem;
            font-weight: 500;
            transition: color 0.15s ease;
            cursor: pointer;
        }

        .nav-link:hover, .nav-link.active {
            color: var(--primary-navy);
        }

        .norway-indicator {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            background: var(--secondary-blue);
            color: var(--brand-blue);
            padding: 0.35rem 0.85rem;
            border-radius: var(--radius-pill);
            font-size: 0.82rem;
            font-weight: 600;
            border: 1px solid rgba(49, 87, 213, 0.15);
        }

        /* Main Container */
        .main-wrapper {
            max-width: 1160px;
            margin: 0 auto;
            padding: 2.75rem 1.5rem 4rem;
            flex: 1;
            width: 100%;
        }

        /* Hero Header */
        .hero-section {
            text-align: center;
            max-width: 760px;
            margin: 0 auto 2.5rem;
        }

        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            background: #ffffff;
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            padding: 0.35rem 0.9rem;
            border-radius: var(--radius-pill);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            box-shadow: var(--shadow-subtle);
            margin-bottom: 1.1rem;
        }

        .hero-heading {
            font-size: 2.75rem;
            font-weight: 800;
            color: var(--primary-navy);
            letter-spacing: -0.03em;
            line-height: 1.2;
            margin-bottom: 0.9rem;
        }

        .hero-subheading {
            font-size: 1.1rem;
            color: var(--text-muted);
            line-height: 1.6;
        }

        /* Search Component */
        .search-container {
            max-width: 720px;
            margin: 0 auto 1.5rem;
        }

        .search-card {
            background: var(--surface-main);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 0.6rem;
            display: flex;
            align-items: center;
            box-shadow: var(--shadow-card);
            transition: all 0.2s ease;
        }

        .search-card:focus-within {
            border-color: var(--border-focus);
            box-shadow: 0 0 0 4px rgba(49, 87, 213, 0.12), var(--shadow-card);
        }

        .search-input-wrapper {
            display: flex;
            align-items: center;
            gap: 0.85rem;
            flex: 1;
            padding: 0.4rem 0.8rem;
        }

        .flag-icon {
            font-size: 1.4rem;
            line-height: 1;
        }

        .search-input {
            width: 100%;
            border: none;
            outline: none;
            font-size: 1.15rem;
            color: var(--primary-navy);
            font-weight: 500;
            background: transparent;
        }

        .search-input::placeholder {
            color: #98A2B3;
            font-weight: 400;
        }

        .find-btn {
            background: var(--brand-blue);
            color: #ffffff;
            border: none;
            border-radius: var(--radius-md);
            padding: 0.85rem 1.8rem;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            transition: background-color 0.15s ease, transform 0.1s ease;
            white-space: nowrap;
        }

        .find-btn:hover {
            background: var(--brand-blue-hover);
        }

        .find-btn:active {
            transform: scale(0.98);
        }

        /* Validation / Inline Error Message */
        .inline-feedback {
            display: none;
            max-width: 720px;
            margin: 0.75rem auto 1.5rem;
            padding: 0.85rem 1.1rem;
            border-radius: var(--radius-md);
            font-size: 0.9rem;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 0.6rem;
        }

        .inline-feedback.error {
            background: var(--danger-bg);
            border: 1px solid rgba(217, 45, 32, 0.2);
            color: var(--danger-red);
        }

        /* Quick Samples / Suggestions */
        .samples-row {
            max-width: 720px;
            margin: 0 auto 2.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            flex-wrap: wrap;
        }

        .samples-label {
            font-size: 0.82rem;
            font-weight: 600;
            color: var(--text-muted);
            margin-right: 0.2rem;
        }

        .sample-pill {
            background: var(--surface-main);
            border: 1px solid var(--border-color);
            color: var(--text-body);
            padding: 0.35rem 0.75rem;
            border-radius: var(--radius-sm);
            font-size: 0.82rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.15s ease;
        }

        .sample-pill:hover {
            border-color: var(--brand-blue);
            color: var(--brand-blue);
            background: var(--secondary-blue);
        }

        /* Loading State */
        .loading-box {
            display: none;
            text-align: center;
            padding: 3.5rem 1rem;
            background: var(--surface-main);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            max-width: 720px;
            margin: 0 auto 2rem;
            box-shadow: var(--shadow-subtle);
        }

        .spinner {
            width: 36px;
            height: 36px;
            border: 3px solid rgba(49, 87, 213, 0.15);
            border-top: 3px solid var(--brand-blue);
            border-radius: 50%;
            animation: spin 0.75s linear infinite;
            margin: 0 auto 1rem;
        }

        @keyframes spin {
            100% { transform: rotate(360deg); }
        }

        .loading-title {
            font-size: 1.05rem;
            font-weight: 600;
            color: var(--primary-navy);
            margin-bottom: 0.25rem;
        }

        .loading-desc {
            font-size: 0.88rem;
            color: var(--text-muted);
        }

        /* Recent Searches Section */
        .recent-searches-box {
            max-width: 720px;
            margin: 0 auto 2.5rem;
            background: var(--surface-main);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 1.1rem 1.3rem;
            box-shadow: var(--shadow-subtle);
            display: none;
        }

        .recent-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.8rem;
        }

        .recent-title {
            font-size: 0.82rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
        }

        .clear-history-btn {
            background: none;
            border: none;
            color: var(--text-muted);
            font-size: 0.8rem;
            font-weight: 500;
            cursor: pointer;
            text-decoration: underline;
        }

        .clear-history-btn:hover {
            color: var(--danger-red);
        }

        .recent-list {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }

        .recent-item {
            background: var(--bg-primary);
            border: 1px solid var(--border-color);
            padding: 0.4rem 0.8rem;
            border-radius: var(--radius-sm);
            font-size: 0.82rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.4rem;
            transition: all 0.15s;
        }

        .recent-item:hover {
            border-color: var(--brand-blue);
            color: var(--brand-blue);
            background: var(--secondary-blue);
        }

        /* Profile Layout */
        .profile-wrapper {
            display: none;
            animation: fadeIn 0.3s ease-out forwards;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Identity Header Card */
        .identity-card {
            background: var(--surface-main);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 2rem;
            margin-bottom: 1.75rem;
            box-shadow: var(--shadow-card);
        }

        .identity-top {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 1.5rem;
            margin-bottom: 1.5rem;
        }

        .identity-left {
            display: flex;
            align-items: flex-start;
            gap: 1.25rem;
        }

        .company-avatar {
            width: 56px;
            height: 56px;
            background: var(--secondary-blue);
            border: 1px solid rgba(49, 87, 213, 0.2);
            color: var(--brand-blue);
            border-radius: var(--radius-md);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.35rem;
            font-weight: 700;
            flex-shrink: 0;
        }

        .company-name-heading {
            font-size: 1.85rem;
            font-weight: 800;
            color: var(--primary-navy);
            letter-spacing: -0.02em;
            line-height: 1.2;
            margin-bottom: 0.4rem;
        }

        .org-id-row {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            flex-wrap: wrap;
        }

        .org-pill {
            font-family: 'JetBrains Mono', monospace;
            background: var(--bg-primary);
            border: 1px solid var(--border-color);
            color: var(--primary-navy);
            padding: 0.25rem 0.65rem;
            border-radius: 6px;
            font-size: 0.9rem;
            font-weight: 600;
        }

        .copy-chip-btn {
            background: var(--bg-primary);
            border: 1px solid var(--border-color);
            color: var(--text-body);
            padding: 0.25rem 0.65rem;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 500;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            transition: all 0.15s ease;
        }

        .copy-chip-btn:hover {
            border-color: var(--brand-blue);
            color: var(--brand-blue);
        }

        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.4rem 0.95rem;
            border-radius: var(--radius-pill);
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0.02em;
        }

        .status-badge.active {
            background: var(--success-green-bg);
            color: var(--success-green);
            border: 1px solid rgba(22, 128, 93, 0.25);
        }

        .status-badge.inactive {
            background: var(--danger-bg);
            color: var(--danger-red);
            border: 1px solid rgba(217, 45, 32, 0.25);
        }

        .status-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: currentColor;
        }

        /* Action Buttons Toolbar */
        .actions-toolbar {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            border-top: 1px solid var(--border-color);
            padding-top: 1.25rem;
            flex-wrap: wrap;
        }

        .action-button {
            background: var(--surface-main);
            border: 1px solid var(--border-color);
            color: var(--text-body);
            padding: 0.5rem 0.95rem;
            border-radius: var(--radius-sm);
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            transition: all 0.15s ease;
        }

        .action-button:hover {
            background: var(--bg-primary);
            border-color: #cbd5e1;
            color: var(--primary-navy);
        }

        /* Two-Column Responsive Layout */
        .layout-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 1.5rem;
        }

        @media (max-width: 860px) {
            .layout-grid {
                grid-template-columns: 1fr;
            }
        }

        /* Section Card */
        .info-card {
            background: var(--surface-main);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: var(--shadow-card);
        }

        .info-card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.1rem;
            padding-bottom: 0.8rem;
            border-bottom: 1px solid var(--border-color);
        }

        .info-card-title {
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--primary-navy);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .data-rows {
            display: flex;
            flex-direction: column;
            gap: 0.95rem;
        }

        .data-row {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            gap: 1rem;
            font-size: 0.92rem;
        }

        .data-key {
            color: var(--text-muted);
            font-weight: 500;
            min-width: 140px;
        }

        .data-val {
            color: var(--primary-navy);
            font-weight: 600;
            text-align: right;
            word-break: break-word;
        }

        .data-val.unavail {
            color: #98A2B3;
            font-weight: 400;
            font-style: italic;
        }

        .data-val a {
            color: var(--brand-blue);
            text-decoration: none;
        }

        .data-val a:hover {
            text-decoration: underline;
        }

        /* Executive Summary Box */
        .summary-box {
            background: #F8FAFC;
            border-left: 4px solid var(--brand-blue);
            padding: 1rem 1.25rem;
            border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
            font-size: 0.95rem;
            color: #334155;
            line-height: 1.6;
            margin-bottom: 1.25rem;
        }

        /* Verified Evidence Accordion / List */
        .evidence-item {
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            padding: 0.9rem 1.1rem;
            margin-bottom: 0.75rem;
            background: var(--surface-main);
            transition: border-color 0.15s;
        }

        .evidence-item:hover {
            border-color: #cbd5e1;
        }

        .evidence-head {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.35rem;
        }

        .evidence-key {
            font-size: 0.76rem;
            text-transform: uppercase;
            font-weight: 700;
            letter-spacing: 0.05em;
            color: var(--brand-blue);
        }

        .evidence-confidence {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.72rem;
            font-weight: 600;
            color: var(--success-green);
            background: var(--success-green-bg);
            padding: 0.15rem 0.5rem;
            border-radius: 4px;
        }

        .evidence-value {
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--primary-navy);
            margin-bottom: 0.4rem;
        }

        .evidence-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.75rem;
            color: var(--text-muted);
            border-top: 1px dashed var(--border-color);
            padding-top: 0.45rem;
            margin-top: 0.45rem;
        }

        .evidence-footer a {
            color: var(--brand-blue);
            text-decoration: none;
            font-weight: 500;
        }

        .evidence-footer a:hover {
            text-decoration: underline;
        }

        /* Toast Notification */
        .toast {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            background: var(--primary-navy);
            color: #ffffff;
            padding: 0.75rem 1.25rem;
            border-radius: var(--radius-md);
            font-size: 0.9rem;
            font-weight: 500;
            box-shadow: var(--shadow-elevated);
            display: none;
            align-items: center;
            gap: 0.5rem;
            z-index: 1000;
            animation: slideUp 0.25s ease-out;
        }

        @keyframes slideUp {
            from { transform: translateY(15px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        /* Footer */
        footer {
            background: var(--surface-main);
            border-top: 1px solid var(--border-color);
            padding: 2.25rem 1.5rem;
            margin-top: auto;
        }

        .footer-inner {
            max-width: 1160px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.85rem;
            color: var(--text-muted);
            flex-wrap: wrap;
            gap: 1rem;
        }

        .footer-source {
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }

        .footer-source strong {
            color: var(--primary-navy);
        }

        /* Empty State */
        .empty-guidance {
            background: var(--surface-main);
            border: 1px dashed var(--border-color);
            border-radius: var(--radius-lg);
            padding: 2.5rem 1.5rem;
            text-align: center;
            max-width: 720px;
            margin: 0 auto;
        }

        .guidance-icon {
            font-size: 2.2rem;
            margin-bottom: 0.6rem;
        }

        .guidance-title {
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--primary-navy);
            margin-bottom: 0.35rem;
        }

        .guidance-text {
            font-size: 0.9rem;
            color: var(--text-muted);
            max-width: 480px;
            margin: 0 auto;
        }
    </style>
</head>
<body>

    <!-- Top Navigation -->
    <header class="navbar">
        <div class="nav-inner">
            <a href="/" class="brand-block">
                <div class="brand-icon-box">⚡</div>
                <div class="brand-name">Signalpost <span>NordIntel</span></div>
            </a>

            <div class="nav-links">
                <a href="#search" class="nav-link active">Search</a>
                <a href="javascript:void(0)" onclick="toggleHistoryView()" class="nav-link">Search History</a>
                <a href="https://data.brreg.no/enhetsregisteret/api" target="_blank" rel="noopener noreferrer" class="nav-link">Data Sources</a>
                <div class="norway-indicator">
                    <span>🇳🇴</span> Norway Enterprise Register
                </div>
            </div>
        </div>
    </header>

    <!-- Main Application Wrapper -->
    <main class="main-wrapper">
        <!-- Hero Section -->
        <section class="hero-section" id="search">
            <div class="hero-badge">
                <span>🇳🇴</span> NORWAY BUSINESS INTELLIGENCE
            </div>
            <h1 class="hero-heading">Know Every Company Behind the Number.</h1>
            <p class="hero-subheading">
                Search a Norwegian organization's 9-digit number to explore its company profile, registration details, business information, and available public records.
            </p>
        </section>

        <!-- Search Experience -->
        <div class="search-container">
            <div class="search-card">
                <div class="search-input-wrapper">
                    <span class="flag-icon">🇳🇴</span>
                    <input 
                        type="text" 
                        id="orgInput" 
                        class="search-input" 
                        placeholder="Enter 9-digit organization number" 
                        maxlength="14"
                        autocomplete="off"
                        aria-label="Norwegian Organization Number"
                    >
                </div>
                <button class="find-btn" id="findBtn" onclick="handleSearchClick()">
                    <span>🔍</span> Find Company
                </button>
            </div>
        </div>

        <!-- Inline Error Feedback -->
        <div class="inline-feedback error" id="inlineError">
            <span style="font-size: 1.1rem;">⚠️</span>
            <span id="inlineErrorText">Please enter a valid 9-digit Norwegian organization number.</span>
        </div>

        <!-- Quick Sample Suggestions -->
        <div class="samples-row">
            <span class="samples-label">Popular Enterprises:</span>
            <button class="sample-pill" onclick="quickFill('923 609 016')">Equinor ASA (923 609 016)</button>
            <button class="sample-pill" onclick="quickFill('916 627 939')">Palmera (916 627 939)</button>
            <button class="sample-pill" onclick="quickFill('989 061 593')">G-Group AS (989 061 593)</button>
            <button class="sample-pill" onclick="quickFill('988 539 473')">EBE-Data (988 539 473)</button>
        </div>

        <!-- Recent Search History Box -->
        <div class="recent-searches-box" id="recentSearchesBox">
            <div class="recent-header">
                <span class="recent-title">Recent Searches</span>
                <button class="clear-history-btn" onclick="clearSearchHistory()">Clear History</button>
            </div>
            <div class="recent-list" id="recentList"></div>
        </div>

        <!-- Loading State -->
        <div class="loading-box" id="loadingState">
            <div class="spinner"></div>
            <div class="loading-title">Looking up company information...</div>
            <div class="loading-desc">Querying Brønnøysundregistrene & extracting verified registry facts</div>
        </div>

        <!-- Empty Guidance State -->
        <div class="empty-guidance" id="emptyGuidance">
            <div class="guidance-icon">🏢</div>
            <div class="guidance-title">Enter any 9-digit Norwegian Organization Number</div>
            <div class="guidance-text">
                Every business entity registered in Norway has a unique 9-digit identifier. Enter the number with or without spaces to see complete verified public records.
            </div>
        </div>

        <!-- Company Profile Layout -->
        <div class="profile-wrapper" id="profileView">
            <!-- Identity Header Card -->
            <div class="identity-card">
                <div class="identity-top">
                    <div class="identity-left">
                        <div class="company-avatar" id="compAvatar">EQ</div>
                        <div>
                            <h2 class="company-name-heading" id="compName">-</h2>
                            <div class="org-id-row">
                                <span class="org-pill" id="compOrgDisplay">ORG: -</span>
                                <button class="copy-chip-btn" onclick="copyOrgNumber()">
                                    <span>📋</span> Copy Org Nr
                                </button>
                                <span class="org-pill" id="compTypeTag" style="color: var(--brand-blue);">-</span>
                            </div>
                        </div>
                    </div>
                    <div class="status-badge active" id="compStatusBadge">
                        <span class="status-dot"></span>
                        <span id="compStatusLabel">ACTIVE</span>
                    </div>
                </div>

                <!-- Executive Summary -->
                <div class="summary-box" id="compSummaryText">-</div>

                <!-- Action Toolbar -->
                <div class="actions-toolbar">
                    <button class="action-button" onclick="copyCompanyName()">
                        <span>📋</span> Copy Company Name
                    </button>
                    <button class="action-button" onclick="shareProfile()">
                        <span>🔗</span> Share Profile
                    </button>
                    <button class="action-button" onclick="exportJSON()">
                        <span>📥</span> Export JSON Data
                    </button>
                    <button class="action-button" onclick="window.print()">
                        <span>🖨️</span> Print / Save PDF
                    </button>
                </div>
            </div>

            <!-- Two-Column Information Hierarchy -->
            <div class="layout-grid">
                <!-- Left Column -->
                <div class="grid-col-left">
                    <!-- 1. Company Overview & Registration Details -->
                    <div class="info-card">
                        <div class="info-card-header">
                            <h3 class="info-card-title"><span>📋</span> Registration & Legal Details</h3>
                        </div>
                        <div class="data-rows">
                            <div class="data-row">
                                <span class="data-key">Legal Name</span>
                                <span class="data-val" id="rowLegalName">-</span>
                            </div>
                            <div class="data-row">
                                <span class="data-key">Organization Number</span>
                                <span class="data-val" id="rowOrgNr" style="font-family: 'JetBrains Mono', monospace;">-</span>
                            </div>
                            <div class="data-row">
                                <span class="data-key">Organization Form</span>
                                <span class="data-val" id="rowOrgForm">-</span>
                            </div>
                            <div class="data-row">
                                <span class="data-key">Registration Date</span>
                                <span class="data-val" id="rowRegDate">-</span>
                            </div>
                            <div class="data-row">
                                <span class="data-key">Operating Status</span>
                                <span class="data-val" id="rowStatus">-</span>
                            </div>
                        </div>
                    </div>

                    <!-- 2. Industry & Business Activity -->
                    <div class="info-card">
                        <div class="info-card-header">
                            <h3 class="info-card-title"><span>📊</span> Industry & Business Activity</h3>
                        </div>
                        <div class="data-rows">
                            <div class="data-row">
                                <span class="data-key">NACE Industry Code</span>
                                <span class="data-val" id="rowNaceCode">-</span>
                            </div>
                            <div class="data-row">
                                <span class="data-key">Industry Description</span>
                                <span class="data-val" id="rowNaceDesc">-</span>
                            </div>
                            <div class="data-row">
                                <span class="data-key">Registered Headcount</span>
                                <span class="data-val" id="rowEmployees">-</span>
                            </div>
                            <div class="data-row">
                                <span class="data-key">Official Website</span>
                                <span class="data-val" id="rowWebsite">-</span>
                            </div>
                        </div>
                    </div>

                    <!-- 3. Address & Location -->
                    <div class="info-card">
                        <div class="info-card-header">
                            <h3 class="info-card-title"><span>📍</span> Address & Location</h3>
                        </div>
                        <div class="data-rows">
                            <div class="data-row">
                                <span class="data-key">Business Address</span>
                                <span class="data-val" id="rowBusinessAddr">-</span>
                            </div>
                            <div class="data-row">
                                <span class="data-key">Municipality (Kommune)</span>
                                <span class="data-val" id="rowMunicipality">-</span>
                            </div>
                            <div class="data-row">
                                <span class="data-key">Postal Address</span>
                                <span class="data-val" id="rowPostalAddr">-</span>
                            </div>
                            <div class="data-row">
                                <span class="data-key">Country</span>
                                <span class="data-val">Norway (Norge)</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Right Column: Verified Public Records & Evidence -->
                <div class="grid-col-right">
                    <div class="info-card">
                        <div class="info-card-header">
                            <h3 class="info-card-title"><span>🛡️</span> Verified Public Evidence</h3>
                            <span style="font-size: 0.78rem; font-weight: 700; color: var(--success-green); background: var(--success-green-bg); padding: 0.2rem 0.5rem; border-radius: 4px;">Official Brønnøysund</span>
                        </div>
                        <p style="font-size: 0.82rem; color: var(--text-muted); margin-bottom: 1rem; line-height: 1.5;">
                            Every single fact extracted by this agent is linked with authentic public authority registries and verification timestamps.
                        </p>
                        <div id="evidenceList"></div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <!-- Toast Notification -->
    <div class="toast" id="toastBox">
        <span id="toastIcon">✓</span>
        <span id="toastMsg">Copied to clipboard!</span>
    </div>

    <!-- Clean SaaS Footer -->
    <footer>
        <div class="footer-inner">
            <div class="footer-source">
                <span>Data Source:</span>
                <strong>Brønnøysundregistrene (Enhetsregisteret)</strong>
                <span>• Official Norwegian Open Data API</span>
            </div>
            <div>
                Signalpost <strong>NordIntel</strong> • Autonomous Corporate Intelligence Platform
            </div>
        </div>
    </footer>

    <script>
        const ERROR_MESSAGE = "Please enter a valid 9-digit Norwegian organization number.";
        const inputElem = document.getElementById('orgInput');
        let currentProfileData = null;

        // Load search history from localStorage
        function getSearchHistory() {
            try {
                return JSON.parse(localStorage.getItem('nordintel_recent_searches') || '[]');
            } catch (e) {
                return [];
            }
        }

        function saveSearchHistory(org, name) {
            try {
                let history = getSearchHistory();
                // Filter out duplicates
                history = history.filter(item => item.org !== org);
                history.unshift({ org, name, timestamp: Date.now() });
                if (history.length > 6) history = history.slice(0, 6);
                localStorage.setItem('nordintel_recent_searches', JSON.stringify(history));
                renderSearchHistory();
            } catch (e) {}
        }

        function clearSearchHistory() {
            try {
                localStorage.removeItem('nordintel_recent_searches');
                renderSearchHistory();
                showToast("Search history cleared");
            } catch (e) {}
        }

        function renderSearchHistory() {
            const history = getSearchHistory();
            const container = document.getElementById('recentSearchesBox');
            const list = document.getElementById('recentList');
            if (!history || history.length === 0) {
                container.style.display = 'none';
                return;
            }
            container.style.display = 'block';
            list.innerHTML = '';
            history.forEach(item => {
                const pill = document.createElement('div');
                pill.className = 'recent-item';
                pill.innerHTML = `<span>🏢</span> <strong>${item.name || 'Company'}</strong> (${formatOrgDisplay(item.org)})`;
                pill.onclick = () => quickFill(item.org);
                list.appendChild(pill);
            });
        }

        function toggleHistoryView() {
            const box = document.getElementById('recentSearchesBox');
            if (box.style.display === 'none' || !box.style.display) {
                renderSearchHistory();
                box.style.display = 'block';
                box.scrollIntoView({ behavior: 'smooth' });
            } else {
                box.style.display = 'none';
            }
        }

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

        // Automatic spacing input formatting
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

        function showInlineError(msg) {
            const box = document.getElementById('inlineError');
            const txt = document.getElementById('inlineErrorText');
            txt.innerText = msg;
            box.style.display = 'flex';
        }

        function hideInlineError() {
            document.getElementById('inlineError').style.display = 'none';
        }

        function showToast(msg) {
            const toast = document.getElementById('toastBox');
            document.getElementById('toastMsg').innerText = msg;
            toast.style.display = 'flex';
            setTimeout(() => { toast.style.display = 'none'; }, 3000);
        }

        function quickFill(org) {
            inputElem.value = formatOrgDisplay(org);
            handleSearchClick();
        }

        async function handleSearchClick() {
            hideInlineError();
            const rawVal = inputElem.value;
            const validation = validateAndNormalizeOrg(rawVal);

            if (!validation.isValid) {
                showInlineError(validation.error);
                return;
            }

            inputElem.value = formatOrgDisplay(validation.normalized);
            await searchCompany(validation.normalized);
        }

        async function searchCompany(normalizedOrg) {
            const loader = document.getElementById('loadingState');
            const profileView = document.getElementById('profileView');
            const emptyGuidance = document.getElementById('emptyGuidance');
            
            loader.style.display = 'block';
            profileView.style.display = 'none';
            emptyGuidance.style.display = 'none';
            hideInlineError();

            try {
                const res = await fetch(`/api/search?org=${encodeURIComponent(normalizedOrg)}`);
                const data = await res.json();
                loader.style.display = 'none';

                if (data.error) {
                    showInlineError(data.error);
                    emptyGuidance.style.display = 'block';
                    return;
                }

                currentProfileData = data;
                saveSearchHistory(normalizedOrg, data.company_name);

                // Populate Company Identity
                const name = data.company_name || 'Unnamed Company';
                document.getElementById('compName').innerText = name;
                
                // Initials Avatar
                const initials = name.split(' ').map(w => w[0]).filter(Boolean).slice(0, 2).join('').toUpperCase() || 'NO';
                document.getElementById('compAvatar').innerText = initials;

                const formattedOrg = formatOrgDisplay(data.org_number);
                document.getElementById('compOrgDisplay').innerText = `ORG: ${formattedOrg}`;
                document.getElementById('compTypeTag').innerText = data.org_type_description || data.org_type || 'Commercial Entity';

                // Status Badge
                const statusBadge = document.getElementById('compStatusBadge');
                const statusLabel = document.getElementById('compStatusLabel');
                if (data.is_bankrupt) {
                    statusBadge.className = 'status-badge inactive';
                    statusLabel.innerText = 'BANKRUPT';
                } else if (!data.is_active) {
                    statusBadge.className = 'status-badge inactive';
                    statusLabel.innerText = 'IN LIQUIDATION / INACTIVE';
                } else {
                    statusBadge.className = 'status-badge active';
                    statusLabel.innerText = 'ACTIVE & REGISTERED';
                }

                // Summary
                document.getElementById('compSummaryText').innerText = data.agent_summary || 'Company profile verified against Norwegian registry records.';

                // Information Table Data Rows
                document.getElementById('rowLegalName').innerText = data.company_name || 'Not available';
                document.getElementById('rowOrgNr').innerText = formattedOrg;
                document.getElementById('rowOrgForm').innerText = data.org_type_description ? `${data.org_type_description} (${data.org_type || ''})` : 'Not available';
                document.getElementById('rowRegDate').innerText = data.registration_date || 'Not available';
                document.getElementById('rowStatus').innerText = data.is_bankrupt ? 'Bankrupt' : (data.is_active ? 'Active / In Good Standing' : 'Under Liquidation');

                // Industry & Business
                document.getElementById('rowNaceCode').innerText = data.industry_code || 'Not available in data source';
                document.getElementById('rowNaceDesc').innerText = data.industry_description || 'Not available in data source';
                document.getElementById('rowEmployees').innerText = (data.employee_count !== null && data.employee_count !== undefined) 
                    ? `${Number(data.employee_count).toLocaleString()} registered employees` 
                    : 'Not specified in registry';

                const websiteCell = document.getElementById('rowWebsite');
                if (data.website) {
                    const cleanUrl = data.website.startsWith('http') ? data.website : `https://${data.website}`;
                    websiteCell.innerHTML = `<a href="${cleanUrl}" target="_blank" rel="noopener noreferrer">${data.website}</a>`;
                } else {
                    websiteCell.innerHTML = `<span class="unavail">Not registered with authority</span>`;
                }

                // Address & Location
                const bAddr = data.business_address || {};
                let fullAddr = 'Not available in current data source';
                let cityKommune = 'Not available';
                if (bAddr && (bAddr.adresse || bAddr.poststed)) {
                    const street = Array.isArray(bAddr.adresse) ? bAddr.adresse.join(', ') : (bAddr.adresse || '');
                    fullAddr = [street, bAddr.postnummer, bAddr.poststed].filter(Boolean).join(', ');
                    cityKommune = [bAddr.poststed, bAddr.kommune].filter(Boolean).join(', ');
                } else if (data.facts) {
                    const factAddr = data.facts.find(f => f.key === 'business_address');
                    if (factAddr && factAddr.value) fullAddr = factAddr.value;
                }
                document.getElementById('rowBusinessAddr').innerText = fullAddr;
                document.getElementById('rowMunicipality').innerText = cityKommune;

                const pAddr = data.postal_address;
                document.getElementById('rowPostalAddr').innerText = pAddr ? (Array.isArray(pAddr.adresse) ? pAddr.adresse.join(', ') : pAddr.poststed) : 'Same as business address';

                // Populate Verified Evidence List
                const evidenceList = document.getElementById('evidenceList');
                evidenceList.innerHTML = '';
                const facts = data.facts || [];
                facts.forEach(fact => {
                    const item = document.createElement('div');
                    item.className = 'evidence-item';
                    const dateFormatted = fact.retrieved_at ? fact.retrieved_at.replace('T', ' ').substring(0, 16) + ' UTC' : 'Live';
                    let displayVal = fact.value;
                    if (fact.key === 'org_number') displayVal = formatOrgDisplay(displayVal);

                    item.innerHTML = `
                        <div class="evidence-head">
                            <span class="evidence-key">${fact.key.replace(/_/g, ' ')}</span>
                            <span class="evidence-confidence">${Math.round((fact.confidence || 1.0) * 100)}% Confirmed</span>
                        </div>
                        <div class="evidence-value">${displayVal}</div>
                        <div class="evidence-footer">
                            <a href="${fact.source_url}" target="_blank" rel="noopener noreferrer">
                                🔗 ${fact.source_name}
                            </a>
                            <span>${dateFormatted}</span>
                        </div>
                    `;
                    evidenceList.appendChild(item);
                });

                profileView.style.display = 'block';
                profileView.scrollIntoView({ behavior: 'smooth' });
            } catch (err) {
                loader.style.display = 'none';
                emptyGuidance.style.display = 'block';
                showInlineError("We couldn't retrieve company information right now. Please try again.");
            }
        }

        // Quick Actions
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
                title: `${currentProfileData.company_name} — Norwegian Company Intelligence`,
                text: `Verified corporate profile for ${currentProfileData.company_name} (Org Nr: ${formatOrgDisplay(currentProfileData.org_number)})`,
                url: window.location.href
            };
            if (navigator.share) {
                navigator.share(shareData).catch(() => {});
            } else {
                navigator.clipboard.writeText(window.location.href).then(() => {
                    showToast("Profile link copied to clipboard");
                });
            }
        }

        function exportJSON() {
            if (!currentProfileData) return;
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(currentProfileData, null, 2));
            const downloadAnchor = document.createElement('a');
            downloadAnchor.setAttribute("href", dataStr);
            downloadAnchor.setAttribute("download", `${currentProfileData.org_number}_profile.json`);
            document.body.appendChild(downloadAnchor);
            downloadAnchor.click();
            downloadAnchor.remove();
            showToast("JSON company record exported");
        }

        // Initialize Search History on Load
        window.addEventListener('DOMContentLoaded', () => {
            renderSearchHistory();
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
            
            # Intelligent normalization and validation at backend
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
    print(f"[*] Signalpost NordIntel SaaS Platform running at http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")

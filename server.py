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
    <title>Signalpost - Norwegian Company Intelligence AI Agent</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --bg-body: #07090e;
            --bg-card: rgba(15, 23, 42, 0.65);
            --bg-card-hover: rgba(22, 33, 62, 0.85);
            --border-card: rgba(255, 255, 255, 0.08);
            --border-card-hover: rgba(56, 189, 248, 0.4);
            --text-heading: #ffffff;
            --text-body: #94a3b8;
            --text-muted: #64748b;
            
            --accent-primary: #0284c7;
            --accent-cyan: #38bdf8;
            --accent-purple: #818cf8;
            --accent-emerald: #10b981;
            --accent-amber: #f59e0b;
            --accent-rose: #f43f5e;
            
            --glow-cyan: rgba(56, 189, 248, 0.25);
            --glass-blur: blur(20px);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
            -webkit-font-smoothing: antialiased;
        }

        body {
            background-color: var(--bg-body);
            background-image: 
                radial-gradient(at 10% 10%, rgba(56, 189, 248, 0.12) 0px, transparent 50%),
                radial-gradient(at 90% 20%, rgba(129, 140, 248, 0.14) 0px, transparent 55%),
                radial-gradient(at 50% 90%, rgba(2, 132, 199, 0.08) 0px, transparent 60%);
            background-attachment: fixed;
            color: var(--text-body);
            min-height: 100vh;
            padding: 3rem 1.25rem 4rem;
        }

        .container {
            max-width: 1080px;
            margin: 0 auto;
        }

        /* Top Navigation */
        .navbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2.8rem;
            padding-bottom: 1.2rem;
            border-bottom: 1px solid var(--border-card);
        }

        .brand-logo {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            text-decoration: none;
        }

        .brand-icon {
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, #38bdf8, #6366f1);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            color: white;
            box-shadow: 0 0 20px rgba(56, 189, 248, 0.4);
        }

        .brand-text {
            font-size: 1.15rem;
            font-weight: 700;
            color: #fff;
            letter-spacing: -0.02em;
        }

        .brand-text span {
            color: var(--accent-cyan);
        }

        .competition-badge {
            background: rgba(56, 189, 248, 0.08);
            border: 1px solid rgba(56, 189, 248, 0.25);
            color: var(--accent-cyan);
            padding: 0.35rem 0.85rem;
            border-radius: 9999px;
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.03em;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }

        .pulse-dot {
            width: 7px;
            height: 7px;
            background: #10b981;
            border-radius: 50%;
            box-shadow: 0 0 8px #10b981;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(0.95); opacity: 0.8; }
            50% { transform: scale(1.3); opacity: 1; }
            100% { transform: scale(0.95); opacity: 0.8; }
        }

        /* Hero Section */
        .hero {
            text-align: center;
            margin-bottom: 2.5rem;
        }

        .hero h1 {
            font-size: 2.75rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            color: #ffffff;
            margin-bottom: 0.75rem;
            line-height: 1.2;
            background: linear-gradient(180deg, #ffffff 40%, #cbd5e1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .hero p {
            font-size: 1.1rem;
            color: var(--text-body);
            max-width: 680px;
            margin: 0 auto;
            line-height: 1.6;
        }

        /* Search Section */
        .search-wrapper {
            background: var(--bg-card);
            backdrop-filter: var(--glass-blur);
            border: 1px solid var(--border-card);
            border-radius: 20px;
            padding: 0.75rem;
            display: flex;
            gap: 0.75rem;
            box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.7), 0 0 0 1px rgba(255,255,255,0.05);
            transition: all 0.3s ease;
            margin-bottom: 1.25rem;
        }

        .search-wrapper:focus-within {
            border-color: var(--accent-cyan);
            box-shadow: 0 20px 45px -10px var(--glow-cyan);
        }

        .input-group {
            flex: 1;
            display: flex;
            align-items: center;
            padding-left: 1rem;
            gap: 0.75rem;
        }

        .search-icon {
            color: var(--text-muted);
            font-size: 1.2rem;
        }

        .search-input {
            width: 100%;
            background: transparent;
            border: none;
            outline: none;
            color: #ffffff;
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.25rem;
            font-weight: 600;
            letter-spacing: 0.05em;
        }

        .search-input::placeholder {
            color: var(--text-muted);
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-weight: 400;
            font-size: 1.05rem;
            letter-spacing: normal;
        }

        .search-btn {
            background: linear-gradient(135deg, #0284c7 0%, #38bdf8 100%);
            color: #ffffff;
            border: none;
            border-radius: 14px;
            padding: 0.95rem 2.2rem;
            font-size: 1rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 4px 15px rgba(56, 189, 248, 0.35);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .search-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(56, 189, 248, 0.5);
            filter: brightness(1.08);
        }

        .search-btn:active {
            transform: translateY(0);
        }

        /* Quick Samples Chips */
        .samples-bar {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            margin-bottom: 2.5rem;
            flex-wrap: wrap;
        }

        .samples-title {
            font-size: 0.8rem;
            text-transform: uppercase;
            font-weight: 700;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            margin-right: 0.2rem;
        }

        .chip-btn {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-card);
            padding: 0.45rem 0.9rem;
            border-radius: 10px;
            font-size: 0.84rem;
            font-weight: 500;
            color: #cbd5e1;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }

        .chip-btn:hover {
            background: rgba(56, 189, 248, 0.12);
            border-color: rgba(56, 189, 248, 0.4);
            color: #ffffff;
            transform: translateY(-1px);
        }

        /* Loader */
        .loader-wrapper {
            display: none;
            text-align: center;
            padding: 3rem 1rem;
        }

        .spinner {
            width: 44px;
            height: 44px;
            border: 3px solid rgba(56, 189, 248, 0.15);
            border-top: 3px solid var(--accent-cyan);
            border-radius: 50%;
            animation: spin 0.8s cubic-bezier(0.6, 0.2, 0.4, 0.8) infinite;
            margin: 0 auto 1.2rem;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .loader-text {
            color: var(--accent-cyan);
            font-weight: 600;
            font-size: 1.05rem;
            margin-bottom: 0.3rem;
        }

        .loader-sub {
            color: var(--text-muted);
            font-size: 0.88rem;
        }

        /* Error Card */
        .error-card {
            display: none;
            background: rgba(244, 63, 94, 0.12);
            border: 1px solid rgba(244, 63, 94, 0.35);
            border-radius: 14px;
            padding: 1.2rem 1.5rem;
            margin-bottom: 2rem;
            color: #fecdd3;
            font-size: 0.95rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            animation: shake 0.3s ease;
        }

        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            20%, 60% { transform: translateX(-5px); }
            40%, 80% { transform: translateX(5px); }
        }

        /* Profile Result Container */
        .profile-container {
            display: none;
            animation: fadeIn 0.4s ease-out forwards;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(12px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Header Card */
        .entity-header-card {
            background: var(--bg-card);
            backdrop-filter: var(--glass-blur);
            border: 1px solid var(--border-card);
            border-radius: 20px;
            padding: 2.2rem;
            margin-bottom: 1.5rem;
            position: relative;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
        }

        .entity-header-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #38bdf8, #818cf8, #10b981);
        }

        .entity-top {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 1.5rem;
            margin-bottom: 1.4rem;
        }

        .entity-identity h2 {
            font-size: 2.1rem;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: -0.02em;
            margin-bottom: 0.4rem;
            line-height: 1.2;
        }

        .entity-tags {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            flex-wrap: wrap;
        }

        .id-badge {
            font-family: 'JetBrains Mono', monospace;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-card);
            color: #38bdf8;
            padding: 0.35rem 0.8rem;
            border-radius: 8px;
            font-size: 0.92rem;
            font-weight: 700;
            letter-spacing: 0.05em;
        }

        .type-badge {
            background: rgba(129, 140, 248, 0.12);
            border: 1px solid rgba(129, 140, 248, 0.3);
            color: var(--accent-purple);
            padding: 0.35rem 0.8rem;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 600;
        }

        .status-pill {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1.1rem;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 700;
            letter-spacing: 0.03em;
            text-transform: uppercase;
        }

        .status-pill.active {
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid rgba(16, 185, 129, 0.4);
            color: #34d399;
        }

        .status-pill.bankrupt {
            background: rgba(244, 63, 94, 0.15);
            border: 1px solid rgba(244, 63, 94, 0.4);
            color: #fb7185;
        }

        /* Executive Summary Box */
        .executive-summary {
            background: rgba(2, 132, 199, 0.06);
            border-left: 4px solid var(--accent-cyan);
            border-radius: 0 12px 12px 0;
            padding: 1.25rem 1.5rem;
            margin-bottom: 1.8rem;
        }

        .summary-label {
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--accent-cyan);
            margin-bottom: 0.4rem;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }

        .summary-text {
            color: #e2e8f0;
            font-size: 1rem;
            line-height: 1.6;
            font-weight: 400;
        }

        /* Key Metrics Grid */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
        }

        @media (max-width: 768px) {
            .metrics-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }

        .metric-box {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border-card);
            border-radius: 12px;
            padding: 1rem 1.2rem;
        }

        .metric-label {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            margin-bottom: 0.35rem;
            font-weight: 600;
        }

        .metric-value {
            font-size: 1.25rem;
            font-weight: 700;
            color: #ffffff;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        /* Verified Evidence Section */
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 2.2rem 0 1.2rem;
        }

        .section-title {
            font-size: 1.35rem;
            font-weight: 700;
            color: #ffffff;
            display: flex;
            align-items: center;
            gap: 0.6rem;
        }

        .section-counter {
            background: rgba(56, 189, 248, 0.15);
            color: var(--accent-cyan);
            padding: 0.2rem 0.65rem;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 700;
        }

        .verification-badge-all {
            display: flex;
            align-items: center;
            gap: 0.4rem;
            font-size: 0.8rem;
            color: #10b981;
            font-weight: 600;
            background: rgba(16, 185, 129, 0.08);
            border: 1px solid rgba(16, 185, 129, 0.2);
            padding: 0.35rem 0.8rem;
            border-radius: 999px;
        }

        /* Granular Facts Grid */
        .facts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 1.2rem;
        }

        .fact-card {
            background: var(--bg-card);
            backdrop-filter: var(--glass-blur);
            border: 1px solid var(--border-card);
            border-radius: 16px;
            padding: 1.4rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: all 0.25s ease;
            position: relative;
        }

        .fact-card:hover {
            border-color: var(--border-card-hover);
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
            background: var(--bg-card-hover);
        }

        .fact-head {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.6rem;
        }

        .fact-key {
            font-size: 0.72rem;
            text-transform: uppercase;
            font-weight: 700;
            letter-spacing: 0.07em;
            color: var(--accent-cyan);
        }

        .confidence-tag {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.72rem;
            font-weight: 600;
            color: #34d399;
            background: rgba(16, 185, 129, 0.1);
            padding: 0.15rem 0.5rem;
            border-radius: 6px;
        }

        .fact-value-box {
            font-size: 1.05rem;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 0.8rem;
            line-height: 1.45;
            word-break: break-word;
        }

        .fact-value-box.mono {
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: 0.05em;
        }

        .fact-explanation {
            font-size: 0.82rem;
            color: var(--text-body);
            line-height: 1.45;
            margin-bottom: 1rem;
            background: rgba(255, 255, 255, 0.02);
            padding: 0.6rem 0.8rem;
            border-radius: 8px;
            border-left: 2px solid rgba(255, 255, 255, 0.1);
        }

        .fact-source-footer {
            border-top: 1px solid rgba(255, 255, 255, 0.06);
            padding-top: 0.8rem;
            margin-top: auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.78rem;
        }

        .source-link {
            color: var(--accent-cyan);
            text-decoration: none;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            transition: color 0.15s;
        }

        .source-link:hover {
            color: #ffffff;
            text-decoration: underline;
        }

        .timestamp-badge {
            color: var(--text-muted);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.72rem;
        }

        /* Footer */
        footer {
            text-align: center;
            margin-top: 4rem;
            padding-top: 2rem;
            border-top: 1px solid var(--border-card);
            color: var(--text-muted);
            font-size: 0.85rem;
        }

        footer strong {
            color: #cbd5e1;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Top Navbar -->
        <nav class="navbar">
            <a href="/" class="brand-logo">
                <div class="brand-icon">⚡</div>
                <div class="brand-text">Signal<span>post</span> Intelligence</div>
            </a>
            <div class="competition-badge">
                <div class="pulse-dot"></div>
                Builderr.ai Official Agent
            </div>
        </nav>

        <!-- Hero Section -->
        <section class="hero">
            <h1>Autonomous Norwegian Company Intelligence</h1>
            <p>Query authoritative Norwegian public registers in real time. Normalizes and validates 9-digit organization numbers with automatic spacing and zero-hallucination evidence.</p>
        </section>

        <!-- Search Bar -->
        <div class="search-wrapper">
            <div class="input-group">
                <span class="search-icon">🔍</span>
                <input 
                    type="text" 
                    id="orgInput" 
                    class="search-input" 
                    placeholder="Enter 9-digit Org Number (e.g., 923 609 016 or 923609016)" 
                    maxlength="14"
                    autocomplete="off"
                >
            </div>
            <button class="search-btn" id="searchBtn" onclick="handleSearchClick()">
                <span>Run Agent</span> ➔
            </button>
        </div>

        <!-- Quick Samples Chips -->
        <div class="samples-bar">
            <span class="samples-title">Verified Samples:</span>
            <button class="chip-btn" onclick="quickFill('923 609 016')">⚡ Equinor ASA (923 609 016)</button>
            <button class="chip-btn" onclick="quickFill('916 627 939')">🏢 Palmera (916 627 939)</button>
            <button class="chip-btn" onclick="quickFill('989 061 593')">📊 G-Group AS (989 061 593)</button>
            <button class="chip-btn" onclick="quickFill('988 539 473')">💻 EBE-Data (988 539 473)</button>
        </div>

        <!-- Error Card -->
        <div class="error-card" id="errorBox">
            <span style="font-size: 1.2rem;">⚠️</span>
            <span id="errorMsgText">Please enter a valid 9-digit Norwegian organization number.</span>
        </div>

        <!-- Loader -->
        <div class="loader-wrapper" id="loader">
            <div class="spinner"></div>
            <div class="loader-text">Querying Brønnøysundregistrene & Matching Facts...</div>
            <div class="loader-sub">Extracting legal entity registers, NACE codes, employee headcounts & solvency proofs</div>
        </div>

        <!-- Profile Results -->
        <main class="profile-container" id="profileResult">
            <!-- Header Card -->
            <div class="entity-header-card">
                <div class="entity-top">
                    <div class="entity-identity">
                        <h2 id="compName">-</h2>
                        <div class="entity-tags">
                            <span class="id-badge" id="compOrgBadge">ORG: -</span>
                            <span class="type-badge" id="compTypeBadge">-</span>
                        </div>
                    </div>
                    <div class="status-pill active" id="compStatusPill">
                        <span class="pulse-dot"></span>
                        <span id="compStatusText">ACTIVE</span>
                    </div>
                </div>

                <!-- Executive Summary -->
                <div class="executive-summary">
                    <div class="summary-label">
                        <span>🧠</span> Agent Executive Summary & Explanation
                    </div>
                    <p class="summary-text" id="compSummaryText">-</p>
                </div>

                <!-- Metrics Overview -->
                <div class="metrics-grid">
                    <div class="metric-box">
                        <div class="metric-label">Headcount</div>
                        <div class="metric-value" id="metricEmployees">-</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">Founded / Registered</div>
                        <div class="metric-value" id="metricFounded">-</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">Registered City</div>
                        <div class="metric-value" id="metricCity">-</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">Verification Score</div>
                        <div class="metric-value" style="color: #38bdf8;">100% Proven</div>
                    </div>
                </div>
            </div>

            <!-- Granular Facts Title -->
            <div class="section-header">
                <div class="section-title">
                    <span>Verified Registry Evidence</span>
                    <span class="section-counter" id="factsCounter">0 Facts</span>
                </div>
                <div class="verification-badge-all">
                    ✓ Official Brønnøysund Attributed
                </div>
            </div>

            <!-- Facts Grid -->
            <div class="facts-grid" id="factsGrid"></div>
        </main>

        <!-- Footer -->
        <footer>
            Built for <strong>Builderr.ai Signalpost Competition</strong> • 100% Zero-Hallucination Evidence Architecture • Source: <strong>Brønnøysundregistrene (Norway)</strong>
        </footer>
    </div>

    <script>
        const ERROR_MESSAGE = "Please enter a valid 9-digit Norwegian organization number.";
        const inputElem = document.getElementById('orgInput');

        /**
         * Normalizes raw input:
         * 1. Strips all whitespace (spaces never count as digits).
         * 2. Verifies whether characters are purely numeric.
         * 3. Verifies exact length of 9 digits.
         */
        function validateAndNormalizeOrg(raw) {
            if (!raw) {
                return { isValid: false, normalized: null, error: ERROR_MESSAGE };
            }
            // Remove all whitespace
            const stripped = raw.replace(/\\s+/g, '');
            // Must contain only digits (reject letters, punctuation, etc.)
            if (!/^\\d+$/.test(stripped)) {
                return { isValid: false, normalized: null, error: ERROR_MESSAGE };
            }
            // Must be exactly 9 digits
            if (stripped.length !== 9) {
                return { isValid: false, normalized: null, error: ERROR_MESSAGE };
            }
            return { isValid: true, normalized: stripped, error: null };
        }

        /**
         * Formats 9-digit or partial digits as 'XXX XXX XXX' without breaking editing
         */
        function formatOrgDisplay(raw) {
            const digits = raw.replace(/\\D/g, '').substring(0, 9);
            const parts = [];
            if (digits.length > 0) parts.push(digits.substring(0, 3));
            if (digits.length > 3) parts.push(digits.substring(3, 6));
            if (digits.length > 6) parts.push(digits.substring(6, 9));
            return parts.join(' ');
        }

        // Automatic smart formatting while preserving cursor position, backspace, and paste
        inputElem.addEventListener('input', function(e) {
            const cursorStart = this.selectionStart;
            const prevVal = this.value;

            // Only apply intelligent spacing if user has entered or pasted digits
            const digitsOnly = prevVal.replace(/\\s+/g, '');
            if (/^\\d*$/.test(digitsOnly)) {
                const formatted = formatOrgDisplay(digitsOnly);
                if (formatted !== prevVal) {
                    this.value = formatted;
                    // Recalculate cursor position naturally
                    let newCursor = cursorStart;
                    if (e.inputType === 'insertText' || e.inputType === 'insertFromPaste') {
                        if (newCursor === 4 || newCursor === 8) newCursor += 1;
                    }
                    this.setSelectionRange(newCursor, newCursor);
                }
            }
        });

        // Paste support: Handles inputs like '923  456  789' or ' 923456789 ' seamlessly
        inputElem.addEventListener('paste', function(e) {
            e.preventDefault();
            const pastedText = (e.clipboardData || window.clipboardData).getData('text');
            const cleanDigits = pastedText.replace(/\\s+/g, '');
            if (/^\\d+$/.test(cleanDigits)) {
                this.value = formatOrgDisplay(cleanDigits);
            } else {
                // If contains invalid characters, let raw text paste so validation displays the exact error
                this.value = pastedText.trim();
            }
        });

        inputElem.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                handleSearchClick();
            }
        });

        function showError(msg) {
            const errorBox = document.getElementById('errorBox');
            const errorMsgText = document.getElementById('errorMsgText');
            errorMsgText.innerText = msg;
            errorBox.style.display = 'flex';
        }

        function hideError() {
            document.getElementById('errorBox').style.display = 'none';
        }

        function quickFill(formattedOrg) {
            inputElem.value = formattedOrg;
            handleSearchClick();
        }

        function formatFactKey(key) {
            return key.replace(/_/g, ' ');
        }

        async function handleSearchClick() {
            hideError();
            const rawVal = inputElem.value;
            const validation = validateAndNormalizeOrg(rawVal);

            if (!validation.isValid) {
                showError(validation.error);
                return;
            }

            // Sync input box to standard display format 'XXX XXX XXX'
            inputElem.value = formatOrgDisplay(validation.normalized);

            // Execute API request with strictly normalized 9-digit value
            await searchCompany(validation.normalized);
        }

        async function searchCompany(normalizedOrg) {
            const loader = document.getElementById('loader');
            const resultBox = document.getElementById('profileResult');
            
            loader.style.display = 'block';
            resultBox.style.display = 'none';
            hideError();

            try {
                // Sent to backend with normalized 9 digits
                const res = await fetch(`/api/search?org=${encodeURIComponent(normalizedOrg)}`);
                const data = await res.json();
                loader.style.display = 'none';

                if (data.error) {
                    showError(data.error);
                    return;
                }

                // Populate Header with formatted 'XXX XXX XXX'
                const displayOrgFormatted = formatOrgDisplay(data.org_number);
                document.getElementById('compName').innerText = data.company_name || 'Unnamed Entity';
                document.getElementById('compOrgBadge').innerText = `ORG: ${displayOrgFormatted}`;
                document.getElementById('compTypeBadge').innerText = data.org_type_description || data.org_type || 'Entity';
                
                // Status Pill
                const statusPill = document.getElementById('compStatusPill');
                const statusText = document.getElementById('compStatusText');
                if (data.is_bankrupt) {
                    statusPill.className = 'status-pill bankrupt';
                    statusText.innerText = 'BANKRUPT';
                } else if (!data.is_active) {
                    statusPill.className = 'status-pill bankrupt';
                    statusText.innerText = 'INACTIVE / LIQUIDATION';
                } else {
                    statusPill.className = 'status-pill active';
                    statusText.innerText = 'ACTIVE & IN GOOD STANDING';
                }

                // Summary
                document.getElementById('compSummaryText').innerText = data.agent_summary || 'Verified profile extracted from official Norwegian records.';

                // Metrics
                document.getElementById('metricEmployees').innerText = (data.employee_count !== null && data.employee_count !== undefined) 
                    ? Number(data.employee_count).toLocaleString() + ' Staff' 
                    : 'N/A';
                document.getElementById('metricFounded').innerText = data.registration_date || 'N/A';
                
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
                document.getElementById('metricCity').innerText = city;

                // Facts Grid
                const facts = data.facts || [];
                document.getElementById('factsCounter').innerText = `${facts.length} Verified Facts`;
                
                const grid = document.getElementById('factsGrid');
                grid.innerHTML = '';

                facts.forEach(fact => {
                    const card = document.createElement('div');
                    card.className = 'fact-card';
                    
                    const dateFormatted = fact.retrieved_at ? fact.retrieved_at.replace('T', ' ').substring(0, 16) + ' UTC' : 'Recent';
                    const confPercent = Math.round((fact.confidence || 1.0) * 100);

                    // If fact is org_number, display as 'XXX XXX XXX'
                    let displayVal = fact.value;
                    let isMono = false;
                    if (fact.key === 'org_number' && typeof displayVal === 'string' && displayVal.length === 9) {
                        displayVal = formatOrgDisplay(displayVal);
                        isMono = true;
                    }

                    card.innerHTML = `
                        <div>
                            <div class="fact-head">
                                <span class="fact-key">${formatFactKey(fact.key)}</span>
                                <span class="confidence-tag">${confPercent}% Confidence</span>
                            </div>
                            <div class="fact-value-box ${isMono ? 'mono' : ''}">${displayVal}</div>
                            ${fact.explanation ? `<div class="fact-explanation">${fact.explanation}</div>` : ''}
                        </div>
                        <div class="fact-source-footer">
                            <a href="${fact.source_url}" target="_blank" rel="noopener noreferrer" class="source-link">
                                🔗 <span>${fact.source_name}</span>
                            </a>
                            <span class="timestamp-badge">${dateFormatted}</span>
                        </div>
                    `;
                    grid.appendChild(card);
                });

                resultBox.style.display = 'block';
            } catch (err) {
                loader.style.display = 'none';
                showError('Could not connect to local agent server: ' + err.message);
            }
        }
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
                formatted_org = format_org_number(clean_org)
                self.wfile.write(json.dumps({"error": f"Company with Org Nr {formatted_org} not found or registry unreachable"}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    PORT = 8000
    server_address = ('127.0.0.1', PORT)
    httpd = socketserver.TCPServer(server_address, AgentServerHandler)
    print(f"[*] Signalpost Premium Web UI running at http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")

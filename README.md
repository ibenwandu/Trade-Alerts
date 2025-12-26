# Trade Alerts - Automated LLM Analysis & Entry Point Monitoring

Automated system that:
1. Reads raw forex data from Google Drive "Forex tracker" folder
2. Sends data to multiple LLMs (ChatGPT, Gemini, Claude) for analysis
3. Uses Gemini to review and synthesize final recommendations
4. Emails all recommendations to you
5. Monitors entry/exit points and sends Pushover alerts when hit

## Architecture

```
Google Drive (Raw Data)
    ↓
Read Latest Reports
    ↓
    ├─→ ChatGPT API (Analysis + Recommendations)
    ├─→ Gemini API (Analysis + Recommendations)
    └─→ Claude API (Analysis + Recommendations)
            ↓
    Gemini API (Review & Synthesize Final Recommendation)
            ↓
    ├─→ Email All 4 Recommendations
    └─→ Extract Entry/Exit Points from Gemini Final
            ↓
    Monitor Prices
            ↓
    Pushover Alerts (when entry points hit)
```

## Features

- 📊 Reads hourly forex reports from Google Drive
- 🤖 Multi-LLM analysis (ChatGPT, Gemini, Claude)
- 🧠 Gemini synthesis of final recommendations
- 📧 Email delivery of all recommendations
- 💹 Real-time price monitoring
- 🔔 Pushover alerts when entry points are hit
- ⏰ Scheduled analysis (4x daily: 7am, 9am, 12pm, 4pm)
- 📝 Full logging of all analysis and alerts

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and configure:

```
# Google Drive (for reading raw data)
GOOGLE_DRIVE_FOLDER_ID=your-forex-tracker-folder-id
GOOGLE_DRIVE_CREDENTIALS_JSON=your-credentials-json
GOOGLE_DRIVE_REFRESH_TOKEN=your-refresh-token

# LLM APIs
ANTHROPIC_API_KEY=your-anthropic-key  # Claude
GOOGLE_API_KEY=your-google-key        # Gemini (also used for final synthesis)
OPENAI_API_KEY=your-openai-key        # ChatGPT

# Email (for sending recommendations)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
RECIPIENT_EMAIL=your-email@gmail.com

# Pushover (for entry point alerts)
PUSHOVER_API_TOKEN=your-pushover-token
PUSHOVER_USER_KEY=your-pushover-user-key

# Price API
PRICE_API_URL=https://api.exchangerate-api.com/v4/latest/USD

# Monitoring
CHECK_INTERVAL=60
ENTRY_TOLERANCE_PIPS=10
ENTRY_TOLERANCE_PERCENT=0.1

# Analysis Schedule (24-hour format)
ANALYSIS_TIMES=07:00,09:00,12:00,16:00
```

### 3. Run the System

```bash
python main.py
```

## Project Structure

```
Trade-Alerts/
├── src/
│   ├── __init__.py
│   ├── drive_reader.py      # Read raw data from Google Drive
│   ├── llm_analyzer.py      # Call LLM APIs (ChatGPT, Gemini, Claude)
│   ├── chatgpt_synthesizer.py  # ChatGPT synthesis
│   ├── email_sender.py      # Send recommendations via email
│   ├── recommendation_parser.py  # Extract entry/exit points
│   ├── price_monitor.py     # Monitor real-time prices
│   ├── alert_manager.py     # Send Pushover alerts
│   ├── alert_history.py     # Track sent alerts
│   ├── scheduler.py         # Schedule analysis times
│   └── logger.py            # Logging setup
├── data/
│   └── alerts_history.json  # History of triggered alerts
├── logs/
│   └── trade_alerts.log     # Application logs
├── main.py                  # Main application loop
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Workflow

1. **Read Data**: System reads latest reports from Google Drive "Forex tracker" folder
2. **LLM Analysis**: 
   - Sends data to ChatGPT (with your custom prompt)
   - Sends data to Gemini (with your custom prompt)
   - Sends data to Claude (with your custom prompt)
3. **Synthesis**: Gemini reviews all 3 recommendations and provides final synthesis
4. **Email**: All 4 recommendations (ChatGPT, Gemini, Claude + Gemini final) are emailed
5. **Extract Points**: Entry/exit points extracted from Gemini final recommendation
6. **Monitor**: System monitors prices continuously
7. **Alert**: Pushover notification sent when entry point is hit

## Usage

The system runs continuously:
- Checks schedule for analysis times (7am, 9am, 12pm, 4pm)
- Runs full analysis workflow at scheduled times
- Monitors prices between analysis cycles
- Sends Pushover alerts when entry points are hit

## Notes

- Entry points are monitored with tolerance (default: 10 pips or 0.1%)
- Alerts are one-time per entry point (prevents spam)
- All analysis and alerts are logged for review
- Email includes all 4 recommendations for comparison

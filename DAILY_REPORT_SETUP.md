# Daily Oura Report - Setup Guide

Automated daily health analysis and email reports from your Oura Ring data.

## Features

- 📊 Comprehensive health data analysis
- 💡 Personalized recommendations based on your metrics
- 📧 Beautiful HTML email reports
- ⏰ Automated daily execution
- 📈 Trend tracking and insights

## Quick Setup

### 1. Configure Environment Variables

Edit your `.env` file and add:

```bash
# Required
OURA_ACCESS_TOKEN=your_oura_token_here
RECIPIENT_EMAIL=your_email@example.com

# Optional (for email sending)
SENDER_EMAIL=your_gmail@gmail.com
SENDER_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### 2. Gmail App Password Setup (for email sending)

If you want to receive email reports:

1. Go to your Google Account settings
2. Navigate to Security → 2-Step Verification (enable if not already)
3. Go to Security → App passwords
4. Generate a new app password for "Mail"
5. Copy the 16-character password
6. Add it to `.env` as `SENDER_PASSWORD`

**Note:** You can use any SMTP server, not just Gmail. Adjust SMTP_SERVER and SMTP_PORT accordingly.

### 3. Test the System

Run manually to test:

```bash
python3 daily_oura_report.py
```

This will:
- Fetch your latest Oura data
- Analyze sleep, activity, and readiness
- Generate recommendations
- Save HTML report locally
- Send email (if configured)

### 4. Set Up Daily Automation

Choose one of the following methods:

#### Option A: Cron Job (Linux/Mac)

1. Make the script executable:
```bash
chmod +x daily_oura_report.py
```

2. Edit crontab:
```bash
crontab -e
```

3. Add one of these lines:

```bash
# Run daily at 8:00 AM
0 8 * * * cd /home/user/datasciencecoursera && /usr/bin/python3 daily_oura_report.py >> oura_report.log 2>&1

# Run daily at 9:00 PM
0 21 * * * cd /home/user/datasciencecoursera && /usr/bin/python3 daily_oura_report.py >> oura_report.log 2>&1
```

Replace `/home/user/datasciencecoursera` with your actual path.

4. Verify cron job:
```bash
crontab -l
```

#### Option B: Systemd Timer (Linux)

Create timer service files (more reliable than cron):

1. Create service file: `/etc/systemd/system/oura-report.service`
```ini
[Unit]
Description=Daily Oura Health Report
After=network.target

[Service]
Type=oneshot
User=youruser
WorkingDirectory=/home/user/datasciencecoursera
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 /home/user/datasciencecoursera/daily_oura_report.py

[Install]
WantedBy=multi-user.target
```

2. Create timer file: `/etc/systemd/system/oura-report.timer`
```ini
[Unit]
Description=Daily Oura Health Report Timer
Requires=oura-report.service

[Timer]
OnCalendar=daily
OnCalendar=*-*-* 08:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

3. Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable oura-report.timer
sudo systemctl start oura-report.timer
```

4. Check status:
```bash
sudo systemctl status oura-report.timer
```

#### Option C: Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task → Name it "Oura Daily Report"
3. Trigger: Daily at your preferred time
4. Action: Start a program
   - Program: `python`
   - Arguments: `daily_oura_report.py`
   - Start in: `C:\path\to\datasciencecoursera`

## Report Contents

Your daily report includes:

### Sleep Analysis
- Total sleep duration
- Sleep efficiency
- Resting heart rate
- Heart rate variability (HRV)
- Deep and REM sleep breakdown
- 7-day averages and trends

### Activity Analysis
- Daily steps
- Calories burned
- Activity levels
- Weekly comparisons

### Readiness Score
- Daily readiness score
- Trend analysis (improving/declining/stable)
- Recovery insights

### Personalized Recommendations
- Priority-based action items
- Specific guidance for improvement
- Science-backed health tips

## Customization

### Change Report Frequency

Edit the cron schedule or timer configuration to run:
- Twice daily: `0 8,20 * * *`
- Weekly: `0 8 * * 1` (Mondays at 8 AM)
- Every 3 days: `0 8 */3 * *`

### Adjust Analysis Period

Edit `daily_oura_report.py` line 36:
```python
start_date = end_date - timedelta(days=30)  # Analyze last 30 days instead of 7
```

### Customize Recommendations

Edit `oura_analyzer.py` method `generate_recommendations()` to adjust:
- Health benchmarks
- Priority thresholds
- Recommendation messages

## Troubleshooting

### No Email Received

1. Check spam/junk folder
2. Verify SENDER_EMAIL and SENDER_PASSWORD in `.env`
3. Ensure Gmail app password is correct (not regular password)
4. Check `oura_report.log` for errors

### No Data Available

1. Ensure Oura Ring is syncing properly
2. Check OURA_ACCESS_TOKEN is valid
3. Verify internet connection
4. Check if token has expired (create new one at cloud.ouraring.com)

### Script Fails

1. Check Python version: `python3 --version` (needs 3.7+)
2. Verify dependencies: `pip list | grep -E "requests|pandas|python-dotenv"`
3. Check file permissions: `ls -la daily_oura_report.py`
4. View logs: `tail -f oura_report.log`

## Manual Report Generation

Generate a report anytime:

```bash
# Full report with email
python3 daily_oura_report.py

# Just analysis (save HTML only)
python3 oura_analyzer.py

# View in browser
python3 oura_report_sender.py
```

## Privacy & Security

- Your Oura token is stored locally in `.env` (excluded from git)
- Data files (CSV) contain your health metrics
- Email password uses app-specific password (not main password)
- All data processing happens locally on your machine
- No data is sent to third parties except your email provider

## Advanced Features

### Integration with Other Tools

Export CSV data for analysis in:
- Excel/Google Sheets
- Jupyter notebooks
- R Studio
- Tableau/PowerBI

### API Access

Use the OuraDataFetcher class in your own scripts:

```python
from oura_data_fetcher import OuraDataFetcher

fetcher = OuraDataFetcher(token)
sleep_data = fetcher.get_sleep_data('2026-01-01', '2026-01-31')
```

## Support

For issues or questions:
- Check the troubleshooting section above
- Review error logs: `tail -f oura_report.log`
- Verify Oura API status at status.ouraring.com

## Updates

To update the system:
```bash
git pull origin claude/oura-data-integration-Q8ouY
```

---

**Keep tracking, stay healthy! 💪**

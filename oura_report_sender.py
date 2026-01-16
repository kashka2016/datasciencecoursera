"""
Oura Report Email Sender
Generates and sends formatted health reports via email.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
from typing import Dict


class OuraReportSender:
    """Sends formatted Oura health reports via email."""

    def __init__(self, smtp_server: str = None, smtp_port: int = None,
                 sender_email: str = None, sender_password: str = None):
        """Initialize email sender with SMTP credentials."""
        self.smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.getenv('SMTP_PORT', '587'))
        self.sender_email = sender_email or os.getenv('SENDER_EMAIL')
        self.sender_password = sender_password or os.getenv('SENDER_PASSWORD')

    def format_report_html(self, report: Dict) -> str:
        """Format report as HTML email."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .section {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    border-left: 4px solid #667eea;
                }}
                .section h2 {{
                    color: #667eea;
                    margin-top: 0;
                    border-bottom: 2px solid #e9ecef;
                    padding-bottom: 10px;
                }}
                .metric {{
                    display: inline-block;
                    background: white;
                    padding: 15px;
                    margin: 10px 10px 10px 0;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    min-width: 150px;
                }}
                .metric-label {{
                    font-size: 12px;
                    color: #6c757d;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                .metric-value {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #667eea;
                    margin-top: 5px;
                }}
                .recommendation {{
                    background: white;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 8px;
                    border-left: 4px solid #28a745;
                }}
                .recommendation.high {{
                    border-left-color: #dc3545;
                }}
                .recommendation.medium {{
                    border-left-color: #ffc107;
                }}
                .priority {{
                    display: inline-block;
                    padding: 3px 10px;
                    border-radius: 12px;
                    font-size: 11px;
                    font-weight: bold;
                    margin-right: 10px;
                }}
                .priority.HIGH {{
                    background: #dc3545;
                    color: white;
                }}
                .priority.MEDIUM {{
                    background: #ffc107;
                    color: #333;
                }}
                .priority.LOW {{
                    background: #28a745;
                    color: white;
                }}
                .action {{
                    margin-top: 8px;
                    padding: 10px;
                    background: #e7f3ff;
                    border-radius: 5px;
                    font-size: 14px;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #6c757d;
                    font-size: 12px;
                    margin-top: 30px;
                }}
                .emoji {{
                    font-size: 24px;
                    margin-right: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🌟 Your Daily Oura Health Report</h1>
                <p style="margin: 5px 0;">Generated: {report['report_date']}</p>
                <p style="margin: 5px 0;">Data for: {report['data_date']}</p>
            </div>
        """

        # Sleep Section
        if 'sleep' in report and 'latest_night' in report['sleep']:
            sleep = report['sleep']['latest_night']
            weekly = report['sleep']['weekly_average']

            html += """
            <div class="section">
                <h2>😴 Sleep Analysis</h2>
                <div>
            """

            html += f"""
                    <div class="metric">
                        <div class="metric-label">Total Sleep</div>
                        <div class="metric-value">{sleep['total_sleep_hours']}h</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Efficiency</div>
                        <div class="metric-value">{sleep['efficiency']}%</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Resting HR</div>
                        <div class="metric-value">{sleep['resting_heart_rate']} bpm</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">HRV</div>
                        <div class="metric-value">{sleep['hrv']} ms</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Deep Sleep</div>
                        <div class="metric-value">{int(sleep['deep_sleep_minutes'])} min</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">REM Sleep</div>
                        <div class="metric-value">{int(sleep['rem_sleep_minutes'])} min</div>
                    </div>
                </div>
                <p style="margin-top: 15px;"><strong>7-day Average:</strong> {weekly['total_sleep_hours']}h sleep, {weekly['efficiency']}% efficiency</p>
            </div>
            """

        # Activity Section
        if 'activity' in report and 'latest_day' in report['activity']:
            activity = report['activity']['latest_day']
            weekly = report['activity']['weekly_average']

            html += """
            <div class="section">
                <h2>🏃 Activity Analysis</h2>
                <div>
            """

            html += f"""
                    <div class="metric">
                        <div class="metric-label">Steps</div>
                        <div class="metric-value">{int(activity['steps']):,}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Active Calories</div>
                        <div class="metric-value">{int(activity['active_calories'])}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Total Calories</div>
                        <div class="metric-value">{int(activity['calories_total'])}</div>
                    </div>
                </div>
                <p style="margin-top: 15px;"><strong>7-day Average:</strong> {int(weekly['steps']):,} steps, {int(weekly['active_calories'])} active calories</p>
            </div>
            """

        # Readiness Section
        if 'readiness' in report and 'latest_day' in report['readiness']:
            readiness = report['readiness']['latest_day']
            weekly = report['readiness']['weekly_average']
            trend = report['readiness'].get('trend', 'stable')

            trend_emoji = {'improving': '📈', 'declining': '📉', 'stable': '➡️'}.get(trend, '➡️')
            trend_color = {'improving': '#28a745', 'declining': '#dc3545', 'stable': '#6c757d'}.get(trend, '#6c757d')

            html += f"""
            <div class="section">
                <h2>⚡ Readiness Score</h2>
                <div>
                    <div class="metric">
                        <div class="metric-label">Today's Score</div>
                        <div class="metric-value">{readiness['score']}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">7-day Average</div>
                        <div class="metric-value">{weekly['score']}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Trend</div>
                        <div class="metric-value" style="color: {trend_color};">{trend_emoji} {trend.title()}</div>
                    </div>
                </div>
            </div>
            """

        # Recommendations Section
        if 'recommendations' in report and report['recommendations']:
            html += """
            <div class="section">
                <h2>💡 Personalized Recommendations</h2>
            """

            for rec in report['recommendations']:
                priority_class = rec['priority'].lower()
                html += f"""
                <div class="recommendation {priority_class}">
                    <div>
                        <span class="priority {rec['priority']}">{rec['priority']}</span>
                        <strong>{rec['category']}</strong>
                    </div>
                    <p style="margin: 10px 0;">{rec['message']}</p>
                    <div class="action">
                        <strong>Action:</strong> {rec['action']}
                    </div>
                </div>
                """

            html += "</div>"

        # Footer
        html += """
            <div class="footer">
                <p>This report was automatically generated from your Oura Ring data.</p>
                <p>Keep tracking your health and staying consistent! 💪</p>
            </div>
        </body>
        </html>
        """

        return html

    def send_report(self, recipient_email: str, report: Dict) -> bool:
        """Send formatted report via email."""
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = f"Your Daily Oura Health Report - {report['data_date']}"
            message['From'] = self.sender_email
            message['To'] = recipient_email

            # Generate HTML content
            html_content = self.format_report_html(report)
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)

            print(f"✓ Report sent successfully to {recipient_email}")
            return True

        except Exception as e:
            print(f"✗ Error sending email: {str(e)}")
            return False

    def save_report_html(self, report: Dict, filename: str = None) -> str:
        """Save report as HTML file."""
        if not filename:
            filename = f"oura_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

        html_content = self.format_report_html(report)

        with open(filename, 'w') as f:
            f.write(html_content)

        print(f"✓ Report saved to {filename}")
        return filename


if __name__ == "__main__":
    # Test report generation
    from oura_analyzer import OuraAnalyzer

    print("Generating Oura health report...")
    analyzer = OuraAnalyzer()
    report = analyzer.generate_full_report()

    sender = OuraReportSender()
    html_file = sender.save_report_html(report)
    print(f"Preview your report by opening: {html_file}")

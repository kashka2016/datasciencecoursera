#!/usr/bin/env python3
"""
Daily Oura Report Automation
Fetches latest data, analyzes it, and sends daily health report.
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from oura_data_fetcher import OuraDataFetcher
from oura_analyzer import OuraAnalyzer
from oura_report_sender import OuraReportSender


def main():
    """Main function to run daily report automation."""
    print(f"=== Daily Oura Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")

    # Load environment variables
    load_dotenv()

    # Check for required environment variables
    oura_token = os.getenv('OURA_ACCESS_TOKEN')
    recipient_email = os.getenv('RECIPIENT_EMAIL')

    if not oura_token:
        print("✗ Error: OURA_ACCESS_TOKEN not set in environment")
        print("Add it to your .env file: OURA_ACCESS_TOKEN=your_token_here")
        sys.exit(1)

    if not recipient_email:
        print("✗ Error: RECIPIENT_EMAIL not set in environment")
        print("Add it to your .env file: RECIPIENT_EMAIL=your_email@example.com")
        sys.exit(1)

    try:
        # Step 1: Fetch latest data from Oura
        print("Step 1: Fetching latest data from Oura...")
        fetcher = OuraDataFetcher(oura_token)

        # Get data for the last 7 days
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)

        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')

        print(f"  Fetching data from {start_str} to {end_str}...")

        # Fetch all data types
        sleep_data = fetcher.get_sleep_data(start_str, end_str)
        if not sleep_data.empty:
            fetcher.export_data_to_csv(sleep_data, 'oura_sleep_data.csv')
            print(f"  ✓ Sleep data: {len(sleep_data)} records")

        activity_data = fetcher.get_daily_activity(start_str, end_str)
        if not activity_data.empty:
            fetcher.export_data_to_csv(activity_data, 'oura_activity_data.csv')
            print(f"  ✓ Activity data: {len(activity_data)} records")

        readiness_data = fetcher.get_daily_readiness(start_str, end_str)
        if not readiness_data.empty:
            fetcher.export_data_to_csv(readiness_data, 'oura_readiness_data.csv')
            print(f"  ✓ Readiness data: {len(readiness_data)} records")

        print("  ✓ Data fetch completed\n")

        # Step 2: Analyze the data
        print("Step 2: Analyzing health data...")
        analyzer = OuraAnalyzer()
        report = analyzer.generate_full_report()
        print("  ✓ Analysis completed\n")

        # Step 3: Generate and send report
        print("Step 3: Generating report...")
        sender = OuraReportSender()

        # Always save HTML report locally
        html_file = sender.save_report_html(report)
        print(f"  ✓ Report saved: {html_file}\n")

        # Check if email is configured
        sender_email = os.getenv('SENDER_EMAIL')
        sender_password = os.getenv('SENDER_PASSWORD')

        if sender_email and sender_password:
            print("Step 4: Sending email report...")
            success = sender.send_report(recipient_email, report)
            if success:
                print("  ✓ Email sent successfully\n")
            else:
                print("  ✗ Email sending failed\n")
        else:
            print("Step 4: Email not configured (skipped)")
            print("  To enable email reports, add to .env:")
            print("    SENDER_EMAIL=your_email@gmail.com")
            print("    SENDER_PASSWORD=your_app_password")
            print(f"  Preview your report at: {html_file}\n")

        # Print summary
        print("=== Report Summary ===")
        if 'recommendations' in report:
            print(f"Generated {len(report['recommendations'])} recommendations")
            high_priority = [r for r in report['recommendations'] if r['priority'] == 'HIGH']
            if high_priority:
                print("\nHigh Priority Items:")
                for rec in high_priority:
                    print(f"  • {rec['category']}: {rec['message']}")

        print("\n✓ Daily report process completed successfully!")

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

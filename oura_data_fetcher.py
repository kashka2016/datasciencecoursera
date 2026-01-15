"""
Oura Ring Data Fetcher
This script connects to the Oura API v2 and retrieves health data.
"""

import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd


class OuraDataFetcher:
    """Class to handle Oura API data retrieval."""

    BASE_URL = "https://api.ouraring.com/v2/usercollection"

    def __init__(self, access_token: str):
        """
        Initialize the Oura data fetcher.

        Args:
            access_token: Personal access token from Oura
        """
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {access_token}'
        }

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the Oura API.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            JSON response as dictionary
        """
        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")

    def get_personal_info(self) -> Dict:
        """Get personal information."""
        return self._make_request("personal_info")

    def get_sleep_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get sleep data for a date range.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with sleep data
        """
        params = {
            'start_date': start_date,
            'end_date': end_date
        }
        data = self._make_request("sleep", params)

        if 'data' in data and len(data['data']) > 0:
            return pd.DataFrame(data['data'])
        else:
            return pd.DataFrame()

    def get_daily_activity(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get daily activity data for a date range.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with activity data
        """
        params = {
            'start_date': start_date,
            'end_date': end_date
        }
        data = self._make_request("daily_activity", params)

        if 'data' in data and len(data['data']) > 0:
            return pd.DataFrame(data['data'])
        else:
            return pd.DataFrame()

    def get_daily_readiness(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get daily readiness data for a date range.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with readiness data
        """
        params = {
            'start_date': start_date,
            'end_date': end_date
        }
        data = self._make_request("daily_readiness", params)

        if 'data' in data and len(data['data']) > 0:
            return pd.DataFrame(data['data'])
        else:
            return pd.DataFrame()

    def get_heart_rate(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get heart rate data for a date range.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with heart rate data
        """
        params = {
            'start_date': start_date,
            'end_date': end_date
        }
        data = self._make_request("heartrate", params)

        if 'data' in data and len(data['data']) > 0:
            return pd.DataFrame(data['data'])
        else:
            return pd.DataFrame()

    def get_workouts(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get workout data for a date range.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with workout data
        """
        params = {
            'start_date': start_date,
            'end_date': end_date
        }
        data = self._make_request("workout", params)

        if 'data' in data and len(data['data']) > 0:
            return pd.DataFrame(data['data'])
        else:
            return pd.DataFrame()

    def export_data_to_csv(self, data: pd.DataFrame, filename: str):
        """
        Export data to CSV file.

        Args:
            data: DataFrame to export
            filename: Output filename
        """
        data.to_csv(filename, index=False)
        print(f"Data exported to {filename}")


def main():
    """Main function to demonstrate usage."""
    # Load access token from environment variable
    access_token = os.getenv('OURA_ACCESS_TOKEN')

    if not access_token:
        print("Error: OURA_ACCESS_TOKEN environment variable not set")
        print("Please set your Oura personal access token:")
        print("export OURA_ACCESS_TOKEN='your_token_here'")
        return

    # Initialize fetcher
    fetcher = OuraDataFetcher(access_token)

    try:
        # Get personal info
        print("Fetching personal information...")
        personal_info = fetcher.get_personal_info()
        print(f"User: {json.dumps(personal_info, indent=2)}")

        # Set date range (last 7 days)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)

        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')

        print(f"\nFetching data from {start_str} to {end_str}...")

        # Get sleep data
        print("\nFetching sleep data...")
        sleep_data = fetcher.get_sleep_data(start_str, end_str)
        if not sleep_data.empty:
            print(f"Retrieved {len(sleep_data)} sleep records")
            fetcher.export_data_to_csv(sleep_data, 'oura_sleep_data.csv')
        else:
            print("No sleep data available")

        # Get activity data
        print("\nFetching activity data...")
        activity_data = fetcher.get_daily_activity(start_str, end_str)
        if not activity_data.empty:
            print(f"Retrieved {len(activity_data)} activity records")
            fetcher.export_data_to_csv(activity_data, 'oura_activity_data.csv')
        else:
            print("No activity data available")

        # Get readiness data
        print("\nFetching readiness data...")
        readiness_data = fetcher.get_daily_readiness(start_str, end_str)
        if not readiness_data.empty:
            print(f"Retrieved {len(readiness_data)} readiness records")
            fetcher.export_data_to_csv(readiness_data, 'oura_readiness_data.csv')
        else:
            print("No readiness data available")

        print("\n✓ Data fetch completed successfully!")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()

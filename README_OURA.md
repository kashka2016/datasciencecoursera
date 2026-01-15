# Oura Data Integration

This project provides a Python script to connect to the Oura Ring API and retrieve health data.

## Features

- Connect to Oura API v2
- Retrieve personal information
- Fetch sleep data
- Fetch daily activity data
- Fetch daily readiness data
- Fetch heart rate data
- Fetch workout data
- Export data to CSV files

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Your Oura Access Token

1. Go to [Oura Cloud Personal Access Tokens](https://cloud.ouraring.com/personal-access-tokens)
2. Log in to your Oura account
3. Create a new personal access token
4. Copy the token (you'll only see it once!)

### 3. Configure Environment

Create a `.env` file in the project directory:

```bash
cp .env.example .env
```

Edit `.env` and add your token:

```
OURA_ACCESS_TOKEN=your_actual_token_here
```

Alternatively, export the token as an environment variable:

```bash
export OURA_ACCESS_TOKEN='your_actual_token_here'
```

## Usage

### Basic Usage

Run the script to fetch the last 7 days of data:

```bash
python oura_data_fetcher.py
```

### Use as a Module

```python
from oura_data_fetcher import OuraDataFetcher
from datetime import datetime, timedelta

# Initialize
access_token = "your_token_here"
fetcher = OuraDataFetcher(access_token)

# Get personal info
personal_info = fetcher.get_personal_info()

# Get sleep data for last 30 days
end_date = datetime.now().date()
start_date = end_date - timedelta(days=30)
sleep_data = fetcher.get_sleep_data(
    start_date.strftime('%Y-%m-%d'),
    end_date.strftime('%Y-%m-%d')
)

# Export to CSV
fetcher.export_data_to_csv(sleep_data, 'my_sleep_data.csv')
```

## Available Data Types

- **Personal Info**: Basic user information
- **Sleep**: Sleep stages, duration, efficiency, heart rate during sleep
- **Activity**: Steps, calories, activity levels, movement
- **Readiness**: Recovery score and contributing factors
- **Heart Rate**: Detailed heart rate measurements
- **Workouts**: Exercise sessions and metrics

## Output Files

The script generates CSV files:
- `oura_sleep_data.csv` - Sleep data
- `oura_activity_data.csv` - Activity data
- `oura_readiness_data.csv` - Readiness scores

## API Documentation

For more information about the Oura API, visit:
- [Oura API v2 Documentation](https://cloud.ouraring.com/v2/docs)

## Security Notes

- Never commit your `.env` file or access token to version control
- The `.gitignore` file is configured to exclude sensitive files
- Rotate your access token periodically for security

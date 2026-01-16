"""
Oura Data Analyzer
Analyzes Oura health data and generates insights and recommendations.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class OuraAnalyzer:
    """Analyzes Oura health data and provides insights."""

    # Health benchmarks
    BENCHMARKS = {
        'sleep': {
            'efficiency_optimal': 85,
            'efficiency_good': 75,
            'total_sleep_optimal': 7 * 3600,  # 7 hours in seconds
            'total_sleep_minimum': 6 * 3600,   # 6 hours in seconds
            'deep_sleep_percent': 15,  # % of total sleep
            'rem_sleep_percent': 20,   # % of total sleep
            'resting_hr_normal': 60,
            'hrv_good': 50,
        },
        'activity': {
            'steps_optimal': 10000,
            'steps_minimum': 5000,
            'calories_active': 300,
        },
        'readiness': {
            'optimal': 85,
            'good': 70,
        }
    }

    def __init__(self, sleep_file: str = 'oura_sleep_data.csv',
                 activity_file: str = 'oura_activity_data.csv',
                 readiness_file: str = 'oura_readiness_data.csv'):
        """Initialize analyzer with data files."""
        self.sleep_df = self._load_csv(sleep_file)
        self.activity_df = self._load_csv(activity_file)
        self.readiness_df = self._load_csv(readiness_file)

    def _load_csv(self, filename: str) -> pd.DataFrame:
        """Load CSV file safely."""
        try:
            return pd.read_csv(filename)
        except FileNotFoundError:
            return pd.DataFrame()

    def get_latest_date(self) -> str:
        """Get the most recent date in the data."""
        dates = []
        if not self.sleep_df.empty and 'day' in self.sleep_df.columns:
            dates.append(pd.to_datetime(self.sleep_df['day']).max())
        if not self.activity_df.empty and 'day' in self.activity_df.columns:
            dates.append(pd.to_datetime(self.activity_df['day']).max())

        if dates:
            return max(dates).strftime('%Y-%m-%d')
        return datetime.now().strftime('%Y-%m-%d')

    def analyze_sleep(self, days: int = 7) -> Dict:
        """Analyze sleep data for the last N days."""
        if self.sleep_df.empty:
            return {'error': 'No sleep data available'}

        df = self.sleep_df.copy()
        df['day'] = pd.to_datetime(df['day'])

        # Get recent data
        latest_date = df['day'].max()
        start_date = latest_date - timedelta(days=days-1)
        recent_df = df[df['day'] >= start_date].copy()

        # Calculate total sleep duration
        if 'total_sleep_duration' in recent_df.columns:
            recent_df['total_sleep_hours'] = recent_df['total_sleep_duration'] / 3600
        elif 'deep_sleep_duration' in recent_df.columns and 'light_sleep_duration' in recent_df.columns:
            recent_df['total_sleep_hours'] = (
                recent_df['deep_sleep_duration'] +
                recent_df['light_sleep_duration'] +
                recent_df.get('rem_sleep_duration', 0)
            ) / 3600

        # Latest night metrics
        latest = recent_df.iloc[-1] if not recent_df.empty else {}

        analysis = {
            'latest_night': {
                'date': latest.get('day', 'N/A'),
                'total_sleep_hours': round(latest.get('total_sleep_hours', 0), 1),
                'efficiency': latest.get('efficiency', 0),
                'deep_sleep_minutes': round(latest.get('deep_sleep_duration', 0) / 60, 0) if 'deep_sleep_duration' in latest else 0,
                'rem_sleep_minutes': round(latest.get('rem_sleep_duration', 0) / 60, 0) if 'rem_sleep_duration' in latest else 0,
                'awake_time_minutes': round(latest.get('awake_time', 0) / 60, 0) if 'awake_time' in latest else 0,
                'resting_heart_rate': latest.get('lowest_heart_rate', latest.get('average_heart_rate', 0)),
                'hrv': latest.get('average_hrv', 0),
            },
            'weekly_average': {
                'total_sleep_hours': round(recent_df.get('total_sleep_hours', pd.Series([0])).mean(), 1),
                'efficiency': round(recent_df.get('efficiency', pd.Series([0])).mean(), 1),
                'resting_heart_rate': round(recent_df.get('lowest_heart_rate', recent_df.get('average_heart_rate', pd.Series([0]))).mean(), 1),
                'hrv': round(recent_df.get('average_hrv', pd.Series([0])).mean(), 1),
            },
            'trends': {
                'sleep_debt': self._calculate_sleep_debt(recent_df),
                'consistency_score': self._calculate_sleep_consistency(recent_df),
            }
        }

        return analysis

    def analyze_activity(self, days: int = 7) -> Dict:
        """Analyze activity data for the last N days."""
        if self.activity_df.empty:
            return {'error': 'No activity data available'}

        df = self.activity_df.copy()
        df['day'] = pd.to_datetime(df['day'])

        # Get recent data
        latest_date = df['day'].max()
        start_date = latest_date - timedelta(days=days-1)
        recent_df = df[df['day'] >= start_date]

        latest = recent_df.iloc[-1] if not recent_df.empty else {}

        analysis = {
            'latest_day': {
                'date': latest.get('day', 'N/A'),
                'steps': latest.get('steps', 0),
                'calories_total': latest.get('calories_total', 0),
                'active_calories': latest.get('active_calories', 0),
                'low_activity_minutes': latest.get('low_activity_time', 0) / 60 if 'low_activity_time' in latest else 0,
                'medium_activity_minutes': latest.get('medium_activity_time', 0) / 60 if 'medium_activity_time' in latest else 0,
                'high_activity_minutes': latest.get('high_activity_time', 0) / 60 if 'high_activity_time' in latest else 0,
            },
            'weekly_average': {
                'steps': round(recent_df.get('steps', pd.Series([0])).mean(), 0),
                'active_calories': round(recent_df.get('active_calories', pd.Series([0])).mean(), 0),
                'total_active_minutes': round(
                    (recent_df.get('medium_activity_time', pd.Series([0])) +
                     recent_df.get('high_activity_time', pd.Series([0]))).mean() / 60, 0
                ),
            }
        }

        return analysis

    def analyze_readiness(self, days: int = 7) -> Dict:
        """Analyze readiness data for the last N days."""
        if self.readiness_df.empty:
            return {'error': 'No readiness data available'}

        df = self.readiness_df.copy()
        df['day'] = pd.to_datetime(df['day'])

        # Get recent data
        latest_date = df['day'].max()
        start_date = latest_date - timedelta(days=days-1)
        recent_df = df[df['day'] >= start_date]

        latest = recent_df.iloc[-1] if not recent_df.empty else {}

        analysis = {
            'latest_day': {
                'date': latest.get('day', 'N/A'),
                'score': latest.get('score', 0),
            },
            'weekly_average': {
                'score': round(recent_df.get('score', pd.Series([0])).mean(), 1),
            },
            'trend': self._calculate_readiness_trend(recent_df),
        }

        return analysis

    def _calculate_sleep_debt(self, df: pd.DataFrame) -> float:
        """Calculate cumulative sleep debt in hours."""
        if 'total_sleep_hours' not in df.columns:
            return 0

        target_sleep = 7.0  # hours
        debt = (target_sleep - df['total_sleep_hours']).sum()
        return round(max(0, debt), 1)

    def _calculate_sleep_consistency(self, df: pd.DataFrame) -> float:
        """Calculate sleep consistency score (0-100)."""
        if df.empty or 'bedtime_start' not in df.columns:
            return 0

        try:
            # Parse bedtime
            df['bedtime_hour'] = pd.to_datetime(df['bedtime_start']).dt.hour
            std_dev = df['bedtime_hour'].std()
            # Convert std dev to score (lower is better)
            score = max(0, 100 - (std_dev * 20))
            return round(score, 1)
        except:
            return 0

    def _calculate_readiness_trend(self, df: pd.DataFrame) -> str:
        """Determine readiness trend."""
        if df.empty or 'score' not in df.columns or len(df) < 3:
            return 'stable'

        recent_avg = df.tail(3)['score'].mean()
        older_avg = df.head(len(df) - 3)['score'].mean() if len(df) > 3 else recent_avg

        diff = recent_avg - older_avg
        if diff > 5:
            return 'improving'
        elif diff < -5:
            return 'declining'
        return 'stable'

    def generate_recommendations(self, sleep_analysis: Dict,
                                 activity_analysis: Dict,
                                 readiness_analysis: Dict) -> List[str]:
        """Generate personalized recommendations based on analysis."""
        recommendations = []

        # Sleep recommendations
        if 'latest_night' in sleep_analysis:
            latest_sleep = sleep_analysis['latest_night']
            avg_sleep = sleep_analysis['weekly_average']

            # Total sleep duration
            if avg_sleep.get('total_sleep_hours', 0) < 6:
                recommendations.append({
                    'category': 'Sleep Duration',
                    'priority': 'HIGH',
                    'message': f"Your average sleep is {avg_sleep['total_sleep_hours']} hours. Aim for 7-9 hours.",
                    'action': 'Try going to bed 30 minutes earlier tonight.'
                })
            elif avg_sleep.get('total_sleep_hours', 0) < 7:
                recommendations.append({
                    'category': 'Sleep Duration',
                    'priority': 'MEDIUM',
                    'message': f"You're getting {avg_sleep['total_sleep_hours']} hours of sleep. Try to reach 7+ hours.",
                    'action': 'Gradually adjust your bedtime to increase sleep duration.'
                })

            # Sleep efficiency
            if avg_sleep.get('efficiency', 0) < 75:
                recommendations.append({
                    'category': 'Sleep Quality',
                    'priority': 'HIGH',
                    'message': f"Sleep efficiency is {avg_sleep['efficiency']}%. Aim for 85%+.",
                    'action': 'Limit screen time 1 hour before bed and keep bedroom cool (65-68°F).'
                })

            # Heart rate variability
            if avg_sleep.get('hrv', 0) < 40:
                recommendations.append({
                    'category': 'Recovery',
                    'priority': 'MEDIUM',
                    'message': f"Your HRV is {avg_sleep['hrv']}ms. Higher is generally better.",
                    'action': 'Focus on stress management, meditation, or deep breathing exercises.'
                })

            # Sleep consistency
            if 'trends' in sleep_analysis and sleep_analysis['trends'].get('consistency_score', 0) < 70:
                recommendations.append({
                    'category': 'Sleep Schedule',
                    'priority': 'MEDIUM',
                    'message': 'Your sleep schedule varies significantly.',
                    'action': 'Try to go to bed and wake up at the same time daily, even on weekends.'
                })

        # Activity recommendations
        if 'weekly_average' in activity_analysis:
            avg_steps = activity_analysis['weekly_average'].get('steps', 0)

            if avg_steps < 5000:
                recommendations.append({
                    'category': 'Physical Activity',
                    'priority': 'HIGH',
                    'message': f"Your daily steps average {int(avg_steps)}. Aim for 8,000-10,000.",
                    'action': 'Take a 15-minute walk after meals or use stairs instead of elevators.'
                })
            elif avg_steps < 8000:
                recommendations.append({
                    'category': 'Physical Activity',
                    'priority': 'MEDIUM',
                    'message': f"You're averaging {int(avg_steps)} steps. Try to reach 10,000.",
                    'action': 'Add a 10-minute walking break mid-day.'
                })

        # Readiness recommendations
        if 'latest_day' in readiness_analysis:
            readiness_score = readiness_analysis['latest_day'].get('score', 0)
            trend = readiness_analysis.get('trend', 'stable')

            if readiness_score < 70:
                recommendations.append({
                    'category': 'Recovery',
                    'priority': 'HIGH',
                    'message': f"Your readiness score is {readiness_score}. Your body needs recovery.",
                    'action': 'Consider light activity today and prioritize sleep tonight.'
                })
            elif trend == 'declining':
                recommendations.append({
                    'category': 'Recovery',
                    'priority': 'MEDIUM',
                    'message': 'Your readiness trend is declining.',
                    'action': 'Review your sleep quality and stress levels. Consider a rest day.'
                })

        # If everything is good
        if not recommendations:
            recommendations.append({
                'category': 'General',
                'priority': 'LOW',
                'message': 'Your health metrics look great!',
                'action': 'Keep up your current routine and stay consistent.'
            })

        return recommendations

    def generate_full_report(self) -> Dict:
        """Generate complete health analysis report."""
        sleep_analysis = self.analyze_sleep()
        activity_analysis = self.analyze_activity()
        readiness_analysis = self.analyze_readiness()
        recommendations = self.generate_recommendations(
            sleep_analysis, activity_analysis, readiness_analysis
        )

        return {
            'report_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_date': self.get_latest_date(),
            'sleep': sleep_analysis,
            'activity': activity_analysis,
            'readiness': readiness_analysis,
            'recommendations': recommendations,
        }


if __name__ == "__main__":
    # Test the analyzer
    analyzer = OuraAnalyzer()
    report = analyzer.generate_full_report()

    print("=== OURA HEALTH REPORT ===")
    print(f"Report Generated: {report['report_date']}")
    print(f"Data Date: {report['data_date']}")

    print("\n--- Sleep Analysis ---")
    if 'latest_night' in report['sleep']:
        latest = report['sleep']['latest_night']
        print(f"Total Sleep: {latest['total_sleep_hours']} hours")
        print(f"Efficiency: {latest['efficiency']}%")
        print(f"Resting HR: {latest['resting_heart_rate']} bpm")
        print(f"HRV: {latest['hrv']} ms")

    print("\n--- Activity Analysis ---")
    if 'latest_day' in report['activity']:
        latest = report['activity']['latest_day']
        print(f"Steps: {int(latest['steps'])}")
        print(f"Active Calories: {int(latest['active_calories'])}")

    print("\n--- Recommendations ---")
    for rec in report['recommendations']:
        print(f"[{rec['priority']}] {rec['category']}: {rec['message']}")
        print(f"  → {rec['action']}\n")

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_large_dataset(start_date="2023-01-01", days=730):
    """
    Generates a large, realistic marketing dataset covering 2 years (default).
    Includes seasonality, channel-specific distinct behaviors, and trends.
    """
    np.random.seed(42)

    # 1. Setup Dates
    start = datetime.strptime(start_date, "%Y-%m-%d")
    date_list = [start + timedelta(days=x) for x in range(days)]

    # 2. Define Channels & Their Characteristics
    # Weights: Probability of a campaign running on this channel
    # Cost Factor: Multiplier for spend
    # Conv Factor: Multiplier for conversion rate
    channels = {
        'Facebook':   {'weight': 0.30, 'cost_base': 500,  'ctr_base': 0.025, 'conv_base': 0.04},
        'Google Ads': {'weight': 0.25, 'cost_base': 1200, 'ctr_base': 0.035, 'conv_base': 0.06},
        'Instagram':  {'weight': 0.20, 'cost_base': 400,  'ctr_base': 0.015, 'conv_base': 0.03},
        'LinkedIn':   {'weight': 0.10, 'cost_base': 2000, 'ctr_base': 0.010, 'conv_base': 0.09},
        'Email':      {'weight': 0.10, 'cost_base': 100,  'ctr_base': 0.080, 'conv_base': 0.12},
        'TikTok':     {'weight': 0.05, 'cost_base': 300,  'ctr_base': 0.045, 'conv_base': 0.02},
    }

    data = []

    print(f"Generating data for {days} days across {len(channels)} channels...")

    for date in date_list:
        # Create multiple entries per day (randomly 3 to 8 campaigns running per day)
        daily_campaigns = np.random.randint(3, 9)

        for _ in range(daily_campaigns):
            # Select Channel based on weight
            channel_name = np.random.choice(list(channels.keys()), p=[c['weight'] for c in channels.values()])
            props = channels[channel_name]

            # --- SEASONALITY & TREND MODIFIERS ---

            # 1. Yearly Trend (Business grows slightly over time)
            days_passed = (date - start).days
            growth_factor = 1 + (days_passed / days) * 0.2  # 20% growth over the period

            # 2. Monthly Seasonality (Spike in Nov/Dec for holidays)
            month = date.month
            seasonality = 1.0
            if month in [11, 12]:
                seasonality = 1.4  # 40% boost
            elif month in [1, 2]:
                seasonality = 0.8  # Slow start to year

            # 3. Weekly Seasonality (Weekends better for B2C, Weekdays for B2B)
            is_weekend = date.weekday() >= 5
            day_factor = 1.0
            if channel_name == 'LinkedIn':
                day_factor = 0.5 if is_weekend else 1.2
            elif channel_name in ['Instagram', 'TikTok', 'Facebook']:
                day_factor = 1.3 if is_weekend else 0.9

            # --- METRIC CALCULATION ---

            # Impressions
            base_impressions = np.random.randint(1000, 20000)
            impressions = int(base_impressions * growth_factor * seasonality * day_factor)

            # Spend (Cost)
            # Random variance +/- 20% on base cost
            spend_variance = np.random.uniform(0.8, 1.2)
            spend = props['cost_base'] * spend_variance * growth_factor * seasonality

            # Clicks
            # Base CTR +/- random noise
            actual_ctr = props['ctr_base'] * np.random.uniform(0.8, 1.2)
            clicks = int(impressions * actual_ctr)

            # Conversions
            actual_conv_rate = props['conv_base'] * np.random.uniform(0.8, 1.25)
            conversions = int(clicks * actual_conv_rate)

            # Revenue
            # Average Order Value (AOV) varies by channel
            if channel_name == 'LinkedIn':
                aov = np.random.normal(500, 50) # High ticket B2B
            elif channel_name == 'TikTok':
                aov = np.random.normal(30, 10)  # Low ticket impulse
            else:
                aov = np.random.normal(80, 20)  # Standard

            revenue = conversions * aov

            # Ensure no negative numbers and logical consistency
            if clicks > impressions: clicks = int(impressions * 0.9)
            if conversions > clicks: conversions = int(clicks * 0.9)

            # Append row
            data.append([
                date.strftime("%Y-%m-%d"),
                channel_name,
                round(spend, 2),
                impressions,
                clicks,
                conversions,
                round(revenue, 2)
            ])

    # Create DataFrame
    df = pd.DataFrame(data, columns=['Date', 'Channel', 'Spend', 'Impressions', 'Clicks', 'Conversions', 'Revenue'])

    # Sort by date
    df = df.sort_values('Date')

    # Save locally
    filename = "marketing_data.csv"
    df.to_csv(filename, index=False)

    print(f"✅ Successfully generated {len(df)} rows of data.")
    print(f"📁 Saved to local disk: {os.path.abspath(filename)}")

    # Attempt to trigger download if running in Google Colab
    try:
        from google.colab import files
        files.download(filename)
        print("⬇️  Triggering Google Colab download...")
    except ImportError:
        print("ℹ️  (If you are running this in a local environment, the file is in the folder displayed above.)")

    return df

if __name__ == "__main__":
    generate_large_dataset()
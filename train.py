import pandas as pd
import numpy as np

# Load existing CSV
df = pd.read_csv('real_estate_crm_data.csv')

# Define lists for new columns
deal_statuses = [
    'Prospecting', 'Initial Contact', 'Viewing Scheduled', 
    'Negotiation', 'Offer Submitted', 'Pending', 
    'Under Contract', 'Closing', 'Closed/Sold', 'Lost'
]

regions = [
    'Urban', 'Suburban', 'Metropolitan', 
    'Downtown', 'Residential', 'Commercial'
]

# Function to generate realistic deal values
def generate_deal_value(region):
    if region in ['Urban', 'Metropolitan', 'Downtown']:
        return np.random.randint(300000, 1500000)
    elif region in ['Suburban', 'Residential']:
        return np.random.randint(250000, 750000)
    else:
        return np.random.randint(100000, 500000)

# Add new columns
df['deal_status'] = np.random.choice(deal_statuses, size=len(df))
df['region'] = np.random.choice(regions, size=len(df))
df['deal_value'] = df['region'].apply(generate_deal_value)

# Save updated CSV
df.to_csv('real_estate_crm_data.csv', index=False)

print("CSV updated successfully!")
print("\nSample data:")
print(df[['deal_status', 'region', 'deal_value']].head())
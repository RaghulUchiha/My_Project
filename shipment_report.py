import pandas as pd
import numpy as np
import traceback
import matplotlib.pyplot as plt

def process_shipment_report(file_path: str) -> None:
    try:
        shipment_df = pd.read_csv(file_path)

        
        print(shipment_df.info())
        print(shipment_df.head())
        print(shipment_df.isnull().sum())
        print(shipment_df.columns.tolist())

        shipment_df.columns = shipment_df.columns.str.strip()

        shipment_df.drop(columns=['EAN'], inplace=True, errors='ignore')  

        shipment_df['Shipment Created At'] = pd.to_datetime(shipment_df['Shipment Created At2'], errors='coerce')
        shipment_df['Accepted At'] = pd.to_datetime(shipment_df['Accepted At'], errors='coerce')
        shipment_df['Acceptance TAT Date & Time'] = pd.to_datetime(shipment_df['Acceptance TAT Date & Time'], errors='coerce')

        shipment_df.drop_duplicates(inplace=True)

        print(shipment_df['Shipment Status'].value_counts())
        print(shipment_df['Shipping Agent Code'].value_counts())
        print(shipment_df['Fulfillment Type'].value_counts())
        print(shipment_df['Payment Method Used'].value_counts())

        shipment_df['Shipment Created At'].dt.date.value_counts().sort_index().plot(kind='line', figsize=(10, 5))
        plt.title("Daily Shipments")
        plt.xlabel("Date")
        plt.ylabel("Number of Shipments")
        plt.xticks(rotation=45)
        plt.grid()
        plt.show()

        shipment_df['Accepted At'].dt.date.value_counts().sort_index().plot(kind='line', figsize=(10, 5))
        plt.title("Daily Accepted Shipments")
        plt.xlabel("Date")
        plt.ylabel("Number of Shipments")
        plt.xticks(rotation=45)
        plt.grid()
        plt.show()

        # Filter Functions
        delivered_shipments = shipment_df[shipment_df['Shipment Status'] == 'delivered']
        print(delivered_shipments.head())

        pending_shipments = shipment_df[shipment_df['Shipment Status'] == 'pending']
        print(pending_shipments.head())

        recent_shipments = shipment_df[shipment_df['Shipment Created At'] > '2025-03-01']
        print(recent_shipments.head())

        # Filtering using query
        print(shipment_df[shipment_df['Fulfiller Name'] == 'Fullfiller X'])
        print(shipment_df.query("`Shipment Status` == 'delivered' and Qty > 5"))
        print(shipment_df.query("`Shipment Status` == 'pending' and Qty > 5"))

        # Apply Function
        shipment_df['Delivery Speed'] = shipment_df.apply(
            lambda row: 'Fast' if pd.notna(row['Accepted At']) and (row['Accepted At'] - row['Shipment Created At']).days <= 2 else 'Slow', 
            axis=1
        )

        shipment_df['Qty Category'] = shipment_df['Qty'].apply(lambda x: 'Small' if x <= 5 else ('Medium' if x <= 20 else 'Large'))

        # Aggregate Functions
        print(shipment_df.groupby('Shipment Status')['Shipment Number'].count())
        print(shipment_df.agg({'Qty': ['sum', 'mean', 'max', 'min']}))
        print(shipment_df.groupby(shipment_df['Shipment Created At'].dt.date)['Shipment Number'].count())

        # Mapping shipment statuses
        status_mapping = {
            "delivered": "SHIPPED",
            "invoiced": "SHIPPED",
            "pick_up_confirmed": "SHIPPED",
            "shipment_returned": "RTO_RECEIVED",
            "created": "PENDING_SHIPMENT",
            "canceled": "CANCELLED"
        }
        shipment_df['fsorderstatus'] = shipment_df['Shipment Status'].map(status_mapping)

        shipment_df['id'] = shipment_df['Shipping Agent Code'].astype(str) + "_" + shipment_df['Shipment Number'].astype(str) + "_" + shipment_df['Sku'].astype(str)

        shipment_df['invoiceprice'] = shipment_df['Item Total'].apply(lambda x: {"total": x, "breakup": []})

        print(shipment_df)
        print("End of Program")
    except Exception as e:
        traceback.print_exc()


# File path
file_path = r"C:\Users\Raghul\Desktop\shipment_report.csv"
process_shipment_report(file_path)


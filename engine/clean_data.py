import os
import pandas as pd
from pathlib import Path

def extract_row(df, row_name):
    # Find the first row where column 0 equals row_name exactly or strip it to be safe
    # Sometimes it's NaN so handle it
    mask = df[0].astype(str).str.strip() == row_name
    match = df[mask]
    if not match.empty:
        return match.iloc[0, 1:].values
    return []

def clean_data():
    data_dir = Path('data')
    # Find all xlsx files recursively to handle them if they are in data/ or data/raw/
    files = list(data_dir.rglob('*.xlsx'))
    
    fraud_companies = ['dhfl', 'satyam', 'il&fs']
    
    all_records = []
    
    for file in files:
        company_name = file.stem
        try:
            df = pd.read_excel(file, sheet_name='Data Sheet', header=None)
            
            dates = extract_row(df, 'Report Date')
            sales = extract_row(df, 'Sales')
            net_profit = extract_row(df, 'Net profit')
            op_cashflow = extract_row(df, 'Cash from Operating Activity')
            borrowings = extract_row(df, 'Borrowings')
            cash_bank = extract_row(df, 'Cash & Bank')
            
            # Determine label
            label = 0
            for f in fraud_companies:
                if f in company_name.lower():
                    label = 1
                    break
            
            for i, date in enumerate(dates):
                if pd.isna(date):
                    continue
                
                # Extract year
                if hasattr(date, 'year'):
                    year = date.year
                elif isinstance(date, str) and len(str(date)) >= 4:
                    year = str(date)[:4]
                else:
                    year = date
                    
                record = {
                    'company': company_name,
                    'year': year,
                    'revenue': sales[i] if i < len(sales) else None,
                    'net_profit': net_profit[i] if i < len(net_profit) else None,
                    'operating_cashflow': op_cashflow[i] if i < len(op_cashflow) else None,
                    'borrowings': borrowings[i] if i < len(borrowings) else None,
                    'cash_and_bank': cash_bank[i] if i < len(cash_bank) else None,
                    'label': label
                }
                all_records.append(record)
        except Exception as e:
            print(f"Error processing {file}: {e}")
            
    result_df = pd.DataFrame(all_records)
    
    # Optional: drop rows where all financial metrics are NaN or None (i.e. future projections that have no data)
    metrics = ['revenue', 'net_profit', 'operating_cashflow', 'borrowings', 'cash_and_bank']
    result_df.dropna(subset=metrics, how='all', inplace=True)
    
    output_path = data_dir / 'master_data.csv'
    result_df.to_csv(output_path, index=False)
    print(f"Successfully processed {len(files)} files and saved to {output_path}")

if __name__ == '__main__':
    clean_data()

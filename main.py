import pandas as pd
import datetime
import time
from tracker import check_rank

# --- CONFIGURATION ---
TARGET_BRAND = "Leaf"
CATEGORIES = [
    "Headphones", 
    "Earbuds", 
    "Neckband", 
    "Smartwatch", 
    "Smart Ring"
]
# ---------------------

def run_leaf_tracker():
    # 1. Load Pincodes
    try:
        df = pd.read_csv("pincodes.csv")
        print(f"Loaded {len(df)} locations.")
    except:
        print("Create 'pincodes.csv' first!")
        return

    results = []

    # 2. Master Loop
    for index, row in df.iterrows():
        pincode = str(row['Pincode'])
        city = row['City']
        
        print(f"\n==========================================")
        print(f"📍 PROCESSING: {city} ({pincode})")
        print(f"==========================================")

        # Check every category for this pincode
        for cat in CATEGORIES:
            data = check_rank(pincode, cat, TARGET_BRAND)
            
            # Print nice output to terminal
            if data['status'] == "Available":
                print(f"  ✅ {cat}: FOUND at Rank #{data['rank']} ({data['product']})")
            else:
                print(f"  ❌ {cat}: Not Found")

            # Save Data
            results.append({
                "Date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "City": city,
                "Pincode": pincode,
                "Category": cat,
                "Is_Available": data['status'],
                "Rank": data['rank'],
                "Top_Product_Name": data['product']
            })
            
            # Small pause between searches to be safe
            time.sleep(3)

    # 3. Save to Excel/CSV
    output_df = pd.DataFrame(results)
    
    # We append to a history file
    file_name = "leaf_brand_report.csv"
    try:
        with open(file_name, "a", encoding='utf-8') as f:
            output_df.to_csv(f, header=f.tell()==0, index=False)
    except FileNotFoundError:
        output_df.to_csv(file_name, index=False)

    print(f"\n🚀 Report saved to {file_name}")

if __name__ == "__main__":
    run_leaf_tracker()
import streamlit as st
import pandas as pd
import sys
import asyncio
from tracker import check_rank

# --- WINDOWS FIX ---
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# --- 1. PRODUCT CATALOG ---
PRODUCT_CATALOG = {
    "Headphones": ["Leaf Bass Wireless Bluetooth Headphones (Carbon Black)"],
    "Earbuds": [
        "Leaf X334 TWS Earbuds (Espresso)",
        "Leaf X334 TWS Earbuds (Glacier)",
        "Leaf X334 AI Sound TWS Earbuds (Matcha)",
        "Leaf X121 TWS Earbuds (Carbon Black)"
    ],
    "Neckband": [], "Smartwatch": [], "Smart Ring": []
}

# --- 2. LOCATION DATABASE ---
LOCATION_DB = {
    "Delhi": [
        "Connaught Place 110001", "Karol Bagh 110005", "Chandni Chowk 110006", 
        "Lajpat Nagar 110024", "Rajouri Garden 110027", "Vasant Kunj 110070", 
        "Saket 110017", "Hauz Khas 110016", "Dwarka 110075", "Janakpuri 110058", 
        "Greater Kailash 110048", "Rohini 110085", "Pitampura 110034", 
        "Mayur Vihar 110091", "Preet Vihar 110092", "Shahdara 110032", 
        "Uttam Nagar 110059", "Paschim Vihar 110063", "Shalimar Bagh 110088", 
        "Ashok Vihar 110052", "Patel Nagar 110008", "Tilak Nagar 110018", 
        "Malviya Nagar 110017", "Green Park 110016", "Defence Colony 110024", 
        "Nehru Place 110019", "Okhla 110020", "Mehrauli 110030", 
        "Chhatarpur 110074", "Laxmi Nagar 110092", "Krishna Nagar 110051", 
        "Model Town 110009", "Civil Lines 110054", "Punjabi Bagh 110026", 
        "Naraina 110028", "Kirti Nagar 110015"
    ],
    "Gurgaon": [
        "DLF Cyber City 122002", "MG Road 122002", "Sushant Lok 122009", 
        "Golf Course Road 122002", "Sohna Road 122018", "Sector 14 122001", 
        "Sector 56 122011", "Palam Vihar 122017", "Sector 45 122003", 
        "Sector 50 122018", "South City (I & II) 122001", "Nirvana Country 122018", 
        "Sector 46 122003", "Sector 31 122001", "Sector 57 122003", 
        "Sector 29 122002", "Udyog Vihar 122016", "Sector 82 122004", 
        "Sector 22 122015"
    ],
    "Ghaziabad": [
        "Indirapuram 201014", "Vaishali 201010", "Kaushambi 201012", 
        "Raj Nagar Extension 201017", "Vasundhara 201012", "Kavi Nagar 201002", 
        "Shastri Nagar 201002", "Crossing Republik 201016", "Nehru Nagar 201001", 
        "Sahibabad 201005", "Mohan Nagar 201007", "Rajendra Nagar 201005", 
        "Sanjay Nagar 201002"
    ],
    "Faridabad": [
        "Sector 15 121007", "Sector 21 121001", "Sector 37 121003", 
        "Sector 7 121006", "Sector 9 121006", "Sector 28 121008", 
        "Sector 46 121010", "Sector 19 121002", "Sector 14 121007", 
        "Sector 11 121006", "Sector 16 121002", "Sector 31 121003", 
        "NIT Faridabad 121001", "Greenfield Colony 121003"
    ],
    "Mumbai": [
        "Colaba 400005", "Andheri West 400053", "Andheri East 400069", 
        "Bandra West 400050", "Powai 400076", "Navi Mumbai (CBD Belapur) 400614", 
        "Juhu 400049", "Malad West 400064", "Borivali West 400092", 
        "Thane West 400601", "Worli 400018", "Dadar 400014", 
        "Lower Parel 400013", "Goregaon East 400063", "Goregaon West 400104", 
        "Kandivali West 400067", "Chembur 400071", "Ghatkopar West 400086", 
        "Mulund West 400080", "Mira Road 401107", "Vasai West 401201", 
        "Vikhroli West 400083", "Vashi 400703"
    ],
    "Bengaluru": [
        "Indiranagar 560038", "Koramangala 560034", "Whitefield 560066", 
        "Jayanagar 560041", "Electronic City 560100", "MG Road 560001", 
        "HSR Layout 560102", "Marathahalli 560037", "Yeshwanthpur 560022", 
        "Rajajinagar 560010", "Banashankari 560050", "Malleswaram 560003", 
        "Bellandur 560103", "Bommanahalli 560068", "Sarjapur Road 560035"
    ],
    "Pune": [
        "Koregaon Park 411001", "Viman Nagar 411014", "Hinjewadi 411057", 
        "Kothrud 411038", "Baner 411045", "Hadapsar 411028", "Aundh 411007", 
        "Wakad 411057", "Magarpatta 411013", "Pimpri 411018", "Camp 411001", 
        "Swargate 411042", "FC Road 411004", "Katraj 411046", 
        "Shivaji Nagar 411005", "Pimple Saudagar 411027", "Bavdhan 411021"
    ],
    "Others": [
        "Bahadurgarh 124507", "Sonipat 131001", "Rohtak 124001"
    ]
}

# --- APP LAYOUT ---
st.set_page_config(page_title="Leaf Blinkit Tracker", page_icon="🍃", layout="wide")
st.title("Leaf Studios - Blinkit Radar")

# --- INITIALIZE SESSION STATE ---
if 'report_data' not in st.session_state:
    st.session_state.report_data = None

# --- SIDEBAR: SETUP ---
with st.sidebar:
    st.header("Select Product")
    cat = st.selectbox("Category", PRODUCT_CATALOG.keys(), index=1)
    
    avail_skus = PRODUCT_CATALOG.get(cat, [])
    if not avail_skus: avail_skus = ["Leaf"]
    targets = st.multiselect("Models:", avail_skus, default=avail_skus)
    
    st.markdown("---")
    if st.button("Clear Previous Results"):
        st.session_state.report_data = None
        st.rerun()

# --- MAIN: LOCATION SELECTION ---
st.header("Select Location")

# Toggle between methods
input_method = st.radio("Input Method:", ["Select from Database", "Manual Entry"], horizontal=True)

final_locations = []
selected_city = "Manual" 

if input_method == "Select from Database":
    col_city, col_area = st.columns(2)
    with col_city:
        selected_city = st.selectbox("Choose City:", list(LOCATION_DB.keys()))
    with col_area:
        areas = LOCATION_DB[selected_city]
        selected_areas = st.multiselect(f"Choose Areas in {selected_city}:", areas, default=[areas[0]])
    final_locations = selected_areas

else:
    # Manual Fallback
    text_input = st.text_area("Type Locations (e.g. 'Saket 110017'):", height=100)
    final_locations = [l.strip() for l in text_input.split('\n') if l.strip()]

# --- SHOW SELECTED ---
if final_locations:
    st.info(f"Ready to scan **{len(final_locations)} locations** for **{len(targets)} products**.")

# --- RUN BUTTON ---
if st.button("Run Analysis", type="primary", disabled=not final_locations):
    
    results = []
    status = st.empty()
    bar = st.progress(0)
    
    total = len(final_locations) * len(targets)
    done = 0
    
    for loc in final_locations:
        st.subheader(f"📍 {loc}")
        
        for prod in targets:
            status.text(f"Scanning {loc} > {prod}...")
            
            try:
                # RUN BOT
                data = check_rank(loc, cat, prod)
                
                # STATUS BADGE
                if data['status'] == "Available":
                    # REMOVED IMAGE DISPLAY LOGIC HERE
                    st.success(f"**#{data['rank']}** {prod}")
                else:
                    st.error(f"{prod}")
                
                results.append({
                    "City": selected_city if input_method == "Select from Database" else "Manual",
                    "Location": loc,
                    "Product": prod,
                    "Rank": data['rank'],
                    "Status": data['status']
                })
            except Exception as e:
                st.error(f"Error: {e}")
            
            done += 1
            bar.progress(done / total)
            
    status.success("Scan Complete!")
    
    # Save to Session State
    if results:
        df = pd.DataFrame(results).astype(str)
        st.session_state.report_data = df

# --- DISPLAY RESULTS FROM MEMORY ---
if st.session_state.report_data is not None:
    st.markdown("---")
    st.subheader("Final Report (Saved)")
    
    st.dataframe(st.session_state.report_data, use_container_width=True)
    
    csv = st.session_state.report_data.to_csv(index=False).encode('utf-8')
    st.download_button("Download Report", csv, "leaf_report.csv", "text/csv")
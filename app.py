import streamlit as st
import pandas as pd
import sys
import asyncio
from tracker import check_rank
import data_manager  # Must have data_manager.py in the same folder

# --- WINDOWS FIX ---
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# --- LOAD DATA DYNAMICALLY ---
config_data = data_manager.load_data()
PRODUCT_CATALOG = config_data["PRODUCT_CATALOG"]
LOCATION_DB = config_data["LOCATION_DB"]

# --- APP LAYOUT ---
st.set_page_config(page_title="Leaf Blinkit Tracker", page_icon="🍃", layout="wide")
st.title("Leaf Studios - Blinkit Radar")

# --- NAVIGATION ---
tab1, tab2 = st.tabs(["Tracker Dashboard", "Admin Panel"])

# ==========================================
# TAB 1: TRACKER DASHBOARD
# ==========================================
with tab1:
    with st.sidebar:
        st.header("Select Product")
        
        # 1. Category
        if PRODUCT_CATALOG:
            cat = st.selectbox("Category", list(PRODUCT_CATALOG.keys()))
            avail_skus = PRODUCT_CATALOG.get(cat, [])
        else:
            cat = None
            avail_skus = []
            st.warning("No Categories found! Add some in Admin Panel.")

        # 2. Products
        if not avail_skus: 
            avail_skus = ["Leaf"]
            
        targets = st.multiselect("Models:", avail_skus, default=avail_skus)
        
        st.markdown("---")
        if st.button("Clear Results"):
            if 'report_data' in st.session_state:
                del st.session_state['report_data']
            st.rerun()

    # --- MAIN INPUT ---
    st.subheader("Select Location")
    
    input_method = st.radio("Input Method:", ["Select from Database", "Manual Entry"], horizontal=True)
    
    final_locations = []
    selected_city = "Manual"

    if input_method == "Select from Database":
        if LOCATION_DB:
            col_city, col_area = st.columns(2)
            with col_city:
                selected_city = st.selectbox("Choose City:", list(LOCATION_DB.keys()))
            with col_area:
                areas = LOCATION_DB.get(selected_city, [])
                selected_areas = st.multiselect(f"Choose Areas in {selected_city}:", areas)
            final_locations = selected_areas
        else:
            st.warning("No Locations found in Database.")
    else:
        text_input = st.text_area("Type Locations (e.g. 'Saket 110017'):", height=100)
        final_locations = [l.strip() for l in text_input.split('\n') if l.strip()]

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
                    data = check_rank(loc, cat, prod)
                    if data['status'] == "Available":
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
        if results:
            df = pd.DataFrame(results).astype(str)
            st.session_state.report_data = df

    if 'report_data' in st.session_state:
        st.markdown("---")
        st.subheader("Final Report")
        st.dataframe(st.session_state.report_data, use_container_width=True)

# ==========================================
# TAB 2: ADMIN PANEL (Add & Delete)
# ==========================================
with tab2:
    st.header("🛠️ Database Management")
    col_prod_admin, col_loc_admin = st.columns(2)

    # --- SECTION A: PRODUCT MANAGEMENT ---
    with col_prod_admin:
        st.subheader("📦 Product Catalog")
        
        # ADD SECTION
        with st.expander("➕ Add New", expanded=True):
            tab_add_cat, tab_add_model = st.tabs(["Category", "Model"])
            
            with tab_add_cat:
                new_cat = st.text_input("New Category Name:")
                if st.button("Save Category"):
                    if new_cat and new_cat not in PRODUCT_CATALOG:
                        PRODUCT_CATALOG[new_cat] = []
                        config_data["PRODUCT_CATALOG"] = PRODUCT_CATALOG
                        data_manager.save_data(config_data)
                        st.success(f"Added '{new_cat}'!")
                        st.rerun()

            with tab_add_model:
                if PRODUCT_CATALOG:
                    target_cat = st.selectbox("Select Category:", list(PRODUCT_CATALOG.keys()))
                    new_model = st.text_input("New Model Name:")
                    if st.button("Save Model"):
                        if new_model and new_model not in PRODUCT_CATALOG[target_cat]:
                            PRODUCT_CATALOG[target_cat].append(new_model)
                            config_data["PRODUCT_CATALOG"] = PRODUCT_CATALOG
                            data_manager.save_data(config_data)
                            st.success(f"Added '{new_model}'!")
                            st.rerun()

        # DELETE SECTION (RED)
        st.write("---")
        with st.expander("Delete Items", expanded=False):
            tab_del_cat, tab_del_model = st.tabs(["Delete Category", "Delete Model"])
            
            with tab_del_cat:
                if PRODUCT_CATALOG:
                    del_cat = st.selectbox("Remove Category:", list(PRODUCT_CATALOG.keys()))
                    if st.button("Delete Category", type="primary"):
                        del PRODUCT_CATALOG[del_cat]
                        config_data["PRODUCT_CATALOG"] = PRODUCT_CATALOG
                        data_manager.save_data(config_data)
                        st.warning(f"Deleted '{del_cat}'!")
                        st.rerun()
            
            with tab_del_model:
                if PRODUCT_CATALOG:
                    cat_for_del = st.selectbox("Select Category:", list(PRODUCT_CATALOG.keys()), key="del_cat_sel")
                    models_in_cat = PRODUCT_CATALOG[cat_for_del]
                    if models_in_cat:
                        del_model = st.selectbox("Remove Model:", models_in_cat)
                        if st.button("Delete Model", type="primary"):
                            PRODUCT_CATALOG[cat_for_del].remove(del_model)
                            config_data["PRODUCT_CATALOG"] = PRODUCT_CATALOG
                            data_manager.save_data(config_data)
                            st.warning(f"Deleted '{del_model}'!")
                            st.rerun()
                    else:
                        st.info("No models in this category.")

    # --- SECTION B: LOCATION MANAGEMENT ---
    with col_loc_admin:
        st.subheader("📍 Location Database")
        
        # ADD SECTION
        with st.expander("➕ Add New", expanded=True):
            tab_add_city, tab_add_area = st.tabs(["City", "Area"])
            
            with tab_add_city:
                new_city = st.text_input("New City Name:")
                if st.button("Save City"):
                    if new_city and new_city not in LOCATION_DB:
                        LOCATION_DB[new_city] = []
                        config_data["LOCATION_DB"] = LOCATION_DB
                        data_manager.save_data(config_data)
                        st.success(f"Added '{new_city}'!")
                        st.rerun()

            with tab_add_area:
                if LOCATION_DB:
                    target_city = st.selectbox("Select City:", list(LOCATION_DB.keys()))
                    new_area = st.text_input("New Area (e.g. 'Sector 15 110001'):")
                    if st.button("Save Area"):
                        if new_area and new_area not in LOCATION_DB[target_city]:
                            LOCATION_DB[target_city].append(new_area)
                            config_data["LOCATION_DB"] = LOCATION_DB
                            data_manager.save_data(config_data)
                            st.success(f"Added '{new_area}'!")
                            st.rerun()

        # DELETE SECTION (RED)
        st.write("---")
        with st.expander("Delete Locations", expanded=False):
            tab_del_city, tab_del_area = st.tabs(["Delete City", "Delete Area"])
            
            with tab_del_city:
                if LOCATION_DB:
                    del_city = st.selectbox("Remove City:", list(LOCATION_DB.keys()))
                    if st.button("Delete City", type="primary"):
                        del LOCATION_DB[del_city]
                        config_data["LOCATION_DB"] = LOCATION_DB
                        data_manager.save_data(config_data)
                        st.warning(f"Deleted '{del_city}'!")
                        st.rerun()
            
            with tab_del_area:
                if LOCATION_DB:
                    city_for_del = st.selectbox("Select City:", list(LOCATION_DB.keys()), key="del_city_sel")
                    areas_in_city = LOCATION_DB[city_for_del]
                    if areas_in_city:
                        del_area = st.selectbox("Remove Area:", areas_in_city)
                        if st.button("Delete Area", type="primary"):
                            LOCATION_DB[city_for_del].remove(del_area)
                            config_data["LOCATION_DB"] = LOCATION_DB
                            data_manager.save_data(config_data)
                            st.warning(f"Deleted '{del_area}'!")
                            st.rerun()
                    else:
                        st.info("No areas in this city.")
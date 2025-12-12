import time
from playwright.sync_api import sync_playwright

# --- HELPER: MANUAL LOCATION SET (Strict 1st Option) ---
def set_location_manually(page, location_identifier):
    print(f"  > 📍 Setting Location: '{location_identifier}'...")
    try:
        # 1. Open Location Modal
        header_clicked = False
        
        # Try clicking "Delivery in..."
        try:
            page.get_by_text("Delivery in", exact=False).first.click(timeout=3000)
            header_clicked = True
        except:
            pass
        
        # Try clicking "Select Location"
        if not header_clicked:
            try:
                page.get_by_text("Select Location", exact=False).first.click(timeout=3000)
                header_clicked = True
            except:
                pass

        # Blind Click Fallback
        if not header_clicked:
            page.mouse.click(200, 50)
        
        time.sleep(2)

        # 2. Type Location
        try:
            page.click("input[type='text']", timeout=3000)
            page.fill("input[type='text']", location_identifier)
        except:
            page.keyboard.type(location_identifier)
            
        # 3. Wait for Results
        print("  > Waiting for dropdown...")
        time.sleep(4) 

        # 4. SELECT THE 1ST OPTION (Strict)
        print("  > Selecting 1st option...")
        
        try:
            # Strategy A: Click the first item in the list directly
            # The list usually has a specific class. We grab the first child div.
            # We use a broad selector that targets the suggestion items
            first_result = page.locator("div[class*='LocationSearchList'] > div").first
            first_result.click(timeout=3000)
            print("  > Clicked 1st result via mouse.")
        except:
            # Strategy B: Keyboard Force (Reliable)
            # If the mouse click fails, we simply press Down -> Enter
            print("  > Mouse failed. Using Keyboard (Down -> Enter)...")
            page.keyboard.press("ArrowDown")
            time.sleep(0.5)
            page.keyboard.press("Enter")

        time.sleep(5)
        return True

    except Exception as e:
        print(f"  > ❌ Location Error: {e}")
        return False

# --- MAIN BOT ---
def check_rank(location_string, category, target_brand="Leaf"):
    print(f"\n--- Checking '{location_string}' for '{category}' ---")
    
    with sync_playwright() as p:
        # Launch browser visible
        browser = p.chromium.launch(headless=False, slow_mo=50)
        context = browser.new_context(viewport={"width": 1280, "height": 720}, locale="en-IN")
        page = context.new_page()

        try:
            page.goto("https://blinkit.com/", timeout=60000)
            
            # 1. SET LOCATION
            set_location_manually(page, location_string)

            # 2. SEARCH CATEGORY
            search_url = f"https://blinkit.com/s/?q={category}"
            page.goto(search_url, timeout=60000)
            
            try:
                page.wait_for_selector("text=ADD", timeout=10000)
            except:
                print("  > Warning: Page slow.")

            # 3. SCAN PRODUCTS (BROAD MATCH + STRICT WALL)
            print(f"  > Scanning for target: '{target_brand}'...")
            
            seen_products = set()
            master_list = [] 
            
            stop_phrases = ["Showing related products", "Related to your search", "You might also like", "Similar products"]

            for scroll_step in range(30):
                # A. CHECK STOP WALL
                hit_wall = False
                wall_y = 999999
                for phrase in stop_phrases:
                    headers = page.get_by_text(phrase, exact=False).all()
                    for h in headers:
                        if h.is_visible():
                            box = h.bounding_box()
                            if box:
                                hit_wall = True
                                wall_y = box['y']
                                print(f"  🛑 Wall detected: '{phrase}' at Y={int(wall_y)}")
                                break
                    if hit_wall: break

                # B. PROCESS CARDS
                visible_buttons = page.locator("text=ADD").all()
                
                for btn in visible_buttons:
                    try:
                        box = btn.bounding_box()
                        if not box: continue
                        
                        # Stop if below wall
                        if hit_wall and box['y'] > wall_y: continue

                        # Get Full Card Text
                        card_element = btn.locator("xpath=../../..")
                        full_card_text = card_element.inner_text().strip()
                        
                        # Generate ID (Best Effort Name)
                        lines = full_card_text.split('\n')
                        best_name = "Unknown"
                        for line in lines:
                            if len(line) > len(best_name) and "₹" not in line and "MINS" not in line:
                                best_name = line.strip()
                        
                        unique_id = best_name
                        
                        if unique_id not in seen_products:
                            seen_products.add(unique_id)
                            master_list.append(unique_id)
                            current_rank = len(master_list)
                            
                            # BROAD MATCH CHECK
                            if target_brand.lower() in full_card_text.lower():
                                print(f"\n  ★ MATCH FOUND at Rank #{current_rank}")
                                return {"status": "Available", "rank": current_rank, "product": unique_id}
                                
                    except:
                        continue
                
                if hit_wall:
                    print("  > Stopped search at Related Products.")
                    return {"status": "Not Found", "rank": "NA", "product": "NA"}

                page.evaluate("window.scrollBy(0, 400)")
                time.sleep(1.0)

            return {"status": "Not Found", "rank": "NA", "product": "NA"}

        except Exception as e:
            print(f"  > ERROR: {e}")
            return {"status": "Error", "rank": "NA", "product": "Error"}
        finally:
            browser.close()

# Dummy for app.py safety
def get_blinkit_suggestions(query): return []
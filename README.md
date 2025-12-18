# 🍃 Leaf Blinkit Radar

**Leaf Blinkit Radar** is an automated intelligence tool designed to track product availability and search ranking on **Blinkit** across multiple locations in real-time.

It simulates a real user to bypass bot detection, scans specific pincodes, and reports whether a product (e.g., "Leaf Earbuds") is available and at what rank it appears in search results.

---

## 🚀 Key Features
* **Real-Time Tracking:** Checks live inventory from Blinkit Dark Stores.
* **Rank Detection:** Tells you exactly where your product appears (e.g., "Rank #4").
* **Top 36 Scan Rule:** The bot scans **only the Top 36 products** (first 6 rows). If your product is found within this range, it shows the rank; otherwise, it marks it as "Not Found" to reflect realistic customer visibility.
* **Multi-Location Scanning:** Scan 50+ locations (Delhi, Mumbai, Noida, etc.) in one go.
* **Admin Panel:** Add/Remove Cities, Areas, and Products without touching code.
---

## 🛠️ Prerequisites
Before running the tool, ensure you have the following installed:
1.  **Python 3.8+**: [Download Here](https://www.python.org/downloads/) (Make sure to check *"Add Python to PATH"* during installation).
2.  **Google Chrome**: The bot uses the Chrome browser engine.

---

## 📥 Installation

1.  **Download & Extract** the project folder.
2.  Open the folder, click the address bar, type `cmd`, and press **Enter**.
3.  Run the following commands one by one:

```bash
# 1. Install required Python libraries
pip install -r requirements.txt

# 2. Install the browser automation engine
playwright install

⚡ How to Run
Option 1: The Easy Way (One-Click)
Double-click the Start_Tracker.bat file included in the folder. It will automatically set up everything and launch the dashboard.

Option 2: The Command Line Way
Open your terminal/command prompt in the project folder and run:

Bash

streamlit run app.py
🖥️ User Guide
1. Tracker Dashboard
Select Product: Choose the category and specific model you want to hunt.

Select Location:

Database: Choose from your saved cities (Delhi, Gurgaon, etc.).

Manual: Type any custom location (e.g., "Sector 18 Noida 201301").

Run Analysis: Click the button and watch the live feed. Green = Found ✅, Red = Not Found ❌.

2. Admin Panel
Go to the "🛠️ Admin Panel" tab.

Add Data: Create new Categories, Products, Cities, or Areas.

Delete Data: Remove outdated items.

Note: All changes are saved permanently to tracker_config.json.

📂 Project Structure
app.py - The main Dashboard (UI).

tracker.py - The automation bot (Playwright logic).

data_manager.py - Handles saving/loading the database.

tracker_config.json - Stores your Cities, Pincodes, and Products.

requirements.txt - List of required Python libraries.

⚠️ Disclaimer
This tool is for educational and internal analytics purposes only.

Do not use this tool to spam or overload Blinkit's servers.

The developers are not responsible for any misuse of this software.

👨‍💻 Developer
Built for Leaf Studios Internal Tracking.

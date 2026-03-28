import streamlit as st
import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import io

# Page Setup
st.set_page_config(page_title="Pilot Pro Scraper", page_icon="🚀", layout="wide")

st.title("🚀 Pro Universal Scraper")
st.markdown("Enter URL to get **Clickable Links** and all data in one Excel file.")

url = st.text_input("Enter Website URL:", placeholder="https://www.example.com")

def universal_scrape(target_url):
    scraper = cloudscraper.create_scraper()
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}
        response = scraper.get(target_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 1. Headings
            headings = [{"Tag": f"H{i}", "Text": h.text.strip()} for i in range(1, 7) for h in soup.find_all(f'h{i}')]
            
            # 2. Clickable Links Logic
            links = []
            for a in soup.find_all('a', href=True):
                href = a.get('href')
                if href.startswith('/'): # Relative links ko absolute banana
                    from urllib.parse import urljoin
                    href = urljoin(target_url, href)
                links.append({"Text": a.text.strip() or "No Text", "URL": href})
            
            # 3. Images
            images = [{"Alt": img.get('alt', 'No Alt'), "Source": img.get('src')} for img in soup.find_all('img', src=True)]
            
            return headings, links, images, None
        else:
            return None, None, None, f"Error: Status {response.status_code}"
    except Exception as e:
        return None, None, None, str(e)

if st.button("Scrape & Prepare Download"):
    if url:
        with st.spinner('Scraping bulky data...'):
            h_data, l_data, i_data, error = universal_scrape(url)
            
            if not error:
                st.success("Data ready!")
                
                # Dataframes
                df_h = pd.DataFrame(h_data)
                df_l = pd.DataFrame(l_data)
                df_i = pd.DataFrame(i_data)

                # --- EXCEL DOWNLOAD LOGIC (Clickable Links) ---
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_h.to_excel(writer, sheet_name='Headings', index=False)
                    df_l.to_excel(writer, sheet_name='Links', index=False)
                    df_i.to_excel(writer, sheet_name='Images', index=False)
                    
                    # Workbook formatting for Clickable Links
                    workbook = writer.book
                    worksheet = writer.sheets['Links']
                    header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC'})
                    
                    # Columns ki width set karna
                    worksheet.set_column('A:A', 30)
                    worksheet.set_column('B:B', 60)

                processed_data = output.getvalue()
                
                st.download_button(
                    label="📥 Download Everything (Excel with Clickable Links)",
                    data=processed_data,
                    file_name="scraped_data_pro.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                # Show Preview on Screen
                t1, t2 = st.tabs(["Preview Links", "Preview Headings"])
                t1.dataframe(df_l, use_container_width=True)
                t2.table(df_h.head(10))
            else:
                st.error(error)

st.markdown("---")
st.caption("Bahi, Excel file open kar ke 'Links' wali sheet check kariyega, wahan URLs clickable hon gay.")

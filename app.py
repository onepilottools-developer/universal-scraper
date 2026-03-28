import streamlit as st
import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import io
from urllib.parse import urljoin

st.set_page_config(page_title="Pilot Pro Scraper", page_icon="🚀")

st.title("🚀 Pro Universal Scraper")
st.markdown("Enter URL and get an Excel with **Headings, Clickable Links, and Images**.")

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
            
            # 2. Links
            links = []
            for a in soup.find_all('a', href=True):
                href = a.get('href')
                full_url = urljoin(target_url, href)
                links.append({"Text": a.text.strip() or "Link", "URL": full_url})
            
            # 3. Images (NEW PORTION)
            images = []
            for img in soup.find_all('img', src=True):
                img_url = urljoin(target_url, img.get('src'))
                images.append({"Alt Text": img.get('alt', 'No Alt'), "Image URL": img_url})
                
            return headings, links, images, None
        return None, None, None, f"Status: {response.status_code}"
    except Exception as e:
        return None, None, None, str(e)

if st.button("Scrape & Prepare Download"):
    if url:
        with st.spinner('Scraping all data including images...'):
            h_data, l_data, i_data, error = universal_scrape(url)
            if not error:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    # Sheet 1: Headings
                    pd.DataFrame(h_data).to_excel(writer, sheet_name='Headings', index=False)
                    
                    # Sheet 2: Links (Clickable)
                    workbook = writer.book
                    link_sheet = workbook.add_worksheet('Links')
                    header_fmt = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1})
                    link_fmt = workbook.add_format({'color': 'blue', 'underline': 1})
                    
                    link_sheet.write(0, 0, 'Link Text', header_fmt)
                    link_sheet.write(0, 1, 'URL', header_fmt)
                    for i, link in enumerate(l_data, start=1):
                        link_sheet.write(i, 0, str(link['Text']))
                        link_sheet.write_url(i, 1, str(link['URL']), link_fmt, str(link['URL']))
                    link_sheet.set_column('A:B', 50)
                    
                    # Sheet 3: Images (NEW SHEET)
                    img_sheet = workbook.add_worksheet('Images')
                    img_sheet.write(0, 0, 'Alt Text', header_fmt)
                    img_sheet.write(0, 1, 'Image Source URL', header_fmt)
                    for i, img in enumerate(i_data, start=1):
                        img_sheet.write(i, 0, str(img['Alt Text']))
                        # Images ke links ko bhi clickable bana diya hai
                        img_sheet.write_url(i, 1, str(img['Image URL']), link_fmt, str(img['Image URL']))
                    img_sheet.set_column('A:B', 60)

                st.success("Everything Scraped Successfully!")
                st.download_button(
                    label="📥 Download Complete Excel (3 Sheets)",
                    data=output.getvalue(),
                    file_name="onepilot_scraped_pro.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.error(error)

import streamlit as st
import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import io
from urllib.parse import urljoin

st.set_page_config(page_title="Pilot Pro Scraper", page_icon="🚀")

st.title("🚀 Pro Universal Scraper")
st.markdown("Headings, Clickable Links, and Images extraction.")

url = st.text_input("Enter Website URL:", placeholder="https://www.example.com")

def universal_scrape(target_url):
    scraper = cloudscraper.create_scraper()
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}
        response = scraper.get(target_url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 1. Headings
            headings = [{"Tag": f"H{i}", "Text": h.text.strip()} for i in range(1, 7) for h in soup.find_all(f'h{i}') if h.text.strip()]
            
            # 2. Links (Filter Out non-URLs)
            links = []
            for a in soup.find_all('a', href=True):
                href = a.get('href').strip()
                full_url = urljoin(target_url, href)
                # Sirf http wale links uthay ga taake Excel crash na ho
                if full_url.startswith('http'):
                    links.append({"Text": a.text.strip() or "Link", "URL": full_url})
            
            # 3. Images
            images = []
            for img in soup.find_all('img', src=True):
                img_url = urljoin(target_url, img.get('src'))
                if img_url.startswith('http'):
                    images.append({"Alt": img.get('alt', 'No Alt'), "Source": img_url})
                
            return headings, links, images, None
        return None, None, None, f"Status Error: {response.status_code}"
    except Exception as e:
        return None, None, None, str(e)

if st.button("Scrape & Prepare Download"):
    if url:
        with st.spinner('Scraping in progress...'):
            h_data, l_data, i_data, error = universal_scrape(url)
            if not error:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    # Headings
                    pd.DataFrame(h_data).to_excel(writer, sheet_name='Headings', index=False)
                    
                    # Formats
                    workbook = writer.book
                    header_fmt = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1})
                    link_fmt = workbook.add_format({'color': 'blue', 'underline': 1})
                    
                    # Links Sheet (Safety First)
                    l_sheet = workbook.add_worksheet('Links')
                    l_sheet.write(0, 0, 'Link Text', header_fmt)
                    l_sheet.write(0, 1, 'Clickable URL', header_fmt)
                    for row_idx, link in enumerate(l_data, start=1):
                        l_sheet.write(row_idx, 0, str(link['Text']))
                        # Try/Except for extra safety in writing URL
                        try:
                            l_sheet.write_url(row_idx, 1, link['URL'], link_fmt, link['URL'])
                        except:
                            l_sheet.write(row_idx, 1, link['URL'])
                    l_sheet.set_column('A:B', 50)
                    
                    # Images Sheet
                    i_sheet = workbook.add_worksheet('Images')
                    i_sheet.write(0, 0, 'Alt Text', header_fmt)
                    i_sheet.write(0, 1, 'Image Source', header_fmt)
                    for row_idx, img in enumerate(i_data, start=1):
                        i_sheet.write(row_idx, 0, str(img['Alt']))
                        try:
                            i_sheet.write_url(row_idx, 1, img['Source'], link_fmt, img['Source'])
                        except:
                            i_sheet.write(row_idx, 1, img['Source'])
                    i_sheet.set_column('A:B', 50)

                st.success("Success! Click below to download.")
                st.download_button(
                    label="📥 Download Excel (Cleaned)",
                    data=output.getvalue(),
                    file_name="scraped_bulky_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.error(error)

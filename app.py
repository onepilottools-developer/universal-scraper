import streamlit as st
import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import io
from urllib.parse import urljoin

st.set_page_config(page_title="Pilot Pro Scraper", page_icon="🚀")

st.title("🚀 Pro Universal Scraper")
st.markdown("Enter URL and get an Excel with **Clickable Links**.")

url = st.text_input("Enter Website URL:", placeholder="https://www.example.com")

def universal_scrape(target_url):
    scraper = cloudscraper.create_scraper()
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}
        response = scraper.get(target_url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            headings = [{"Tag": f"H{i}", "Text": h.text.strip()} for i in range(1, 7) for h in soup.find_all(f'h{i}')]
            links = []
            for a in soup.find_all('a', href=True):
                href = a.get('href')
                full_url = urljoin(target_url, href)
                links.append({"Text": a.text.strip() or "Link", "URL": full_url})
            return headings, links, None
        return None, None, f"Status: {response.status_code}"
    except Exception as e:
        return None, None, str(e)

if st.button("Scrape & Prepare Download"):
    if url:
        with st.spinner('Scraping...'):
            h_data, l_data, error = universal_scrape(url)
            if not error:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    # 1. Headings Sheet
                    pd.DataFrame(h_data).to_excel(writer, sheet_name='Headings', index=False)
                    
                    # 2. Links Sheet
                    workbook = writer.book
                    worksheet = workbook.add_worksheet('Links')
                    
                    # Formats (Bold and Color)
                    header_fmt = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1})
                    link_fmt = workbook.add_format({'color': 'blue', 'underline': 1})
                    
                    # Header Columns
                    worksheet.write(0, 0, 'Link Text', header_fmt)
                    worksheet.write(0, 1, 'URL', header_fmt)
                    
                    # Data Rows
                    for i, link in enumerate(l_data, start=1):
                        txt = str(link['Text'])
                        u = str(link['URL'])
                        worksheet.write(i, 0, txt)
                        if u.startswith('http'):
                            worksheet.write_url(i, 1, u, link_fmt, u)
                        else:
                            worksheet.write(i, 1, u)
                    
                    worksheet.set_column('A:B', 50)

                st.success("Scraping Successful!")
                st.download_button(
                    label="📥 Download Clickable Excel",
                    data=output.getvalue(),
                    file_name="scraped_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.error(error)

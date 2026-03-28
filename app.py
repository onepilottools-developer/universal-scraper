import streamlit as st
import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import io
from urllib.parse import urljoin

st.set_page_config(page_title="Pilot Pro Scraper", page_icon="🚀")

st.title("🚀 Pro Universal Scraper")
st.markdown("Enter URL and get an Excel with **Clickable Links**.")

# 1. URL Input
url = st.text_input("Enter Website URL:", placeholder="https://www.example.com")

def universal_scrape(target_url):
    scraper = cloudscraper.create_scraper()
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}
        response = scraper.get(target_url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Headings
            headings = [{"Tag": f"H{i}", "Text": h.text.strip()} for i in range(1, 7) for h in soup.find_all(f'h{i}')]
            
            # Links
            links = []
            for a in soup.find_all('a', href=True):
                href = a.get('href')
                full_url = urljoin(target_url, href)
                links.append({"Text": a.text.strip() or "Link", "URL": full_url})
            
            return headings, links, None
        return None, None, f"Status Error: {response.status_code}"
    except Exception as e:
        return None, None, str(e)

# 2. Button Logic
if st.button("Scrape & Prepare Download"):
    if url:
        with st.spinner('Scraping data... Please wait.'):
            h_data, l_data, error = universal_scrape(url)
            
            if not error:
                output = io.BytesIO()
                # XlsxWriter engine use kar rahe hain clickable links ke liye
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    # Headings Sheet (Simple)
                    pd.DataFrame(h_data).to_excel(writer, sheet_name='Headings', index=False)
                    
                    # Links Sheet (Clickable)
                    workbook = writer.book
                    worksheet = workbook.add_worksheet('Links')
                    
                    # Formats
                    header_fmt = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1})
                    link_fmt = workbook.add_format({'color': 'blue', 'underline': 1})
                    
                    # Headers likhna
                    worksheet.write(0, 0, 'Link Text', header_fmt)
                    worksheet.write(0, 1, 'Clickable URL', header_format=header_fmt)
                    
                    # Data likhna (Standard write function)
                    for i, link in enumerate(l_data, start=1):
                        text = str(link['Text'])
                        link_url = str(link['URL'])
                        
                        worksheet.write(i, 0, text) # Column A
                        # Hyperlink Column B
                        if link_url.startswith('http'):
                            worksheet.write_url(i, 1, link_url, link_fmt, link_url)
                        else:
                            worksheet.write(i, 1, link_url)
                    
                    worksheet.set_column('A:A', 30)
                    worksheet.set_column('B:B', 70)

                st.success("Scraping Complete!")
                st.download_button(
                    label="📥 Download Clickable Excel",
                    data=output.getvalue(),
                    file_name="scraped_links.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.error(f"Error: {error}")
    else:
        st.warning("Please enter a URL first!")

import streamlit as st
import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import io
from urllib.parse import urljoin

# ... (Baki setup wahi rahay ga) ...

if st.button("Scrape & Prepare Download"):
    if url:
        with st.spinner('Scraping bulky data...'):
            h_data, l_data, i_data, error = universal_scrape(url)
            
            if not error:
                st.success("Data ready!")
                
                # Excel file create karna memory mein
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    # 1. Headings Sheet
                    pd.DataFrame(h_data).to_excel(writer, sheet_name='Headings', index=False)
                    
                    # 2. Links Sheet (Custom logic for Clickable Links)
                    workbook = writer.book
                    worksheet = workbook.add_worksheet('Links')
                    
                    # Header likhna
                    header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1})
                    worksheet.write(0, 0, 'Text', header_format)
                    worksheet.write(0, 1, 'Clickable URL', header_format)
                    
                    # Links ko clickable banana
                    link_format = workbook.add_format({'color': 'blue', 'underline': 1})
                    
                    for row_num, link in enumerate(l_data, start=1):
                        text = link.get('Text', 'No Text')
                        href = link.get('URL', '')
                        
                        worksheet.write(row_num, 0, text)
                        # Yahan hum 'write_url' use kar rahay hain jo link ko clickable banata hai
                        if href.startswith('http'):
                            worksheet.write_url(row_num, 1, href, link_format, href)
                        else:
                            worksheet.write(row_num, 1, href)
                    
                    # 3. Images Sheet
                    pd.DataFrame(i_data).to_excel(writer, sheet_name='Images', index=False)
                    
                    # Column width set karna
                    worksheet.set_column('A:A', 30)
                    worksheet.set_column('B:B', 70)

                processed_data = output.getvalue()
                
                st.download_button(
                    label="📥 Download Excel (Clickable Links)",
                    data=processed_data,
                    file_name="scraped_clickable_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

import streamlit as st
import dns.resolver
import pandas as pd
import re

def extract_domain(email_or_domain):
    # Remove leading '@' if present
    email_or_domain = email_or_domain.lstrip('@')
    
    # Simple regex to extract domain from email or return the domain if it's already a domain
    match = re.search(r'(?:(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9])$', email_or_domain.lower())
    return match.group() if match else None

def check_mx_record(domain):
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        return [str(mx.exchange) for mx in mx_records]
    except dns.resolver.NoAnswer:
        return []
    except dns.resolver.NXDOMAIN:
        return None
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    st.title("Email/Domain MX Record Checker")

    # Input area for emails or domains
    input_text = st.text_area("Enter email addresses or domains (one per line):", height=150)
    
    if st.button("Check MX Records"):
        if input_text:
            inputs = input_text.split('\n')  # Split by newline instead of whitespace
            unique_domains = set()
            for item in inputs:
                domain = extract_domain(item.strip())
                if domain:
                    unique_domains.add(domain)

            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()

            for i, domain in enumerate(unique_domains):
                mx_records = check_mx_record(domain)

                if isinstance(mx_records, str) and mx_records.startswith("Error"):
                    status = mx_records
                elif mx_records is None:
                    status = "Domain does not exist"
                elif mx_records:
                    status = "Valid MX records"
                else:
                    status = "No MX records found"

                results.append({
                    "Domain": domain,
                    "MX Records": ', '.join(mx_records) if isinstance(mx_records, list) else str(mx_records),
                    "Status": status
                })
                
                progress = (i + 1) / len(unique_domains)
                progress_bar.progress(progress)
                status_text.text(f"Processed {i+1}/{len(unique_domains)} domains")

            df = pd.DataFrame(results)
            st.dataframe(df)

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Download results as CSV",
                csv,
                "mx_check_results.csv",
                "text/csv",
                key='download-csv'
            )
        else:
            st.warning("Please enter at least one email address or domain.")

if __name__ == "__main__":
    main()
import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="LegitScript Compliance Scanner", layout="wide")

# Risky phrases to flag
risky_phrases = [
    "FDA-approved semaglutide", "Same as Ozempic", "Generic Ozempic",
    "Lose 20 lbs in 1 month", "Guaranteed weight loss", "Rapid weight loss solution",
    "Safe and effective", "We offer Ozempic for less", "Order Mounjaro here",
    "Get Wegovy compounded", "Magic shot for weight loss", "Cure for obesity",
    "No side effects", "Risk-free weight loss", "Act now to claim your weight loss shot!",
    "No prescription required"
]

# Structural checks
other_checks = {
    "Missing HIPAA-compliant privacy policy": ["privacy", "hipaa", "protected health information"],
    "No physical address listed": ["address", "location", "contact"],
    "No phone number found": ["phone", "call", "contact"],
    "Compounded tirzepatide offered (post-shortage)": ["compounded tirzepatide"],
    "Unverified customer reviews or rating claims": ["4.9 out of 5", "verified customer"],
    "Unclear jurisdictional licensing": ["states we serve", "licensed in", "coverage area"],
    "Mismatch across social media and site": ["NAD+", "enclomiphene", "metformin"],
    "Misleading pickup claim": ["pickup available"]
}

# Fetch and parse page text
def get_page_text(url):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        return soup.get_text(separator=" ", strip=True)
    except Exception as e:
        return f"Error fetching site: {e}"

# Scan logic
def scan_text(text):
    issues = []
    for phrase in risky_phrases:
        if re.search(rf'\b{re.escape(phrase)}\b', text, re.IGNORECASE):
            issues.append(f"⚠️ Risky marketing phrase found: **{phrase}**")

    for label, keywords in other_checks.items():
        if not any(k.lower() in text.lower() for k in keywords):
            issues.append(f"❌ Potential issue: **{label}**")

    return issues

# Streamlit UI
st.title("🛡️ LegitScript Compliance Scanner")
st.caption("Audit telehealth sites for FDA and LegitScript compliance")

url = st.text_input("Enter a full website URL (e.g., https://example.com):")

if url:
    with st.spinner("Scanning website..."):
        text = get_page_text(url)
        if text.startswith("Error"):
            st.error(text)
        else:
            findings = scan_text(text)
            if findings:
                st.warning("⚠️ Compliance Issues Found:")
                for f in findings:
                    st.markdown(f)
            else:
                st.success("✅ No major compliance issues found.")

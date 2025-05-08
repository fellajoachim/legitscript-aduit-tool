
import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="LegitScript Compliance Scanner", layout="wide")

# Compliance rules
compliance_rules = {
    "FDA-approved semaglutide": {
        "category": "Marketing Claims",
        "risk": 10,
        "fix": "Replace with: 'Compounded semaglutide is not FDA-approved and is only prescribed when appropriate.'",
        "reference": "FDA + LegitScript: Compounded drugs must not be misrepresented as FDA-approved."
    },
    "Same as Ozempic": {
        "category": "Misleading Equivalence",
        "risk": 10,
        "fix": "Do not suggest equivalence. Say 'Compounded GLP-1 similar in function but not identical to Ozempic.'",
        "reference": "FDA prohibits implying compounded meds are equivalent to brand-name drugs."
    },
    "No prescription required": {
        "category": "Prescription Compliance",
        "risk": 15,
        "fix": "State clearly that prescriptions require a provider review.",
        "reference": "LegitScript Standard 6 - Consults must occur before prescribing medication."
    },
    "Guaranteed weight loss": {
        "category": "Unsubstantiated Claims",
        "risk": 10,
        "fix": "Use: 'Results vary. Medication is prescribed based on individual needs.'",
        "reference": "FDA/FTC prohibit absolute guarantees in healthcare outcomes."
    },
    "privacy": {
        "category": "HIPAA Compliance",
        "risk": 10,
        "fix": "Include a HIPAA-compliant privacy policy outlining PHI usage, rights, and contact person.",
        "reference": "LegitScript Standard 9 - HIPAA-aligned privacy disclosure is required."
    },
    "phone": {
        "category": "Contact Info",
        "risk": 5,
        "fix": "Add a callable business phone number to Contact page.",
        "reference": "LegitScript Standard 8 - Patient Services requires contactable support."
    },
    "address": {
        "category": "Business Location",
        "risk": 5,
        "fix": "Add a valid business address for your organization and any affiliated pharmacy.",
        "reference": "LegitScript Standard 8 - Real addresses for businesses and pharmacies are required."
    },
    "compounded tirzepatide": {
        "category": "FDA Shortage Compliance",
        "risk": 15,
        "fix": "Remove unless you clearly justify compounding under FDA exemption and post-shortage protocols.",
        "reference": "FDA Guidance Dec 2024: Tirzepatide is no longer in shortage."
    }
}

def extract_text(url):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        return soup.get_text(separator=" ", strip=True)
    except Exception as e:
        return None, str(e)

def scan_for_violations(text):
    findings = []
    total_score = 100
    for phrase, details in compliance_rules.items():
        if re.search(rf'\b{re.escape(phrase)}\b', text, re.IGNORECASE):
            total_score -= details["risk"]
            findings.append({
                "phrase": phrase,
                "category": details["category"],
                "risk": details["risk"],
                "fix": details["fix"],
                "reference": details["reference"]
            })
    return findings, max(total_score, 0)

# Streamlit UI
st.title("🛡️ LegitScript Compliance Scanner — Enhanced Audit")
st.caption("Enter a telehealth site to get detailed FDA & LegitScript compliance audit")

url = st.text_input("🔗 Website URL (e.g., https://example.com):")

if url:
    with st.spinner("Scanning and analyzing website..."):
        text, error = extract_text(url), None
        if isinstance(text, tuple):  # error occurred
            text, error = text
        if error:
            st.error(f"Error fetching content: {error}")
        elif not text:
            st.warning("No readable content found on the site.")
        else:
            results, score = scan_for_violations(text)
            st.markdown(f"### 🧮 Compliance Score: `{score}/100`")
            if score < 80:
                st.info("This site may be at **moderate to high risk** of LegitScript rejection. Review below.")

            if results:
                st.markdown("### ❌ Compliance Issues Detected:")
                for issue in results:
                    with st.expander(f"⚠️ {issue['phrase']} — {issue['category']}"):
                        st.markdown(f"- **Risk Score Impact**: -{issue['risk']}")
                        st.markdown(f"- **Why it's an issue**: {issue['reference']}")
                        st.markdown(f"- **Suggested Fix**: {issue['fix']}")
            else:
                st.success("✅ No major compliance risks found.")

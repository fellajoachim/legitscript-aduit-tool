
import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="LegitScript + HIPAA Compliance Scanner", layout="wide")

# Define advanced compliance rulebook
compliance_rules = {
    "FDA-approved semaglutide": {
        "category": "Misleading FDA Claim",
        "risk": 15,
        "description": "Do not represent compounded semaglutide as FDA-approved.",
        "reference": "FDA / LegitScript Guidance"
    },
    "Same as Ozempic": {
        "category": "Implied Equivalence",
        "risk": 10,
        "description": "Avoid implying compounded drugs are equivalent to brand-name products.",
        "reference": "FDA Rules on Drug Compounding"
    },
    "Guaranteed weight loss": {
        "category": "Unsubstantiated Health Claim",
        "risk": 10,
        "description": "No guaranteed outcomes in health claims unless backed by peer-reviewed studies.",
        "reference": "FTC Health Marketing Compliance"
    },
    "No prescription required": {
        "category": "Prescription Flow Violation",
        "risk": 15,
        "description": "Prescriptions must be issued after provider review. This phrase implies bypassing that.",
        "reference": "LegitScript Standard 6"
    },
    "Lose \d+ lbs in \d+ (days|weeks|months)": {
        "category": "Unverified Outcome",
        "risk": 10,
        "description": "Numerical claims of weight loss must be backed by specific, cited clinical studies.",
        "reference": "FTC / FDA Ad Guidelines"
    },
    "HIPAA": {
        "category": "HIPAA Mention Check",
        "risk": -1,
        "description": "HIPAA mention detected; manual check still required to confirm PHI handling details.",
        "reference": "HIPAA Privacy Rule"
    },
    "privacy policy": {
        "category": "Privacy Policy Presence",
        "risk": -1,
        "description": "Check that the privacy policy includes PHI usage, patient rights, and privacy official contact.",
        "reference": "LegitScript Standard 9 / HIPAA"
    },
    "pickup available": {
        "category": "Dispensing Transparency",
        "risk": 8,
        "description": "Must clarify pharmacy pickup rules or remove if not allowed.",
        "reference": "LegitScript Standard 8"
    },
    "compounded tirzepatide": {
        "category": "Post-Shortage Compounding Risk",
        "risk": 15,
        "description": "Tirzepatide is no longer on the FDA shortage list. Usage must be clinically justified.",
        "reference": "FDA Dec 2024 Guidance"
    }
}

# Helper function
def extract_sections(html):
    soup = BeautifulSoup(html, "html.parser")
    sections = soup.find_all(["section", "div", "footer", "header", "article"])
    page_sections = {}
    for i, sec in enumerate(sections):
        text = sec.get_text(separator=" ", strip=True)
        if len(text) > 50:
            page_sections[f"Section {i+1}"] = text[:300] + "..." if len(text) > 300 else text
    return page_sections

def scan_section(text):
    findings = []
    for phrase, rule in compliance_rules.items():
        if re.search(phrase, text, re.IGNORECASE):
            findings.append({
                "phrase": phrase,
                "category": rule["category"],
                "risk": rule["risk"],
                "description": rule["description"],
                "reference": rule["reference"]
            })
    return findings

def get_page_html(url):
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        return res.text, None
    except Exception as e:
        return None, str(e)

# Streamlit UI
st.title("🛡️ Advanced Telehealth Compliance Scanner")
st.caption("Strictly scans live websites for LegitScript, HIPAA, FDA, and FTC red flags")

url = st.text_input("Paste a full URL (e.g., https://example.com):")

if url:
    with st.spinner("Analyzing page structure and scanning for violations..."):
        html, err = get_page_html(url)
        if err:
            st.error(f"Error fetching page: {err}")
        elif html:
            section_texts = extract_sections(html)
            total_risk = 0
            total_findings = 0
            st.markdown("## 🔍 Section-by-Section Analysis")

            for sec_label, sec_text in section_texts.items():
                findings = scan_section(sec_text)
                if findings:
                    with st.expander(f"⚠️ {sec_label} — {len(findings)} potential issue(s)"):
                        for issue in findings:
                            st.markdown(f"**Phrase:** `{issue['phrase']}`")
                            st.markdown(f"- **Category:** {issue['category']}")
                            st.markdown(f"- **Description:** {issue['description']}")
                            st.markdown(f"- **Reference:** {issue['reference']}")
                            st.markdown("---")
                            total_risk += issue['risk'] if issue['risk'] > 0 else 0
                            total_findings += 1
                else:
                    st.markdown(f"✅ {sec_label}: No major issues detected.")

            final_score = max(100 - total_risk, 0)
            st.markdown("## 📊 Overall Compliance Score")
            st.markdown(f"### `{final_score}/100`")
            if final_score < 80:
                st.warning("⚠️ This site may face LegitScript certification risks. Review the flagged sections carefully.")
            elif final_score == 100:
                st.success("✅ No compliance issues detected across major rulesets.")


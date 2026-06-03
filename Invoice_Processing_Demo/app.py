import streamlit as st
import re
import json
from typing import Optional
from pydantic import BaseModel

from pypdf import PdfReader

from langchain.tools import tool
###from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain.agents import create_agent


# -------------------------------
# Schema
# -------------------------------
class Invoice(BaseModel):
    vendor: str
    amount: float
    invoice_number: str
    is_valid: Optional[bool] = None
    risk_flag: Optional[str] = None


# -------------------------------
# PDF Extraction
# -------------------------------
def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text


# -------------------------------
# Tools
# -------------------------------
@tool
def extract_invoice(text: str) -> dict:
    """Extract structured invoice details from text"""

    vendor_match = re.search(r"from ([A-Za-z ]+)", text)
    amount_match = re.search(r"(\d+)", text)
    invoice_match = re.search(r"(INV[- ]?\d+)", text)

    return {
        "vendor": vendor_match.group(1) if vendor_match else "Unknown",
        "amount": float(amount_match.group(1)) if amount_match else 0,
        "invoice_number": invoice_match.group(1) if invoice_match else "INV-UNKNOWN"
    }


@tool
def validate_invoice(data: dict) -> dict:
    """Validate invoice fields"""

    valid = True

    if data["amount"] <= 0:
        valid = False
    if data["vendor"] == "Unknown":
        valid = False

    data["is_valid"] = valid
    return data


@tool
def risk_assessment(data: dict) -> dict:
    """Assess invoice risk"""

    if data["amount"] > 10000:
        data["risk_flag"] = "🔴 High value - needs approval"
    elif data["amount"] < 100:
        data["risk_flag"] = "🟢 Low value - auto approve"
    else:
        data["risk_flag"] = "🟡 Normal"

    return data


tools = [extract_invoice, validate_invoice, risk_assessment]


# -------------------------------
# Load Agent (cached)
# -------------------------------
@st.cache_resource
def load_agent():
    ## llm = ChatGoogleGenerativeAI(
     ##   model="models/gemini-2.0-flash",
     ##   temperature=0,
     ##   api_key="somekey"   # 🔴 replace or use env var
     ## )

    llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key="somekey"
    )
    print(llm.invoke("Hello"))

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=(
            "You are an AI finance assistant. "
            "Extract invoice details, validate them, assess risk, "
            "and return ONLY a clean JSON output."
        )
    )
    return agent


agent = load_agent()


# -------------------------------
# UI
# -------------------------------
st.set_page_config(page_title="AI Invoice Agent", layout="centered")

st.title("📄 AI Invoice Processing Agent")
st.markdown("Upload or paste invoice → AI extracts, validates & flags risk")

# -------------------------------
# Input Section
# -------------------------------
st.subheader("📥 Input Invoice")

uploaded_file = st.file_uploader("Upload Invoice PDF", type=["pdf"])

invoice_text = st.text_area(
    "Or paste invoice text",
    placeholder="Invoice from ABC Corp for 1200 INV-001"
)

input_text = ""

if uploaded_file is not None:
    input_text = extract_text_from_pdf(uploaded_file)
    st.success("✅ PDF uploaded and text extracted")

    with st.expander("📄 View Extracted Text"):
        st.text(input_text)

elif invoice_text:
    input_text = invoice_text


# -------------------------------
# Options
# -------------------------------
show_steps = st.checkbox("Show agent steps (debug mode)")

# -------------------------------
# Process Button
# -------------------------------
if st.button("🚀 Process Invoice"):

    if not input_text.strip():
        st.warning("Please upload a PDF or enter invoice text")

    else:
        with st.spinner("Processing..."):
            response = agent.invoke({
                "messages": [{"role": "user", "content": input_text}]
            })

        # -------------------------------
        # Extract final AI message
        # -------------------------------
        final_output = None

        for msg in response["messages"]:
            if msg.type == "ai" and msg.content:
                final_output = msg.content

        st.subheader("📊 Results")

        # -------------------------------
        # Try parsing JSON output
        # -------------------------------
        parsed = None

        try:
            if isinstance(final_output, list):
                final_output = final_output[0]["text"]

            parsed = json.loads(final_output)
        except:
            pass

        # -------------------------------
        # Display nicely
        # -------------------------------
        if parsed:
            col1, col2 = st.columns(2)

            with col1:
                st.metric("Vendor", parsed.get("vendor", "-"))
                st.metric("Amount", parsed.get("amount", "-"))

            with col2:
                st.metric("Invoice #", parsed.get("invoice_number", "-"))
                st.metric("Valid", "✅ Yes" if parsed.get("is_valid") else "❌ No")

            risk = parsed.get("risk_flag", "")

            if "High" in risk:
                st.error(risk)
            elif "Low" in risk:
                st.success(risk)
            else:
                st.info(risk)

        else:
            # fallback if JSON parsing fails
            st.write(final_output)

        # -------------------------------
        # Debug view
        # -------------------------------
        if show_steps:
            st.subheader("🧠 Agent Steps")

            for msg in response["messages"]:
                st.write(f"**{msg.type.upper()}**")
                st.write(msg.content)
import streamlit as st
import json
import random
import pandas as pd
from datetime import datetime, timedelta
import base64
from fpdf import FPDF
import io

# Initialize session state
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'current_agent' not in st.session_state:
    st.session_state.current_agent = "Master"
if 'customer_data' not in st.session_state:
    st.session_state.customer_data = {}
if 'loan_status' not in st.session_state:
    st.session_state.loan_status = "initial"
if 'approved_loan' not in st.session_state:
    st.session_state.approved_loan = {}

class MasterAgent:
    def __init__(self):
        self.name = "Tata Capital AI Assistant"
        self.agents = {
            "Sales": SalesAgent(),
            "KYC": KYCAgent(),
            "Underwriter": UnderwritingAgent(),
            "Sanction": SanctionAgent()
        }
    
    def process_message(self, user_input, customer_data):
        # Analyze intent and sentiment
        intent = self._detect_intent(user_input)
        sentiment = self._detect_sentiment(user_input)
        
        # Update conversation flow based on current state
        if st.session_state.loan_status == "initial":
            return self._handle_initial_contact(user_input, customer_data)
        elif st.session_state.loan_status == "sales":
            return self.agents["Sales"].process_message(user_input, customer_data)
        elif st.session_state.loan_status == "kyc":
            return self.agents["KYC"].process_message(user_input, customer_data)
        elif st.session_state.loan_status == "underwriting":
            return self.agents["Underwriter"].process_message(user_input, customer_data)
        elif st.session_state.loan_status == "approved":
            return self.agents["Sanction"].process_message(user_input, customer_data)
        else:
            return "I'm here to help with your loan needs. How can I assist you today?"
    
    def _detect_intent(self, text):
        text_lower = text.lower()
        if any(word in text_lower for word in ['loan', 'borrow', 'money', 'need funds']):
            return "loan_inquiry"
        elif any(word in text_lower for word in ['holiday', 'vacation', 'travel']):
            return "holiday_loan"
        elif any(word in text_lower for word in ['marriage', 'wedding']):
            return "marriage_loan"
        elif any(word in text_lower for word in ['medical', 'hospital', 'treatment']):
            return "medical_loan"
        elif any(word in text_lower for word in ['yes', 'sure', 'okay', 'proceed']):
            return "affirmative"
        elif any(word in text_lower for word in ['no', 'not now', 'later']):
            return "negative"
        else:
            return "general"
    
    def _detect_sentiment(self, text):
        positive_words = ['good', 'great', 'excellent', 'happy', 'thanks', 'thank you']
        negative_words = ['bad', 'poor', 'terrible', 'unhappy', 'angry', 'frustrated']
        
        if any(word in text.lower() for word in positive_words):
            return "positive"
        elif any(word in text.lower() for word in negative_words):
            return "negative"
        else:
            return "neutral"
    
    def _handle_initial_contact(self, user_input, customer_data):
        intent = self._detect_intent(user_input)
        
        if intent in ["loan_inquiry", "holiday_loan", "marriage_loan", "medical_loan"]:
            st.session_state.loan_status = "sales"
            return self.agents["Sales"].process_message(user_input, customer_data)
        elif intent == "affirmative":
            st.session_state.loan_status = "sales"
            return self.agents["Sales"].process_message("I want a loan", customer_data)
        else:
            return "Hello! I'm your AI Loan Assistant from Tata Capital. I can help you get a personal loan quickly and easily. Would you like to apply for a loan today?"

class SalesAgent:
    def process_message(self, user_input, customer_data):
        if 'name' not in customer_data:
            return "Great! I'd be happy to help you with a loan. Let me get some basic details first. What's your full name?"
        elif 'loan_amount' not in customer_data:
            return "Thanks {}. How much loan amount are you looking for?".format(customer_data['name'])
        elif 'purpose' not in customer_data:
            return "What's the purpose of this loan? (e.g., holiday, marriage, medical, home renovation, etc.)"
        elif 'employment' not in customer_data:
            return "Are you salaried or self-employed?"
        elif 'monthly_income' not in customer_data:
            return "What's your approximate monthly income?"
        elif 'city' not in customer_data:
            return "Which city do you live in?"
        else:
            # All sales data collected, move to KYC
            st.session_state.loan_status = "kyc"
            st.session_state.current_agent = "KYC"
            return "Perfect! I have all the basic details. Now let me transfer you to our verification team to complete the KYC process."

class KYCAgent:
    def process_message(self, user_input, customer_data):
        if 'pan_number' not in customer_data:
            return "Welcome to KYC verification. Please provide your PAN card number."
        elif 'aadhaar_number' not in customer_data:
            return "Thank you. Please provide your Aadhaar number."
        elif 'phone_number' not in customer_data:
            return "Please share your registered mobile number."
        elif 'email' not in customer_data:
            return "Please provide your email address."
        else:
            # KYC complete, move to underwriting
            st.session_state.loan_status = "underwriting"
            st.session_state.current_agent = "Underwriter"
            return "KYC verification complete! Now transferring you to our underwriting team for loan approval."

class UnderwritingAgent:
    def __init__(self):
        self.credit_scores = {}
    
    def process_message(self, user_input, customer_data):
        # Mock credit score API
        pan = customer_data.get('pan_number', 'default')
        if pan not in self.credit_scores:
            self.credit_scores[pan] = random.randint(650, 850)
        
        credit_score = self.credit_scores[pan]
        monthly_income = customer_data.get('monthly_income', 0)
        loan_amount = customer_data.get('loan_amount', 0)
        
        # Underwriting logic
        max_eligible = monthly_income * 12  # 1 year income
        emi = self.calculate_emi(loan_amount, 10.5, 3)  # 10.5% interest, 3 years
        
        # Decision logic
        if credit_score >= 750 and loan_amount <= max_eligible and emi <= monthly_income * 0.5:
            # Approved
            st.session_state.loan_status = "approved"
            st.session_state.current_agent = "Sanction"
            st.session_state.approved_loan = {
                'amount': loan_amount,
                'interest_rate': 10.5,
                'tenure': 3,
                'emi': emi,
                'credit_score': credit_score
            }
            return f"🎉 Congratulations! Your loan has been approved!\n\nCredit Score: {credit_score}\nApproved Amount: ₹{loan_amount:,}\nInterest Rate: 10.5%\nTenure: 3 years\nMonthly EMI: ₹{emi:,.2f}\n\nGenerating your sanction letter now..."
        elif credit_score >= 700 and emi > monthly_income * 0.5:
            # Suggest lower amount
            suggested_amount = (monthly_income * 0.5 * 12) / 1.2  # Conservative estimate
            return f"Based on your income, we can approve a lower amount. Your credit score is {credit_score}. Would you like to consider ₹{suggested_amount:,.0f} instead?"
        else:
            # Rejected
            st.session_state.loan_status = "rejected"
            return f"Unfortunately, we cannot approve your loan at this time. Credit Score: {credit_score}. Reason: {'Low credit score' if credit_score < 700 else 'EMI too high compared to income'}."
    
    def calculate_emi(self, principal, rate, years):
        monthly_rate = rate / 12 / 100
        months = years * 12
        emi = (principal * monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
        return emi

class SanctionAgent:
    def process_message(self, user_input, customer_data):
        # Generate PDF sanction letter
        pdf_buffer = self.generate_sanction_letter(customer_data, st.session_state.approved_loan)
        
        # Convert to base64 for download
        pdf_b64 = base64.b64encode(pdf_buffer.getvalue()).decode()
        
        download_link = f'''
        <a href="data:application/pdf;base64,{pdf_b64}" download="sanction_letter.pdf" style="
            display: inline-block;
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
        ">📄 Download Sanction Letter</a>
        '''
        
        return f"Your sanction letter is ready! {download_link}<br><br>Thank you for choosing Tata Capital!"
    
    def generate_sanction_letter(self, customer_data, loan_data):
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'TATA CAPITAL', 0, 1, 'C')
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'LOAN SANCTION LETTER', 0, 1, 'C')
        pdf.ln(10)
        
        # Customer Details
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Customer Details:', 0, 1)
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 8, f"Name: {customer_data.get('name', 'N/A')}", 0, 1)
        pdf.cell(0, 8, f"PAN: {customer_data.get('pan_number', 'N/A')}", 0, 1)
        pdf.cell(0, 8, f"Phone: {customer_data.get('phone_number', 'N/A')}", 0, 1)
        pdf.cell(0, 8, f"Email: {customer_data.get('email', 'N/A')}", 0, 1)
        pdf.ln(5)
        
        # Loan Details
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Loan Details:', 0, 1)
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 8, f"Sanctioned Amount: ₹{loan_data['amount']:,}", 0, 1)
        pdf.cell(0, 8, f"Interest Rate: {loan_data['interest_rate']}% p.a.", 0, 1)
        pdf.cell(0, 8, f"Loan Tenure: {loan_data['tenure']} years", 0, 1)
        pdf.cell(0, 8, f"Monthly EMI: ₹{loan_data['emi']:,.2f}", 0, 1)
        pdf.cell(0, 8, f"Credit Score: {loan_data['credit_score']}", 0, 1)
        pdf.ln(10)
        
        # Terms and Conditions
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Terms & Conditions:', 0, 1)
        pdf.set_font('Arial', '', 10)
        terms = [
            "1. This sanction is valid for 30 days from the date of issue.",
            "2. Final disbursement subject to documentation verification.",
            "3. Interest rates are subject to change as per market conditions.",
            "4. Prepayment charges may apply as per policy.",
            "5. Late payment fees will be charged for delayed EMI payments."
        ]
        for term in terms:
            pdf.multi_cell(0, 6, term)
        
        # Footer
        pdf.ln(15)
        pdf.cell(0, 10, 'Authorized Signatory', 0, 1, 'R')
        pdf.cell(0, 5, 'Tata Capital Financial Services Ltd.', 0, 1, 'R')
        
        pdf_buffer = io.BytesIO()
        pdf.output(pdf_buffer)
        pdf_buffer.seek(0)
        return pdf_buffer

# Streamlit UI
def main():
    st.set_page_config(page_title="Tata Capital AI Loan Agent", page_icon="🏦", layout="wide")
    
    # Custom CSS
    st.markdown("""
    <style>
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        background-color: #f9f9f9;
    }
    .user-message {
        background-color: #0078D4;
        color: white;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        text-align: right;
        max-width: 80%;
        margin-left: 20%;
    }
    .agent-message {
        background-color: #E8E8E8;
        color: black;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        max-width: 80%;
    }
    .status-bar {
        background-color: #2E8B57;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/2830/2830284.png", width=80)
    with col2:
        st.title("Tata Capital AI Loan Officer Team")
        st.subheader("Your 24/7 Virtual Banking Assistant")
    
    # Status bar
    status_col1, status_col2, status_col3 = st.columns(3)
    with status_col1:
        st.markdown(f'<div class="status-bar">Current Agent: <b>{st.session_state.current_agent}</b></div>', unsafe_allow_html=True)
    with status_col2:
        st.markdown(f'<div class="status-bar">Loan Status: <b>{st.session_state.loan_status.upper()}</b></div>', unsafe_allow_html=True)
    with status_col3:
        if st.session_state.customer_data:
            st.markdown(f'<div class="status-bar">Customer: <b>{st.session_state.customer_data.get("name", "New")}</b></div>', unsafe_allow_html=True)
    
    # Agent workflow visualization
    st.markdown("### 🚀 AI Agent Workflow")
    agents = ["Master", "Sales", "KYC", "Underwriter", "Sanction"]
    current_index = agents.index(st.session_state.current_agent) if st.session_state.current_agent in agents else 0
    
    cols = st.columns(5)
    for i, (col, agent) in enumerate(zip(cols, agents)):
        with col:
            if i <= current_index:
                st.success(f"✅ {agent}")
            else:
                st.info(f"⏳ {agent}")
    
    # Chat interface
    st.markdown("### 💬 Loan Application Chat")
    
    # Display conversation
    chat_html = '<div class="chat-container">'
    for msg in st.session_state.conversation:
        if msg['type'] == 'user':
            chat_html += f'<div class="user-message">{msg["content"]}</div>'
        else:
            chat_html += f'<div class="agent-message"><b>{msg["agent"]}:</b> {msg["content"]}</div>'
    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)
    
    # User input
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_input("Type your message here:", key="user_input", placeholder="Ask about loans, provide information...")
    with col2:
        send_button = st.button("Send", use_container_width=True)
    
    # Process user input
    if send_button and user_input:
        # Add user message to conversation
        st.session_state.conversation.append({
            'type': 'user',
            'content': user_input,
            'timestamp': datetime.now()
        })
        
        # Process through master agent
        master_agent = MasterAgent()
        response = master_agent.process_message(user_input, st.session_state.customer_data)
        
        # Add agent response to conversation
        st.session_state.conversation.append({
            'type': 'agent',
            'agent': st.session_state.current_agent,
            'content': response,
            'timestamp': datetime.now()
        })
        
        # Extract data from user input
        extract_customer_data(user_input)
        
        # Rerun to update UI
        st.rerun()
    
    # Data collection helper buttons
    if st.session_state.loan_status == "sales":
        st.markdown("### 📝 Quick Input (Optional)")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Holiday Loan", use_container_width=True):
                st.session_state.conversation.append({
                    'type': 'user',
                    'content': "I need a loan for holiday travel",
                    'timestamp': datetime.now()
                })
                st.rerun()
        with col2:
            if st.button("Marriage Loan", use_container_width=True):
                st.session_state.conversation.append({
                    'type': 'user',
                    'content': "I need a loan for marriage",
                    'timestamp': datetime.now()
                })
                st.rerun()
        with col3:
            if st.button("Medical Loan", use_container_width=True):
                st.session_state.conversation.append({
                    'type': 'user',
                    'content': "I need a loan for medical expenses",
                    'timestamp': datetime.now()
                })
                st.rerun()
    
    # Reset conversation
    if st.button("Start New Application"):
        st.session_state.conversation = []
        st.session_state.current_agent = "Master"
        st.session_state.customer_data = {}
        st.session_state.loan_status = "initial"
        st.session_state.approved_loan = {}
        st.rerun()

def extract_customer_data(user_input):
    """Extract and store customer data from user input"""
    input_lower = user_input.lower()
    
    # Extract name (simple heuristic)
    if st.session_state.customer_data.get('name') is None and len(user_input.split()) >= 2:
        # If it looks like a name and we don't have one yet
        if not any(word in input_lower for word in ['loan', 'amount', 'purpose', 'income', 'salary', 'self']):
            st.session_state.customer_data['name'] = user_input.title()
    
    # Extract loan amount
    if 'loan_amount' not in st.session_state.customer_data:
        if '₹' in user_input or 'rs' in input_lower or 'inr' in input_lower:
            words = user_input.split()
            for i, word in enumerate(words):
                if word.replace(',', '').isdigit() and int(word.replace(',', '')) > 10000:
                    st.session_state.customer_data['loan_amount'] = int(word.replace(',', ''))
                    break
    
    # Extract purpose
    if 'purpose' not in st.session_state.customer_data:
        purposes = ['holiday', 'travel', 'marriage', 'wedding', 'medical', 'treatment', 'home', 'renovation', 'education']
        for purpose in purposes:
            if purpose in input_lower:
                st.session_state.customer_data['purpose'] = purpose
                break
    
    # Extract employment type
    if 'employment' not in st.session_state.customer_data:
        if 'salaried' in input_lower:
            st.session_state.customer_data['employment'] = 'salaried'
        elif 'self' in input_lower:
            st.session_state.customer_data['employment'] = 'self_employed'
    
    # Extract income
    if 'monthly_income' not in st.session_state.customer_data:
        words = user_input.split()
        for i, word in enumerate(words):
            if word.replace(',', '').isdigit() and 10000 <= int(word.replace(',', '')) <= 500000:
                if i > 0 and words[i-1].lower() in ['income', 'salary', 'earning', 'monthly']:
                    st.session_state.customer_data['monthly_income'] = int(word.replace(',', ''))
                elif len([w for w in words if w.lower() in ['income', 'salary', 'monthly']]) > 0:
                    st.session_state.customer_data['monthly_income'] = int(word.replace(',', ''))
    
    # Extract city
    if 'city' not in st.session_state.customer_data and len(user_input.split()) <= 3:
        # Simple city detection
        cities = ['mumbai', 'delhi', 'bangalore', 'chennai', 'kolkata', 'hyderabad', 'pune', 'ahmedabad']
        for city in cities:
            if city in input_lower:
                st.session_state.customer_data['city'] = user_input.title()
                break
        else:
            # If it's a short input and doesn't contain numbers, assume it's a city
            if len(user_input) > 2 and not any(char.isdigit() for char in user_input):
                st.session_state.customer_data['city'] = user_input.title()
    
    # Extract KYC details
    if st.session_state.loan_status == "kyc":
        # PAN (typically 10 characters, alphanumeric)
        if 'pan_number' not in st.session_state.customer_data and len(user_input.replace(' ', '')) == 10:
            if user_input.replace(' ', '').isalnum():
                st.session_state.customer_data['pan_number'] = user_input.upper()
        
        # Aadhaar (typically 12 digits)
        if 'aadhaar_number' not in st.session_state.customer_data and len(user_input.replace(' ', '')) == 12:
            if user_input.replace(' ', '').isdigit():
                st.session_state.customer_data['aadhaar_number'] = user_input
        
        # Phone number (10 digits)
        if 'phone_number' not in st.session_state.customer_data and len(user_input.replace(' ', '')) == 10:
            if user_input.replace(' ', '').isdigit():
                st.session_state.customer_data['phone_number'] = user_input
        
        # Email (contains @ and .)
        if 'email' not in st.session_state.customer_data and '@' in user_input and '.' in user_input:
            st.session_state.customer_data['email'] = user_input

if __name__ == "__main__":
    main()
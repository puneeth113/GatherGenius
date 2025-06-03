import gradio as gr
import datetime
import spacy
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Define FAQs and intents
faqs = {
    "What types of events do you manage?": "We manage weddings, corporate events, birthday parties, and more.",
    
    "Do you offer catering services?": "Yes, we provide a range of catering services tailored to your event.",
    
    "Can you help with event decoration?": "Absolutely! Our team specializes in creative event decor solutions.",
    
    "Do you offer on-site event coordination?": "Yes, we have experienced coordinators for smooth event execution.",
    
    "Can you provide audio/visual equipment?": "Yes, A/V equipment can be arranged on request.",
    
    "How do you manage event budgets?": "We offer tools to create, track, and optimize budgets, notifying you if expenses exceed your plan.",
    
    "Can you create an event schedule?": "We provide tailored timelines to ensure all tasks are completed on schedule.",
    
    "How do you handle guest management?": "We manage guest lists, send invitations, track RSVPs, and provide follow-up reminders.",
    
    "Do you provide support during the event?": "We offer real-time assistance to coordinate vendors and address issues during your event.",
    
    "Can you organize virtual or hybrid events?": "We assist with platform selection and technical setup for virtual or hybrid events.",
    
    "How do you personalize my event?": "We tailor recommendations for decor, entertainment, and more based on your preferences.",
    
    "Is support available 24/7 for planning?": "We provide round-the-clock assistance for all your event planning needs."
}


faq_questions = list(faqs.keys())

# Setup Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("GatherGenius.json", scope)
client = gspread.authorize(creds)
sheet = client.open("EventLeads").sheet1

# NLP matcher
def match_question(user_input):
    user_doc = nlp(user_input.lower())
    best_match = None
    best_score = 0
    for question, answer in faqs.items():
        faq_doc = nlp(question.lower())
        score = user_doc.similarity(faq_doc)
        if score > best_score:
            best_score = score
            best_match = question
    return faqs.get(best_match, "Sorry, I didn't understand that. Please ask something related to events.")

# Handle hybrid input
def handle_faq(manual_input, dropdown_input):
    question = manual_input if manual_input.strip() else dropdown_input
    if not question:
        return "Please ask a question or select one from the dropdown."
    return match_question(question)

# Handle lead data
def handle_event_lead(name, email, phone, event_type, budget, event_date):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([name, email, phone, event_type, budget, event_date, timestamp])
    return f"Thanks, {name}! We've received your event details."

# Gradio UI
with gr.Blocks(title="EventBot") as demo:
    gr.Markdown("##  Ask a Question About Our Event Services")
    with gr.Row():
        manual_input = gr.Textbox(placeholder="Type your question...", label="Your Question")
        dropdown_input = gr.Dropdown(choices=faq_questions, label="Or Select a Question")

    faq_button = gr.Button("Get Answer")
    faq_output = gr.Textbox(label="Bot Answer")

    faq_button.click(fn=handle_faq, inputs=[manual_input, dropdown_input], outputs=faq_output)

    gr.Markdown("---")
    gr.Markdown("##  Tell Us About Your Event")
    with gr.Column():
        name = gr.Textbox(label="Full Name")
        email = gr.Textbox(label="Email")
        phone = gr.Textbox(label="Phone Number")
        event_type = gr.Textbox(label="Type of Event")
        budget = gr.Textbox(label="Budget")
        event_date = gr.Textbox(label="Event Date (YYYY-MM-DD)")

    submit_button = gr.Button("Submit Event Details")
    submission_status = gr.Textbox(label="Status")

    submit_button.click(fn=handle_event_lead,
                        inputs=[name, email, phone, event_type, budget, event_date],
                        outputs=submission_status)

demo.launch()


import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from textblob import TextBlob
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pandas as pd

os.environ["GOOGLE_API_KEY"] = "AIzaSyDeCfka3goQtaqdQFQ6IDW2qkdneps-Otw"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "preferences" not in st.session_state:
    st.session_state.preferences = {}
if "user_sessions" not in st.session_state:
    st.session_state.user_sessions = {}

def analyze_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity  

def sentiment_label(score):
    if score > 0.1:
        return "Positive"
    elif score < -0.1:
        return "Negative"
    else:
        return "Neutral"

def get_response(user_query, chat_history, bot_type, temperature, max_tokens, language="en"):
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=None,
        max_retries=2,
    )

    if bot_type == "Chef":
        system_message = """You are a professional Chef AI, specializing in cooking recipes and culinary advice.
                           You only respond to questions related to cooking. If a question is not about cooking, politely inform the user that you cannot answer it."""
    elif bot_type == "Teacher":
        system_message = """You are an expert Teacher AI with knowledge across various subjects. You should only respond to questions related to education and teaching. Do not answer any unrelated queries."""
    elif bot_type == "Nutritionist":
        system_message = """You are a professional Nutritionist AI. You provide advice about healthy eating, nutrition, and related topics. Do not answer questions outside of this domain."""
    elif bot_type == "Hr":
        system_message = """You are an HR consultant AI, assisting users with job interview preparation, resume advice, and related topics. Do not answer questions unrelated to HR and employment matters."""
    elif bot_type == "Custom" and st.session_state.custom_system_message:
        system_message = st.session_state.custom_system_message

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_message),
            ("human", "{input}"),
        ]
    )

    user_query = f"Translate response to {language}. {user_query}"

    chain = prompt | llm | StrOutputParser()
    return chain.stream(
        {
            "history": chat_history,
            "input": user_query,
        }
    )

st.set_page_config(page_title="Multi-Chatbot App", page_icon="🤖")
st.title("Multi-Chatbot App")

with st.sidebar:
    st.header("Choose a Chatbot")
    bot_choice = st.selectbox("Select a bot:", ["Chef", "Teacher", "Nutritionist", "Hr", "Custom"])

    temperature = st.slider("Creativity Level (Temperature):", 0.0, 1.0, 0.5)
    max_tokens = st.slider("Response Length (Max Tokens):", 50, 1000, 256)

    language = st.selectbox("Select Response Language:", ["en", "es", "fr", "de"])

    custom_bot = st.checkbox("Custom Bot")
    if custom_bot:
        st.session_state.custom_system_message = st.text_area("Enter custom system message for the bot:")
        bot_choice = "Custom"

    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.success("Chat history cleared!")


    if st.button("Download Conversation (PDF)"):
        conversation = "\n".join([f"Human: {msg.content}" if isinstance(msg, HumanMessage) else f"AI: {msg.content}" for msg in st.session_state.chat_history])
        if conversation:
            pdf_file = "chat_history.pdf"
            c = canvas.Canvas(pdf_file, pagesize=letter)
            width, height = letter
            c.setFont("Helvetica", 12)
            y = height - 40
            for line in conversation.split("\n"):
                c.drawString(40, y, line)
                y -= 20
                if y < 40:
                    c.showPage()
                    c.setFont("Helvetica", 12)
                    y = height - 40
            c.save()
            with open(pdf_file, "rb") as f:
                st.download_button(label="Download PDF", data=f, file_name=pdf_file, mime="application/pdf")
        else:
            st.warning("No conversation history available to create a PDF.")

    if st.button("Download Conversation (CSV)"):
        conversation_data = [{"User": msg.content if isinstance(msg, HumanMessage) else "", "Bot": msg.content if isinstance(msg, AIMessage) else ""} for msg in st.session_state.chat_history]
        df = pd.DataFrame(conversation_data)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(label="Download CSV", data=csv, file_name="chat_history.csv", mime="text/csv")


for message in st.session_state.chat_history:
    if isinstance(message, HumanMessage):
        sentiment = analyze_sentiment(message.content)
        with st.chat_message("Human"):
            st.markdown(f"{message.content} (Sentiment: {sentiment_label(sentiment)})")
    else:
        with st.chat_message("AI"):
            st.markdown(message.content)

user_query = st.chat_input("Your message")
if user_query:
    st.session_state.chat_history.append(HumanMessage(user_query))

    with st.chat_message("Human"):
        st.markdown(user_query)

    with st.chat_message("AI"):
        message_placeholder = st.empty()
        full_response = ""

        for chunk in get_response(user_query, st.session_state.chat_history, bot_choice, temperature, max_tokens, language):
            full_response += chunk
            message_placeholder.markdown(full_response)

        st.session_state.chat_history.append(AIMessage(full_response))

with st.expander("Chatbot Analytics Dashboard"):
    total_chats = len(st.session_state.chat_history)
    avg_sentiment = sum(analyze_sentiment(msg.content) for msg in st.session_state.chat_history if isinstance(msg, HumanMessage)) / max(len(st.session_state.chat_history), 1)
    st.write("Total Chat Sessions:", total_chats)
    st.write("Average Sentiment Score:", avg_sentiment)







# import streamlit as st
# from langchain_core.messages import HumanMessage, AIMessage
# import os
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.output_parsers import StrOutputParser
# from textblob import TextBlob
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
# import pandas as pd

# os.environ["GOOGLE_API_KEY"] = "AIzaSyDeCfka3goQtaqdQFQ6IDW2qkdneps-Otw"

# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []
# if "preferences" not in st.session_state:
#     st.session_state.preferences = {}
# if "user_sessions" not in st.session_state:
#     st.session_state.user_sessions = {}

# def analyze_sentiment(text):
#     blob = TextBlob(text)
#     return blob.sentiment.polarity  

# def sentiment_label(score):
#     if score > 0.1:
#         return "Positive"
#     elif score < -0.1:
#         return "Negative"
#     else:
#         return "Neutral"

# def is_irrelevant_query(query, bot_type):
#     # Define topics that are relevant to each bot
#     relevant_queries = {
#     "Chef": [
#     # Recipe and cooking-related keywords
#     "recipe", "greetings", "hi", "cooking", "ingredient", "meal", "food", "dish", "kitchen", "cuisine", "flavor", "taste", "spices",
#     "herbs", "seasoning", "marinate", "sauce", "gravy", "snack", "appetizer", "main course", "dessert", "beverage",
#     "baking", "roasting", "grilling", "frying", "steaming", "boiling", "broiling", "simmering", "sauteing",
#     "stir-frying", "slow cooking", "pressure cooking", "microwave", "oven", "stove", "pan", "pot", "knife",
#     "chopping", "cutting", "slicing", "dicing", "peeling", "mixing", "whisking", "blending", "pureeing", "kneading",

#     # Specific foods and ingredients
#     "vegetable", "fruit", "meat", "fish", "chicken", "beef", "pork", "lamb", "seafood", "egg", "cheese", "milk",
#     "butter", "cream", "yogurt", "rice", "bread", "pasta", "noodle", "flour", "sugar", "salt", "pepper", "chili",
#     "garlic", "onion", "ginger", "tomato", "potato", "carrot", "broccoli", "spinach", "cabbage", "corn", "beans",
#     "lentils", "oil", "vinegar", "soy sauce", "honey", "lemon", "lime", "coconut", "nuts", "seeds", "spice mix",
    
#     # Processes and techniques
#     "boil", "bake", "grill", "fry", "steam", "roast", "poach", "ferment", "pickle", "preserve", "dehydrate",
#     "smoke", "caramelize", "blend", "whip", "fold", "temper", "chill", "cool", "freeze", "melt", "infuse",
#     "reduce", "thicken", "strain", "sieve", "coat", "glaze", "decorate", "season", "garnish", "plate", "serve",

#     # Types of dishes
#     "soup", "stew", "curry", "salad", "sandwich", "burger", "pizza", "pasta", "risotto", "pie", "cake", "cookie",
#     "brownie", "pancake", "waffle", "ice cream", "sorbet", "juice", "smoothie", "cocktail", "mocktail",
#     "sauce", "dip", "spread", "jam", "jelly", "condiment", "broth", "stock", "marinade", "glaze", "dressing",

#     # Specific cuisines
#     "Indian", "Chinese", "Italian", "Mexican", "Thai", "Japanese", "Mediterranean", "French", "American",
#     "Korean", "Spanish", "Middle Eastern", "Vietnamese", "Greek", "Caribbean", "African", "Turkish", "Moroccan",

#     # Others
#     "chef", "cook", "kitchen tip", "cooking method", "recipe ideas", "meal prep", "food storage", "food safety",
#     "quick recipe", "easy recipe", "healthy recipe", "vegetarian", "vegan", "gluten-free", "low-carb", "high-protein",
#     "comfort food", "gourmet", "fusion cuisine", "home-cooked", "traditional", "authentic", "flavor profile"
#     ],

#     "Teacher": [
#     # General teaching-related keywords
#     "homework", "greetings", "hi", "school", "study", "lesson", "exam", "subject", "education", "classroom", "teacher", "student",
#     "syllabus", "curriculum", "teaching", "learning", "quiz", "test", "assignment", "project", "presentation",
#     "lecture", "grading", "marks", "topics", "lesson plan", "revision", "practice", "concept", "theory",
#     "experiment", "lab", "research", "science", "math", "history", "geography", "language", "reading", "writing",
    
#     # Math-specific terms
#     "algebra", "geometry", "calculus", "trigonometry", "arithmetic", "equation", "formula", "graph", "derivative",
#     "integral", "statistics", "probability", "logarithm", "mean", "median", "mode", "circle", "triangle", "area",
#     "volume", "perimeter", "angle", "slope", "matrix", "vector", "coordinate", "quadratic", "factorization",

#     # Science and chemical topics
#     "physics", "chemistry", "biology", "atom", "molecule", "reaction", "chemical equation", "periodic table",
#     "compound", "element", "bond", "acid", "base", "pH", "oxidation", "reduction", "organic", "inorganic",
#     "photosynthesis", "cell", "DNA", "genetics", "evolution", "force", "motion", "energy", "gravity", "momentum",
#     "electricity", "magnetism", "optics", "waves", "light", "sound", "radiation", "nuclear", "thermodynamics",

#     # Other academic topics
#     "computer science", "coding", "programming", "algorithm", "data structure", "history", "culture", "economics",
#     "government", "civics", "environment", "ecology", "climate", "literature", "poetry", "prose", "grammar",
#     "syntax", "vocabulary", "trignometry","foreign language", "translation", "philosophy", "logic", "art", "music", "sports"
#     ],

#     "Nutritionist": [
#     # Core Nutrition Topics
#     "nutrition", "diet", "greetings", "hi", "calories", "health", "vitamin", "meal plan", "macronutrient", "micronutrient", "protein",
#     "carbohydrate", "fats", "fiber", "minerals", "water", "hydration", "antioxidants", "omega-3", "omega-6", "amino acid",
#     "probiotic", "prebiotic", "metabolism", "digestion", "absorption", "immune system", "hormonal balance", "enzymes",

#     # Diet Types
#     "keto diet", "paleo diet", "vegan diet", "vegetarian diet", "low-carb diet", "high-protein diet", "Mediterranean diet",
#     "DASH diet", "flexitarian diet", "gluten-free diet", "low-fat diet", "weight loss", "weight gain", "dietary restriction",
#     "intermittent fasting", "detox diet", "balanced diet", "heart-healthy diet", "diabetic diet", "plant-based diet",
#     "anti-inflammatory diet", "raw food diet", "macrobiotic diet", "clean eating", "whole30", "meal replacement",

#     # Health Conditions and Diet
#     "diabetes", "hypertension", "cholesterol", "obesity", "weight management", "IBS", "gut health", "thyroid",
#     "anemia", "osteoporosis", "pregnancy nutrition", "lactation nutrition", "child nutrition", "sports nutrition",
#     "PCOS", "autoimmune disease", "cancer nutrition", "liver health", "kidney health", "heart health", "brain health",

#     # Foods and Nutrients
#     "superfood", "fruits", "vegetables", "nuts", "seeds", "grains", "legumes", "dairy", "meat", "fish", "poultry",
#     "eggs", "tofu", "tempeh", "soy", "chia seeds", "flaxseeds", "quinoa", "oats", "whole grains", "spinach", "kale",
#     "broccoli", "berries", "apple", "banana", "orange", "avocado", "salmon", "chicken breast", "almond", "walnut",

#     # Vitamins and Supplements
#     "vitamin A", "vitamin B", "vitamin C", "vitamin D", "vitamin E", "vitamin K", "magnesium", "zinc", "calcium",
#     "iron", "potassium", "sodium", "iodine", "selenium", "copper", "folate", "niacin", "riboflavin", "thiamine",
#     "biotin", "choline", "dietary supplement", "multivitamin", "protein powder", "collagen", "fish oil", "fiber supplement",

#     # Meal Planning and Tips
#     "meal prep", "portion control", "healthy snack", "low-sodium meal", "sugar-free", "low-calorie", "high-energy food",
#     "low GI food", "high GI food", "organic food", "GMOs", "processed food", "junk food", "sustainable eating",
#     "food label", "reading labels", "nutritional value", "calorie count", "meal timing", "pre-workout meal",
#     "post-workout meal", "food pyramid", "balanced plate", "mindful eating", "emotional eating", "food allergy"
#     ],

#     "HR": [
#     # Core HR Functions
#     "interview", "resume", "greetings", "hi", "job", "career", "application", "salary", "recruitment", "onboarding", "offboarding",
#     "training", "development", "employee", "employer", "performance", "management", "evaluation", "feedback",
#     "appraisal", "promotion", "retention", "resignation", "termination", "exit interview", "payroll", "benefits",

#     # Policies and Legal
#     "HR policy", "compliance", "labor law", "workplace", "diversity", "inclusion", "harassment", "discrimination",
#     "code of conduct", "confidentiality", "workplace safety", "disciplinary action", "grievance", "employee rights",
#     "leave policy", "vacation", "sick leave", "maternity leave", "paternity leave", "equal opportunity", "ethics",

#     # Recruitment and Hiring
#     "talent acquisition", "headhunting", "job description", "job posting", "candidate screening", "selection",
#     "reference check", "interview question", "job offer", "negotiation", "background check", "skills assessment",
#     "aptitude test", "psychometric test", "internship", "freelancer", "contractor", "full-time", "part-time",
#     "remote work", "hybrid work", "gig economy",

#     # Employee Engagement and Culture
#     "team building", "motivation", "recognition", "reward", "workplace culture", "collaboration", "conflict resolution",
#     "employee satisfaction", "work-life balance", "engagement survey", "communication", "leadership", "mentoring",
#     "coaching", "teamwork", "diversity initiative", "innovation", "employee morale", "inclusive workplace",

#     # HR Tools and Technology
#     "HR software", "HRIS", "HRMS", "payroll software", "performance management software", "LMS", "ATS",
#     "employee portal", "self-service portal", "HR analytics", "data-driven HR", "workforce planning", "succession planning",
#     "time tracking", "attendance", "shift scheduling", "job board", "LinkedIn", "Indeed", "Glassdoor", "HR metrics",

#     # Other HR Topics
#     "compensation", "reward strategy", "incentive", "career development", "succession planning", "organizational design",
#     "change management", "employer branding", "HR trends", "remote hiring", "cybersecurity", "emotional intelligence",
#     "confidentiality agreement", "job satisfaction", "personal development", "health and wellness", "HR audit", "workforce"
#     ],

#     "Custom": []  # Add relevant keywords based on your custom role
# }


#     relevant_keywords = relevant_queries.get(bot_type, [])

#     # Check if any of the relevant keywords are in the query
#     if any(keyword.lower() in query.lower() for keyword in relevant_keywords):
#         return False  # Query is relevant
#     else:
#         return True  # Query is irrelevant

# def get_response(user_query, chat_history, bot_type, temperature, max_tokens, language="en"):
#     llm = ChatGoogleGenerativeAI(
#         model="gemini-1.5-pro",
#         temperature=temperature,
#         max_tokens=max_tokens,
#         timeout=None,
#         max_retries=2,
#     )

#     if bot_type == "Chef":
#         system_message = """You are a professional Chef AI, specializing in cooking recipes and culinary advice.
#                            You only respond to questions related to cooking. If a question is not about cooking, politely inform the user that you cannot answer it."""
#     elif bot_type == "Teacher":
#         system_message = """You are an expert Teacher AI with knowledge across various subjects. You should only respond to questions related to education and teaching. Do not answer any unrelated queries."""
#     elif bot_type == "Nutritionist":
#         system_message = """You are a professional Nutritionist AI. You provide advice about healthy eating, nutrition, and related topics. Do not answer questions outside of this domain."""
#     elif bot_type == "Hr":
#         system_message = """You are an HR consultant AI, assisting users with job interview preparation, resume advice, and related topics. Do not answer questions unrelated to HR and employment matters."""
#     elif bot_type == "Custom" and st.session_state.custom_system_message:
#         system_message = st.session_state.custom_system_message

#     prompt = ChatPromptTemplate.from_messages(
#         [
#             ("system", system_message),
#             ("human", "{input}"),
#         ]
#     )

#     user_query = f"Translate response to {language}. {user_query}"

#     chain = prompt | llm | StrOutputParser()
#     return chain.stream(
#         {
#             "history": chat_history,
#             "input": user_query,
#         }
#     )

# st.set_page_config(page_title="Multi-Chatbot App", page_icon="🤖")
# st.title("Multi-Chatbot App")

# with st.sidebar:
#     st.header("Choose a Chatbot")
#     bot_choice = st.selectbox("Select a bot:", ["Chef", "Teacher", "Nutritionist", "Hr", "Custom"])

#     temperature = st.slider("Creativity Level (Temperature):", 0.0, 1.0, 0.5)
#     max_tokens = st.slider("Response Length (Max Tokens):", 50, 1000, 256)

#     language = st.selectbox("Select Response Language:", ["en", "es", "fr", "de"])

#     custom_bot = st.checkbox("Custom Bot")
#     if custom_bot:
#         st.session_state.custom_system_message = st.text_area("Enter custom system message for the bot:")
#         bot_choice = "Custom"

#     if st.button("Clear Chat History"):
#         st.session_state.chat_history = []
#         st.success("Chat history cleared!")

#     if st.button("Download Conversation (PDF)"):
#         conversation = "\n".join([f"Human: {msg.content}" if isinstance(msg, HumanMessage) else f"AI: {msg.content}" for msg in st.session_state.chat_history])
#         if conversation:
#             pdf_file = "chat_history.pdf"
#             c = canvas.Canvas(pdf_file, pagesize=letter)
#             width, height = letter
#             c.setFont("Helvetica", 12)
#             y = height - 40
#             for line in conversation.split("\n"):
#                 c.drawString(40, y, line)
#                 y -= 20
#                 if y < 40:
#                     c.showPage()
#                     c.setFont("Helvetica", 12)
#                     y = height - 40
#             c.save()
#             with open(pdf_file, "rb") as f:
#                 st.download_button(label="Download PDF", data=f, file_name=pdf_file, mime="application/pdf")
#         else:
#             st.warning("No conversation history available to create a PDF.")

#     if st.button("Download Conversation (CSV)"):
#         conversation_data = [{"User": msg.content if isinstance(msg, HumanMessage) else "", "Bot": msg.content if isinstance(msg, AIMessage) else ""} for msg in st.session_state.chat_history]
#         df = pd.DataFrame(conversation_data)
#         csv = df.to_csv(index=False).encode('utf-8')
#         st.download_button(label="Download CSV", data=csv, file_name="chat_history.csv", mime="text/csv")

# for message in st.session_state.chat_history:
#     if isinstance(message, HumanMessage):
#         sentiment = analyze_sentiment(message.content)
#         with st.chat_message("Human"):
#             st.markdown(f"{message.content} (Sentiment: {sentiment_label(sentiment)})")
#     else:
#         with st.chat_message("AI"):
#             st.markdown(message.content)

# user_query = st.chat_input("Your message")
# if user_query:
#     st.session_state.chat_history.append(HumanMessage(user_query))

#     with st.chat_message("Human"):
#         st.markdown(user_query)

#     with st.chat_message("AI"):
#         message_placeholder = st.empty()
#         full_response = ""

#         # Check if the query is irrelevant before processing
#         if is_irrelevant_query(user_query, bot_choice):
#             # Show an irrelevant query message and don't proceed
#             message_placeholder.markdown(f"Sorry, but your question seems irrelevant to my role as a {bot_choice}. Please ask me something related to {bot_choice.lower()}.")
#         else:
#             # Get response based on bot choice and the user's input
#             response = get_response(user_query, st.session_state.chat_history, bot_choice, temperature, max_tokens, language)
#             for chunk in response:
#                 full_response += chunk
#                 message_placeholder.markdown(full_response)

#             # Append response to chat history
#             st.session_state.chat_history.append(AIMessage(full_response))

# with st.expander("Chatbot Analytics Dashboard"):
#     total_chats = len(st.session_state.chat_history)
#     avg_sentiment = sum(analyze_sentiment(msg.content) for msg in st.session_state.chat_history if isinstance(msg, HumanMessage)) / max(len(st.session_state.chat_history), 1)
#     st.write("Total Chat Sessions:", total_chats)
#     st.write("Average Sentiment Score:", avg_sentiment)

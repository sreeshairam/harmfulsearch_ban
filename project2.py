import sqlite3
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Download NLTK resources (only required once)
nltk.download('punkt')
nltk.download('stopwords')

# Define harmful keywords
banned_keywords = {"kill", "murder", "terror", "attack", "violence", "suicide", "blood", "horror", "porn"}

# Connect to SQLite database
def init_db():
    conn = sqlite3.connect("flagged_content.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flagged (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            reason TEXT
        )
    """)
    conn.commit()
    conn.close()

# Function to clean and tokenize input
def preprocess_text(text):
    text = text.lower()
    words = word_tokenize(text)
    words = [word for word in words if word.isalnum()]
    words = [word for word in words if word not in stopwords.words('english')]
    return words

# Function to check content for harmful words
def check_content(text):
    words = set(preprocess_text(text))
    flagged_words = words.intersection(banned_keywords)
    
    # Allow if "prevent" or its synonyms are present
    safe_words = {"prevent", "avoid", "stop", "protect"}
    if any(word in words for word in safe_words):
        return "Content is safe."
    
    if flagged_words:
        store_flagged_content(text, ", ".join(flagged_words))
        return f"Content blocked! Found harmful words: {', '.join(flagged_words)}"
    return "Content is safe."

# Function to store flagged content in the database
def store_flagged_content(text, reason):
    conn = sqlite3.connect("flagged_content.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO flagged (content, reason) VALUES (?, ?)", (text, reason))
    conn.commit()
    conn.close()

# Main execution
if __name__ == "__main__":
    init_db()
    user_input = input("Enter content to check: ")
    result = check_content(user_input)
    print(result)

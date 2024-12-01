from flask import Flask, request, jsonify
from flask_cors import CORS
import spacy
from textblob import TextBlob
import math
from spacy.lang.en.stop_words import STOP_WORDS
import nltk

nltk.data.path.append(os.path.join(os.getcwd(), "nltk_data"))



# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Use spaCy's built-in stopwords
stop_words = set(STOP_WORDS)

# Define initial categories with keywords and patterns
CATEGORIES = {
    "Glorification of a Past Golden Age": {
    "keywords": [
        {"word": "centuries", "weight": 2.0},  # Strong frequency (62)
        {"word": "bourgeoisie", "weight": 1.5},  # Moderate frequency (25)
        {"word": "restore", "weight": 2.5},  # Relevant and moderate frequency (26)
        {"word": "bourgeois", "weight": 1.5},  # Moderate frequency (37)
        {"word": "historical", "weight": 2.0},  # Strong frequency (68)
        {"word": "history", "weight": 2.5},  # Very high frequency (123)
        {"word": "tradition", "weight": 2.0},  # Moderate frequency (43)
        {"word": "cultural", "weight": 1.5},  # Moderate frequency (36)
        {"word": "past glory", "weight": 3.0},  # Highly relevant despite low frequency (0)
        {"word": "sacred", "weight": 2.0},  # Strong frequency (56)
        {"word": "heritage", "weight": 2.5},  # Relevant despite low frequency (8)
        {"word": "soul", "weight": 2.0}  # Moderate frequency (60)
    ],
    "patterns": [
        {"phrase": "return to greatness", "weight": 3.0},  # Highly indicative
        {"phrase": "revive the past", "weight": 3.0},  # Highly indicative
        {"phrase": "restore our tradition", "weight": 3.0}  # Highly indicative
    ]
},
   "Us vs. Them Mentality": {
    "keywords": [
        {"word": "fatherland", "weight": 2.5},  # High frequency (79)
        {"word": "assembly", "weight": 1.5},  # Moderate frequency (31)
        {"word": "class", "weight": 2.0},  # Strong frequency (82)
        {"word": "socalled", "weight": 1.5},  # Moderate frequency (57)
        {"word": "regime", "weight": 2.0},  # Strong frequency (70)
        {"word": "victory", "weight": 2.5},  # Very strong frequency (109)
        {"word": "cannot", "weight": 2.0},  # Very strong frequency (106)
        {"word": "struggle", "weight": 2.5},  # High frequency (79)
        {"word": "peasants", "weight": 1.0},  # Low frequency (21)
        {"word": "perhaps", "weight": 1.5},  # Moderate frequency (78)
        {"word": "soldier", "weight": 2.5},  # Strong frequency (89)
        {"word": "threat", "weight": 3.0},  # Critical term, moderate frequency (51)
        {"word": "soldiers", "weight": 2.5},  # Strong frequency (72)
        {"word": "fought", "weight": 2.0},  # Moderate frequency (62)
        {"word": "victorious", "weight": 2.0},  # Moderate frequency (42)
        {"word": "empire", "weight": 2.5},  # Strong frequency (64)
        {"word": "comrade", "weight": 2.5},  # Strong frequency (91)
        {"word": "solidarity", "weight": 2.0},  # Moderate frequency (36)
        {"word": "council", "weight": 1.0},  # Low frequency (35)
        {"word": "bourgeois", "weight": 1.5},  # Moderate frequency (37)
        {"word": "party", "weight": 2.0},  # Strong frequency (89)
        {"word": "workers", "weight": 1.5},  # Moderate frequency (58)
        {"word": "ideological", "weight": 1.0},  # Low frequency (14)
        {"word": "regards", "weight": 1.0},  # Low frequency (38)
        {"word": "outsider", "weight": 3.0},  # Critical term, no direct count but key to category
        {"word": "enemy", "weight": 3.5},  # Critical term, strong frequency (68)
        {"word": "league", "weight": 1.5},  # Moderate frequency (47)
        {"word": "towards", "weight": 1.5},  # Moderate frequency (84)
        {"word": "army", "weight": 2.5},  # Strong frequency (73)
        {"word": "traitor", "weight": 3.0},  # Critical term, moderate frequency (23)
        {"word": "opposition", "weight": 2.5},  # Critical term, moderate frequency (32)
        {"word": "front", "weight": 2.0},  # Strong frequency (85)
        {"word": "situation", "weight": 2.0},  # Strong frequency (79)
        {"word": "ranks", "weight": 1.5},  # Moderate frequency (37)
        {"word": "partys", "weight": 1.0},  # Low frequency (14)
        {"word": "bolshevism", "weight": 1.5},  # Moderate frequency (26)
        {"word": "division", "weight": 2.0},  # Strong frequency (45)
        {"word": "elements", "weight": 1.5},  # Moderate frequency (55)
        {"word": "discipline", "weight": 2.0},  # Strong frequency (77)
        {"word": "fight", "weight": 3.0},  # Critical term, very high frequency (115)
        {"word": "decisive", "weight": 2.0},  # Strong frequency (46)
        {"word": "comrades", "weight": 2.5},  # Strong frequency (83)
        {"word": "bourgeoisie", "weight": 1.5},  # Moderate frequency (25)
        {"word": "movement", "weight": 2.0}  # Strong frequency (75)
    ],
    "patterns": [
        {"phrase": "divide and conquer", "weight": 3.5},  # Highly indicative
        {"phrase": "fight against them", "weight": 3.5},  # Highly indicative
        {"phrase": "threat to our way of life", "weight": 3.5},  # Highly indicative
        {"phrase": "youth league", "weight": 1.0},  # Strong relevance
        {"phrase": "first place", "weight": 2.0},  # Moderate relevance
        {"phrase": "workers peasants", "weight": 2.5}  # Strong relevance
    ]
    },
    "Cult of Personality": {
    "keywords": [
        {"word": "fatherland", "weight": 2.5},  # High frequency (79)
        {"word": "leader", "weight": 3.5},  # Strong indicator and frequency (72)
        {"word": "wish", "weight": 2.0},  # Moderate frequency (99)
        {"word": "only I", "weight": 4.0},  # Highly relevant despite low frequency (0)
        {"word": "truly", "weight": 1.5},  # Moderate frequency (53)
        {"word": "spiritual", "weight": 1.5},  # Moderate frequency (52)
        {"word": "idea", "weight": 2.5},  # Strong frequency (103)
        {"word": "attitude", "weight": 1.5},  # Moderate frequency (59)
        {"word": "certainly", "weight": 1.5},  # Moderate frequency (71)
        {"word": "savior", "weight": 4.0},  # Highly relevant despite low frequency (0)
        {"word": "youth", "weight": 1.0},  # Moderate frequency (40)
        {"word": "sacred", "weight": 2.0},  # Strong frequency (56)
        {"word": "hero", "weight": 3.0},  # Strong frequency (72)
        {"word": "soul", "weight": 2.0}  # Moderate frequency (60)
    ],
    "patterns": [
        {"phrase": "I alone can fix it", "weight": 4.0},  # Highly indicative pattern
        {"phrase": "the chosen one", "weight": 3.5},  # Strong cult of personality indicator
        {"phrase": "worship our leader", "weight": 4.0},  # Strong relevance
        {"phrase": "one thing", "weight": 2.5}  # Moderate relevance
    ]
}, "Militarism or Violence": {
    "keywords": [
        {"word": "death penalty", "weight": 4.0},  # Very relevant despite low frequency (1)
        {"word": "victory", "weight": 3.0},  # High frequency (109)
        {"word": "struggle", "weight": 2.5},  # Moderate frequency (79)
        {"word": "dead", "weight": 2.0},  # Moderate frequency (57)
        {"word": "prolonged", "weight": 1.0},  # Low frequency (22)
        {"word": "destroy", "weight": 2.5},  # Moderate frequency (59)
        {"word": "crush", "weight": 3.0},  # Relevant due to militaristic tone (29)
        {"word": "soldier", "weight": 2.5},  # Strong frequency (89)
        {"word": "soldiers", "weight": 2.5},  # Strong frequency (72)
        {"word": "fought", "weight": 2.0},  # Moderate frequency (62)
        {"word": "victorious", "weight": 2.0},  # Moderate frequency (42)
        {"word": "empire", "weight": 2.5},  # Strong frequency (64)
        {"word": "comrade", "weight": 2.5},  # High frequency (91)
        {"word": "kill", "weight": 3.5},  # Militaristic relevance, moderate frequency (28)
        {"word": "force", "weight": 3.0},  # Very high frequency (132)
        {"word": "shouts", "weight": 1.0},  # Low frequency (26)
        {"word": "enemy", "weight": 3.5},  # Strong frequency (68)
        {"word": "blood", "weight": 3.0},  # Strong frequency (88)
        {"word": "army", "weight": 2.5},  # Strong frequency (73)
        {"word": "duce", "weight": 3.0},  # Strong frequency (90)
        {"word": "fight", "weight": 3.5},  # Very high frequency (115)
        {"word": "comrades", "weight": 2.5}, # Strong frequency (83)
        {"word": "army", "weight": 1.0}  
    ],
    "patterns": [
        {"phrase": "death penalty", "weight": 4.0},  # Highly relevant pattern
        {"phrase": "call for violence", "weight": 4.0},  # Militaristic tone
        {"phrase": "migrant kills", "weight": 3.5},  # Specific militaristic phrasing
        {"phrase": "with violence", "weight": 2.0} ,
        {"phrase": "arm the people", "weight": 2.0}
    ]
}, "Suppression of Dissent": {
    "keywords": [
        {"word": "technical", "weight": 1.0},  # Low frequency (22)
        {"word": "assembly", "weight": 1.5},  # Moderate frequency (31)
        {"word": "socalled", "weight": 1.5},  # Moderate frequency (57)
        {"word": "regime", "weight": 2.5},  # Strong frequency (70)
        {"word": "masses", "weight": 2.0},  # Strong frequency (58)
        {"word": "reactionary", "weight": 1.5},  # Moderate frequency (25)
        {"word": "peasants", "weight": 1.0},  # Low frequency (21)
        {"word": "ideology", "weight": 1.0},  # Low frequency (14)
        {"word": "prolonged", "weight": 1.0},  # Low frequency (22)
        {"word": "labour", "weight": 1.5},  # Moderate frequency (45)
        {"word": "revolution", "weight": 2.0},  # High frequency (101)
        {"word": "revolutionary", "weight": 1.5},  # Moderate frequency (36)
        {"word": "construction", "weight": 1.5},  # Moderate frequency (49)
        {"word": "solidarity", "weight": 1.5},  # Moderate frequency (36)
        {"word": "council", "weight": 1.0},  # Low frequency (35)
        {"word": "party", "weight": 2.0},  # Strong frequency (89)
        {"word": "reality", "weight": 1.5},  # Moderate frequency (57)
        {"word": "fake news", "weight": 4.0},  # Very relevant despite low frequency (1)
        {"word": "moral", "weight": 2.0},  # Strong frequency (97)
        {"word": "collaboration", "weight": 1.5},  # Moderate frequency (29)
        {"word": "unity", "weight": 2.5},  # Very high frequency (96)
        {"word": "shouts", "weight": 1.0},  # Low frequency (26)
        {"word": "intellectuals", "weight": 1.0},  # Low frequency (7)
        {"word": "front", "weight": 2.0},  # Strong frequency (85)
        {"word": "situation", "weight": 2.0},  # Strong frequency (79)
        {"word": "traitor", "weight": 2.0},  # Moderate frequency (23)
        {"word": "opposition", "weight": 2.0},  # Moderate frequency (32)
        {"word": "proletariat", "weight": 1.0},  # Low frequency (26)
        {"word": "organizations", "weight": 1.0},  # Low frequency (33)
        {"word": "partys", "weight": 1.0},  # Low frequency (14)
        {"word": "bolshevism", "weight": 1.5},  # Moderate relevance (26)
        {"word": "control", "weight": 2.0},  # Strong frequency (37)
        {"word": "duce", "weight": 3.0},  # Very high frequency (90)
        {"word": "imperialism", "weight": 1.5},  # Moderate frequency (25)
        {"word": "decisive", "weight": 1.5},  # Moderate frequency (46)
        {"word": "completely", "weight": 1.5},  # Moderate frequency (46)
        {"word": "silence", "weight": 3.5},  # Very relevant despite low frequency (12)
        {"word": "movement", "weight": 2.0},  # Strong frequency (75)
        {"word": "political", "weight": 2.5}  # Very high frequency (123)
    ],
    "patterns": [
        {"phrase": "shut them down", "weight": 4.0},
        {"phrase": "enemies of the people", "weight": 4.0},
        {"phrase": "ban opposition parties", "weight": 4.0},
        {"phrase": "general assembly", "weight": 2.0},
        {"phrase": "workers party", "weight": 2.5},
        {"phrase": "central committee", "weight": 2.0}
    ]
}, "Anti-Intellectualism": {
    "keywords": [
        {"word": "technical", "weight": 1.0},
        {"word": "class", "weight": 1.5},  # Increased based on frequency (82)
        {"word": "science", "weight": 2.0},  # Increased slightly due to its importance
        {"word": "cannot", "weight": 2.0},  # High frequency (106)
        {"word": "masses", "weight": 2.0},  # Reflects strong frequency (58)
        {"word": "attitude", "weight": 1.5},  # Moderate frequency (59)
        {"word": "ideology", "weight": 1.5},
        {"word": "intellectual", "weight": 2.0},  # Retain high weight due to direct relevance
        {"word": "labour", "weight": 1.0},
        {"word": "revolution", "weight": 2.0},  # Strong frequency (101)
        {"word": "revolutionary", "weight": 1.5},
        {"word": "construction", "weight": 1.5},  # Adjusted based on moderate frequency (49)
        {"word": "idea", "weight": 2.0},  # High frequency (103)
        {"word": "youth", "weight": 1.0},
        {"word": "collaboration", "weight": 1.5},
        {"word": "reality", "weight": 1.5},  # Adjusted due to moderate frequency (57)
        {"word": "moral", "weight": 2.0},  # Increased due to strong frequency (97)
        {"word": "workers", "weight": 2.0},  # Reflects frequency (58)
        {"word": "elite", "weight": 2.5},  # Keep high weight as a key indicator
        {"word": "ideological", "weight": 1.5},
        {"word": "unity", "weight": 2.0},  # Strong frequency (96)
        {"word": "regards", "weight": 1.0},
        {"word": "truly", "weight": 1.5},
        {"word": "spiritual", "weight": 1.5},
        {"word": "expert", "weight": 2.0},
        {"word": "history", "weight": 2.0},  # High frequency (123)
        {"word": "intellectuals", "weight": 2.0},
        {"word": "cultural", "weight": 1.5},
        {"word": "sphere", "weight": 1.5},  # Moderate frequency (55)
        {"word": "events", "weight": 1.5},  # Moderate frequency (68)
        {"word": "towards", "weight": 1.5},  # Moderate frequency (84)
        {"word": "ranks", "weight": 1.5},  # Moderate frequency (37)
        {"word": "proletariat", "weight": 1.5},  # Adjusted based on relevance (26)
        {"word": "socialists", "weight": 1.0},
        {"word": "centuries", "weight": 1.5},
        {"word": "organizations", "weight": 1.0},
        {"word": "truth", "weight": 2.5},  # High frequency (65)
        {"word": "elements", "weight": 1.5},  # Moderate frequency (55)
        {"word": "discipline", "weight": 2.0},  # High frequency (77)
        {"word": "education", "weight": 2.0},
        {"word": "imperialism", "weight": 1.0},
        {"word": "historical", "weight": 2.0},  # High frequency (68)
        {"word": "certainly", "weight": 1.5},  # Moderate frequency (71)
        {"word": "political", "weight": 2.0}  # High frequency (123)
    ],
    "patterns": [
        {"phrase": "distrust experts", "weight": 3.0},
        {"phrase": "people must", "weight": 2.0},
        {"phrase": "common sense over knowledge", "weight": 3.5},
        {"phrase": "point view", "weight": 2.0},
        {"phrase": "revolutionary spirit", "weight": 2.5},
        {"phrase": "league nations", "weight": 2.0},
        {"phrase": "working people", "weight": 2.0},
        {"phrase": "working class", "weight": 2.0},
        {"phrase": "whole people", "weight": 1.5},
        {"phrase": "national economy", "weight": 2.5},
        {"phrase": "one must", "weight": 1.5},
        {"phrase": "working classes", "weight": 2.0},
        {"phrase": "third world", "weight": 2.0},
        {"phrase": "people people", "weight": 1.5},
        {"phrase": "historical sites", "weight": 2.0},
        {"phrase": "working masses", "weight": 2.0},
        {"phrase": "ideological work", "weight": 2.0}
    ]
}
}

def detect_attack_on_minority(doc):
    """
    Detect attacks on minorities in text, focusing on both hostile language
    and disdainful contexts.
    """
    attack_keywords = ["blame", "threat", "enemy", "problem", "destroy", "eradicate", "kill", "eliminate", "oppress"]
    disdain_keywords = ["lazy", "unworthy", "dangerous", "inferior", "undesirable"]
    attacks = []

    for sent in doc.sents:
        minority_groups = [ent.text for ent in sent.ents if ent.label_ == "NORP"]
        attack_words = [word for word in attack_keywords if word in sent.text.lower()]
        disdain_words = [word for word in disdain_keywords if word in sent.text.lower()]
        sentiment = TextBlob(sent.text).sentiment.polarity

        if (attack_words or disdain_words) and minority_groups:
            attacks.append({
                "sentence": sent.text,
                "minority_groups": minority_groups,
                "attack_keywords": attack_words + disdain_words,
                "sentiment": round(sentiment, 2)
            })

    return attacks

def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            if lemma.name().lower() not in stop_words:  # Exclude stopwords
                synonyms.add(lemma.name().lower())
    return list(synonyms)


# Expand keywords with synonyms
for category, data in CATEGORIES.items():
    expanded_keywords = set()
    for keyword_dict in data["keywords"]:
        keyword = keyword_dict["word"]
        expanded_keywords.add(keyword)
        expanded_keywords.update(get_synonyms(keyword))
    data["keywords"] = [{"word": kw, "weight": 1.0} for kw in expanded_keywords]

# Function to match patterns in text
def match_phrases(doc, patterns):
    matches = []
    for pattern in patterns:
        if pattern["phrase"].lower() in doc.text.lower():
            matches.append(pattern["phrase"])
    return matches

# Function to calculate relevance score
def calculate_score(sentence, keywords, patterns):
    doc = nlp(sentence)

    # Calculate keyword score
    keyword_score = sum(
        kw["weight"] for token in doc for kw in keywords if token.text.lower() == kw["word"]
    )

    # Calculate pattern score
    pattern_score = sum(
        pattern["weight"] for pattern in patterns if pattern["phrase"] in sentence.lower()
    )

    return keyword_score + pattern_score

def highlight_relevant_text(text, keywords, patterns, category):
    """
    Extract and highlight relevant sentences with category filtering.
    The logic reflects the scoring system used in the 'analyze' function.
    """
    doc = nlp(text)
    location_tokens = {ent.text.lower() for ent in doc.ents if ent.label_ in {"GPE", "LOC", "NORP"}}
    relevant_sentences = []

    violent_keywords = ["army", "soldier", "fight", "weapon", "border", "force"]
    glorification_keywords = ["heritage", "tradition", "glory"]
    hostility_keywords = ["enemy", "threat", "problem"]
    disdain_keywords = ["lazy", "unworthy", "dangerous", "inferior", "undesirable"]

    for sent in doc.sents:
        # Filter tokens in the sentence
        valid_tokens = [
            token for token in sent
            if not token.is_punct and not token.is_space and token.text.lower() not in stop_words and token.text.lower() not in location_tokens
        ]

        # Match keywords and calculate their weight
        matched_keywords = [
            kw["word"] for kw in keywords 
            if kw["word"] in [token.text.lower() for token in valid_tokens]
        ]
        keyword_score = sum(kw["weight"] for kw in keywords if kw["word"] in matched_keywords)

        # Match patterns and calculate their weight
        matched_patterns = [
            pattern["phrase"] for pattern in patterns 
            if pattern["phrase"].lower() in sent.text.lower()
        ]
        pattern_score = sum(pattern["weight"] for pattern in patterns if pattern["phrase"] in matched_patterns)

        # Add minority attack detection
        minority_groups = [ent.text for ent in sent.ents if ent.label_ == "NORP"]
        attack_words = [word for word in hostility_keywords if word in sent.text.lower()]
        disdain_words = [word for word in disdain_keywords if word in sent.text.lower()]
        if (attack_words or disdain_words) and minority_groups:
            matched_keywords.extend(minority_groups)
            matched_patterns.extend(attack_words + disdain_words)
            keyword_score += 5  # Amplify relevance score for attacks on minorities

        # Add violent/militaristic adjacency detection
        if any(ent.label_ in {"ORG", "LOC"} for ent in sent.ents):
            if any(kw in sent.text.lower() for kw in violent_keywords):
                keyword_score += 5  # Amplify relevance score for violent contexts

        # Add glorification or hostility toward NORP
        for ent in sent.ents:
            if ent.label_ == "NORP":
                if any(kw in sent.text.lower() for kw in glorification_keywords):
                    keyword_score += 3  # Amplify for glorification
                if any(kw in sent.text.lower() for kw in hostility_keywords):
                    keyword_score += 5  # Amplify for hostility

        # Normalize the score
        sentence_length = max(len(valid_tokens), 1)  # Avoid divide by zero
        normalized_score = (keyword_score + pattern_score) / sentence_length

        # Include sentence if normalized score exceeds the equivalent analysis threshold
        if normalized_score > 0.04:  # Reflect the threshold logic from 'analyze'
            relevant_sentences.append({
                "category": category,
                "sentence": sent.text,
                "keywords": matched_keywords,
                "patterns": matched_patterns,
                "score": round(normalized_score * 500, 2)  # Scale to match analysis scoring
            })

    return relevant_sentences

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    speech = data.get("speech", "")

    if not speech:
        print("No speech text provided.")
        return jsonify({"error": "No speech text provided"}), 400

    results = {}
    relevant_sentences = []

    # Preprocess the speech
    doc = nlp(speech)

    # Extract location-based entity tokens
    location_tokens = {ent.text.lower() for ent in doc.ents if ent.label_ in {"GPE", "LOC", "NORP"}}

    # Filter tokens to exclude stopwords, punctuation, and location-based entities
    valid_tokens = [
        token for token in doc
        if not token.is_punct and not token.is_space and token.text.lower() not in stop_words and token.text.lower() not in location_tokens
    ]
    total_tokens = len(valid_tokens)
    total_sentences = len(list(doc.sents))

    # Analyze speech for each category
    for category, data in CATEGORIES.items():
        keywords = data["keywords"]
        patterns = data.get("patterns", [])

        # Count keyword matches
        count = sum(1 for token in doc for kw in keywords if token.text.lower() == kw["word"])

        # Apply normalization
        density = count / max(total_tokens, 50)  # Token density normalization
        sentence_complexity = 1 + (total_sentences / max(total_tokens, 1))
        adjusted_score = (density * (count ** 0.5) * 500) / sentence_complexity

        # Apply minimum threshold
        if adjusted_score > 10:
            results[category] = round(adjusted_score, 2)

        # Highlight relevant sentences with category filtering
        relevant_sentences.extend(highlight_relevant_text(speech, keywords, patterns, category))

    # **Amplify Scores for Nationalism or Identity Themes**
    for ent in doc.ents:
        if ent.label_ == "NORP":  # Nationalities, religious groups, political groups
            # Check for glorification
            if any(kw in ent.sent.text.lower() for kw in ["heritage", "tradition", "glory"]):
                results["Glorification of a Past Golden Age"] = results.get("Glorification of a Past Golden Age", 0) + 5
            # Check for hostility
            if any(kw in ent.sent.text.lower() for kw in ["enemy", "threat", "problem"]):
                results["Us vs. Them Mentality"] = results.get("Us vs. Them Mentality", 0) + 5

    # **Detect Violent or Militaristic Phrases with Entity Adjacency**
    violent_keywords = ["army", "soldier", "fight", "weapon", "border", "force"]
    for ent in doc.ents:
        if ent.label_ in {"ORG", "LOC"}:  # Military or location entities
            if any(kw in ent.sent.text.lower() for kw in violent_keywords):
                results["Militarism or Violence"] = results.get("Militarism or Violence", 0) + 5

    # Add sentiment analysis
    sentiment = TextBlob(speech).sentiment.polarity
    results["Overall Sentiment"] = round(sentiment, 2)

    # Add relevant sentences
    results["Relevant Sentences"] = relevant_sentences

    return jsonify(results)

@app.route("/")
def helloworld():
    return "Hello World!"

if __name__ == "__main__":
    app.run(port=3001)
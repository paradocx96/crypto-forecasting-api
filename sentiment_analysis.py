import pickle
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import ssl
import nltk

# load vectorizer
path_vectorizer = 'model/vectorizer.pickle'
with open(path_vectorizer, 'rb') as data:
    vectorizer = pickle.load(data)

# load model
path_model = 'model/best_rfc.pickle'
with open(path_model, 'rb') as data:
    model = pickle.load(data)

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Downloading punkt and wordnet from NLTK
nltk.download('omw-1.4')
nltk.download('punkt')
print("------------------------------------------------------------")
nltk.download('wordnet')
# Downloading the stop words list
nltk.download('stopwords')

# Saving the lemmatizer into an object
wordnet_lemmatizer = WordNetLemmatizer()

# Loading the stop words in english
stop_words = list(stopwords.words('english'))


def pre_processing(sentence):
    # 1.1. Replace \n and \t
    sentence = sentence.replace("\r", " ")
    sentence = sentence.replace("\n", " ")

    # 1.2. Convert to lowercase
    sentence = sentence.lower()

    # 1.3. Remove punctuation signs
    punctuation_signs = list("?:!.,;-$&^*%(){}[]/><@#~`|+_=“”…’−‘")
    for punct_sign in punctuation_signs:
        sentence = sentence.replace(punct_sign, '')

    # 1.4. Remove possessive pronouns
    sentence = sentence.replace("'s", "")

    # 1.5. Remove numbers
    digits = list("1234567890")
    for digit in digits:
        sentence = sentence.replace(digit, '')

    # 1.6. Remove single quote and double quote
    sentence = sentence.replace("'", "")
    sentence = sentence.replace('"', '')

    # 1.7. Lemmatization
    lemmatized_list = []
    text_words = sentence.split(" ")
    for word in text_words:
        lemmatized_list.append(wordnet_lemmatizer.lemmatize(word, pos="v"))
    sentence = " ".join(lemmatized_list)

    # 1.8. Remove Stop words
    for stop_word in stop_words:
        regex_stopword = r"\b" + stop_word + r"\b"
        sentence = sentence.replace(regex_stopword, '')

    # 1.9. Remove Extra Spaces
    sentence = sentence.split()
    sentence = " ".join(sentence)

    return sentence


def predict(sentence):
    sentence = pre_processing(sentence)
    vector = vectorizer.transform([sentence]).toarray()
    pred = model.predict(vector)
    return pred[0]

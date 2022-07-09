import nltk
from nltk.corpus import stopwords
import pandas as pd
import random
import re
from nltk import FreqDist
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tokenize.toktok import ToktokTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from bs4 import BeautifulSoup
from sklearn.linear_model import SGDClassifier
from sklearn.svm import SVC
from sklearn.metrics import classification_report
#import necessary libraries

################################################
###LTSM libraries(failed)###
#from keras.datasets import imdb
#from keras.models import Sequential
#from keras.layers import Dense
#from keras.layers import LSTM
#from keras.layers.embeddings import Embedding
#from keras.preprocessing import sequence
################################################
#any code surrounded by the lines of ('#') is considered failed code or testing code 
dataset = pd.read_csv('IMBD.csv')
#reads the EXCL file , the read_csv is set because it is csv file which gives
#an error if not specfied as CSV instead of excel manually

#shuffle dataset (testing purposses only)
#all text proccesing functions(
print('part 2-----------------------------------')
def remove_char (text):
    regex = r'[^a-zA-z0-9\s]'
    text=re.sub(regex,'',text)
    return text

sw =set(stopwords.words('english'))
def remove_sp (text ):
    tokens = ToktokTokenizer().tokenize(text)
    tokens = [token.strip() for token in tokens]
    filtered = [token for token in tokens if token not in sw]
    filtered2 = ' '.join(filtered)
    return filtered2
def rhtml (text):
    return BeautifulSoup(text, "html.parser").get_text()
def RMbracket (text):
    regex = r'\[[^]]*\]'
    return re.sub(regex, '', text)
def textprossesing (text):
    text = remove_char (text)
    text = remove_sp (text)
    text = rhtml (text)
    text = RMbracket(text)
    return text

#)
#part 3 and 2 code 
reviewList = dataset['review'].to_numpy()
#converts our column into numby list
punct= re.findall("[^a-zA-z0-9\s]" , str(reviewList))
punctFD = FreqDist(punct)
#finding all punctuation and freqency of the punct 
Rcount = dataset['review'].describe()
Scount = dataset['sentiment'].value_counts()
#description of data in both column
avglenBTP = sum(len(x.split()) for x in dataset['review']) / len(dataset['review'])
#find setence length and each row in review
dataset['review'] = dataset['review'].apply(textprossesing)
print('part2: \n removed non alphpatical characters\n removed stop words from (nltk.corpus/stopwords)\n html links removed \n removed square barkets')
#applies the text prosessing function 
avglenATP = sum(len(x.split()) for x in dataset['review']) / len(dataset['review'])
#find setence length and each row in review after text prossesing
review = pd.DataFrame(dataset, columns = ['review'])
sentiment = pd.DataFrame(dataset, columns = ['sentiment'])
#sperates our columes into 2 diffrent data sets 
reviewL = dataset['review'].to_numpy()
sentimentL = dataset['sentiment'].to_numpy()
#converts our column into numby list after removing stop words and punct
train = reviewL[:40000]
test =  reviewL[40000:]
#---------------------------------
train_sen = sentimentL[:40000]
test_sen =  sentimentL[40000:]
#inserts first 4k into train and last 1k into test
############################
###shuffle train and test sets (testing)
#random.shuffle(train)
#random.shuffle(test)
#random.shuffle(train_sen)
#random.shuffle(test_sen)
#############################
TFIDF = TfidfVectorizer(min_df=0,max_df=1,use_idf=True,ngram_range=(1,3))
trainTV =TFIDF.fit_transform(train)
testTV =TFIDF.transform(test)
############################################
######(failed)
#train2 = review[:40000]
#test2 =  review[40000:]
#-------------------------------------
#train_sen2 = sentiment[:40000]
#test_sen2 =  sentiment[40000:]
############################################
print('part 3:')
print('_________________________________________')
print(' average length [ \n before text prossesing :',avglenBTP)
print(' after text prossesing :',avglenATP , ' ]')
print('_________________________________________')
print('punctuation:\n' , punctFD.most_common(), '\nmanual testing for punctuation shows the punctuation is not accurate so keeping that in mind I am unsure the result or how to fix it ')
print('_________________________________________')
print ('review \n', Rcount)
print('_________________________________________')
print ('sentiment \n', Scount)
print('_________________________________________')
print('TFIDF \n trin TFIDF:',trainTV.shape , '\n test TFIDF:',testTV.shape)
print('_________________________________________')
#prints all the features nesseary for part 3
print ('part 4:sk.learn_SVM')
svm=SGDClassifier(loss='hinge',max_iter=500,random_state=42)
#bulding the model
TV_SGDC = svm.fit( trainTV, train_sen)
#train the model
#print(TV_SGDC)
print('_________________________________________')
TVprd = svm.predict(testTV)
#setting the predections 
print(TVprd)
print('_________________________________________')
print('part 5:sk.learn_SVM')
TVCR = classification_report (test_sen, TVprd , target_names=['postive','negtive'])
# finding recall , accuracy .....etc 
print(TVCR)
print('_________________________________________')
print('LTSM model has been commented since I wasnt able to get it working')
print('_________________________________________')
#refrences
#[1]"Sentiment Analysis of IMDB Movie Reviews", Kaggle.com, 2022. [Online].[Accessed: 28- dec- 2021].
#[2]"How to Import an Excel File into Python using Pandas - Data to Fish", Datatofish.com, 2022. [Online].[Accessed: 8- dec- 2021].
#[3]G. row? and A. Bandi, "Get list from pandas dataframe column or row?", Stack Overflow, 2022. [Online].  [Accessed: 08- Dec- 2021].
#[4]y. PANDAS &amp; glob - Excel file format cannot be determined and f. aa, "PANDAS & glob - Excel file format cannot be determined, you must specify an engine manually", Stack Overflow, 2022. [Online]. [Accessed: 08- Dec- 2021].
#[5]M. Mayo, "Text Data Preprocessing: A Walkthrough in Python - KDnuggets", KDnuggets, 2022. [Online].[Accessed: 28- Dec- 2021].
#[6]"how to count average sentence length (in words) from a text file contains 100 sentences using python-XSZZ.ORG", Xszz.org, 2022. [Online]. [Accessed: 01- Jan- 2022].
#[7] using labs from the CE314 module on moodle
print ('refrences\n[1]"Sentiment Analysis of IMDB Movie Reviews", Kaggle.com, 2022. [Online].[Accessed: 28- dec- 2021].\n[2]"How to Import an Excel File into Python using Pandas - Data to Fish", Datatofish.com, 2022. [Online].[Accessed: 8- dec- 2021].\n[3]G. row? and A. Bandi, "Get list from pandas dataframe column or row?", Stack Overflow, 2022. [Online].  [Accessed: 08- Dec- 2021].\n[4]y. PANDAS &amp; glob - Excel file format cannot be determined and f. aa, "PANDAS & glob - Excel file format cannot be determined, you must specify an engine manually", Stack Overflow, 2022. [Online]. [Accessed: 08- Dec- 2021].\n[5]M. Mayo, "Text Data Preprocessing: A Walkthrough in Python - KDnuggets", KDnuggets, 2022. [Online].[Accessed: 28- Dec- 2021].\n[6]"how to count average sentence length (in words) from a text file contains 100 sentences using python-XSZZ.ORG", Xszz.org, 2022. [Online]. [Accessed: 01- Jan- 2022].\n[7] using labs from the CE314 module on moodle')
#######################################################################################################
###LTSM model(failed)
#num = 50000
#(train2 ,test2), (train_sen2, test_sen2) = imdb.load_data(num_words=num)
#EVL = 3200
#model = Sequential()
#model.add(Embedding(num, EVL, input_length=10000))
#model.add(LSTM(100))
#model.add(Dense(11, activation='sigmoid'))
#model.compile(loss='binary_crossentropy', optimizer='adam' , metrics=['accuracy'])
#print(model.summary())
#model.fit(train2 , train_sen2 , validation_data=(test2 , test_sen2), epochs=3 , batch_size=64 )
#scores = model.evaluate(test2 , test_sen2 , verbose=0)
#print((scores[1]*10000))
#######################################################################################################

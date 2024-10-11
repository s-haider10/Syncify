#!/usr/bin/env python
# coding: utf-8

# # Spotify Rec Sys
# 
# 
# - Since we have song features, let’s focus on content-based filtering.
# - Compute similarity between songs using techniques like cosine similarity.
# - And then make it dyanmic by adding user data
# - Recommend songs similar to those a user has already liked and then use collaborative filtering and then use hybrid model
# 
# 
# 
# 

# In[1]:


file_path = 'spotify_data/train.csv'
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#turn into a pandas dataframe
data = pd.read_csv(file_path)
data.shape


# In[2]:


# I wanna only take a smaller subset of the data to make it easier to work with
data = data.sample(frac=0.05, random_state=1)
data.shape


# In[3]:


data


# # Data Preprocessing
# ## Check for missing values

# In[4]:


# Check for missing values coded as NA or -1 or empty string
missing_values = data.isin(['NA', -1, ''])
if missing_values.any().any():
    print("Missing values detected:")
    print(data[missing_values.any(axis=1)])
else:
    print("No missing values detected.")


#  ## Normalize
# Next we will normalize our data using min,max normalization  $X_n = \frac{x-min_x}{max_x-min_x}$

# In[5]:


# drop columns with categorical data
non_categorical_columns = ['acousticness', 'danceability', 'duration_ms', 'energy', 'instrumentalness', 'key', 'liveness', 'loudness', 'mode', 'speechiness', 'tempo', 'valence', 'popularity']
df_non_categorical = data[non_categorical_columns]
norm_data = (df_non_categorical-df_non_categorical.min())/(df_non_categorical.max()-df_non_categorical.min())
norm_data.head()


# ## Pearson Correlation 

# In[6]:


def highly_correlated_features(df, threshold):
    correlation_matrix = df.corr() # Calculate the correlation matrix
    
    features_to_drop = set()
    highly_correlated_pairs = []
    
    for i in range(correlation_matrix.shape[0]):
        for j in range(i+1, correlation_matrix.shape[1]):
            # If the absolute value of the correlation coefficient is above the threshold, add the feature to the set
            if abs(correlation_matrix.iloc[i, j]) > threshold:
                features_to_drop.add(correlation_matrix.columns[j])
                highly_correlated_pairs.append((correlation_matrix.columns[i], correlation_matrix.columns[j], correlation_matrix.iloc[i, j]))

    return features_to_drop , highly_correlated_pairs


# In[7]:


drop_features, correlated_pairs  = highly_correlated_features(norm_data, 0.7)


print("We can drop these Features:",drop_features)
print()
print("Correlated Pairs and their coefficient")
for i in correlated_pairs:
    print(i)


# In[8]:


filtered_data = norm_data.drop(columns=drop_features)
filtered_data.head()


# In[9]:


# Compute clsuters to do unsupervised learning
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# Create a list to store the silhouette scores
silhouette_scores = []

# Create a list of different number of clusters to try
n_clusters = [2, 3, 4, 5, 6, 7, 8, 9, 10]

# Loop through each cluster
for n in n_clusters:
    # Create a KMeans object with n clusters and fit it to the data
    kmeans = KMeans(n_clusters=n, random_state=0)
    kmeans.fit(filtered_data)
    
    # Calculate the silhouette score and append it to the list
    silhouette_scores.append(silhouette_score(filtered_data, kmeans.labels_))

# Plot the silhouette scores
plt.plot(n_clusters, silhouette_scores)
plt.xlabel('Number of Clusters')
plt.ylabel('Silhouette Score')
plt.title('Silhouette Score vs Number of Clusters')
plt.show()


# 

# In[10]:


# compute cosine similarity with all the songs
from sklearn.metrics.pairwise import cosine_similarity

# Calculate the cosine similarity matrix
cosine_similarity_matrix = cosine_similarity(filtered_data)

# Create a DataFrame for the cosine similarity matrix
cosine_similarity_df = pd.DataFrame(cosine_similarity_matrix, index=filtered_data.index, columns=filtered_data.index)
cosine_similarity_df.head()


# # Collab filtering with cosine similarity

# In[11]:


data_new = data.drop(columns=drop_features)
data_new.head()

# Create a function to get recommendations based on the cosine similarity matrix
def get_recommendations(song_title, cosine_similarity_df, data):
    # Get the index of the song
    song_index = data[data['name'] == song_title].index[0]
    
    # Get the similarity scores of the song
    similarity_scores = cosine_similarity_df[song_index]
    
    # Get the indices of the songs with the highest similarity scores
    similar_songs = similarity_scores.sort_values(ascending=False).index[1:6]
    
    # return like this: Index: 1, Name: 'song name', Artists: 'artist name'
    recommended_songs = []
    for i in similar_songs:
        recommended_songs.append({'Index': i, 'Name': data['name'][i], 'Artists': data['artists'][i]})
    
    return recommended_songs


# ## Test the function

# In[12]:


# Get recommendations for the song 'SLovelight' by ABBA
song = 'The Set Up'
recommendations = get_recommendations(song, cosine_similarity_df, data_new)
#fix the print statement print(f"Since you listened to {},you might also like:") # fix this, make it f%
print(f"Since you listened to {song}, you might also like:")
for i in recommendations:
    print('Index:', i['Index'], 'Name:', i['Name'], ' By:', i['Artists'])


# - we need to make the user sign up on our database first before we can recommend songs to them
# - we can use the user's listening history to recommend songs to them
# - we can also add a feature to allow the user to rate the recommended songs
# - we can also add a feature to allow the user to search for songs and artists

# # Create user profile

# In[13]:


def generate_unique_user_id(user_data):
    while True:
        user_id = np.random.randint(100000, 999999)
        if user_id not in user_data['user_id'].values:
            return user_id

def user_signup(user_data, user_name, user_email, user_password):
    user_id = generate_unique_user_id(user_data)
    new_user = pd.DataFrame({'user_id': [user_id], 'user_name': [user_name], 'user_email': [user_email], 'user_password': [user_password]})
    user_data = pd.concat([user_data, new_user], ignore_index=True)
    print("User signed up successfully!")
    return user_data

def user_login(user_data, user_email, user_password):
    user = user_data[(user_data['user_email'] == user_email) & (user_data['user_password'] == user_password)]
    if user.empty:
        print("Invalid email or password. Please try again.")
        return None
    else:
        print("User logged in successfully!")
        return user.iloc[0]['user_id']

def add_to_database(user_data, user_id, user_name, user_email, user_password):
    new_user = pd.DataFrame({'user_id': [user_id], 'user_name': [user_name], 'user_email': [user_email], 'user_password': [user_password]})
    user_data = pd.concat([user_data, new_user], ignore_index=True)
    return user_data

def rate_song(user_id, song_index, rating, ratings_data):
    new_rating = pd.DataFrame({'user_id': [user_id], 'song_index': [song_index], 'rating': [rating]})
    ratings_data = pd.concat([ratings_data, new_rating], ignore_index=True)
    print("Song rated successfully!")
    return ratings_data

def search_song(song_name, data):
    search_results = data[data['name'].str.contains(song_name, case=False)]
    if search_results.empty:
        print("No matching songs found.")
    else:
        print("Matching songs found:")
        print(search_results[['name', 'artists']])
    return search_results


# # ## Test user profile

# # In[14]:


# # Initialize user data
# user_data = pd.DataFrame(columns=['user_id', 'user_name', 'user_email', 'user_password'])

# # sign up 
# user_name = "John Doe"
# user_email = "john@example.com"
# user_password = "password123"
# user_data = user_signup(user_data, user_name, user_email, user_password)


# # In[15]:


# # Log in 
# user_email = "john@example.com"
# user_password = "password123"
# user_id = user_login(user_data, user_email, user_password)


# # In[16]:


# user_data


# # In[17]:


# # # Initialize ratings data
# ratings_data = pd.DataFrame(columns=['user_id', 'song_index', 'rating'])

# # Rate a song
# user_id = user_data[user_data['user_email'] == user_email]['user_id'].values[0] 
# song_index = 247933
# rating = 5 
# ratings_data = rate_song(user_id, song_index, rating, ratings_data)


# # In[18]:


# ratings_data


# # In[19]:


# # search for a song
# song_name = "The Set Up" 
# search_results = search_song(song_name, data)


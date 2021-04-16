import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import yagmail
import os
import glob


def aggregation():
    extension = 'csv'
    all_filenames = [i for i in glob.glob('*.{}'.format(extension))]
    # combine all books files in the list
    combined_books = pd.concat([pd.read_csv(f) for f in all_filenames if 'Book_' in f])
    # export to csv
    combined_books.to_csv("Bridge_Books.csv", index=False)
    # combine all books files in the list
    combined_ratings = pd.concat([pd.read_csv(f) for f in all_filenames if 'Ratings_' in f])
    # export to csv
    combined_ratings.to_csv("Bridge_Book-Ratings.csv", index=False)


class Ai:
    def __init__(self, account_name, account_passwd):
        # connect to smtp server.
        self.yag_smtp_connection = yagmail.SMTP(user=account_name, password=account_passwd, host='smtp.gmail.com')
        # email subject
        self.subject = 'BOOK SHARING - recommendations'

    def compute_recommendations_for_all(self):
        aggregation()
        rating = pd.read_csv('Bridge_Book-Ratings.csv', sep=';')
        for index, row in rating[['userID', 'email']].drop_duplicates().iterrows():
            self.compute_recommendations_for_one(row.userID, row.email)
        # for index, row in rating[['userID']].drop_duplicates().iterrows():
        #     self.compute_recommendations_for_one(row.userID, 'brunopao97@gmail.com')

    def compute_recommendations_for_one(self, target_user_id, email):
        book = pd.read_csv('Books.csv', sep=';')
        '''book.columns = ['ID', 'ID_DRAWER', 'title', 'author', 'isbn', 'original_owner_ID', 'current_owner_ID',
                        'date_of_loan', 'date_of_reserve']
        # excluding target user books (they are already yours!)
        book = book[book['original_owner_ID'] != target_user_id]
        # we want recommend only books in the lockers (doing this we also exclude target user current books)
        book = book[book['current_owner_ID'].isna()]'''
        rating = pd.read_csv('Book-Ratings.csv', sep=';')
        '''# in order to recommend something we only need the ratings of the target user
        rating = rating.drop(['email'], axis=1)'''
        # creating a unique table
        combine_book_rating = pd.merge(rating, book, on='isbn')
        combine_book_rating = combine_book_rating.drop_duplicates(['userID', 'title'])
        '''# we don't need all the columns in order to recommend a book
        drop_columns = ['ID', 'ID_DRAWER', 'author', 'original_owner_ID', 'current_owner_ID', 'date_of_loan',
                        'date_of_reserve']
        # We keep only ['userID', 'isbn', 'bookRating', 'title']
        combine_book_rating = combine_book_rating.drop(drop_columns, axis=1)'''
        # We convert our table to a 2D matrix, and fill the missing values with zeros (since we will calculate distances
        # between rating vectors)
        combine_book_rating_pivot = combine_book_rating.pivot(index='title', columns='userID',
                                                              values='bookRating').fillna(0)
        # Transform the values (ratings) of the matrix dataframe into a scipy sparse matrix for more efficient
        # calculations
        combine_book_rating_matrix = csr_matrix(combine_book_rating_pivot.values)
        # Fit K-NN (unsupervised) for recommend something (we use the cosine metric
        # between rating vectors and the brute algorithm)
        model_knn = NearestNeighbors(metric='cosine', algorithm='brute')
        model_knn.fit(combine_book_rating_matrix)
        # Recommend over a user book of the pivot table
        query_index = np.random.choice(list(np.where(combine_book_rating_pivot[target_user_id] != 0.0)[0]))
        # Recommend over a casual book of the pivot table
        # query_index = np.random.choice(combine_book_rating_pivot.shape[0])
        # 4-NN
        distances, indices = model_knn.kneighbors(combine_book_rating_pivot.iloc[query_index, :].values.reshape(1, -1),
                                                  n_neighbors=4)

        contents = 'Book Sharing wants to recommend a book to you:\n'
        for i in range(0, len(distances.flatten())):
            if i == 0:
                print('\nRecommendations for {0}:\n'.format(combine_book_rating_pivot.index[query_index]))
            else:
                print('{0}: {1}, with distance of {2}'.format(i, combine_book_rating_pivot.index[indices.flatten()[i]],
                                                               distances.flatten()[i]))
                # email content with attached file path.
                contents += f'{combine_book_rating_pivot.index[indices.flatten()[i]]} \n'
        # send the email
        self.yag_smtp_connection.send(email, self.subject, contents)


if __name__ == '__main__':
    GMAIL_NAME = "adrenalineDeveloper97"
    GMAIL_PASSWD = "GCPDeveloper97"
    ai = Ai(GMAIL_NAME, GMAIL_PASSWD)
    ai.compute_recommendations_for_all()

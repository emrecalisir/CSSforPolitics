import numpy as np
from nltk.corpus import stopwords
from nltk import download
from gensim.models import Word2Vec
import pandas as pd
from sklearn import svm
from sklearn.metrics import confusion_matrix
import csv
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
import sklearn
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import scale
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from sklearn.model_selection import cross_val_predict
from sklearn.model_selection import cross_validate
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDClassifier
from sklearn import metrics
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
from time import time
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score


def remove_extra_chars_from_word(word):
    # this method is related with Word2Vec
    word = word.replace('?', '')
    word = word.replace('.', '')
    word = word.replace('!', '')
    word = word.replace('-', ' ')
    word = word.replace('(', '')
    word = word.replace(')', '')
    word = word.replace(':', '')
    word = word.replace('&', '')
    word = word.replace('√', '')
    word = word.replace('®', '')

    return word


def is_weblink(word):
    # this method is related with Word2Vec
    res = False
    if 'http' in word or 'www' in word:
        res = True
    return res


def get_stop_words():
    # this method is related with Word2Vec
    # download('stopwords')  # stopwords dictionary, run once
    stop_words_it = stopwords.words('italian')
    stop_words_en = stopwords.words('english')
    stop_words_en.extend(stop_words_it)
    return stop_words_en


stop_words_voc = get_stop_words()


def is_stopword(word):
    # this method is related with Word2Vec
    res = False
    if stop_words_voc is None:
        exit(-1)
    if word in stop_words_voc:
        res = True
    return res


word2vec_model = None


def get_trained_word2vec_model(dimension):
    # this method is related with Word2Vec
    try:
        global word2vec_model
        if word2vec_model is not None:
            return word2vec_model

        filename = "C:/Users/emre2/Desktop/Museums/latest_data/model_voc_02_03_vocab" + str(dimension)
        new_model = Word2Vec.load(filename)
        word2vec_model = new_model

    except Exception as ex:
        print("model load error", ex)

    return word2vec_model


def get_mean_vector_value_of_text(text, dimension):
    # this method is related with Word2Vec
    model = get_trained_word2vec_model(dimension)

    splitted = text.split(" ")
    current_word2vec = []
    try:

        for word in splitted:
            word = remove_extra_chars_from_word(word)

            if is_weblink(word):
                continue
            elif is_stopword(word):
                continue
            else:
                if word in model.wv.vocab:
                    vec_word = model[word]
                    current_word2vec.append(vec_word)
                else:
                    print("not existing in model: " + word)

        if len(current_word2vec) == 0:
            zeros = [0] * dimension
            current_word2vec.append(zeros)

        averaged_word2vec = list(np.array(current_word2vec).mean(axis=0))

    except Exception as exception:
        print('Oops!  An error occurred.  Try again...', exception)

    return averaged_word2vec


def train_word2vec_csv(dimensions):
    # with open('C:/Users/emre2/Desktop/Museums/step-1.csv', newline='', encoding='utf-8') as f:
    print("started building Word2Vec vocabulary from scratch")

    with open('C:/Users/emre2/Desktop/Museums/latest_data/vocab_build_all_after_fulltext_0203.csv', newline='',
              encoding='utf-8') as f:
        try:
            reader = csv.reader(f)
            whole_tweet_contents = []
            counter_vocabulary_word = 0
            whole_words = []
            unique_words = []
            counter = 0
            for row in reader:
                try:
                    counter += 1

                    tweet_content = row[2]
                    if tweet_content == 'text':
                        # this is for skipping header row
                        continue
                    tweet_content_words = tweet_content.split(" ")
                    tweet_content_list = []

                    for word in tweet_content_words:
                        word = remove_extra_chars_from_word(word)
                        if is_weblink(word):
                            continue
                        elif is_stopword(word):
                            continue
                        else:
                            whole_words.append(word)
                            if word not in unique_words:
                                unique_words.append(word)
                            counter_vocabulary_word += 1
                            tweet_content_list.append(word)

                    whole_tweet_contents.append(tweet_content_list)

                except Exception as exception:
                    print('Oops!  An error occurred.  Try again...', exception)

            print("all words count" + str(len(whole_words)))
            print("unique all words count" + str(len(unique_words)))

            model = Word2Vec(whole_tweet_contents, size=dimensions, window=5, min_count=1, workers=4)

            filename = "C:/Users/emre2/Desktop/Museums/latest_data/model_voc_02_03_vocab" + str(dimensions)
            model.save(filename)

        except Exception as exception:
            print('Oops!  An error occurred.  Try again...', exception)
            print("completed building Word2Vec vocabulary from scratch")
    print("completed building Word2Vec vocabulary from scratch")

#OLD
'''def ratio(is_tp_ratio, y_true, y_pred, pct):
    if y_pred.ndim == 2:
        y_pred = y_pred[:, 1]
    n = int(round(len(y_true) * pct))
    idx = np.argsort(y_pred)[-n:]
    prob_min = y_pred[idx[0]]
    y_true_sum = y_true[idx].sum()
    if not is_tp_ratio:
        y_emre = []
        for id in idx:
            y_emre.append(str(y_pred[id]) + ";" + str(y_true[id]))
        # print(y_emre)
    ratio_float = (y_true_sum / float(n))
    ratio_val = "{0:.2f}%".format(ratio_float * 100)

    if is_tp_ratio:
        res = "tp_ratio: " + str(ratio_val) + " , lowest probability score: " + str(round(prob_min, 2))
    else:
        res = "tn_ratio: " + str(ratio_val) + " , lowest probability score: " + str(round(prob_min, 2))
    return res '''

def ratio(y_true, y_pred, pct):
    if y_pred.ndim == 2:
        y_pred = y_pred[:, 1]
    n = int(round(len(y_true) * pct))
    idx = np.argsort(y_pred)[-n:]
    prob_min = y_pred[idx[0]]
    y_true_sum = y_true[idx].sum()
    y_emre = []
    for id in idx:
        y_emre.append(str(y_pred[id]) + ";" + str(y_true[id]))
        # print(y_emre)
    ratio_float = (y_true_sum / float(n))
    ratio_val = "{0:.2f}%".format(ratio_float * 100)

    res = "tp_ratio: " + str(ratio_val) + " , lowest probability score: " + str(round(prob_min, 2))
    return res


def generate_feature_ngram(filename, test_percentage, is_shuffle, is_yes_1):
    data_df = pd.read_csv(filename)
    X_train, X_test, y_train, y_test = train_test_split(data_df["text"], data_df["check"], test_size=test_percentage,
                                                        shuffle=is_shuffle)

    if is_yes_1:
        y_train = y_train.replace("N", 0).replace("Y", 1)
        y_test = y_test.replace("N", 0).replace("Y", 1)
    else:
        y_train = y_train.replace("N", 1).replace("Y", 0)
        y_test = y_test.replace("N", 1).replace("Y", 0)

    X_train = X_train.values
    X_test = X_test.values
    y_train = y_train.values
    y_test = y_test.values

    return X_train, X_test, y_train, y_test


def generate_feature_word2vec(begin_index, end_index, dimension, filename, isYes1):
    # This is based on single feature, which contains the average Vector value for each tweet.
    try:
        data_df = pd.read_csv(filename)

        data_df = data_df[begin_index:end_index]
        textvalues = np.array(data_df["text"])
        vect_means = []

        for textvalue in textvalues:
            vect_mean = get_mean_vector_value_of_text(textvalue, dimension)
            vect_means.append(vect_mean)

        X = vect_means
        if isYes1:
            y = (np.array(data_df["check"]
                          .replace("N", 0)
                          .replace("Y", 1)))
        else:
            y = (np.array(data_df["check"]
                          .replace("N", 1)
                          .replace("Y", 0)))

    except Exception as exception:
        print('Oops!  An error occurred.  Try again...', exception)
    return X, y


def evaluate_cross_validation(clf, x_all, y_all):
    print("cross val score: " + str(cross_val_score(clf, x_all, y_all, cv=10).mean()))
    # scoring = ['precision_macro', 'recall_macro']

    y_pred = cross_val_predict(clf, x_all, y_all, cv=10)
    tn, fp, fn, tp = confusion_matrix(y_all, y_pred).ravel()
    print("tn:" + str(tn) + " fn:" + str(fn) + " tp:" + str(tp) + " fp:" + str(fp))


def evaluate_train_test(clf, y_test, y_pred):
    print("expected test results  :" + str(y_test))
    print("predicted test results: " + str(y_pred))

    print("accuracy score:" + str(accuracy_score(y_test, y_pred)))
    # print(precision_recall_fscore_support(y_test, y_pred, average=None))

    # test precision
    # precision = precision_score(y_test, y_pred, average=None)
    # print("Precision: " + str(precision[1]))
    # test recall
    # recall = recall_score(y_test, y_pred, average=None)
    # print("Recall: " + str(recall[1]))
    # test F1 score
    # f_measure = f1_score(y_test, y_pred, average=None)
    # print("F1 score score: " + str(f_measure[1]))

    print(metrics.classification_report(y_test, y_pred, target_names=None))

    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()

    actual_yes, actual_no = get_yes_no_count(y_test)
    pred_yes_cnt, pred_no_cnt = get_yes_no_count(y_pred)

    print("output of confusion matrix: tn:" + str(tn) + " fp:" + str(fp) + " fn: " + str(fn) + " tp:" + str(tp))
    # print("manual accuracy: " + str((tp + tn) / len(y_pred)))
    # print("manual misclassification rate: " + str((fp + fn) / len(y_pred)))
    # recall = tp / actual_yes
    # print("manual tp rate (sensitivity-recall): " + str(recall))
    # print("manual fp rate: " + str((fp) / actual_no))
    # print("manual specificity: " + str((tn) / actual_no))
    # precision = tp / pred_yes_cnt
    # print("manual precision: " + str(precision))
    # print("manual prevalence: " + str(actual_yes / len(y_pred)))
    # print("manual f1 score: " + str(2 * recall * precision / (recall + precision)))


def evaluate_probability_based_train_test_model(clf_prob, X_train, y_train, X_test, y_test):
    clf_prob.fit(X_train, y_train)
    print("Natural TP rate=" + str(sum(y_test) / len(y_test)))
    y_pred_prob = clf_prob.predict_proba(X_test)[:, 1]
    print("test started")
    #print('Top 100 first' + str(len(y_test)) + ' records in test dataset) -> ' + str(
    #    ratio(y_test, y_pred_prob, 1)))

    print("test ended")
    print('ROC AUC:', roc_auc_score(y_test, y_pred_prob))
    for i in [x * 0.1 for x in range(1, 6)]:
        i = round(i, 1)
        print('Top' + str(int(i * 100)) + 'percentile = (first ' + str(
            int(i * len(y_test))) + ' records in test dataset) -> ' + str(
            ratio(y_test, y_pred_prob, pct=i)))


def evaluate_probability_based_cross_val_model(clf_prob, X_all, y_all, is_tp_ratio):
    clf_prob.fit(X_all, y_all)
    print("Natural TP rate=" + str(sum(y_all) / len(y_all)))
    y_pred_prob = cross_val_predict(clf_prob, X_all, y_all, cv=10, method='predict_proba')[:, 1]
    print('ROC AUC:', roc_auc_score(y_all, y_pred_prob))
    for i in [x * 0.1 for x in range(1, 6)]:
        i = round(i, 1)
        print('Top' + str(int(i * 100)) + 'percentile = (first ' + str(
            int(i * len(y_all))) + ' records in whole dataset) -> ' + str(
            ratio(y_all, y_pred_prob, pct=i)))


def convert_text_to_word2vec(data, dimension):
    vect_means = []
    for textvalue in data:
        vect_mean = get_mean_vector_value_of_text(textvalue, dimension)
        vect_means.append(vect_mean)

    np_vect_means = np.asarray(vect_means)
    return np_vect_means


def generate_features_scaled_encoded_including_word2vec(begin_index_train, end_index_train, begin_index_test,
                                                        end_index_test, dimension,
                                                        filename, isyes1):
    try:
        data_df = pd.read_csv(filename)

        data_df_train = data_df[begin_index_train:end_index_train]
        data_df_test = data_df[begin_index_test:end_index_test]

        print("distribution of train output classes: " + str(
            data_df_train["check"].value_counts() / data_df_train["check"].count()))
        print("distribution of test output classes: " + str(
            data_df_test["check"].value_counts() / data_df_test["check"].count()))

        npvectmeans_train = convert_text_to_word2vec(np.array(data_df_train["text"]), dimension)
        npvectmeans_test = convert_text_to_word2vec(np.array(data_df_test["text"]), dimension)

        # Define which columns should be encoded vs scaled
        columns_to_scale = ['tw_retweet_count', 'tw_favorite_count', 'user_friends_count', 'user_followers_count',
                            'user_listed_count', 'user_favourites_count', 'user_statuses_count']
        columns_categorical = ['tw_source', 'tw_lang', 'user_screen_name', 'user_verified', 'user_geo_enabled',
                               'user_default_profile']
        X_train = data_df[begin_index_train:end_index_train]
        X_test = data_df[begin_index_test:end_index_test]

        # currently sentiment is not included in feature list
        # X_train['sentiment'] = X_train['sentiment'].fillna('missing')
        # X_test['sentiment'] = X_test['sentiment'].fillna('missing')

        # Instantiate encoder/scaler
        scaler = StandardScaler()
        enc = OneHotEncoder(sparse=False)
        min_max = MinMaxScaler()
        le = LabelEncoder()

        for col in X_test.columns.values:
            # Encoding only categorical variables
            try:
                if col not in columns_categorical:
                    continue
                print("type:", str(X_test[col].dtypes))
                if X_test[col].dtypes == 'object':
                    # Using whole data to form an exhaustive list of levels
                    data = X_train[col].append(X_test[col])
                    try:
                        le.fit(data.values)
                    except Exception as exception:
                        print('Oops!  An error occurred.  Try again...', exception)
                        continue
                    X_train[col] = le.transform(X_train[col])
                    X_test[col] = le.transform(X_test[col])
            except Exception as exception:
                print('Oops!  An error occurred.  Try again...', exception)
                continue

        # scaled_columns = min_max.fit_transform(data_df[columns_to_scale])
        # scaled_columns = scaler.fit_transform(data_df[columns_to_scale])
        # encoded_columns = ohe.fit_transform(data_df[columns_to_encode])

        # scaled_columns_train = scale(data_df_train[columns_to_scale])
        # scaled_columns_test = scale(data_df_test[columns_to_scale])

        # one hot encoding ready?
        # X_train = np.concatenate((npvectmeans_train, scaled_columns_train), axis=1)
        # X_test = np.concatenate((npvectmeans_test, scaled_columns_test), axis=1)

        X_train_1 = X_train
        X_test_1 = X_test

        columns_categorical_finale = []
        for col in columns_categorical:
            # creating an exhaustive list of all possible categorical values
            data = X_train[[col]].append(X_test[[col]])
            try:
                enc.fit(data)
            except Exception as exception:
                print('Oops!  An error occurred.  Try again...', exception)
                continue

            # Fitting One Hot Encoding on train data
            temp = enc.transform(X_train[[col]])
            # Changing the encoded features into a data frame with new column names
            temp = pd.DataFrame(temp, columns=[(col + "_" + str(i)) for i in data[col]
                                .value_counts().index])
            # In side by side concatenation index values should be same
            # Setting the index values similar to the X_train data frame
            temp = temp.set_index(X_train.index.values)
            # adding the new One Hot Encoded varibales to the train data frame
            X_train_1 = pd.concat([X_train_1, temp], axis=1)
            # fitting One Hot Encoding on test data
            temp = enc.transform(X_test[[col]])
            # changing it into data frame and adding column names
            temp = pd.DataFrame(temp, columns=[(col + "_" + str(i)) for i in data[col]
                                .value_counts().index])
            # Setting the index for proper concatenation
            print(list(temp.columns.values))
            for new_col in temp.columns.values:
                columns_categorical_finale.append(new_col)
            temp = temp.set_index(X_test.index.values)
            # adding the new One Hot Encoded varibales to test data frame
            X_test_1 = pd.concat([X_test_1, temp], axis=1)

        # todo scale
        # X_train_scale = scale(X_train_1)
        # X_test_scale = scale(X_test_1)

        X_train = X_train_1
        X_test = X_test_1

        # scaled_columns_train = scale(X_train[columns_to_scale])
        # scaled_columns_test = scale(X_test[columns_to_scale])

        scaled_columns_train = min_max.fit_transform(X_train[columns_to_scale])
        scaled_columns_test = min_max.fit_transform(X_test[columns_to_scale])

        one_hot_res_train = X_train_1[columns_categorical_finale]
        one_hot_res_test = X_test_1[columns_categorical_finale]

        X_train = np.concatenate((npvectmeans_train, scaled_columns_train, one_hot_res_train), axis=1)
        X_test = np.concatenate((npvectmeans_test, scaled_columns_test, one_hot_res_test), axis=1)

        if isyes1:
            y_train = (np.array(data_df_train["check"].replace("Y", 1).replace("N", 0)))
            y_test = (np.array(data_df_test["check"].replace("Y", 1).replace("N", 0)))
        else:
            y_train = (np.array(data_df_train["check"].replace("Y", 0).replace("N", 1)))
            y_test = (np.array(data_df_test["check"].replace("Y", 0).replace("N", 1)))

    except Exception as exception:
        print('Oops!  An error occurred.  Try again...', exception)
    return X_train, y_train, X_test, y_test


def generate_features_all_including_word2vec(begin_index, end_index, dimension, filename, isyes1):
    try:
        data_df = pd.read_csv(filename)

        data_df = data_df[begin_index:end_index]
        textvalues = np.array(data_df["text"])

        print("distribution of output classes: " + str(data_df["check"].value_counts() / data_df["check"].count()))

        # data_df[data_df.dtypes[(data_df.dtypes == "float64") | (data_df.dtypes == "int64")]
        #   .index.values].hist(figsize=[11, 11])

        vect_means = []

        for textvalue in textvalues:
            vect_mean = get_mean_vector_value_of_text(textvalue, dimension)
            vect_means.append(vect_mean)

        npvectmeans = np.asarray(vect_means)

        # Define which columns should be encoded vs scaled
        columns_to_scale = ['tw_retweet_count', 'tw_favorite_count', 'user_friends_count', 'user_followers_count',
                            'user_listed_count', 'user_favourites_count', 'user_statuses_count']

        scaled_columns = scale(data_df[columns_to_scale])

        # X = np.concatenate((npvectmeans, tw_retweet_count[:, None], tw_favorite_count[:, None], user_friends_count[:, None], user_followers_count[:, None], user_listed_count[:, None], user_favourites_count[:, None], user_statuses_count[:, None]), axis=1)
        X = np.concatenate((npvectmeans, scaled_columns), axis=1)
        if isyes1:
            y = (np.array(data_df["check"]
                          .replace("N", 0)
                          .replace("Y", 1)))
        else:
            y = (np.array(data_df["check"]
                          .replace("N", 1)
                          .replace("Y", 0)))

    except Exception as exception:
        print('Oops!  An error occurred.  Try again...', exception)
    return X, y


def train_1(begin_index, end_index, dimension, filename, isYes1):
    # This is based on single feature, which contains the average Vector value for each tweet.
    try:
        data_df = pd.read_csv(filename)

        X_train, y_train = get_train_test(data_df, begin_index, end_index, dimension)
        X_test, y_true = get_train_test(data_df, 21, 25, dimension)

        classifier = svm.LinearSVC()

        model = classifier.fit(X_train, y_train)
        print("ok")
        y_predicted = model.predict(X_test)

        print(sklearn.metrics.accuracy_score(y_true, y_predicted))
        print("good so far")

    except Exception as exception:
        print('Oops!  An error occurred.  Try again...', exception)


def get_yes_no_count(set):
    actual_yes = 0
    actual_no = 0
    for res in set:
        if res == 1:
            actual_yes += 1
        elif res == 0:
            actual_no += 1
    return actual_yes, actual_no


def get_cross_val_input(feature_type, vocab_dimension, filename, is_yes_1):
    if feature_type == 1:
        print("feature type 1: one single feature, mean vector value of Word2Vec")
        num_lines = sum(1 for line in open(filename, newline='', encoding='utf-8'))
        X_all, y_all = generate_feature_word2vec(0, num_lines, vocab_dimension,
                                                 filename, is_yes_1)
    elif feature_type == 3:
        print("feature type 3: n-gram with Tfidf")
        data_df = pd.read_csv(filename)
        X_all = data_df["text"].values
        y_all = data_df["check"].values
        if is_yes_1:
            y_all = (np.array(data_df["check"]
                              .replace("N", 0)
                              .replace("Y", 1)))
        else:
            y_all = (np.array(data_df["check"]
                              .replace("N", 1)
                              .replace("Y", 0)))

    return X_all, y_all


def get_train_test(feature_type, vocab_dimension, filename, is_yes_1, test_percentage, is_test, num_lines):
    train_start_index, train_end_index, test_start_index, test_end_index = get_train_test_indexes(is_test,
                                                                                                  num_lines,
                                                                                                  test_percentage)

    if feature_type == 1:
        print(
            "feature type 1: many features including mean of Word2Vec values, for other features scaling and one hot encoding enabled")
        X_train, y_train, X_test, y_test = generate_features_scaled_encoded_including_word2vec(train_start_index,
                                                                                               train_end_index,
                                                                                               test_start_index,
                                                                                               test_end_index,
                                                                                               vocab_dimension,
                                                                                               filename, is_yes_1)

    elif feature_type == 2:
        print("feature type 2: one single feature, mean vector value of Word2Vec")
        X_train, y_train = generate_feature_word2vec(train_start_index, train_end_index, vocab_dimension,
                                                     filename, is_yes_1)
        X_test, y_test = generate_feature_word2vec(test_start_index, test_end_index, vocab_dimension,
                                                   filename, is_yes_1)

    elif feature_type == 3:
        print("feature type 3: n-gram with Tfidf ")
        is_shuffle = False
        X_train, X_test, y_train, y_test = generate_feature_ngram(filename, test_percentage, is_shuffle, is_yes_1)

    else:
        return
    return X_train, y_train, X_test, y_test


def do_kfold(clf, X, y):
    print("started kfold")
    kf = KFold(n_splits=10)
    i = 0
    final_score = 0
    for train_ind, test_ind in kf.split(X):
        i += 1
        xtrain, ytrain = X[train_ind], y[train_ind]
        xtest, ytest = X[test_ind], y[test_ind]
        clf.fit(xtrain, ytrain)
        y_pred = clf.predict(xtest)
        score = np.mean(y_pred == ytest)
        final_score += score
        print(str(i) + ": accuracy:" + str(score))
        tn, fp, fn, tp = confusion_matrix(ytest, y_pred).ravel()

        print("tn:" + str(tn) + " fn:" + str(fn) + " tp:" + str(tp) + " fp:" + str(fp))

    print("average score: " + str(final_score / 10))
    print("completed kfold")


def old_code_do_tfidf(filename):
    try:
        text_clf = Pipeline([('vect', CountVectorizer(ngram_range=(1, 4), analyzer='word')),
                             ('tfidf', TfidfTransformer()),
                             ('clf', svm.SVC(kernel='linear')),
                             ])
        data_df = pd.read_csv(filename)

        train_x, test_x, train_y, test_y = train_test_split(data_df["text"], data_df["check"], test_size=0.2,
                                                            shuffle=True)
        print(train_x.shape, train_y.shape)
        print(test_x.shape, test_y.shape)
        text_clf.fit(train_x, train_y)

        predicted = text_clf.predict(test_x)
        print(np.mean(predicted == test_y))

        print(metrics.classification_report(test_y, predicted, target_names=None))
        print(metrics.confusion_matrix(test_y, predicted))

        probability_enabled = False
        if probability_enabled:
            X = np.array(data_df["text"])
            y = (np.array(data_df["check"]
                          .replace("N", 0)
                          .replace("Y", 1)))
            train_x, test_x, train_y, test_y = train_test_split(X, y, test_size=0.2,
                                                                shuffle=True)

            clf_prob = Pipeline([('vect', CountVectorizer(ngram_range=(1, 4), analyzer='word')),
                                 ('tfidf', TfidfTransformer()),
                                 ('clf', svm.SVC(kernel='linear', probability=True)),
                                 ])
            clf_prob.fit(train_x, train_y).predict_proba(test_x)
            a = clf_prob.predict_proba(test_x)
            y_pred_prob = clf_prob.predict_proba(test_x)[:, 1]
            print('Made predictions for test')
            print('ROC AUC:', roc_auc_score(test_y, y_pred_prob))
            print('True positive ratio at top 10%%: %0.2f%%' % (tp_ratio(test_y, y_pred_prob, pct=0.1) * 100))
            print('True positive ratio at top 20%%: %0.2f%%' % (tp_ratio(test_y, y_pred_prob, pct=0.2) * 100))
            print('True positive ratio at top 50%%: %0.2f%%' % (tp_ratio(test_y, y_pred_prob, pct=0.5) * 100))
            print('True positive ratio at top 75%%: %0.2f%%' % (tp_ratio(test_y, y_pred_prob, pct=0.75) * 100))

            y = (np.array(data_df["check"]
                          .replace("N", 1)
                          .replace("Y", 0)))

            train_x, test_x, train_y, test_y = train_test_split(X, y, test_size=0.2,
                                                                shuffle=True)

            clf_prob = Pipeline([('vect', CountVectorizer(ngram_range=(1, 4), analyzer='word')),
                                 ('tfidf', TfidfTransformer()),
                                 ('clf', svm.SVC(kernel='linear', probability=True)),
                                 ])
            clf_prob.fit(train_x, train_y).predict_proba(test_x)
            a = clf_prob.predict_proba(test_x)
            y_pred_prob = clf_prob.predict_proba(test_x)[:, 1]
            print('Made predictions for test')
            print('ROC AUC:', roc_auc_score(test_y, y_pred_prob))
            print('True positive ratio at top 10%%: %0.2f%%' % (tp_ratio(test_y, y_pred_prob, pct=0.1) * 100))
            print('True positive ratio at top 20%%: %0.2f%%' % (tp_ratio(test_y, y_pred_prob, pct=0.2) * 100))
            print('True positive ratio at top 50%%: %0.2f%%' % (tp_ratio(test_y, y_pred_prob, pct=0.5) * 100))
            print('True positive ratio at top 75%%: %0.2f%%' % (tp_ratio(test_y, y_pred_prob, pct=0.75) * 100))

        cross_val_predict_proba_enabled = False
        if cross_val_predict_proba_enabled:
            clf = Pipeline([('vect', CountVectorizer(ngram_range=(1, 4), analyzer='word')),
                            ('tfidf', TfidfTransformer()),
                            ('clf', svm.SVC(kernel='linear', probability=True)),
                            ])
            X = data_df["text"].values
            y = data_df["check"].values
            y = (np.array(data_df["check"]
                          .replace("N", 0)
                          .replace("Y", 1)))

            clf.fit(X, y)

            y_pred_prob = cross_val_predict(clf, X, y, cv=10, method='predict_proba')[:, 1]
            print('Made predictions for test')
            print('ROC AUC:', roc_auc_score(y, y_pred_prob))
            print('True positive ratio at top 10%%: %0.2f%%' % (tp_ratio(y, y_pred_prob, pct=0.1) * 100))
            print('True positive ratio at top 20%%: %0.2f%%' % (tp_ratio(y, y_pred_prob, pct=0.2) * 100))
            print('True positive ratio at top 50%%: %0.2f%%' % (tp_ratio(y, y_pred_prob, pct=0.5) * 100))
            print('True positive ratio at top 75%%: %0.2f%%' % (tp_ratio(y, y_pred_prob, pct=0.75) * 100))

            y = (np.array(data_df["check"]
                          .replace("N", 1)
                          .replace("Y", 0)))

            y_pred_prob = cross_val_predict(clf, X, y, cv=10, method='predict_proba')[:, 1]
            print('Made predictions for test')
            print('ROC AUC:', roc_auc_score(y, y_pred_prob))
            print('True positive ratio at top 10%%: %0.2f%%' % (tp_ratio(y, y_pred_prob, pct=0.1) * 100))
            print('True positive ratio at top 20%%: %0.2f%%' % (tp_ratio(y, y_pred_prob, pct=0.2) * 100))
            print('True positive ratio at top 50%%: %0.2f%%' % (tp_ratio(y, y_pred_prob, pct=0.5) * 100))
            print('True positive ratio at top 75%%: %0.2f%%' % (tp_ratio(y, y_pred_prob, pct=0.75) * 100))

        cross_val_enabled = False
        if cross_val_enabled:
            clf = Pipeline([('vect', CountVectorizer(ngram_range=(1, 4), analyzer='word')),
                            ('tfidf', TfidfTransformer()),
                            ('clf', svm.SVC(kernel='linear', probability=True)),
                            ])
            X = data_df["text"].values
            y = data_df["check"].values
            clf.fit(X, y)
            scores = cross_val_score(clf, X, y, cv=6)
            print("cross val scores: ", scores)

            print("cross val score mean: " + str(scores.mean()))
            # scoring = ['precision_macro', 'recall_macro']

            y_pred = cross_val_predict(clf, X, y, cv=10)

            tn, fp, fn, tp = confusion_matrix(y, y_pred).ravel()
            print("tn, fp, fn, tp")
            print(str(tn), str(fp), str(fn), str(tp))

        kfold_enabled = True
        if kfold_enabled:
            clf = Pipeline([('vect', CountVectorizer(ngram_range=(1, 4), analyzer='word')),
                            ('tfidf', TfidfTransformer()),
                            ('clf', svm.SVC(kernel='linear')),
                            ])

            X = data_df["text"].values
            y = data_df["check"].values
            do_kfold(clf, X, y)

        grid_search_enabled = False

        if grid_search_enabled:
            parameters = {'vect__ngram_range': [(1, 1), (1, 2)], 'tfidf__use_idf': (True, False),
                          'clf__alpha': (1e-2, 1e-3)}
            gs_clf = GridSearchCV(text_clf, parameters, n_jobs=-1)
            gs_clf = gs_clf.fit(train_x, train_y)
            print(gs_clf.best_score_)
            for param_name in sorted(parameters.keys()):
                print("%s: %r" % (param_name, gs_clf.best_params_[param_name]))
    except Exception as ex:
        print(ex)
        print("ok")


def get_file(file_id):
    if file_id == 0:
        filename = "C:/Users/emre2/Desktop/Museums/latest_data/test.csv"
    elif file_id == 1:
        filename = "C:/Users/emre2/Desktop/Museums/latest_data/scala_sample_fulltext_utf_header.csv"
    elif file_id == 2:
        filename = "C:/Users/emre2/Desktop/Museums/latest_data/pompei_sample_fulltext_utf_header.csv"
    elif file_id == 3:
        filename = "C:/Users/emre2/Desktop/Museums/latest_data/colosseo_sample_fulltext_utf_header.csv"
    elif file_id == 4:
        filename = "C:/Users/emre2/Desktop/Museums/latest_data/pompei_colosseo_scala_sample_fulltext_utf_header_rnd.csv"
    elif file_id == 5:
        filename = "C:/Users/emre2/Desktop/Museums/latest_data/merged_with_sentiment.csv"
    elif file_id == 6:
        filename = "C:/Users/emre2/Desktop/Museums/latest_data/pompei_colosseo_scala_sample_fulltext_utf_header_rnd_363x2.csv"

    return filename


def get_model(model_id, prob_enabled):
    C = 1  # SVM regularization parameter
    if model_id == 1:
        print("model type: SVM Linear Kernel. Prob enabled")
        clf = svm.SVC(kernel="linear", C=1, probability=prob_enabled)
    elif model_id == 2:
        print("model type: SVM RBF Kernel")
        clf = svm.SVC(kernel='rbf', gamma=0.7, C=C)
    elif model_id == 3:
        print("model type: Random Forest")
        clf = RandomForestClassifier(n_estimators=100)
    elif model_id == 4:
        print("model type: Logistic Regression")
        clf = LogisticRegression()
    elif model_id == 5:
        print("model type: KNeighborsClassifier")
        clf = KNeighborsClassifier(n_neighbors=5)
    elif model_id == 6:
        print("model type: n-grams with Tfidf")
        clf = Pipeline([('vect', CountVectorizer(ngram_range=(1,1), analyzer='word')),
                        ('tfidf', TfidfTransformer()),
                        ('clf', svm.SVC(kernel='linear', probability=prob_enabled)),
                        ])
    elif model_id == 7:
        print("model type: n-grams with Tfidf")
        clf = Pipeline([('vect', CountVectorizer(ngram_range=(1,3), analyzer='word')),
                        ('tfidf', TfidfTransformer()),
                        ('clf', LogisticRegression()),
                        ])
    return clf


def get_train_test_indexes(is_test, num_lines, percentage):
    if is_test:
        train_start_index = 0
        train_end_index = 17
        test_start_index = 17
        test_end_index = 26
    else:
        train_start_index = 0
        train_end_index = int(num_lines * percentage)
        test_start_index = train_end_index
        test_end_index = num_lines

    return train_start_index, train_end_index, test_start_index, test_end_index


def test():
    v = CountVectorizer(ngram_range=(1, 3))
    print(v.fit(["an apple a day keeps the doctor away"]).vocabulary_)


def main():
    try:
        test_enabled = False
        if test_enabled:
            test()
            exit(-1)

        vocab_dimension = 25

        train_vocab_enabled = False
        if train_vocab_enabled:
            train_word2vec_csv(vocab_dimension)
            return

        filename = get_file(4)

        num_lines = sum(1 for line in open(filename, newline='', encoding='utf-8'))

        model_id = 6
        # "model type:1 SVM Linear Kernel"
        # "model type:2 SVM RBF Kernel"
        # "model type:3 Random Forest"
        # "model type:4 Logistic Regression"
        # "model type:5 KNeighborsClassifier"
        # "model type:6 n-grams with Tfidf")
        clf = get_model(model_id, False)

        is_test = False

        feature_type = 3
        # "feature type 1: many features including mean of Word2Vec values, for other features scaling and one hot encoding enabled"
        # "feature type 2: one single feature, mean vector value of Word2Vec"
        # "feature type 3: n-gram with Tfidf "

        test_percentage = 0.2

        normal_run_enabled = True
        cross_val_enabled = True
        probabilistic_evaluation_enabled = False
        kfold_enabled = True

        if normal_run_enabled:
            print("\nSTARTED TRAIN-TEST SPLIT. PROBABILITY IS NOT ENABLED\n")

            is_yes_1 = False
            print("Y=0, N=1")
            X_train, y_train, X_test, y_test = get_train_test(feature_type, vocab_dimension,
                                                              filename, is_yes_1, test_percentage, is_test, num_lines)
            print("size of [train,test]: [" + str(len(X_train)) + "," + str(len(X_test)) + "]")

            clf.fit(X_train, y_train)
            if model_id == 6:
                count_vectorizer = clf.steps[0][1]
                vocabulary = count_vectorizer.vocabulary_
                print("n-gram vocabulary size: " + str(len(vocabulary)))

            # print(clf.coef_)
            y_pred = clf.predict(X_test)
            evaluate_train_test(clf, y_test, y_pred)
            print("\nCOMPLETED TRAIN-TEST SPLIT. PROBABILITY IS NOT ENABLED\n")

            if probabilistic_evaluation_enabled:
                print("\nSTARTED TRAIN-TEST SPLIT. PROBABILITY IS ENABLED\n")

                clf_prob = get_model(model_id, True)

                # is_yes_1 = True
                # print("Y=1, N=0")
                # X_train, y_train, X_test, y_test = get_train_test(feature_type, train_start_index, train_end_index,
                #                                                  test_start_index, test_end_index, vocab_dimension,
                #                                                  filename, is_yes_1)
                # evaluate_probability_based_train_test_model(clf_prob, X_train, y_train, X_test, y_test, is_yes_1)

                is_yes_1 = False
                print("Y=0, N=1")
                X_train, y_train, X_test, y_test = get_train_test(feature_type, vocab_dimension,
                                                                  filename, is_yes_1, test_percentage, is_test,
                                                                  num_lines)
                evaluate_probability_based_train_test_model(clf_prob, X_train, y_train, X_test, y_test)
                print("\n COMPLETED TRAIN-TEST SPLIT. PROBABILITY IS ENABLED\n")

        if cross_val_enabled:
            print("\nSTARTED CROSS VALIDATION. PROBABILITY IS NOT ENABLED\n")

            X_all, y_all = get_cross_val_input(feature_type, vocab_dimension, filename, True)
            clf.fit(X_all, y_all)
            evaluate_cross_validation(clf, X_all, y_all)
            print("\nCOMPLETED CROSS VALIDATION. PROBABILITY IS NOT ENABLED\n")

            if probabilistic_evaluation_enabled:
                print("\nSTARTED CROSS VALIDATION. PROBABILITY IS ENABLED\n")

                clf_prob = get_model(model_id, True)

                # is_yes_1 = True
                # print("Y=1, N=0")
                # X_all, y_all = get_cross_val_input(feature_type, vocab_dimension, filename, True)
                # evaluate_probability_based_cross_val_model(clf_prob, X_all, y_all, is_yes_1)

                is_yes_1 = False
                print("Y=0, N=1")
                X_all, y_all = get_cross_val_input(feature_type, vocab_dimension, filename, is_yes_1)

                evaluate_probability_based_cross_val_model(clf_prob, X_all, y_all, is_yes_1)
                print("\nCOMPLETED CROSS VALIDATION. PROBABILITY IS ENABLED\n")

        if kfold_enabled:
            print("\nSTARTED K-FOLD. PROBABILITY IS NOT ENABLED\n")

            is_yes_1 = False

            print("Y=0, N=1")
            X_all, y_all = get_cross_val_input(feature_type, vocab_dimension, filename, is_yes_1)
            do_kfold(clf, X_all, y_all)

            print("\nCOMPLETED K-FOLD. PROBABILITY IS NOT ENABLED\n")
    except Exception as exception:
        print('Oops!  An error occurred.  Try again...', exception)


if __name__ == "__main__":
    main()
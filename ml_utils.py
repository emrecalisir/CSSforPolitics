from sklearn.model_selection import cross_val_score, cross_val_predict, GridSearchCV, train_test_split, RandomizedSearchCV
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import roc_curve, auc, precision_score, recall_score, f1_score, accuracy_score, confusion_matrix, roc_auc_score
from sklearn import metrics, svm, datasets
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import label_binarize
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from imblearn.pipeline import Pipeline
from sklearn import svm
from xgboost import XGBClassifier
import matplotlib.pyplot as plt
import seaborn as sns
import utils as utils
from sklearn.pipeline import FeatureUnion
import TextStatsTransformer
import ItemSelector
import VipTransformer
import logging as logger
import pandas as pd
import globals
from sklearn.model_selection import StratifiedKFold
from scipy import interp
from time import time



def find_best_parameters(parameters, pipeline, X, y):
    #parameter_searcher = GridSearchCV(pipeline, parameters, cv=5, n_jobs=2, verbose=1)
    n_iter_search = 20
    parameter_searcher = RandomizedSearchCV(pipeline, param_distributions=parameters,
                                       n_iter=n_iter_search)
    logger.info("Performing grid search...")
    logger.info("pipeline:", [name for name, _ in pipeline.steps])
    logger.info("parameters:")
    logger.info(parameters)
    t0 = time()
    parameter_searcher.fit(X, y)
    logger.info("done in %0.3fs" % (time() - t0))

    logger.info("Best score: %0.3f" % parameter_searcher.best_score_)
    logger.info("Best parameters set:")
    best_parameters = parameter_searcher.best_estimator_.get_params()
    for param_name in sorted(parameters.keys()):
        logger.info("\t%s: %r" % (param_name, best_parameters[param_name]))
    logger.info("Completed grid search")


def get_model(model_name):
    if model_name == "svm-linear":
        return svm.SVC(kernel="linear", C=1)
    elif model_name == "svm-linear-prob":
        return svm.SVC(kernel="linear", C=1, probability=True)
    elif model_name == "svm-rbf":
        return svm.SVC(kernel='rbf', gamma=0.7, C=1)
    elif model_name == "xgboost":
        return XGBClassifier(seed=42)
    elif model_name == "rf":
        return RandomForestClassifier(n_estimators=20)
    elif model_name == "log":
        return LogisticRegression()
    elif model_name == "sgd":
        return SGDClassifier(**globals.SGD_BEST_PARAMS)


def draw_confusion_matrix(y_test, y_pred):
    # Model Evaluation here
    font = {'family': 'normal',
            'weight': 'bold',
            'size': 16}
    plt.rc('font', **font)
    plt.interactive(False)
    conf_mat = confusion_matrix(y_test, y_pred)
    sns.heatmap(conf_mat, annot=True, fmt='d', xticklabels=[1, 2],
                yticklabels=[1, 2])
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.show(block=True)


def print_confusion_matrix(is_binary_classification, y_test, y_pred):
    if is_binary_classification:
        tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
        logger.info("tn:" + str(tn) + " fn:" + str(fn) + " tp:" + str(tp) + " fp:" + str(fp))
    else:
        logger.info(confusion_matrix(y_test, y_pred))


def run_and_evaluate_cross_validation(is_binary_classification, is_scaling_enabled, classifier, X, y, is_plot_enabled=False):
    if is_scaling_enabled:
        X = scale_X(X)

    cross_val_scores = cross_val_score(classifier, X, y, cv=10)
    logger.info(str(cross_val_scores))
    logger.info("cross val score: " + str(cross_val_scores.mean()))
    y_pred = cross_val_predict(classifier, X, y, cv=10)
    print_false_predicted_entries(X, y_pred, y)
    logger.info(metrics.classification_report(y, y_pred, target_names=None))
    print_confusion_matrix(is_binary_classification, y, y_pred)

    if is_plot_enabled:
        draw_confusion_matrix(y, y_pred)


def run_prob_based_train_test_kfold_roc_curve_plot(classifier, X, y, is_plot_enabled=True,remove_low_pred=False):
    n_splits = 6
    cv = StratifiedKFold(n_splits=n_splits)
    tprs = []
    aucs = []
    mean_fpr = np.linspace(0, 1, 100)
    y = label_binarize(y, classes=[0, 1])
    logger.info(X)
    i = 0
    try:
        for train, test in cv.split(X, y):
            X = np.array(X)
            X_train = X[train]
            y_train = y[train]
            X_test = X[test]
            classifier.fit(X_train, y_train)
            probas_ = classifier.predict_proba(X_test)

            # probas_ = classifier.fit(X[train], y[train]).predict_proba(X[test])
            # Compute ROC curve and area the curve
            y_pred = probas_[:, 1]
            y_test = y[test]
            if remove_low_pred:
                y_test, y_pred = remove_low_pred_prob_prediction_entries(y_test, y_pred)
            fpr, tpr, thresholds = roc_curve(y_test, y_pred)
            tprs.append(interp(mean_fpr, fpr, tpr))
            tprs[-1][0] = 0.0
            roc_auc = auc(fpr, tpr)
            aucs.append(roc_auc)
            if is_plot_enabled:
                plt.plot(fpr, tpr, lw=1, alpha=0.3,
                     label='ROC fold %d (AUC = %0.2f)' % (i, roc_auc))

            i += 1



        mean_tpr = np.mean(tprs, axis=0)
        mean_tpr[-1] = 1.0
        mean_auc = auc(mean_fpr, mean_tpr)
        std_auc = np.std(aucs)
        logger.info("Mean AUC: " + str(mean_auc))
        if is_plot_enabled:
            plt.plot([0, 1], [0, 1], linestyle='--', lw=2, color='r',
                 label='Luck', alpha=.8)
            plt.plot(mean_fpr, mean_tpr, color='b',
                 label=r'Mean ROC (AUC = %0.2f $\pm$ %0.2f)' % (mean_auc, std_auc),
                 lw=2, alpha=.8)

            std_tpr = np.std(tprs, axis=0)
            tprs_upper = np.minimum(mean_tpr + std_tpr, 1)
            tprs_lower = np.maximum(mean_tpr - std_tpr, 0)
            plt.fill_between(mean_fpr, tprs_lower, tprs_upper, color='grey', alpha=.2,
                             label=r'$\pm$ 1 std. dev.')

            plt.xlim([-0.05, 1.05])
            plt.ylim([-0.05, 1.05])
            plt.xlabel('False Positive Rate')
            plt.ylabel('True Positive Rate')
            plt.title('Stratified k-fold with k='+str(n_splits))
            plt.legend(loc="lower right")
            plt.show()
    except Exception as e:
        print(e)


def run_and_evaluate_train_test(is_binary_classification, is_scaling_enabled, classifier, X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=True)
    classifier.fit(X_train, y_train)
    if is_binary_classification:
        logger.info("Natural TP rate=" + str(sum(y_test) / len(y_test)))

    if is_scaling_enabled:
        X_train, X_test = scale_train_test(X_train, X_test)

    logger.info(pd.Series(y_test).value_counts())
    y_pred = classifier.predict(X_test)
    logger.info("expected test results  :" + str(y_test))
    logger.info("predicted test results: " + str(y_pred))
    logger.info("accuracy score:" + str(accuracy_score(y_test, y_pred)))
    print_confusion_matrix(is_binary_classification, y_test, y_pred)
    logger.info(metrics.classification_report(y_test, y_pred, target_names=None))
    print_evaluation_stats(y_test, y_pred)
    draw_confusion_matrix(y_test, y_pred)
    print("ok")


def print_evaluation_stats(y_test, y_pred):
    logger.info("Accuracy Score:" + str(accuracy_score(y_test, y_pred)))
    logger.info("Precision Score:" + str(precision_score(y_test, y_pred, average='weighted')))
    logger.info("Recall Score:" + str(recall_score(y_test, y_pred, average='weighted')))
    logger.info("F1 Score:" + str(f1_score(y_test, y_pred, average='weighted')))


def tryy():
    iris = datasets.load_iris()
    X = iris.data
    y = iris.target

    # Binarize the output
    y = label_binarize(y, classes=[0, 1, 2])
    n_classes = y.shape[1]

    # Add noisy features to make the problem harder
    random_state = np.random.RandomState(0)
    n_samples, n_features = X.shape
    X = np.c_[X, random_state.randn(n_samples, 200 * n_features)]

    # shuffle and split training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.5,
                                                        random_state=0)

    # Learn to predict each class against the other
    classifier = OneVsRestClassifier(svm.SVC(kernel='linear', probability=True,
                                             random_state=random_state))
    y_score = classifier.fit(X_train, y_train).decision_function(X_test)

    # Compute ROC curve and ROC area for each class
    fpr = dict()
    tpr = dict()
    roc_auc = dict()
    for i in range(n_classes):
        fpr[i], tpr[i], _ = roc_curve(y_test[:, i], y_score[:, i])
        roc_auc[i] = auc(fpr[i], tpr[i])

    # Compute micro-average ROC curve and ROC area
    fpr["micro"], tpr["micro"], _ = roc_curve(y_test.ravel(), y_score.ravel())
    roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])


def multiclass_roc(X_train, X_test, y_train, y_test, n_classes):
    # tryy()
    classifier = OneVsRestClassifier(svm.SVC(kernel='linear', probability=True,
                                             random_state=False))
    y_score = classifier.fit(X_train, y_train).decision_function(X_test)

    # Compute ROC curve and ROC area for each class
    fpr = dict()
    tpr = dict()
    roc_auc = dict()
    for i in range(n_classes):
        fpr[i], tpr[i], _ = roc_curve(y_test[:, i], y_score[:, i])
        roc_auc[i] = auc(fpr[i], tpr[i])

    # Compute micro-average ROC curve and ROC area
    fpr["micro"], tpr["micro"], _ = roc_curve(y_test.ravel(), y_score.ravel())
    roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])

    draw_plt(0, fpr, tpr, roc_auc)
    draw_plt(1, fpr, tpr, roc_auc)
    draw_plt(2, fpr, tpr, roc_auc)


def draw_plt(lw, fpr, tpr, roc_auc):
    plt.figure()
    plt.plot(fpr[2], tpr[2], color='darkorange',
             lw=lw, label='ROC curve (area = %0.2f)' % roc_auc[2])
    plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic example')
    plt.legend(loc="lower right")
    plt.show()


def print_false_predicted_entries(inputs, predictions, labels):
    for input, prediction, label in zip(inputs, predictions, labels):
        if prediction != label:
            logger.info("### " + input + ' ### has been classified as ' + str(prediction) + ' and should be '+ str(label))


def convert_continuous_prob_to_label(y_pred):
    y_pred[y_pred > 0.5] = 1
    y_pred[y_pred <= 0.5] = 0
    y_pred = label_binarize(y_pred, classes=[0, 1])
    return y_pred


def remove_low_pred_prob_prediction_entries(y_test, y_pred):
    y_test_new = []
    y_pred_new = []
    counter_discarded = 0
    for i in range(0, len(y_pred)):
        if y_pred[i] > 0.4 and y_pred[i] < 0.6:
            logger.info(str(i) + "th record pred prob: " + str(y_pred[i]) + ". It'll be discarded from evaluation part")
            counter_discarded += 1
            continue;
        y_pred_new.append(y_pred[i])
        y_test_new.append(y_test[i])
    logger.info("number of discarded entries in evaluation part: " + str(counter_discarded))
    return y_test_new, y_pred_new


def old_remove_low_pred_prob_prediction_entries(y_test, y_pred):
    y_test_new = []
    y_pred_new = []
    counter_discarded = 0
    for i in range(0, len(y_pred)):
        pred_label = 0
        if y_pred[i] > 0.4 and y_pred[i] < 0.6:
            logger.info(str(i) + "th record pred prob: " + str(y_pred[i]) + ". It'll be discarded from evaluation part")
            counter_discarded += 1
            continue;
        if y_pred[i] > 0.5:
            pred_label = 1
        y_pred_new.append(pred_label)
        y_test_new.append(y_test[i])
    logger.info("number of discarded entries in evaluation part: " + str(counter_discarded))
    return y_test_new, y_pred_new


def run_prob_based_train_test_roc_curve_plot(is_binary_classification, is_scaling_enabled, classifier, X, y, remove_low_pred=False):
    y = label_binarize(y, classes=[0, 1])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=True)
    if is_scaling_enabled:
        X_train, X_test = scale_train_test(X_train, X_test)

    if not is_binary_classification:
        multiclass_roc(X_train, X_test, y_train, y_test, 3)
    else:
        classifier.fit(X_train, y_train)
        if is_binary_classification:
            logger.info("Natural TP rate=" + str(sum(y_test) / len(y_test)))
        y_pred_pair = classifier.predict_proba(X_test)
        y_pred = y_pred_pair[:, 1]

        # logger.info('Top 100 first' + str(len(y_test)) + ' records in test dataset) -> ' + str(
        #    ratio(y_test, y_pred_prob, 1)))

        logger.info("test ended")
        logger.info('ROC AUC:', roc_auc_score(y_test, y_pred))
        # for i in [x * 0.1 for x in range(1, 6)]:
        #    i = round(i, 1)
        #    logger.info('Top' + str(int(i * 100)) + 'percentile = (first ' + str(
        #        int(i * len(y_test))) + ' records in test dataset) -> ' + str(
        #        ratio(y_test, y_pred_prob, pct=i)))

        is_roc_plot_enabled = True
        if is_roc_plot_enabled:
            plot_roc(y_test, y_pred)

        if remove_low_pred:
            y_test, y_pred = remove_low_pred_prob_prediction_entries(y_test, y_pred)

        y_pred = convert_continuous_prob_to_label(y_pred)
        print_evaluation_stats(y_test, y_pred)
        print_false_predicted_entries(X_test, y_pred, y_test)


def svc_param_selection(X, y, nfolds):
    Cs = [0.001, 0.01, 0.1, 1, 10]
    gammas = [0.001, 0.01, 0.1, 1]
    param_grid = {'C': Cs, 'gamma': gammas}
    grid_search = GridSearchCV(svm.SVC(kernel='rbf'), param_grid, cv=nfolds)
    grid_search.fit(X, y)
    grid_search.best_params_
    logger.info(grid_search.best_params_)
    return grid_search.best_params_


def scale_X(X):
    scaler = MinMaxScaler()
    scaled_X = scaler.fit_transform(X)
    return scaled_X


def scale_train_test(X_train, X_test):
    scaler = MinMaxScaler()
    scaled_X_train = scaler.fit_transform(X_train)
    scaled_X_test = scaler.transform(X_test)
    return scaled_X_train, scaled_X_test


def plot_roc(y_test, preds):
    fpr, tpr, threshold = metrics.roc_curve(y_test, preds)
    roc_auc = metrics.auc(fpr, tpr)

    plt.title('Receiver Operating Characteristic')
    plt.plot(fpr, tpr, 'b', label='AUC = %0.2f' % roc_auc)
    plt.legend(loc='lower right')
    plt.plot([0, 1], [0, 1], 'r--')
    plt.xlim([0, 1])
    plt.ylim([0, 1])
    plt.ylabel('True Positive Rate')
    plt.xlabel('False Positive Rate')
    plt.show()


def get_pipeline(feature_type, vect, tfidf, clf):
    pipeline = None
    if feature_type == "single":
        pipeline = Pipeline([('vect', vect),
                             ('tfidf', tfidf),
                             ('clf', clf),
                             ])
    elif feature_type == "feature_union":
        pipeline = Pipeline([

            ('union', FeatureUnion(
                transformer_list=[
                    ('text_stats_pipe', Pipeline([
                        ('selector', ItemSelector(key=globals.PROCESSED_TEXT_COLUMN)),
                        ('text_stats', TextStatsTransformer()),
                        ('special_keywords', VipTransformer()),
                    ])),
                    ('ngram_tf_idf', Pipeline([
                        ('selector', ItemSelector(key=globals.PROCESSED_TEXT_COLUMN)),
                        ('vect', vect),
                        ('tf_idf', tfidf)
                    ]))
                ],

                # weight components in FeatureUnion
                transformer_weights={
                    'text_stats_pipe': 1,
                    'ngram_tf_idf': 0.3
                }
            )),
            ('clf', clf)
        ]
        )
    return pipeline
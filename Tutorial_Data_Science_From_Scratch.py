def accuracy(tp, fp, fn, tn):

    correct = tp + tn
    total = tp + fp + fn + tn
    return correct / total


def precision(tp, fp, fn, tn):
    # Precision measures how accurate our positive predictions were
    return tp / (tp + fp)


def correctness(measure, tp, fp, fn, tn):
    # fp (false positive) is a Type 1 error
    # fn (false negative) is a Type 2 error
    result = 0.0

    # accuracy is defined as the fraction of correct predictions
    if measure == 'accuracy':
        correct = tp + tn
        total = tp + fp + fn + tn
        result = correct / total

    # Precision measures how accurate our positive predictions were
    elif measure == 'precision':
        result = tp / (tp + fp)

    # recall measures what fraction of the positives our model identified
    elif measure == 'recall':
        result = tp / (tp + fn)

    # F1 score - harmonic mean
    elif measure == 'F1':
        p = tp / (tp + fp)
        r = tp / (tp + fn)
        result = 2 * p * r / (p + r)

    return result


def chapter11():
    # 5 babies out of every 1000 are named Luke
    # 14 people out of every 1000 get leukemia
    # The Test: predict leukemia if and only if the baby is named Luke (which sounds sort of like “leukemia”).
    print('accuracy: {}'.format(accuracy(70, 4930, 13930, 981070)))
    print('precision: {}'.format(precision(70, 4930, 13930, 981070)))


if __name__ == "__main__":
    chapter11()
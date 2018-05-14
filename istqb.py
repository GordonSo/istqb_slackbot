import os


def get_path(i=None, extension=None):
    if i is None and extension is None:
        return os.path.dirname(os.path.abspath(__file__)) + '/'
    else:
        return os.path.dirname(os.path.abspath(__file__)) + '/' + "tmp_{}".format(i) + extension


def load_question_and_answers():
    import pickle
    path = get_path()
    question_and_answer_path = path + 'qa.dat'
    print("loading pre-exacted question and answers")
    with open(question_and_answer_path, "rb") as f:
        mapped_question_and_answer = pickle.load(f)
    return mapped_question_and_answer


if __name__ == "__main__":
    print('start')
    questions_and_answers = load_question_and_answers()
    print('end')

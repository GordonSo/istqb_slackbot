import os
import requests
import tools.pdf2txt as pdf2txt
import re

session = requests.session()


def get_past_paper(num):
    pdf_mock_test_template = \
        "http://istqbexamcertification.com/{}/{}-{}.pdf"
    pdf_mock_test_url = pdf_mock_test_template.format(
        "wp-content/uploads/2014/09",
        "istqbExamCertification.com-ISTQB-Dumps-and-Mock-Tests-for-Foundation-Level-Paper",
        num + 1
    )
    mock_test_response = session.get(pdf_mock_test_url)  # stream=True
    mock_test_response.raise_for_status()
    return mock_test_response.content


def get_path(i=None, extension=None):
    if i is None and extension is None:
        return os.path.dirname(os.path.abspath(__file__)) + '/resource/'
    else:
        return os.path.dirname(os.path.abspath(__file__)) + '/resource/' + "tmp_{}".format(i) + extension


def extract_to_text(i):
    # The pdfReader variable is a readable object that will be parsed
    path = get_path()
    pdf_file_path = get_path(i, ".pdf")
    txt_file_path = get_path(i, ".txt")
    if not os.path.exists(path):
        os.makedirs(path)

    if not os.path.exists(txt_file_path):
        mock_test_file = get_past_paper(i)
        with open(pdf_file_path, "wb") as f:
            f.write(mock_test_file)

        s = 'pdf2txt -o%s %s' % (txt_file_path, pdf_file_path)
        pdf2txt.main(s.split(' ')[1:])
        os.remove(pdf_file_path)

    with open(txt_file_path, "r+", encoding="utf-8") as f:
        tmp_text = f.read()
        clean_mock_paper_text = filter_mock_paper_text(tmp_text)

    with open(txt_file_path, "wb") as f:
        f.write(str.encode(clean_mock_paper_text))

    return clean_mock_paper_text


def filter_mock_paper_text(text):
    dirty_strings = [
        "Download more sample papers at – istqbExamCertification.com Download more sample papers at – istqbExamCertification.com ",
        "Download more sample papers at – ",
        "istqbExamCertification.com Download more sample papers at – ",
        "istqbExamCertification.com "
    ]
    for dirty_string in dirty_strings:
        text = text.replace(dirty_string, "")
    return text


def extract_question_and_answers(clean_mock_paper_text, answer_split_str="Answers:", pivot_template="{}."):
    mock_test_pattern = r"(.*)({}\s?)(.*)".format(answer_split_str)
    mock_test_regex = re.compile(mock_test_pattern)
    g = mock_test_regex.findall(clean_mock_paper_text)
    questions_str = next(g.__iter__())[0]
    answers_str = next(g.__iter__())[2]

    # question_pattern = r"(\d+\.)(^(\d+\.))*"
    # questions_regex = re.compile
    questions_and_answers = []
    questions_title = questions_str.split(pivot_template.format(1))[0]
    questions_title = questions_str.split(pivot_template.format(1))[0] if questions_title is None else questions_title

    questions_str = questions_str.replace(questions_title, "")

    for char in [".", "(", ")", ":", "-", "Q"]:
        answers_str = answers_str.replace(char, "")

    for i in range(2, 99999, 1):
        pivot_str = pivot_template.format(i)

        if "{}".format(i) not in answers_str:
            questions_and_answers.append((questions_str, answers_str))
            break

        question = questions_str.split(pivot_str)[0]
        answer = answers_str.split(str(i))[0].strip()
        assert len(answer) < 6, "Got answer: {}".format(answer)
        questions_and_answers.append((question, answer))

        questions_str = questions_str.replace(question, "", 1)
        answers_str = answers_str.replace(answer, "", 1)

    return questions_and_answers


def load_question_and_answers():
    import pickle
    path = get_path()
    question_and_answer_path = path + 'qa.dat'

    mapped_question_and_answer = []
    if not os.path.exists(question_and_answer_path):
        for i in range(1, 34-1):
            if i in [14]:
                continue
            print('mapping_{}'.format(i))
            clean_mock_paper_text = extract_to_text(i)

            if i in range(19, 27):
                mapped_question_and_answer += extract_question_and_answers(clean_mock_paper_text, pivot_template="{}:")
            else:
                mapped_question_and_answer += extract_question_and_answers(clean_mock_paper_text)
            #assert len(mapped_question_and_answer) > 19, "Expected more questions then {} - {}".format(len(mapped_question_and_answer), mapped_question_and_answer[-1][0])
            print('mapping_{} - found {} question and answers'.format(i, len(mapped_question_and_answer)))

        with open(question_and_answer_path, "wb") as f:
            pickle.dump(mapped_question_and_answer, f)
    else:
        print("loading pre-exacted question and answers")
        with open(question_and_answer_path, "rb") as f:
            mapped_question_and_answer = pickle.load(f)

    past_q = "empty"
    for q, a in mapped_question_and_answer:
        assert len(q) > 0, past_q
        past_q = q
    return mapped_question_and_answer


if __name__ == "__main__":

    print('start')
    load_question_and_answers()
    print('end')
#!/usr/bin/python3
# from deep_translator import GoogleTranslator
from random import randint
import base64
import hashlib
import json
import sys
import os

import streamlit.components.v1 as components
import streamlit as st


from requests import get
def add_pronunciations(language):
    with open(f"languages/{language}.json") as lang:
        words = json.loads(lang.read())
        for word in words:
            word = word['text']

            print(word)

            word_hash = str(hashlib.sha256(word.encode('utf-8')).hexdigest())
            audio_path = f"languages/{language}/{word_hash}.mp3"
            if os.path.isfile(audio_path): continue

            try:
                url = f"https://apifree.forvo.com/key/94d8d2eecc51cf9285f73508c9dce1a7/format/json/action/word-pronunciations/word/{word}/language/{language}"
                r = get(url)
                if r.status_code != 200: 
                    print(r.status_code)
                    print(r.text)
                    continue
                r = json.loads(r.text)
                mp3_path = r['items'][0]['pathmp3']
                r = get(mp3_path, allow_redirects=True)

                file_name = str(hashlib.sha256(word.encode('utf-8')).hexdigest())
                print(file_name)
                with open(f"languages/{language}/{file_name}.mp3", 'wb') as mp3:
                    mp3.write(r.content)
            except Exception as e:
                print(f"[!] exception: {e}")
                continue
            # return

def create_lang(meanings, lang):
    with open(f'languages/{lang}.json', 'w') as lang_json:
        lang_dict = []
        counter = 0

        try:
            for m in meanings:
                # TODO: translate + pronunciation
                translated = GoogleTranslator(source='auto', target=lang).translate(m)
                print("{} > {}".format(m, translated))

                lang_dict.append(   {
                                        "text": translated,
                                        "pronunciation": m,
                                    })

                counter += 1
            lang_json.write(json.dumps(lang_dict, indent=4))
        except Exception as e:
            print(f"[!] {e}")

def build_db():
    with open('meanings.json') as f:
        meanings = json.load(f)

    langs = [
                "english",
                "hebrew",
                "italian",
                "french",
                "hindi",
                "spanish",
                "arabic",
                "russian",
                "japanese",
                "thai",
                "zh-CN"
            ]

    with open("languages.json", 'w') as langs_json:
        langs_json.write(json.dumps(langs, indent=4))

    for lang in langs:
        create_lang(meanings, lang)

def choose_random_word():
    with open("meanings.json") as meanings:
        meanings = json.loads(meanings.read())
        choise = randint(0, len(meanings) - 1)
        return choise, meanings[choise]

def get_available_languages():
    with open("languages.json") as languages:
        languages = json.loads(languages.read())
    return languages

def choose_random_language(languages):
    choise = randint(0, len(languages) - 1)
    return languages[choise]

def get_word(language, meaning_id):
    with open(f"languages/{language}.json") as language_file:
        words = json.loads(language_file.read())
        word = words[meaning_id]
        word['language'] = language
        return word

def get_audio(word):
    word_hash = str(hashlib.sha256(word['text'].encode('utf-8')).hexdigest())
    audio_path = f"languages/{word['language']}/{word_hash}.mp3"

    if not os.path.isfile(audio_path): return None

    with open(audio_path, 'rb') as audio: return audio.read()

def word_to_string(word):
    return f"{word['text']} [{word['pronunciation']}] ({word['language']})"

def generate_options(   meaning_id,
                        languages,
                        original_language,
                        num_of_options=3):
    # TODO: make it harder
    options = []

    while num_of_options > 0:
        _meaning_id, meaning_eng = choose_random_word()
        while meaning_id == _meaning_id:
            _meaning_id, meaning_eng = choose_random_word()

        language = choose_random_language(languages)
        while language == original_language:
            language = choose_random_language(languages)
        word = get_word(language, _meaning_id)

        retry = False
        for o in options:
            if o['text'] == word['text']:
                retry = True
                break
        if retry: continue

        options.append(word)
        num_of_options -= 1
    return options

def shuffle_options(options, answer):
    correct_index = randint(0, len(options))

    options.insert(correct_index, answer)

    return options, correct_index

def create_audio_button_html(audio_bytes):
    encoded_bytes = base64.b64encode(audio_bytes).decode('utf-8')
    button_html = """
    <audio id="question_audio" src="data:audio/wav;base64, __AUDIO_BYTES__"></audio>
    <button onclick="document.getElementById('question_audio').play();">&#xf144;</button>
    """
    button_html = button_html.replace("__AUDIO_BYTES__", encoded_bytes)
    return button_html

def render_question(question):
    # st.markdown(f"# {word_to_string(question)}")
    # audio_bytes = get_audio(question)
    # if audio_bytes:
        # question_html = """
        # <div>
            # <h1>
                # __QUESTION__
                # __AUDIO__
            # </h1>
        # </div>
        # """
        # question_html = question_html.replace("__QUESTION__", word_to_string(question))
        # question_html = question_html.replace("__AUDIO__", create_audio_button_html(audio_bytes))
    # else:
        # question_html = """
        # <div>
            # <h1>
                # __QUESTION__
            # </h1>
        # </div>
        # """
        # question_html = question_html.replace("__QUESTION__", word_to_string(question))

    # components.html(question_html,
                    # height=70)
    cols = st.columns(4)
    cols[0].markdown(f"# {question['text']}")
    cols[1].markdown(f"# {question['pronunciation']}")
    cols[2].markdown(f"# {question['language']}")
    audio_bytes = get_audio(question)
    if audio_bytes:
        cols[3].audio(audio_bytes, format='audio/wav')

def render_option_button(option, index):
    # st.button(word_to_string(option), key=f"option_{index}")
    cols = st.columns(4)
    # cols[0].markdown(f"# {question['text']}")
    cols[0].button(option['text'], key=f"option_{index}")
    cols[1].markdown(option['pronunciation'])
    cols[2].markdown(option['language'])
    audio_bytes = get_audio(option)
    if audio_bytes:
        cols[3].audio(audio_bytes, format='audio/wav')

def game():
    questions_languages = st.multiselect("questions languages pool",
                                get_available_languages(),
                                [   "english",
                                    "russian",
                                    "arabic",
                                    "japanese",
                                    # "french",
                                    # "spanish"
                                ])
    answers_languages = st.multiselect("answers languages pool",
                                get_available_languages(),
                                [   "english",
                                    "russian",
                                    "arabic",
                                    "japanese",
                                    # "french",
                                    # "spanish"
                                ])

    if "answer" in st.session_state:
        answer = st.session_state['answer']
        question = st.session_state['question']
        question_meaning = st.session_state['question_meaning']
        options = st.session_state['options']
        correct_index = st.session_state['correct_index']
        selections = [
                    st.session_state['option_0'],
                    st.session_state['option_1'],
                    st.session_state['option_2'],
                    st.session_state['option_3']
                  ]

        chosen_index = -1
        for i, selection in enumerate(selections):
            if selection:
                chosen_index = i
                break
        if chosen_index != -1:
            chosen = options[chosen_index]

            if selections[correct_index]:
                st.write(f"Correct!")
            else:
                st.write(f"Wrong!")

            st.write(f"{word_to_string(question)} == {word_to_string(answer)} ({get_word('english', question_meaning)['text']})")

    meaning_id, meaning_eng = choose_random_word()

    question_language = choose_random_language(questions_languages)

    question = get_word(question_language, meaning_id)
    render_question(question)

    answer_language = choose_random_language(answers_languages)
    while answer_language == question_language:
        answer_language = choose_random_language(answers_languages)

    answer = get_word(answer_language, meaning_id)

    options = generate_options(meaning_id, answers_languages, question_language)
    options, correct_index = shuffle_options(options, answer)

    st.session_state['question'] = question
    st.session_state['question_meaning'] = meaning_id
    st.session_state['answer'] = answer
    st.session_state['options'] = options
    st.session_state['correct_index'] = correct_index

    for i, option in enumerate(options):
        render_option_button(option, i)


if __name__=="__main__":
    st.set_page_config(layout="wide")
    game()

    # add_pronunciations(sys.argv[1])
    # word = get_word(sys.argv[1],int(sys.argv[2]))
    # print(f"{word['pronunciation']} => {word['text']}")

    # build_db()

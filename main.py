#!/usr/bin/python3
from deep_translator import GoogleTranslator
from random import randint
import streamlit as st
import base64
import hashlib
import json
import sys
import os


from requests import get
def add_pronunciations(language):
    with open(f"languages/{language}.json") as lang:
        words = json.loads(lang.read())
        for word in words:
            word = word['text']
            print(word)

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

def get_word(lang, meaning_id):
    with open(f"languages/{lang}.json") as lang:
        words = json.loads(lang.read())
        return words[meaning_id]

def get_audio(word, language):
    word_hash = str(hashlib.sha256(word['text'].encode('utf-8')).hexdigest())
    audio_path = f"languages/{language}/{word_hash}.mp3"

    if not os.path.isfile(audio_path): return None

    with open(audio_path, 'rb') as audio: return audio.read()

def word_to_string(word, language):
    return f"{word['text']} [{word['pronunciation']}] ({language})"

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
        # option = f"{word['text']} ({language})"
        option = word_to_string(word, language)
        if option in options: continue

        options.append(option)
        num_of_options -= 1
    return options

def shuffle_options(options, answer):
    correct_index = randint(0, len(options))

    options.insert(correct_index, answer)

    return options, correct_index

def game():
    selected_languages = st.multiselect("what languages to include?",
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

            st.write(f"{question} == {answer} ({get_word('english', question_meaning)['text']})")

    meaning_id, meaning_eng = choose_random_word()

    question_language = choose_random_language(selected_languages)

    question_word = get_word(question_language, meaning_id)

    # question = f"{question_word['text']} ({question_language})"
    question = word_to_string(question_word, question_language)
    # st.write(question)
    audio_bytes = get_audio(question_word, question_language)
    if audio_bytes:
        encoded_bytes = base64.b64encode(audio_bytes).decode('utf-8')
        audio_tag = f'<audio controls src="data:audio/wav;base64,{encoded_bytes}"></audio>'
        st.markdown(audio_tag, unsafe_allow_html=True)

    st.markdown(f"# {question}")

    answer_language = choose_random_language(selected_languages)
    while answer_language == question_language:
        answer_language = choose_random_language(selected_languages)

    answer_word = get_word(answer_language, meaning_id)
    # answer = f"{answer_word['text']} ({answer_language})"
    answer = word_to_string(answer_word, answer_language)

    options = generate_options(meaning_id, selected_languages, question_language)
    options, correct_index = shuffle_options(options, answer)

    st.session_state['question'] = question
    st.session_state['question_meaning'] = meaning_id
    st.session_state['answer'] = answer
    st.session_state['options'] = options
    st.session_state['correct_index'] = correct_index

    for i, option in enumerate(options):
        st.button(option, key=f"option_{i}")


if __name__=="__main__":
    game()

    # add_pronunciations(sys.argv[1])
    # word = get_word(sys.argv[1],int(sys.argv[2]))
    # print(f"{word['pronunciation']} => {word['text']}")

    # build_db()

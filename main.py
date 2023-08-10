#!/usr/bin/python3
import json


def create_english(meanings):
    with open('english.json', 'w') as english_json:
        english = []
        counter = 0
        for m in meanings:
            english.append({
                "text": m,
                "pronunication": m,
                "priority": counter
                })

            counter += 1
        english_json.write(json.dumps(english, indent=4))

from googletrans import Translator
def create_hebrew(meanings):
    with open('hebrew.json', 'w') as hebrew_json:
        hebrew = []
        counter = 0

        translator = Translator()

        for m in meanings:
            # TODO: translate + pronunciation
            result = translator.translate(m, dest='he')
            print(result)


            # hebrew.append({
                # "text": m,
                # "pronunication": m,
                # "priority": counter
                # })

            counter += 1
        hebrew_json.write(json.dumps(hebrew, indent=4))

def build_db():
    with open('meanings.json') as f:
        meanings = json.load(f)

    # create_english(meanings)
    create_hebrew(meanings)

def main():
    # build_db()

    with open('hebrew.json') as f:
        hebrew = json.load(f)

    print(hebrew[0])


if __name__ == '__main__':
    main()

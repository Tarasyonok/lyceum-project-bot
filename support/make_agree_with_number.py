import pymorphy3 as pm

morph_analyzer = pm.MorphAnalyzer()


def make_agree_with_number(word, num):
    word_parse = morph_analyzer.parse(word)[0]
    word_num = word_parse.make_agree_with_number(int(num)).word
    return f'{num} {word_num}'

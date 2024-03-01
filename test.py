import random

def generate_sentence(text, n=random.randint(1, 7), max_sentences=random.randint(1, 15)):
    words = text.split()
    word_dict = {}

    # Создаем словарь, где ключами являются кортежи из n слов,
    # а значениями - списки следующих слов
    for i in range(len(words) - n):
        key = tuple(words[i:i + n])
        value = words[i + n]
        if key in word_dict:
            word_dict[key].append(value)
        else:
            word_dict[key] = [value]

    # Выбираем случайное начальное слово
    current_words = random.choice(list(word_dict.keys()))
    sentence = ' '.join(current_words)

    # Генерируем предложение, выбирая следующее слово на основе вероятностей перехода
    sentence_count = 1
    while current_words in word_dict and sentence_count < max_sentences:
        next_word = random.choice(word_dict[current_words])
        sentence += ' ' + next_word
        current_words = tuple(sentence.split()[-n:])
        sentence_count += 1

    return sentence


book_text = """А где фул?
В интернете
Неплохой саунд и доброе
Доброе
На счёт сегодня, вы встречаете, да? Или без него?
Хз, спроси
Я бы хотел, чтобы он тоже пришел, если сможет
24 декабря
Пук пук
С помощью кода ток
Завтра три строчки ебану и чекну, сколько
А жаль
Завтра три строчки ебану и чекну, сколько
Давай
Там буквально три
Я так же итоги в ВК музыке
Я так же итоги в ВК музыке
А когда они будут, ты не знаешь?
Слушай
Ты не против, если она согласится и придёт к нам на НГ?
Нуууу хз
Такое, конечно, маловероятно
Но никогда не равно 0
Скорее против, чем за
Мне лично не кайф было бы
Просто если она празднует одна, мне жалко её немножко
Да и за хату страшно
Рандом типов приводить
Да и за хату страшно
Я лично за ней следить буду :/
Мне лично не кайф было бы
Я понимаю
Вот и спросил
Я не знаю ее
Может она вообще не согласится
Забей
И сидеть за одним столом и снова даже среди своих маску натягивать из-за одного человека"""
generated_sentence = generate_sentence(book_text, n=random.randint(1, 7), max_sentences=random.randint(1, 15))
print(generated_sentence)
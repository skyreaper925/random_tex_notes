import itertools

# Генерация всех перестановок букв алфавита длиной пять
alphabets = set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')

# Список запрещенных букв
forbidden_letters = {'е', 'й', 'а', 'н'}
alphabets = alphabets.difference(forbidden_letters)

for letter in itertools.permutations(alphabets, 5):
    word = "".join(letter)
    if (word.count('г') or word.count('р') or word.count('о')) and (word[0] != 'ы' or word[0] != 'ъ' or word[0] != 'ь'):
        print(word)

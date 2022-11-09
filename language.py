with open('languages.txt', encoding='utf8') as file:
    languages = file.read().split('\n')

    for line in languages:
        print(line)
        sprache, code = line.split(',')
        print(sprache)
        print(code)
        print()
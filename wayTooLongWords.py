n = int(input().strip())
words = [input().strip() for _ in range(n)]

for word in words:
    if len(word) > 10:
        print(f"{word[0]}{len(word) - 2}{word[-1]}")
    else:
        print(word)
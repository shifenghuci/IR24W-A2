import re


#Given a str, return a generator of token, with each token being defined as ay sequence of alphanumeric character, not include apostrophies
def yieldToken(text:str):
    # return a generator of token to lower case from a generator of file
    pattern = re.compile(r'[a-zA-Z0-9]+', re.IGNORECASE)  # pattern being any sequence of alphanumeric character
    return (token.lower() for token in pattern.findall(text))  # yield lowercase token

#Given a list of tokens and a freq_dict, update the word count based on the word tokens
def updateWordFrequencies(tokens, freq_dict)-> None:
    for token in tokens:
        freq_dict[token] = freq_dict.get(token, 0) + 1 # if new to dict, assign 1, if not, increment
    

# n being size of frequencies dictionary, O(n), traverse through dictionary item (list) and print each O(1) operation
def printFrequencies(frequencies):
    for (token, count) in sorted(frequencies.items(), key=lambda item: item[1],reverse=True):  # sort each pair by value
        print(f'{token}\t{count}')
    return









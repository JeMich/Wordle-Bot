import discord
import random
import re

#alias
client = discord.Client()  

#change these to whatever. STRONGLY recommend keeping your token file elsewhere to avoid tragic git accidents.
tokenFile = "../token.txt"
validWordsFile = "valid_solutions.csv"

#this causes me pain but I'm too lazy to google how to make a multi-line string in python
helpText = 'Use *!wb custom ||word||* to start a game with a custom word, \n *!wb verified ||word||* to start a game with a verified custom word, \n *!wb random* to start a game with a random verified word selected for you, \n *!wb guess word* to make a guess, \n and *!wb stop* to quit a game in progress.'

#globals
wordle = ""
guesses = 6
badLetters = []
goodLetters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
verifiedWords = []

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    global wordle
    wavingHand = "\U0001F44B"
    
    if message.author == client.user:
        return
    
    if message.content.startswith('!wb'):
        splitMessage = message.content.split()
        msglength = len(splitMessage)
        
        if msglength <= 1:
            await message.channel.send('I don\'t understand that. ' + helpText)
            return
        
        command = splitMessage[1]
        if command == 'hello' or command == 'Hello' or command == 'HELLO':
            await message.add_reaction(wavingHand)
            await message.channel.send("Hello! I'm ready when you are :^).")
            return
            
        elif command == 'help' or command == 'Help' or command == 'HELP':
            await message.channel.send(helpText)
            return
        
        elif (command == 'custom' or command == 'Custom' or command == 'CUSTOM') and msglength == 3:
            await handle_custom(message, splitMessage[2])
        
        elif (command == 'verified' or command == 'Verified' or command == 'VERIFIED') and msglength == 3:
            await handle_verified(message, splitMessage[2])
            
        elif (command == 'random' or command == 'Random' or command == 'RANDOM') and msglength == 2:
            await handle_random(message)
        
        elif (command == 'quit' or command == 'Quit' or command == 'QUIT') and msglength == 2:
            if wordle == "":
                await message.channel.send('There is no game in progress to quit.')
                return
            
            await message.channel.send('Ok, I\'ll stop the game. The word was ' + wordle)
            wordle = ""
            return
        
        elif (command == 'guess' or command == 'Guess' or command == 'GUESS') and wordle != "" and msglength == 3:        
            await handle_guess(message, splitMessage[2])
                
        else:
            await message.channel.send('I don\'t understand that. ' + helpText)

async def handle_custom(message, argument):
    global wordle
    
    if wordle != "":
        await message.channel.send('A game is already in progress. Please finish the game, or quit it using *!wb quit* before starting a new game.')
        return
        
    if not argument.startswith('||'):
        await message.channel.send('You should wrap your word in spoiler markers (||), so that no one sees it!')
        return
    
    cleanWord = re.sub(r'[^a-zA-Z]', '', argument.replace('|', '')) 
    if len(cleanWord) == 5:
        await message.delete()
        await start_game(cleanWord.upper(), message)
    else:
        await message.channel.send('Wordle words should be 5 letters long and only made of alphanumerics (and they should be real words, but I\'m trusting you on this one).')
        
async def handle_guess(message, guess):
    global guesses
    global wordle
    global goodLetters
    global badLetters
    
    greatAdjectives = ['Fantastic', 'Amazing', 'Outstanding', 'Incredible', 'Superb']
    goodAdjectives = ['Good', 'Nice', 'Solid', 'Reasonable', 'Clever']
    # Unicode for all emojis can be found here:  https://unicode.org/emoji/charts/full-emoji-list.html
    redBoxEmoji = "\U0001F7E5"
    yellowBoxEmoji = "\U0001F7E8"
    greenBoxEmoji = "\U0001F7E9"
    shockedEmoji = "\U0001F632"
    heartEmoji = "\U0002764"
    closeEmoji = "\U0001F628"
    cryEmoji = "\U0001F622"
    
    cleanGuess = re.sub(r'[^a-zA-Z]', '', guess) 
    if len(cleanGuess) != 5:
        await message.channel.send('Wordle guesses should be 5 letters exactly (and real words, but for custom wordles I\'ll cut you some slack)')
        return;
    
    guesses -= 1
    cleanGuess = cleanGuess.upper()
    guessEmojis = ['','','','','']
    duplicatesDict = {}
    
    for c in wordle:
        if c in duplicatesDict:
            duplicatesDict[c] += 1
        else:
            duplicatesDict[c] = 1
       
    # do two loops to prioritize green matches. There's probably a better way
    #but it's midnight soooooo...
    for i in range(len(cleanGuess)):
        letter = cleanGuess[i]
        if cleanGuess[i] == wordle[i]:
            duplicatesDict[letter] -= 1
            guessEmojis[i] = greenBoxEmoji
    
    for i in range(len(cleanGuess)):
        if guessEmojis[i] != '':
            continue
        
        letter = cleanGuess[i]
        if letter not in wordle:
            guessEmojis[i] = redBoxEmoji
            if letter not in badLetters:
                goodLetters.remove(letter)
                badLetters.append(letter)
        else:
            if duplicatesDict[letter] >= 1:
                duplicatesDict[letter] -= 1
                guessEmojis[i] = yellowBoxEmoji
            else:
                guessEmojis[i] = redBoxEmoji
    
    #construct the final response. If it's the right word, add congrats and react to the guess.
    #if it's the wrong word and they're out of guesses, sad reacts in the chat and tell them the word.
    #otherwise, just tell them how many guesses are left.
    elongatedGuess = ""
    for c in cleanGuess:
        elongatedGuess += c + "    "
    initialResponse = elongatedGuess + '\n' + ''.join(guessEmojis) + '\n' + 'Good Letters: ' + ', '.join(goodLetters) + '\n' + 'Bad Letters: ' + ', '.join(badLetters) + '\n' #python pogthon
    
    finalResponse = ""
    if cleanGuess != wordle and guesses > 0:
        finalResponse = initialResponse + 'You have ' + str(guesses) + ' guesses left.'
        await message.channel.send(finalResponse)
    else:
        if cleanGuess == wordle and guesses == 5:
            finalResponse = initialResponse + 'Either you\'re cheating, lucky, or you play too much wordle. . . but congrats, the word was ' + wordle
            await message.add_reaction(shockedEmoji)
        elif cleanGuess == wordle and guesses >= 3:
            finalResponse = initialResponse + random.choice(greatAdjectives) + ' guesses! The word was ' + wordle
            await message.add_reaction(shockedEmoji)
        elif cleanGuess == wordle and guesses > 0:
            finalResponse = initialResponse + random.choice(goodAdjectives) + ' guesses! The word was ' + wordle
            await message.add_reaction(heartEmoji)
        elif cleanGuess == wordle and guesses == 0:
            finalResponse = initialResponse + 'Close one! The word was indeed ' + wordle
            await message.add_reaction(closeEmoji)
        elif guesses == 0:
            finalResponse = initialResponse + 'Sorry, you didn\'t quite get it. The word was ' + wordle
            await message.add_reaction(cryEmoji)
        
        await message.channel.send(finalResponse)
        wordle = ""
                
async def handle_verified(message, argument):
    global wordle
    global verifiedWords
    
    if wordle != "":
        await message.channel.send('A game is already in progress. Please finish the game, or quit it using *!wb quit* before starting a new game.')
        return
        
    if not argument.startswith('||'):
        print(splitMessage)
        await message.channel.send('You should wrap your word in spoiler markers (||), so that no one sees it!')
        return
    
    cleanWord = re.sub(r'[^a-zA-Z]', '', argument.replace('|', '')) 
    if len(cleanWord) != 5:
        await message.channel.send("Wordle words need to be exactly 5 letters long, and contain only alphanumerics")
        return
    if cleanWord not in verifiedWords:
        await message.channel.send('Sorry, but that word isn\'t in my list of verified words.')
        return
        
    await message.delete()
    await start_game(cleanWord.upper(), message)
    return

async def handle_random(message):
    global wordle
    global verifiedWords
    
    await message.channel.send("I get to pick one? Hmm, let me think . . .")
    await start_game(random.choice(verifiedWords).upper(), message)
    
async def start_game(word, message):
    global wordle
    global goodLetters
    global badLetters
    global guesses
    
    wordle = word
    guesses = 6
    goodLetters = goodLetters + badLetters
    badLetters.clear()            
    goodLetters = sorted(goodLetters)
    await message.channel.send('Ok, I\'m ready to hear your guesses :). You have 6 attempts left.')     

     
file = open(tokenFile)
token = file.readline()
file.close()

with open(validWordsFile) as file:
    for line in file:
        strippedLine = line.strip()
        if len(strippedLine) != 5:
            print("Invalid word in verified words doc: " + strippedLine)
        else:
            verifiedWords.append(strippedLine)
                            
client.run(token)
try:
    from getch import getch        # Linux
except ImportError:
    from msvcrt import getch       # Windows
import os

def getTracklist(filename):
	tracklist = []
	dirName = os.path.dirname(__file__)
	f = open(f"{dirName}/{filename}", "r")
	lines = f.readlines()
	for line in lines:
		tracklist.append(line.strip())
	f.close()
	return tracklist

def printTracklist(lineNb, tracklist, songPlaying):
	textColor = 30
	backgroundColor = 47
	os.system('cls' if os.name == 'nt' else 'clear')
	count = 0	
	for line in tracklist:
		if count == lineNb:
			if count == songPlaying:
				textColor = 32
			else: 
				textColor = 30
				backgroundColor = 47
			print(f"\033[{textColor};{backgroundColor}m{line}\033[m")
		else:
			if count == songPlaying:
				textColor = 32
				print(f"\033[{textColor}m{line}\033[m")
			else:
				print(line)
		count += 1

def tracklistActions(songPlaying, maxLines, tracklist):
	lineNb = 0
	while(1):
		userInput = getKey()
		if userInput == 'q':
			os.system('cls' if os.name == 'nt' else 'clear')
			return -1
		elif userInput == 'up':
			lineNb = incrementLine(False, lineNb, maxLines)
			printTracklist(lineNb, tracklist, songPlaying)
		elif userInput == 'down':
			lineNb = incrementLine(True, lineNb, maxLines)
			printTracklist(lineNb, tracklist, songPlaying)
		elif userInput == '\n' or userInput == ' ':
			songPlaying = lineNb
			os.system('cls' if os.name == 'nt' else 'clear')
			return songPlaying
		continue

def incrementLine(increment, lineNb, maxLines):
	if increment:
		if lineNb < maxLines:
			lineNb += 1
	else: 
		if lineNb != 0:
			lineNb -= 1
	return lineNb

def getKey():
    userInput = getch()
    if userInput == '\x1b':
        escapeSequence = getch() + getch()
        arrowKeyMap = {
            '[A': 'up',
            '[B': 'down',
            '[C': 'right',
            '[D': 'left'
        }
        # Check if the escape sequence is in the arrow key map
        direction = arrowKeyMap.get(escapeSequence)
        if direction is not None:
            return direction
    # If it's not an arrow key or another recognized sequence, return the input character
    return userInput

if __name__ == '__main__':
	lineNb = 0
	songPlaying = 3
	maxLines = 40 - 1
	globalTracklist = getTracklist("tracklist.txt")
	printTracklist(lineNb, globalTracklist, songPlaying)
	tracklistActions(songPlaying, maxLines, globalTracklist)
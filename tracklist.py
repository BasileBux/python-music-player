try:
    from getch import getch        # Linux
except ImportError:
    from msvcrt import getch       # Windows
import os, subprocess

def getTracklist(filename):
	tracklist = []
	f = open(f"{filename}", "r")
	lines = f.readlines()
	for line in lines:
		tracklist.append(line.strip())
	f.close()
	return tracklist

def reframe(lineNb, height, maxLines):
	if lineNb >= (maxLines - height):
		maxBoundary = maxLines
		minBoundary = maxLines - height
	else: 
		minBoundary = lineNb
		maxBoundary = lineNb + height
	return minBoundary, maxBoundary

def manageInterval(lineNb, minBoundary, maxBoundary, maxLines):
	height = os.get_terminal_size()[1] - 2
	if (maxBoundary - minBoundary) != height:
		return reframe(lineNb, height, maxLines)
	if lineNb <= maxBoundary and lineNb >= minBoundary:
		return minBoundary, maxBoundary
	elif lineNb < minBoundary:
		return lineNb, maxBoundary - 1
	elif lineNb > maxBoundary:
		return minBoundary + 1, lineNb


def printTracklist(lineNb, tracklist, songPlaying, minBoundary, maxBoundary, maxLines):
	textColor = 30
	backgroundColor = 47
	os.system('cls' if os.name == 'nt' else 'clear')
	minBoundary, maxBoundary = manageInterval(lineNb, minBoundary, maxBoundary, maxLines)

	for i in range(len(tracklist)):
		if i < minBoundary:
			continue
		if i > maxBoundary:
			break

		if i == lineNb:
			if i == songPlaying: 
				textColor = 32
			else:
				textColor = 30
			print(f"\033[{textColor};{backgroundColor}m{tracklist[i]}\033[m")
		else: 
			if i == songPlaying:
				textColor = 32
				print(f"\033[{textColor}m{tracklist[i]}\033[m")
			else: 
				print(tracklist[i])
	return minBoundary, maxBoundary

def tracklistActions(songPlaying, maxLines, tracklist):
	lineNb = 0
	minBoundary = 0
	maxBoundary = os.get_terminal_size()[1] - 2
	while(1):
		userInput = getKey()
		if userInput == 'q' or userInput == '\x7f':
			os.system('cls' if os.name == 'nt' else 'clear')
			return -1
		elif userInput == 'up':
			lineNb = incrementLine(False, lineNb, maxLines)
			minBoundary, maxBoundary = printTracklist(lineNb, tracklist, songPlaying, minBoundary, maxBoundary, maxLines)
		elif userInput == 'down':
			lineNb = incrementLine(True, lineNb, maxLines)
			minBoundary, maxBoundary = printTracklist(lineNb, tracklist, songPlaying, minBoundary, maxBoundary, maxLines)
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
            '[D': 'left', 
			'\x7f': 'q'
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
	subprocess.run('', shell=True)
	globalTracklist = getTracklist("tracklist.txt")
	printTracklist(lineNb, globalTracklist, songPlaying, 0, (os.get_terminal_size()[1]) - 2, maxLines)
	tracklistActions(songPlaying, maxLines, globalTracklist)
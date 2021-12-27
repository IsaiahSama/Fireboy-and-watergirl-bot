# Fireboy-and-watergirl-bot

# About

This project is a bot that will play as either Fireboy or Watergirl, with a human player, so the player does not have to be all alone anymore :')

The entire bot will be coded using the Python programming language, and all of the code will be right here in this repository.

# Features

Bot should be able to recognise the basic dangers and elements of the level, such as 

- Opposing Liquids
- Green liquids
- Buttons and Levers
- The goal


## Voice Recognition
For (Hopeful) ease of use, I will be making use of voice recognition, in order to give the bot commands.

## Different Modes
As Fireboy and Watergirl is also a strategy game and has different modes, the bot should be able to react accordingly.

### Sync
Certain levels require both players to move at the same time, as such, the bot should be able to match the movements of the player exactly.

### Reverse Sync
Other levels, require both players to move in sync... but in opposite directions, and as such, the bot should be able to handle these as well.

### Roam
Bot should be able to make it's own way to the goal... Hopefully XD

### Switch
Whether because the player wishes to play as the other character, or simply wishes to help out the bot in a tight spot.

### Listen and Deafen
As with any software that uses Voice Recognition, it should be toggleable.

## TODO

1. Read keyboard inputs
2. React correspondingly to keyboard inputs
3. toggle between different modes
4. Recognize where on the screen it is
5. Recognize all other entities of relevance on the screen
6. Head towards entities such as gems and the other player
7. Avoid obstacles
8. Voice lines
9. Recognize voice commands
10. At least beat the first level

## Packages to be used

- Pyautogui for image recognition
- Keyboard for input detection and keyboard manipulation
- SpeechRecognition for recognizing speech

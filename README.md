# Scrabble Bot
A GADDAG-based computer Scrabble player written in Python.
![](board.png)

## Features

- A CLI to play full games of Scrabble
  - Can pit computers against each other or challenge them yourself
- The game of Scrabble recreated in Python
- An object-oriented implementation of the GADDAG data structure
- Move generation, validation, and evaluation algorithms

## Folder Hierarchy
    gaddag
      ↳ Source code for GADDAG data structure.
    
    scrabble_game
      ↳ Components needed to implement Scrabble.

    tests
      ↳ Test suite for Scrabble implementation.

## Usage
Clone the repository:

`git clone https://github.com/taaziz1/scrabble-bot`

Create the GADDAG locally by running `gen_gaddag.py`:

`py gen_gaddag.py`

Start interactive mode to play against a computer or with other humans:

`py play_interactive.py`
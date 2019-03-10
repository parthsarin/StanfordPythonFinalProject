"""
Methods for an AI that Q-learns how to drive a car.
"""
from pathlib import Path # for remembering the table
import numpy as np # for math
import collections # for storing (state, action) pairs
import pickle # for storing the table
import random
import errors
import itertools

import IO
import QLearning

MEMORY_FILE = 'memory/qlearning.mem'
REWARD_RANGE = 100
DEFAULT_LEARNING_RATE = .465

def process(state, NUM_TO_DIR):
	"""Decides which direction to move based on the current state.

	:state: The current state of the game.
	:type state: IO.State
	:NUM_TO_DIR: A dictionary that translates single-digit directions
	into a dictionary of booleans containing directional information.
	:LEARNING_RATE: A number between 0 and 1 that represents how fast
	the algorithm should learn.
	"""
	approximations = {}
	qtable = loadQTable()
	qlstate = QLearning.QLState(state)

	# Approximate the value of each action
	for direction in NUM_TO_DIR:
		key = QTableKey(qlstate, IO.Movement(**NUM_TO_DIR[direction]))
		approximations[direction] = qtable[key]

	print("Approximated ", approximations)

	# Sort and pick the action which gives the highest approximated value
	optimalDirection = sorted(approximations.items(), key=lambda x: x[1])[::-1][0]
	return IO.Movement(**NUM_TO_DIR[optimalDirection[0]])

def train(state, action, reward, LEARNING_RATE = DEFAULT_LEARNING_RATE):
	"""Train the AI by adding the reward for a particular (state, action) pair
	to the table.

	:state: The state from which the action was taken.
	:type state: IO.State
	:action: The action that was taken.
	:type action: IO.Movement
	:reward: The reward that was recieved.
	:type reward: float
	"""
	qlstate = QLearning.QLState(state) # convert to a QLState

	qtable = loadQTable() # load the Q-table
	
	# Update the value
	key = QTableKey(qlstate, action)
	qtable[key] = newValue(qlstate, action, reward, qtable, LEARNING_RATE)

	writeQTable(qtable) # write the table to the disk

def newValue(qlstate, action, known_reward, qtable, LEARNING_RATE):
	"""Calculates the new value that should replace a value from the Q-table
	after the AI has learned the reward it recieves from that point.

	:qlstate: The state from which the AI took the action.
	:type qlstate: QLearning.QLState
	:action: The action the AI took.
	:type action: IO.Movement
	:known_reward: The reward the AI recieved.
	:type known_reward: float
	:qtable: The Q-table that contains the previously-known 
	:type qtable: collections.defaultdict
	:LEARNING_RATE: A number between 0 and 1 that represents how fast
	the algorithm should learn.
	:type LEARNING_RATE: float
	"""
	old_reward = qtable[QTableKey(qlstate, action)]
	new_reward = (1-LEARNING_RATE) * old_reward + LEARNING_RATE * known_reward

	return new_reward

def QTableKey(qlstate, action):
	"""Constructs the key for the defaultdict that represents the
	Q-table.

	:qlstate: The state that the AI is in.
	:type qlstate: QLearning.QLState
	:action: The action the AI takes.
	:type action: IO.Movement
	"""
	return (tuple(qlstate.distances), tuple(qlstate.velocity), action.asNum())

def loadQTable():
	"""Load the Q-table from the memory file by depickling it.
	"""
	tablePath = Path(MEMORY_FILE)
	if tablePath.exists():
		with tablePath.open('rb') as f:
			return pickle.load(f)
	else:
		raise errors.NoMemTable("Please create a q-learning table at {}.".format(MEMORY_FILE))

def writeQTable(table):
	"""Write the table to the MEMORY_FILE using pickle.
	Note: This function *rewrites* the table!

	:table: The table to be written to the memory file.
	"""
	tablePath = Path(MEMORY_FILE)
	if tablePath.exists():
		with tablePath.open('wb') as f:
			pickle.dump(table, f)
	else:
		raise errors.NoMemTable("Please create a q-learning table at {}.".format(MEMORY_FILE))
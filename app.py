#! /usr/bin/python3

from flask import Flask, make_response, jsonify, render_template
from flask import request as flask_request
import random
import string
import redis
import os
import sys
import pickle

try:
	redis_db = redis.from_url(os.environ.get("REDIS_URL"))
except Exception as err:
	print("ERROR:", err)
	sys.exit(1)

app = Flask(__name__)

# deck codes
START_DECK = 0
POLICE_DECK = 1
GROC_DECK = 2
SCHOOL_DECK = 3
LIB_DECK = 4
HOS_DECK = 5
GAS_DECK = 6

def save_state(game_num, game_obj, save_prev):
	if redis_db.exists(game_num) and save_prev:
		prev_game = redis_db.get(game_num)
		redis_db.set(game_num+"_prev", prev_game)
	redis_db.set(game_num, pickle.dumps(game_obj))

# must be called after asserting that the game does indeed exist
def load_state(game_num):
	try:
		game = pickle.loads(redis_db.get(game_num))
		return game
	except Exception as err:
		print(err)
		return Game()

###################################
###          Game class         ###
###################################
class Game():
	def __init__(self, players_, sdeck_, pdeck_, gdeck_, scdeck_, ldeck_, hdeck_, gasdeck_):
		self.player_map         = players_
		self.start_cards        = sdeck_
		self.police_cards       = pdeck_
		self.grocery_cards      = gdeck_
		self.school_cards       = scdeck_
		self.library_cards      = ldeck_
		self.hospital_cards     = hdeck_
		self.gas_station_cards  = gasdeck_
		self.log                = ""
		self.crisis_deck        = []

	def get_deck(self, deckType):
		if deckType == START_DECK:
			return self.start_cards
		elif deckType == POLICE_DECK:
			return self.police_cards
		elif deckType == GROC_DECK:
			return self.grocery_cards
		elif deckType == SCHOOL_DECK:
			return self.school_cards
		elif deckType == LIB_DECK:
			return self.library_cards
		elif deckType == HOS_DECK:
			return self.hospital_cards
		elif deckType == GAS_DECK:
			return self.gas_station_cards

	def log_transaction(self, info):
		self.log += info + "<br>"
		print(info)

	def cardNums(self):
		return [self.police_cards.size, self.grocery_cards.size, self.school_cards.size, self.library_cards.size, self.hospital_cards.size, self.gas_station_cards.size, len(self.crisis_deck)]

	def __eq__(self, other):
		if self.player_map != other.player_map:
			return False
		if self.start_cards != other.start_cards:
			return False
		if self.police_cards != other.police_cards:
			return False
		if self.grocery_cards != other.grocery_cards:
			return False
		if self.school_cards != other.school_cards:
			return False
		if self.library_cards != other.library_cards:
			return False
		if self.hospital_cards != other.hospital_cards:
			return False
		if self.gas_station_cards != other.gas_station_cards:
			return False
		if self.crisis_deck != other.crisis_deck:
			return False
		return True
	def __ne__(self, other):
		return not self == other

###################################
###    Card class and Decks     ###
###################################
class Deck():
	def __init__(self, deckType):
		if deckType == START_DECK:
			self.size = 25
			self.cards = {"Food 1":10, "Junk": 5, "Fuel":5, "Medicine":5}
			self.name = "Starting Deck"
		elif deckType == POLICE_DECK:
			self.size = 20
			self.cards = {"Pistol":3, "Sniper Rifle":2, "Shotgun":1, "Fuel":4, "Junk":1, "Pad Lock":1, "Night Vision Goggles":1, "Walkie Talkie":1, "Food 1":3, "Outsider 1":1, "Outsider 2":2}
			self.name = "Police Station"
		elif deckType == GROC_DECK:
			self.size = 20
			self.cards = {"Junk":1, "Rotten Flesh":1, "Hammer":1, "Snow Shoes":1, "Wrench":1, "Food 1":2, "Food 2":2, "Food 3":2, "Medicine":6, "Outsider 1":1, "Outsider 2":2}
			self.name = "Grocery Store"
		elif deckType == SCHOOL_DECK:
			self.size = 20
			self.cards = {"Junk":1, "Scissors":1, "Megaphone":1, "Baseball Bat":1, "Food 1":3, "Food 2":3, "Guide to Leadership":1, "Beginner's Guide to Marshall Arts":1, "1,2,3 Barricades":1, "School Blueprints":1, "Medicine":3, "Outsider 1":2, "Outsider 3":1}
			self.name = "School"
		elif deckType == LIB_DECK:
			self.size = 20
			self.cards = {"Junk":1, "Reading Lamp":1, "Fuel":4, "A Journey in Jazzercise":1, "Survivor's Cookbook":1, "Police Station Blueprints":1, "Grocery Store Blueprints":1, "Library Blueprints":1, "Hospital Blueprints":1, "Gas Station Blueprints":1, "Food 1":4, "Outsider 1":1, "Outsider 2":2}
			self.name = "Library"
		elif deckType == HOS_DECK:
			self.size = 20
			self.cards = {"Junk":1, "Mop":1, "Flashlight":1, "Fuel":4, "Food 2":4, "Medicine":4, "Adrenaline Shot": 2, "Outsider 2":3}
			self.name = "Hospital"
		elif deckType == GAS_DECK:
			self.size = 20
			self.cards = {"Lighter":2, "Switchblade":2, "Shotgun":1, "Fuel":6, "Food 1":3, "Medicine":3, "Outsider 1":1, "Outsider 2":2}
			self.name = "Gas Station"
		else:
			raise ValueError("Wrong deck type!")

		self.deck = []
		for name, num in self.cards.items():
			for _ in range(num):
				self.deck.append(name)

		
		self.shuffle()
		return

	def shuffle(self):
		# shuffle 7 times because I noticed it wasn't working too well with just once
		random.shuffle(self.deck)
		random.shuffle(self.deck)
		random.shuffle(self.deck)
		random.shuffle(self.deck)
		random.shuffle(self.deck)
		random.shuffle(self.deck)
		random.shuffle(self.deck)

	def showTop(self, cardNum):
		ret = []
		for i in range(cardNum):
			ret.append(self.deck[i])
		return ret

	def removeCards(self, cardList, full_list):
		for card in cardList:
			self.deck.remove(card)

		# shift the cards that weren't taken to the bottom of the deck
		shiftBy = len(full_list) - len(cardList)
		if shiftBy > 0:
			botCards = self.deck[:shiftBy]
			self.deck = self.deck[shiftBy:]
			self.deck.extend(botCards)

		self.size = len(self.deck)
		return
	
	def __eq__(self, other):
		if self.deck == other.deck:
			return True
		else:
			return False
	def __ne__(self, other):
		return not self == other

# global variables
secret_obj = []
betray_obj = []
secret_file = open("obj_nonbetray.txt", "r")
betray_file = open("obj_betray.txt", "r")
for line in secret_file.readlines():
	secret_obj.append(line)
for line in betray_file.readlines():
	betray_obj.append(line)

All_cards = set() # every card in the game
for i in range(7):
	cards = Deck(i)
	for card in cards.deck:
		All_cards.add(card)

All_cards = sorted(list(All_cards))

###################################
## home page and initialization  ##
###################################
@app.route("/", methods=['GET'])
def home():
	return render_template('home.html') # join an existing game vs start a new game

@app.route("/init", methods=['POST'])
def init():
	try:
		players = flask_request.values.get('player_list')
		betray_variant = flask_request.values.get('betray') # 'none', 'standard', 'betrayer'
		assert(players != None)
		assert(betray_variant != None)
	except:
		print("Failed to get player list or betray_variant!")
		response = make_response("Failed to get player list or betray variant!", 400)
		return response

	print("Initializing new game!")
	start_cards         = Deck(START_DECK)
	police_cards        = Deck(POLICE_DECK)
	grocery_cards       = Deck(GROC_DECK)
	school_cards        = Deck(SCHOOL_DECK)
	library_cards       = Deck(LIB_DECK)
	hospital_cards      = Deck(HOS_DECK)
	gas_station_cards   = Deck(GAS_DECK)

	players = [x.strip() for x in players.split(",")]
	secret_cards = []
	if betray_variant == 'betrayer':
		secret_cards = random.sample(secret_obj, k=len(players))
		secret_cards.append(random.choice(betray_obj))
	else:
		secret_cards = random.sample(secret_obj, k=len(players)*2)
		if betray_variant != "none":
			secret_cards.append(random.choice(betray_obj))
	
	# shuffle 3 times because shuffling only once doesn't seem to work so well
	random.shuffle(secret_cards)
	random.shuffle(secret_cards)
	random.shuffle(secret_cards)

	player_obj_map = {}
	for i, player in enumerate(players):
		player_obj_map[player] = (secret_cards[i], False)

	game_code = ""
	while True:
		game_code = ''.join(random.sample(string.ascii_uppercase, k=4))
		if not redis_db.exists(game_code):
			break
	new_game = Game(player_obj_map, start_cards, police_cards, grocery_cards, school_cards, library_cards, hospital_cards, gas_station_cards)
	save_state(game_code, new_game, False)
	print("Done creating new game Game Code:", game_code)
	return make_response(jsonify(status="OK", gameCode=game_code), 200)

@app.route("/<gamecode_>/join", methods=['GET'])
def join(gamecode_):
	print("Someone attemping to join game", gamecode_)
	try:
		assert(gamecode_ != None)
		assert(redis_db.exists(gamecode_)) # joining current active game
	except:
		print('game code missing or incorrect')
		response = make_response("Game code missing or incorrect", 400)
		return response

	game = load_state(gamecode_)
	player_dict = game.player_map

	return render_template('playerList.html', player_list=player_dict.keys())

@app.route("/<gamecode_>/init_player", methods=['GET'])
def init_player(gamecode_):
	try:

		assert(gamecode_ != None)
		assert(redis_db.exists(gamecode_)) # joining current active game
	except:
		print('game code missing or incorrect')
		response = make_response("Game code missing or incorrect", 400)
		return response

	game = load_state(gamecode_)

	try:
		player_name = flask_request.values.get('player_name')
		assert(player_name != None)
		assert(player_name in game.player_map)
	except:
		print("Player name missing or not in list of players", player_name)
		response = make_response("Player name missing or not in list of players", 400)
		return response
	try:
		assert(game.player_map[player_name][1] == False) # no one has taken this player yet
	except:
		print("Player name is already taken", player_name)
		response = make_response("Player name is already taken", 400)
		return response

	game.player_map[player_name] = (game.player_map[player_name][0], True) # this objective has been taken
	starting_hand = []
	if len(game.player_map) > 2:
		starting_hand = game.start_cards.showTop(5)
		game.start_cards.removeCards(starting_hand, starting_hand)
	else:
		starting_hand = game.start_cards.showTop(7)
		game.start_cards.removeCards(starting_hand, starting_hand)

	save_state(gamecode_, game, False)

	return make_response(jsonify(status="OK", objective=game.player_map[player_name][0], cards=starting_hand), 200)

###################################
###  Managing Game in Progress  ###
###################################
@app.route("/<gamecode_>/<player_name>/game", methods=['GET'])
def game(gamecode_, player_name):
	try:
		assert(gamecode_ != None)
		assert(redis_db.exists(gamecode_)) # joining current active game
	except:
		print('game code missing or incorrect')
		response = make_response("Game code missing or incorrect", 400)
		return response

	return render_template('game.html', cards=All_cards)

@app.route("/<gamecode_>/<player_name>/crisis_deck", methods=['GET', 'PUT', 'DELETE'])
def crisis_deck(gamecode_, player_name):
	try:
		assert(gamecode_ != None)
		assert(redis_db.exists(gamecode_)) # joining current active game
	except:
		print('game code missing or incorrect')
		response = make_response("Game code missing or incorrect", 400)
		return response

	game = load_state(gamecode_)
	if flask_request.method == 'GET':
		if len(game.crisis_deck) > 0:
			game.log_transaction(player_name + " revealed the crisis deck")
			save_state(gamecode_, game, False)
			response = make_response("<br>".join(game.crisis_deck), 200)
			return response
		else:
			response = make_response("Crisis deck is empty", 400)
			return response
	elif flask_request.method == 'PUT': # adding a card to the crisis
		try:
			card = flask_request.values.get('card')
			loc = flask_request.values.get('loc')
			assert(card != None)
			assert(loc != None)
		except:
			print("Failed to get card or location for adding crisis_card")
			response = make_response("Failed to get card or location for adding crisis_card!", 400)
			return response

		toAdd = card + " from the " + loc
		game.crisis_deck.append(toAdd)
		game.log_transaction(player_name + " added a card to the crisis deck")
		save_state(gamecode_, game, True)
		response = make_response("Successfully added a card to the crisis", 200)
		return response
	else: # clearing the crisis deck
		game.crisis_deck = []
		game.log_transaction(player_name + " removed all cards from the crisis deck")
		save_state(gamecode_, game, True)
		response = make_response("Successfully cleared the crisis deck")
		return response

@app.route("/<gamecode_>/<player_name>/card_decks", methods=['GET', 'DELETE'])
def card_decks(gamecode_, player_name):
	try:
		assert(gamecode_ != None)
		assert(redis_db.exists(gamecode_)) # joining current active game
	except:
		print('game code missing or incorrect')
		response = make_response("Game code missing or incorrect", 400)
		return response

	try:    
		deckType = int(flask_request.values.get('deckType'))
		assert(deckType != None)
	except:
		print("Failed to get deckType")
		response = make_response("Failed to get deckType!", 400)
		return response

	game = load_state(gamecode_)
	if flask_request.method == 'GET':
		try:
			cardNum = int(flask_request.values.get('cardNum'))
			assert(cardNum != None)
		except:
			print("Failed to get cardNum")
			response = make_response("Failed to get cardNum!", 400)
			return response
		
		if cardNum == 1:
			game.log_transaction(player_name + " looked at the top card at the " + game.get_deck(deckType).name)
		else:
			game.log_transaction(player_name + " looked at the top " + str(cardNum) + " cards at the " + game.get_deck(deckType).name)
		cards = game.get_deck(deckType).showTop(cardNum)
		save_state(gamecode_, game, False)
		# display the top cardNum cards 
		return make_response(jsonify(cards=cards), 200)
	else: # DELETE request, tells us how what cards have been taken by a player's hand
		try:
			cardList = flask_request.values.get('cardList')
			fullList = flask_request.values.get('fullList')
			assert(cardList != None)
			assert(fullList != None)
		except:
			print("Failed to get cardList or fullList")
			response = make_response("Failed to get cardList or fullList!", 400)
			return response

		if len(cardList) == 0:
			game.log_transaction(player_name + " left the card(s) on the top of the " + game.get_deck(deckType).name + " deck")  
		else:
			cardList = [x.strip() for x in cardList.split(",")]
			fullList = [x.strip() for x in fullList.split(",")]
			if len(cardList) == 1:
				game.log_transaction(player_name + " took " + str(len(cardList)) + " card from the " + game.get_deck(deckType).name)
			elif len(cardList) > 1:
				game.log_transaction(player_name + " took " + str(len(cardList)) + " cards from the " + game.get_deck(deckType).name)
			
			cards = game.get_deck(deckType).removeCards(cardList, fullList)
			save_state(gamecode_, game, True)
		return make_response("OK", 200)

###################################
###  Function to delete games   ###
###################################
@app.route("/<gamecode_>/delete", methods=['DELETE'])
def delete_game(gamecode_):
	try:
		assert(gamecode_ != None)
		assert(redis_db.exists(gamecode_))
	except:
		print('game code missing or incorrect')
		response = make_response("Game code missing or incorrect", 400)
		return response

	redis_db.delete(gamecode_)
	response = make_response("Successfully deleted game", 200)
	return response

@app.route("/<gamecode_>/<player_name>/undo_action", methods=['PUT'])
def undo_action(gamecode_, player_name):
	try:
		assert(redis_db.exists(gamecode_)) # joining current active game
	except:
		print('game code missing or incorrect')
		response = make_response("Game code missing or incorrect", 400)
		return response

	prev_game = load_state(gamecode_+"_prev")
	game = load_state(gamecode_)
	if prev_game != game:
		prev_game.log = game.log
		prev_game.log_transaction(player_name + " undid previous take/add action")
		save_state(gamecode_, prev_game, False) # overwrite the current game state
		response = make_response("Sucessfully reverted game state", 200)
		return response
	else:
		response = make_response("Revert did nothing", 200)
		return response

###################################
# Functions for general game info #
###################################
@app.route("/<gamecode_>/log", methods=['GET'])
def getlog(gamecode_):
	try:
		assert(gamecode_ != None)
		assert(redis_db.exists(gamecode_)) # joining current active game
	except:
		print('game code missing or incorrect')
		response = make_response("Game code missing or incorrect", 400)
		return response

	game = load_state(gamecode_)
	return make_response(game.log, 200)

@app.route("/<gamecode_>/card_nums", methods=['GET'])
def get_nums(gamecode_):
	try:
		assert(gamecode_ != None)
		assert(redis_db.exists(gamecode_)) # joining current active game
	except:
		print('game code missing or incorrect')
		response = make_response("Game code missing or incorrect", 400)
		return response

	game = load_state(gamecode_)
	return make_response(jsonify(cardNums=game.cardNums()), 200)


if __name__ == '__main__':
	app.run(host='0.0.0.0', threaded=False)
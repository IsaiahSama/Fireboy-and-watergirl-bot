import keyboard as kb
import speech_recognition as sr
from playsound import playsound
from pyautogui import locateCenterOnScreen as lcos
from pyautogui import locateAllOnScreen as laos
from pyautogui import moveTo

from os import listdir
from time import sleep
from random import choice
from threading import Thread

wg_to_fb = {"w":"up", "a": "left", "d": "right"}
fb_to_wg = dict(zip(wg_to_fb.values(), wg_to_fb.keys()))

states = {"still": 0, "sync": 1, "mirror": 2, "roam": 3}
lines = {"None": 0, "switch":1, "alone": 2, "deafen": 3, "listen": 4, "yes": 5, "follow": 6}
inverse_lines = dict(zip(lines.values(), lines.keys()))

images = list(listdir("./images"))
images = ["./images/"+img for img in images]

bot_dict = {
	"water":{
			"mapping": wg_to_fb,
			"player": "./images/watergirl.png",
			"goal": "./images/water_door.png",
			"gem": "./images/water_gem.png",
			"liquid": ["./images/fire_liquid.png", "./images/dead_liquid.png"],
			"switch":"fire"
	},
	"fire":{
			"mapping": fb_to_wg,
			"player": "./images/fireboy.png",
			"goal": "./images/fire_door.png",
			"gem": "./images/fire_gem.png",
			"liquid": ["./images/water_liquid.png", "./images/dead_liquid.png"],
			"switch": "water"
	}
}

class TheGame:

	def __init__(self):
		self.running = True
		self.start()

	def start(self):
		"""This function starts everything"""
		print("We've begun")
		self.setup()
		# ---------------------------------------------------------- #
		quit_thread = Thread(target=self.waiter, daemon=True)
		quit_thread.start()
		find_self_thread = Thread(target=self.find_self, daemon=True)
		find_self_thread.start()
		state_thread = Thread(target=self.handle_state, daemon=True)
		state_thread.start()
		voice_recog = Thread(target=self.listen_to_speech, daemon=True)
		voice_recog.start()
		audio_thread = Thread(target=self.handle_audio, daemon=True)
		audio_thread.start()
		# ---------------------------------------------------------- #
		while self.running: sleep(1)

	def setup(self):
		self.bot = "water"
		self.state = states['sync']
		self.bot_box = None
		self.player_box = None
		self.line = None
		self.listening = True
		self.audio_dict = {}		
		fire_audio = [file for file in listdir("./audio") if file.startswith("fire")]
		water_audio = [file for file in listdir("./audio") if file.startswith("water")]

		key_lines = list(lines.keys())[1:]
		key_lines.append("turn")
		for key in key_lines:
			self.audio_dict[key] = {"fire": [audio for audio in fire_audio if key in audio], "water": [audio for audio in water_audio if key in audio]}
		self.mic_dict = {"stay": self.stay, "don't move": self.stay, "follow": self.follow, "come": self.follow, "switch": self.switch, "next": self.switch, "leave": self.leave, "mirror": self.mirror, "reverse":self.mirror, "deafen":self.deafen, "shush":self.deafen, "listen":self.listen, "attention": self.listen}

	def handle_audio(self):
		while self.running:
			block = False
			switch_count = 0
			if self.line:
				chosen = []
				if self.line == lines['switch']:
					chosen.extend(self.audio_dict['switch']['fire'])
					chosen.extend(self.audio_dict['switch']['water'])
					chosen.append(choice(self.audio_dict['turn'][self.bot]))
				else:
					chosen.append(choice(self.audio_dict[inverse_lines[self.line]][self.bot]))		
			
				for voice_line in chosen:
					print(voice_line)
					if "switch" in voice_line: switch_count += 1
					playsound("./audio/"+voice_line, block=block)
					if switch_count == 1: block = True
					
				self.line = lines['None']
			sleep(0.5)

	def find_gems(self) -> list:
		
		gems = sorted(list(laos(bot_dict[self.bot]['gem'], confidence=0.8)), reverse=True)
		different = [0, 0]
		updated_gems = []
		for gem in gems:
			if (gem[0] in range(different[0] - 10, different[0] + 10)) and (gem[1] in range(different[1] -10, different[1] + 10)):
				continue
			updated_gems.append(gem)
			different[0], different[1] = gem[0], gem[1]
		
		return updated_gems

	def find_liquids(self) -> list:
		bad_liquids = []
		for liquid in bot_dict[self.bot]['liquid']:
			bad_liquids.extend(sorted(list(laos(liquid, confidence=0.8)), reverse=True))
		
		filtered_liquids = []
		different = [0, 0]
		for box in bad_liquids:
			if (box[0] in range(different[0] - 10, different[0] + 10)) and (box[1] in range(different[1] -10, different[1] + 10)):
				continue
			different[0], different[1] = box[0], box[1]
			filtered_liquids.append(box)

		return filtered_liquids

	def find_goal(self):
		goal = lcos(bot_dict[self.bot]['goal'], confidence=0.9)
		return goal

	def find_self(self):
		while self.running:
			self.bot_box = lcos(bot_dict[self.bot]['player'], confidence=0.6)
			print("Bot Box", self.bot_box)
			self.player_box = lcos(bot_dict[bot_dict[self.bot]['switch']]['player'], confidence=0.6)
			sleep(0.5)

	def goto(self, target:tuple):
		if not self.bot_box:
			print("Bot could not be located at this time")
			return False

		if not target:
			print("Could not find the target")
			return False

		key = None

		while self.bot_box and self.bot_box[0] < target[0] and self.bot_box not in range(target[0]-20, target[0]+1): 
			key = list(bot_dict[self.bot]['mapping'].keys())[2]
			kb.press(key)
			sleep(0.5)

		while self.bot_box and self.bot_box[0] > target[0] and self.bot_box not in range(target[0]-1, target[0]+20):
			key = list(bot_dict[self.bot]['mapping'].keys())[1]
			kb.press(key)
			sleep(0.5)

		if key: kb.release(key)
		
	def waiter(self):
		kb.wait("q")

	def listen_to_speech(self):
		sample_rate = 48000
		data_size = 8192
		recog = sr.Recognizer()
		while self.running:
			with sr.Microphone(sample_rate=sample_rate, chunk_size=data_size) as source:
				if not self.listening: print("Note: Not listening")
				recog.adjust_for_ambient_noise(source, duration=0.5)
				print('Tell Something: ')
				speech = recog.listen(source, phrase_time_limit=2.7)
				try:
					text = recog.recognize_google(speech)
					print('You have said: ' + text)
					self.handle_mic(text)
				except sr.UnknownValueError:
   					print('Unable to recognize the audio')
				except sr.RequestError as e: 
   					print("Error from Google SR service; {}".format(e))
				except Exception as err:
					print(err)
			
	def handle_state(self):
		while self.running:
			try:
				kb.remove_all_hotkeys()
			except Exception as err:
				print("Couldn't remove all hotkeys")
			if self.state == states['still']:
				pass
			elif self.state == states['roam']:
				pass
			else:
				if self.bot == "water":
					kb.add_hotkey("up", lambda x="w": self.thread_key(x))
					kb.add_hotkey("left", lambda x="a": self.thread_key(x))
					kb.add_hotkey("right", lambda x="d": self.thread_key(x))
				else:
					kb.add_hotkey("w", lambda x="up": self.thread_key(x))
					kb.add_hotkey("a", lambda x="left": self.thread_key(x))
					kb.add_hotkey("d", lambda x="right": self.thread_key(x))
			self.set_default_keys()
			sleep(1)
			# print("Updated")

	def thread_key(self, key:str):
		thread = Thread(target=self.press_key, kwargs={"key":key})
		thread.start()

	def press_key(self, key:str):
		if self.state == states['mirror']:
			if key in ["a", "d"]: key = "a" if key == "d" else "a"
			elif key in ["right", "left"]: key = "right" if key == "left" else "right"
			# if key == "a": key = "d"
			# elif key == "d": key = "a"
			# elif key == "right": key = "left"
			# elif key == "left": key = "right"

		print(key, "was pressed")

		kb.press(key)
		try:
			while kb.is_pressed(bot_dict[self.bot]['mapping'][key]):
				sleep(0.01)
		except KeyError as err:
			print(err)
		kb.release(key)

	def handle_mic(self, text:str):
		if not self.listening and not any([val for val in ['listen', 'attention'] if val in text.lower()]): return False
		action = None
		for key, value in self.mic_dict.items():
			if key in text.lower():
				action = value
				break
		if action: action()

	def set_default_keys(self):
		kb.add_hotkey("q", self.leave)
		kb.add_hotkey("1", self.stay)
		kb.add_hotkey("f", self.follow)
		kb.add_hotkey("3", self.mirror)
		kb.add_hotkey("5", self.switch)	
		kb.add_hotkey("m", self.deafen)
		kb.add_hotkey("7", self.listen)
		kb.add_hotkey("x", self.scan)
	
	def switch(self):
		self.bot = "water" if self.bot == "fire" else "fire"
		self.line = lines['switch']
		print("Switched")

	def follow(self):
		self.state = states['sync']
		self.line = lines['follow']
		self.goto(self.player_box)
		print("Following")

	def mirror(self):
		self.state = states['mirror']
		self.line = lines['yes']
		print("Reversed Syncing")

	def stay(self):
		self.state = states['still']
		self.line = lines['alone']
		print("Staying still")

	def deafen(self):
		self.line = lines['deafen']
		self.listening = False
		print("Not listening")

	def listen(self):
		self.line = lines['listen']
		self.listening = True
		print("Listening")

	def scan(self):
		self.gems = self.find_gems()
		self.liquid = self.find_liquids()
		self.goal = self.find_goal()

	def leave(self):
		print("EMERGENCY EXIT!!!")
		self.running = False
		raise SystemExit
		
TheGame()

"""
def find_self(self):
		while self.running:
			player = lcos(bot_dict[self.bot]['player'], confidence=0.6)
			moveTo(player)
			sleep(1)
			gems = sorted(list(laos(bot_dict[self.bot]['gem'], confidence=0.8)), reverse=True)
			
			different = [0, 0]
			for gem in gems:
				if (gem[0] in range(different[0] - 10, different[0] + 10)) and (gem[1] in range(different[1] -10, different[1] + 10)):
					continue
				moveTo(gem)
				different[0], different[1] = gem[0], gem[1]
				sleep(1)
				

			bad_liquids = []
			for liquid in bot_dict[self.bot]['liquid']:
				bad_liquids.extend(sorted(list(laos(liquid, confidence=0.8)), reverse=True))
			
			different = [0, 0]
			for box in bad_liquids:
				if (box[0] in range(different[0] - 10, different[0] + 10)) and (box[1] in range(different[1] -10, different[1] + 10)):
					continue
				different[0] = box[0]
				different[1] = box[1]
				moveTo(box)
				sleep(1)				

			goal = lcos(bot_dict[self.bot]['goal'], confidence=0.9)
			moveTo(goal)
			sleep(1)"""

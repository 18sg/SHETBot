from twisted.words.protocols.irc import IRCClient
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet import reactor
from shet.client import ShetClient

import re


class ShetBotProtocol(IRCClient):
	nickname = "ShetBot"
	chan = "#18sg"
	
	root = "/irc/"
	
	# SHET Paths for users who will be added to the SHET tree
	user_paths = {
		"ShetBot"     : "/irc/bot/",
		"J616S"       : "/james/irc/",
		"jonathan"    : "/jonathan/irc/",
		"karl"        : "/karl/irc/",
		"matty3269"   : "/matt/irc/",
		"tomn"        : "/tom/irc/",
	}
	user_events = {}
	
	
	@property
	def bot_path(self):
		return self.user_paths[self.nickname]
	
	@property
	def users(self):
		return self.user_paths.keys()
	
	def signedOn(self):
		self.join(self.chan)
	
	
	def connectionMade(self):
		IRCClient.connectionMade(self)
		self.shet = ShetClient()
		self.shet.install()
		self.shet.root = self.root
		
		# Channel monitoring actions
		self.on_action = self.shet.add_event("on_action")
		self.on_say = self.shet.add_event("on_say")
		self.on_join = self.shet.add_event("on_join")
		self.on_quit = self.shet.add_event("on_quit")
		
		# This bot can be controlled over SHET
		self.shet.add_action(self.bot_path + "say", self.shet_say)
		self.shet.add_action(self.bot_path + "describe", self.shet_describe)
		self.shet.add_action(self.bot_path + "pm", self.shet_pm)
		
		# Can listen to bot's PMs
		self.on_bot_pm = self.shet.add_event(self.bot_path + "on_pm")
		self.on_bot_pm_action = self.shet.add_event(self.bot_path + "on_pm_action")
		
		# User monitoring/contacting
		for user in self.user_paths:
			path = self.user_paths[user]
			user_events = {}
			self.user_events[user] = user_events
			
			# Ways to contact the user (via the bot)
			self.shet.add_action(path + "say_to", self.get_say_to_fn(user))
			self.shet.add_action(path + "pm_to", self.get_pm_to_fn(user))
			
			# User's channel events
			user_events["on_join"] = self.shet.add_event(path + "on_join")
			user_events["on_quit"] = self.shet.add_event(path + "on_quit")
			user_events["on_say"] = self.shet.add_event(path + "on_say")
			user_events["on_action"] = self.shet.add_event(path + "on_action")
			
			# Events other can people trigger related to the user
			user_events["on_mention"] = self.shet.add_event(path + "on_mention")
			user_events["on_address"] = self.shet.add_event(path + "on_address")
			
			# User interractions with the bot
			user_events["on_mention_bot"] = self.shet.add_event(path + "on_mention_bot")
			user_events["on_address_bot"] = self.shet.add_event(path + "on_address_bot")
			user_events["on_pm_bot"] = self.shet.add_event(path + "on_pm_bot")
			user_events["on_pm_bot_action"] = self.shet.add_event(path + "on_pm_bot_action")
	
	
	def shet_say(self, msg):
		self.privmsg(self.nickname, self.chan, msg)
		self.say(self.chan, str(msg), 100)
	
	def shet_describe(self, msg):
		self.privmsg(self.nickname, self.chan, msg, action = True)
		self.describe(self.chan, str(msg))
	
	def shet_pm(self, user, msg):
		self.msg(user, str(msg), 100)
	
	
	def privmsg(self, userinfo, channel, message, action = False):
		"""
		Called by twisted on messages to the channel or the bot
		"""
		
		user = userinfo.partition("!")[0]
		
		if channel == self.chan:
			# Message to channel
			if action:
				self.on_action(user, message)
				self.user_events[user]["on_action"](message)
			else:
				self.on_say(user, message)
				self.user_events[user]["on_say"](message)
			
			
			self.notify_mentions(user, message)
			self.notify_addresses(user, message)
		
		elif channel == self.nickname:
			# Private message to bot
			if action:
				self.on_bot_pm_action(user, message)
				if user in self.users:
					self.user_events[user]["on_pm_bot_action"](message)
			else:
				self.on_bot_pm(user, message)
				if user in self.users:
					self.user_events[user]["on_pm_bot"](message)
			
			
	
	
	def action(self, *args):
		"""
		Called by twisted on /me's to the channel or the bot
		"""
		self.privmsg(*args, action = True)
	
	
	def userJoined(self, userinfo, channel):
		"""
		Called by twisted on a user arriving in the channel
		"""
		user = userinfo.partition("!")[0]
		self.on_join(user)
		if user in self.users:
			self.user_events[user]["on_join"]()
	
	
	def userQuit(self, userinfo, message):
		"""
		Called by twisted on a user quitting
		"""
		user = userinfo.partition("!")[0]
		self.on_quit(user, message)
		if user in self.users:
			self.user_events[user]["on_quit"](message)
	
	
	def get_pm_to_fn(self, user):
		"""
		Create a function which sends a PM to the given user.
		"""
		def pm_to(msg):
			self.shet_pm(user, msg)
		
		return pm_to
	
	
	def get_say_to_fn(self, user):
		"""
		Create a function which sends an addressed message to the given user.
		"""
		def say_to(msg):
			self.shet_say("%s: %s"%(user, msg))
		
		return say_to
	
	
	def mentioned(self, user, message):
		"""
		Is the user mentioned in the message?
		"""
		return re.search(r"\b%s\b"%user, message, re.I) is not None
	
	
	def addressed(self, user, message):
		"""
		Is the user addressed in the message?
		"""
		return re.match(r".*\b%s\b.*:"%user, message, re.I) is not None
	
	
	def notify_mentions(self, sender, message):
		"""
		Send notifications if any users are mentioned
		"""
		for user in self.users:
			if self.mentioned(user, message):
				self.user_events[user]["on_mention"](sender, message)
		
		# Did the bot get mentioned by a user
		if self.mentioned(self.nickname, message) and sender in self.users:
			self.user_events[sender]["on_mention_bot"](message)
	
	
	def notify_addresses(self, sender, message):
		"""
		Send notifications if any users are addressed
		"""
		for user in self.users:
			if self.addressed(user, message):
				self.user_events[user]["on_address"](sender, message)
		
		# Did the bot get addressed by a user
		if self.addressed(self.nickname, message) and sender in self.users:
			self.user_events[sender]["on_address_bot"](message)


class ShetBot(ReconnectingClientFactory):
	protocol = ShetBotProtocol


if __name__ == "__main__":
	reactor.connectTCP("18sg.net", 6667, ShetBot())
	reactor.run()

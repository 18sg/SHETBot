from twisted.words.protocols.irc import IRCClient
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet import reactor
from shet.client import ShetClient


class ShetBotProtocol(IRCClient):
	nickname = "ShetBot"
	chan = "#18sg"
	
	def signedOn(self):
		self.join(self.chan)
	
	def connectionMade(self):
		IRCClient.connectionMade(self)
		self.shet = ShetClient()
		self.shet.install()
		self.shet.root = "/irc/"
		self.shet.add_action("say", self.shet_say)
		self.shet.add_action("describe", self.shet_describe)
		self.action = self.shet.add_event("on_action")
		self.privmsg = self.shet.add_event("on_privmsg")
	
	def shet_say(self, msg):
		self.say(self.chan, str(msg), 100)
	
	def shet_describe(self, msg):
		self.describe(self.chan, str(msg))


class ShetBot(ReconnectingClientFactory):
	protocol = ShetBotProtocol


if __name__ == "__main__":
	reactor.connectTCP("18sg.net", 6667, ShetBot())
	reactor.run()

#! /usr/bin/env python
#
# signbot is an IRC Bot to talk to the Ace Monster Toys LED Sign
# based on an example program using ircbot.py by Joel Rosdahl <joel@rosdahl.net>
# 

"""AMT LED Sign Bot


commands are:

    display -- display something on the led sign

    clear -- clear the sign

    disconnect -- Disconnect the bot.  The bot will try to reconnect
                  after 60 seconds.

    die -- Let the bot cease to exist.
"""

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad, ip_quad_to_numstr
import serial

class Sign():
    def __init__(self, dev, id):
        self.signfile = serial.Serial(dev, 9600)
        self.id = str(id)
    
    def OneLine(self, message):
        self.signfile.write("<ID" + self.id + "><PA><FE>")
        self.signfile.write(message)
        self.signfile.write("\r\n")
        self.signfile.write("<ID" + self.id + "><RPA>\r\n")

    def TwoLine(self, top, bottom):
        self.signfile.write("<ID" + self.id + "><PA><FE><L1>")
        self.signfile.write(top)
        self.signfile.write("<L2>")
        self.signfile.write(bottom)
        self.signfile.write("\r\n")
        self.signfile.write("<ID" + self.id + "><RPA>\r\n")


class SignBot(SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port, sign):
        SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.irc_display_buffer = []
        self.message_display_buffer = "" 
        self.sign = sign

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments()[0])

    def on_pubmsg(self, c, e):
        a = e.arguments()[0].split(":", 1)
        if len(a) > 1 and irc_lower(a[0]) == irc_lower(self.connection.get_nickname()):
            self.do_command(e, a[1].strip())
        else:
            source_nick = nm_to_n(e.source())
            self.irc_display_buffer.append(source_nick + ": " + e.arguments()[0])
            if len(self.irc_display_buffer) > 3:
                self.irc_display_buffer = self.irc_display_buffer[1::]
            last_message = ""
            for message in self.irc_display_buffer:
                print message 
                self.sign.TwoLine(last_message, message)
                last_message = message
        return

    def on_dccmsg(self, c, e):
        return

    def on_dccchat(self, c, e):
        return

    def do_command(self, e, cmd):
        nick = nm_to_n(e.source())
        c = self.connection

        if cmd.startswith("display "):
           message = cmd[8:]
           if len(message) > 1:
               c.notice(nick, "I'm displaying " + message)
               print message
               self.message_display_buffer = message
               self.sign.OneLine(message)
        elif cmd == "clear":
           c.notice(nick, "I'm clearing the sign")
           self.message_display_buffer = ""
           self.sign.OneLine("")
           print 
        elif cmd == "disconnect":
            self.disconnect()
        elif cmd == "die":
            self.die()
        elif cmd == "help":
            c.notice(nick, "Hi " + nick + ", my name is " + self.get_version())
            c.notice(nick, "--- Here's what I can do:")
            c.notice(nick, "help")
            c.notice(nick, "disconnect")
            c.notice(nick, "die")
            c.notice(nick, "display - display something on the sign")
            c.notice(nick, "clear - clear the sign")
        else:
            c.notice(nick, "I don't know how to " + cmd)

    def get_version(self):
        return "signbot by atom_bomb <atom_bomb@rocketmail.com>"

def main():
    import sys

    server = "irc.freenode.org"
    port = 6667
    channel = "#botwar"
    nickname = "signbot"

    sign = Sign('/dev/ttyUSB0', 52)

    bot = SignBot(channel, nickname, server, port, sign)
    bot.start()

if __name__ == "__main__":
    main()

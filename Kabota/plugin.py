###
# Copyright (c) 2008, Kyle Johnson
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
###
import re
import sys, string
import supybot.conf as conf
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.ircmsgs as ircmsgs
import supybot.callbacks as callbacks
import supybot.world as world

class Kabota(callbacks.PluginRegexp):
    """A log searching utility plugin written by Kabaka
       from irc.sinsira.net. This is a partial version
       of the plugin."""
    threaded = True

    def runShCmd(self, irc, cmd):
        import commands
        for line in commands.getoutput(cmd).splitlines():
            irc.reply("Result: " + line, prefixNick=False)

    def sendmsg(self, irc, msg, args, dest, text):
        """<nick> <text>

        Sends <text> to <nick> in a privmsg.
        """
        irc.sendMsg(ircmsgs.privmsg(dest, text))
    sendmsg = wrap(sendmsg, ['owner', 'nick', 'text'])

    def logcount(self, irc, msg, args, channel, text):
        """[<channel>] <text>

        Counts the number of instances of <text> in my logs. <channel> is only
necessary if the command is called outside of the channel.
        """
        world.flush()
        filename=str(conf.supybot.directories.log) + "/ChannelLogger/"
        filename+= irc.network + "/" + channel + "/" + channel + ".log"
        self.runShCmd(irc, "grep -c \'" + text + "\' " + filename)
    logcount = wrap(logcount, ['owner', 'channel', 'text'])

    def logsearch(self, irc, msg, args, channel, text):
        """[<channel>] <text>

        greps for <text> in my logs. <channel> is only
necessary if the command is called outside of the channel.
        """
        world.flush()
        filename=str(conf.supybot.directories.log) + "/ChannelLogger/"
        filename+= irc.network + "/" + channel + "/" + channel + ".log"
        self.runShCmd(irc, "grep -m 4 \'" + text + "\' " + filename)
    logsearch = wrap(logsearch, ['owner', 'channel', 'text'])

    def first(self, irc, msg, args, channel, text):
        """[<channel>] <text>

        Find the first instance of <text> in my logs. <channel> is only
necessary if the command is called outside of the channel.
        """
        world.flush()
        filename=str(conf.supybot.directories.log) + "/ChannelLogger/"
        filename+= irc.network + "/" + channel + "/" + channel + ".log"
        f=open(filename,'r')

        line=f.readline()
        while line:
            if string.find(line, text) > -1:
                irc.reply(line[0:-1], prefixNick=False)
                return
            line=f.readline()
        irc.reply("I could not find that text in the logs.", prefixNick=True)

    first = wrap(first, ['channel', 'text'])

    def last(self, irc, msg, args, channel, text):
        """[<channel>] <text>

        Find the last instance of <text> in my logs. <channel> is not necessary
unless the command is called outside of the channel.
        """
        result="I could not find that text in the logs."
        prevResult="" + result
        world.flush()

        filename=str(conf.supybot.directories.log) + "/ChannelLogger/"
        filename+= irc.network + "/" + channel + "/" + channel + ".log"
        f=open(filename,'r')

        line=f.readline()

        lastWasMatch=False

        while line:
            lastWasMatch = False
            if string.find(line, text) > -1:
                prevResult = "" + result
                result=line[0:-1]
                lastWasMatch = True
            line=f.readline()

        if not lastWasMatch or prevResult == result:
            irc.reply(result, prefixNick=False)
            return
        irc.reply(prevResult, prefixNick=False)

    last = wrap(last, ['channel', 'text'])

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

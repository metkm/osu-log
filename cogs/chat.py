import os
import random
import asyncio
from discord.ext import commands


def fix_username(player) -> str:
    return player.lower().replace("_", "").replace(" ", "_")


class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @property
    def logs(self) -> list:
        return [file for file in os.listdir("Logs/")]


    def logs_in_language(self, language) -> list:
        return os.listdir(f"./Logs/{language}/")


    def language_logs(self, language) -> list:
        return os.listdir(f"./Logs/{language}/")


    async def add_reaction(self, ctx, msg, content_length):
        await msg.add_reaction("♿")

        def check_reaction(react, user):
            if react.message.id != msg.id:
                return False
            if user != ctx.message.author:
                return False
            if str(react.emoji) != "♿":
                return False
            return True

        try:
            await self.bot.wait_for("reaction_add", timeout=20, check=check_reaction)
            await msg.clear_reactions()
        except asyncio.TimeoutError:
            return await msg.clear_reactions()

        msg_splitted = msg.content.splitlines()[:3]
        language = msg_splitted[0].split(" ")[1].strip()
        date = msg_splitted[1].split(" ")[1].strip()
        index = int(msg_splitted[2].split(" ")[1].strip())

        if index < 5:
            index = 5

        chatmsg = "```"
        with open(f"./Logs/{language}/{date}", "r", encoding="utf-8", errors="replace") as file:
            content = file.read().splitlines()

            messages = content[index - 5: index + 6]

        for firsts in messages:
            chatmsg += f"{firsts} \n"

        chatmsg += "```"

        context_msg = await ctx.send(chatmsg)
        await self.add_reaction_scroll(ctx, index, language, context_msg, content_length, date)
        return await msg.clear_reactions()


    async def add_reaction_scroll(self, ctx, index, language, context_msg, content_length, date):
        if content_length < 5:
            return

        reacts_emojis = ["⏫", "⏬"]
        for react in reacts_emojis:
            await context_msg.add_reaction(react)

        def check_reactions_arrow(reaction, user):
            if reaction.message.id != context_msg.id:
                return False
            if user != ctx.author:
                return False
            if str(reaction.emoji) not in reacts_emojis:
                return False
            return True

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=25, check=check_reactions_arrow)
                await reaction.remove(user)
            except asyncio.TimeoutError:
                return await context_msg.clear_reactions()

            react_list = [reaction.emoji for reaction in reaction.message.reactions]
            if str(reaction.emoji) == "⏫":
                index -= 4

                if "⏬" not in react_list:
                    if not (index + 6) > content_length:
                        await context_msg.clear_reactions()
                        for react in reacts_emojis:
                            await context_msg.add_reaction(react)

                if index <= 5:
                    index = 5
                    await reaction.clear()

            elif str(reaction.emoji) == "⏬":
                index += 4

                if "⏫" not in react_list:
                    if not (index - 5) < 0:
                        await context_msg.clear_reactions()
                        for react in reacts_emojis:
                            await context_msg.add_reaction(react)

                if index >= content_length:
                    index = content_length - 6
                    await reaction.clear()

            chatmsg = "```"
            with open(f"./Logs/{language}/{date}", "r", encoding="utf-8", errors="replace") as file:
                content = file.read().splitlines()
                messages = content[index - 5: index + 6]

            for firsts in messages:
                chatmsg += f"{firsts} \n"

            chatmsg += "```"
            await context_msg.edit(content=chatmsg)


    @commands.command()
    async def random(self, ctx, language = None):
        """
            Gets Random Message
        """
        
        if not language:
            random_language = random.choice(self.logs)
        else:
            random_language = language

        random_date = random.choice(os.listdir(f"Logs/{random_language}/"))

        with open(f"./Logs/{random_language}/{random_date}", "r", encoding="utf-8", errors="replace") as file:
            content = file.read().splitlines()

        msg = random.choice(content)
        msg_index = content.index(msg)

        if msg_index < 5:
            msg_index = 5

        chatmsg = f"```{msg_index} | {msg} \n```"

        try:
            msg = await ctx.send(f"""
            **Language**: {random_language}\n**Date**: {random_date}\n**Index**: {msg_index}\n{chatmsg}
            """)
            await self.add_reaction(ctx, msg, len(content))
        except:

            pass


    @commands.command()
    async def chat(self, ctx, language, chatlimit=10):
        """
            Last 10 messages of given Language chat
        """
        
        if language not in self.logs:
            await ctx.send("Cant find language | Example: #turkish")
            return

        last_log_language = self.language_logs(language)[-1]
        with open(f"./Logs/{language}/{last_log_language}", "r", encoding="utf-8", errors="replace") as file:
            content = file.read().splitlines()[-chatlimit:]

        chatmsg = "```"
        for line in content:
            chatmsg += f"{line}\n"
        chatmsg += "```"

        try:
            await ctx.send(chatmsg)
        except Exception as err:
            await ctx.send(err)
            

    @commands.command()
    async def getrandom(self, ctx, player: fix_username, language):
        """ 
            Get random message from given player
        """

        player_messages = {}
        counter = 0

        msg = await ctx.send(f"Searching {player}")
        for date in self.logs_in_language(language):
            with open(f"./Logs/{language}/{date}", "r", encoding="utf-8", errors="replace") as file:
                content = file.read().splitlines()
                for index, line in enumerate(content):
                    line = line.strip()
                    
                    try:
                        username = line.split(">")[0].split("<")[-1].strip().lower()
                    except:
                        continue

                    if len(username) > 15:
                        continue

                    if player in username:
                        counter += 1

                        player_messages[str(counter)] = {
                            "language": language,
                            "date": date,
                            "index": index,
                            "line": line
                        }


        if len(player_messages) < 1:
            await msg.edit(content=f"Cant find message from {player} :pensive:")
            return

        random_message_id = random.choice(list(player_messages.keys()))
        random_message = player_messages[random_message_id]
        try:
            await msg.edit(
                content=f"**Language**: {random_message['language']}\n**Date**: {random_message['date']}\n**Index**: {random_message['index']}\n```{random_message['line']}```")
            await self.add_reaction(ctx, msg, len(content))
        except Exception as err:
            await ctx.send(err)
            await msg.clear_reactions()



def setup(bot):
    bot.add_cog(Chat(bot))

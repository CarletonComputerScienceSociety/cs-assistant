import sys

import discord
from discord import app_commands

from src.completions.services.completion_service import ask
from src.config import settings
from src.config.logger import get_logger

log = get_logger(__name__)


class CsAssistantBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self) -> None:
        guild = discord.Object(id=settings.discord_guild_id)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        log.info("discord_ready", self_user=self.user, guild=settings.discord_guild_id)

    async def on_message(self, message) -> None:
        # runs only in servers
        if message.guild is None:
            return

        # ignores other bots and itself
        if message.author.bot:
            return

        bot_standard_mention = f"<@{self.user.id}>"
        bot_nickname_mention = f"<@!{self.user.id}>"

        # triggering on explicit mention
        if bot_standard_mention in message.content or bot_nickname_mention in message.content:
            question = await question_assembler(message, self.user.id)

            # if question is just empty/non-text
            if question == "":
                return

            try:
                async with message.channel.typing():
                    answer = await ask(question=question)
            except Exception as e:
                await message.reply("❌ I couldn't process this request, please try again later.")
                log.error("discord_ask_failed", error=str(e))
                return

            content = render_answer_content(answer)
            await message.reply(content)


client = CsAssistantBot()


@client.tree.command(name="ask", description="Receive advice for Carleton CS")
@app_commands.describe(question="Your question")
async def ask_command(interaction: discord.Interaction, question: str) -> None:
    await interaction.response.defer()
    log.info("discord_ask_received", interaction_id=interaction.id, question=question)

    try:
        answer = await ask(question=question)
    except Exception as e:
        await interaction.followup.send(
            "❌ I couldn't process this request, please try again later."
        )
        log.error("discord_ask_failed", interaction_id=interaction.id, error=str(e))
        return

    content = render_answer_content(answer)
    await interaction.followup.send(content)
    log.info("discord_ask_completed", interaction_id=interaction.id)


async def question_assembler(message, bot_id: int) -> str:
    # if message is reply to a question
    referenced_text = ""
    if message.reference and message.reference.message_id:
        try:
            referenced_message = await message.channel.fetch_message(message.reference.message_id)
            referenced_text = referenced_message.content
        except discord.NotFound:
            log.info(
                "referenced_message_not_found",
                channel_id=message.channel.id,
                channel_name=message.channel.name,
                guild_id=message.guild.id,
                target_message_id=message.reference.message_id,
            )
        except discord.Forbidden:
            log.warning(
                "referenced_message_forbidden",
                channel_id=message.channel.id,
                channel_name=message.channel.name,
                guild_id=message.guild.id,
                target_message_id=message.reference.message_id,
            )

    return question_assembler_helper(
        content=message.content,
        bot_id=bot_id,
        referenced_text=referenced_text,
    )


def question_assembler_helper(*, content: str, bot_id: int, referenced_text: str = "") -> str:
    mention_text = strip_bot_mention(content, bot_id)

    if referenced_text:
        return referenced_text + "\n\n" + mention_text
    return mention_text


def strip_bot_mention(content: str, bot_id: int) -> str:
    mention_text = content
    for x in {f"<@{bot_id}>", f"<@!{bot_id}>"}:
        mention_text = mention_text.replace(x, "")
    return mention_text.strip()


def render_answer_content(answer) -> str:
    content = answer.text
    if answer.sources:
        content += "\n\n**Sources:**\n" + "\n".join(f"• {source.url}" for source in answer.sources)
    return content


if __name__ == "__main__":
    if settings.discord_bot_token is None or settings.discord_guild_id is None:
        print("Discord config is incomplete or nonexistent", file=sys.stderr)
        sys.exit(1)

    client.run(settings.discord_bot_token)

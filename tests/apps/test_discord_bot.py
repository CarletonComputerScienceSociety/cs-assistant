from src.apps.discord_bot import question_assembler_helper, strip_bot_mention

BOT_ID = 123456789


def test_plain_mention():
    message = f"<@{BOT_ID}> test question"
    assert (strip_bot_mention(message, BOT_ID)) == "test question"


def test_both_mentions():
    message = f"<@{BOT_ID}> <@!{BOT_ID}> test question"
    assert (strip_bot_mention(message, BOT_ID)) == "test question"


def test_concatenate_reference_and_original():
    message = f"<@{BOT_ID}> test question"
    referenced_text = "Original text"
    assert (
        question_assembler_helper(content=message, bot_id=BOT_ID, referenced_text=referenced_text)
        == "Original text\n\ntest question"
    )


def test_empty_response():
    message = f"<@{BOT_ID}>"
    assert (question_assembler_helper(content=message, bot_id=BOT_ID)) == ""

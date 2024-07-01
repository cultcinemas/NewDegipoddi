import asyncio
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import (
    ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, 
    DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, 
    AUTO_DELETE_MESSAGE_1, AUTO_DELETE_MESSAGE_2
)
from database.database import add_user, del_user, full_userbase, present_user
from helper_func import is_notsubscribed, decode, get_messages, auto_delete_message

loop = asyncio.get_event_loop()

@Bot.on_message(filters.command('start') & filters.private)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id

    if fsub_ids := await is_notsubscribed(client, user_id):
        btn = []
        for fid in fsub_ids:
            try:
                invite_link = await client.create_chat_invite_link(fid)
                chat_info = await client.get_chat(fid)
            except:
                continue
            else:
                btn.append([InlineKeyboardButton(chat_info.title, url=invite_link.invite_link)])

        if btn:
            try:
                btn.append([InlineKeyboardButton('Try Again', url=f"https://t.me/{client.username}?start={message.command[1]}")])
            except IndexError:
                pass
            text = FORCE_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=user_id
            )
            await message.reply_text(
                text=text,
                quote=True,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
                disable_notification=True,
                reply_markup=InlineKeyboardMarkup(btn)
            )
            return

    if not await present_user(user_id):
        try:
            await add_user(user_id)
        except:
            pass

    text = message.text
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
        except:
            return
        
        string = await decode(base64_string)
        argument = string.split("-")
        
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
            except:
                return
            if start <= end:
                ids = range(start, end + 1)
            else:
                ids = []
                i = start
                while True:
                    ids.append(i)
                    i -= 1
                    if i < end:
                        break
        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except:
                return

        temp_msg = await message.reply("Please wait. 5 min Bitlu Videos On The Way")

        try:
            messages = await get_messages(client, ids)
        except:
            await message.reply_text("Something went wrong..!")
            return

        await temp_msg.delete()

        
                    protect_content=PROTECT_CONTENT
                )
                msgs.append(cmsg)
                await asyncio.sleep(0.5)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                cmsg = await msg.copy(
                    chat_id=message.from_user.id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                    protect_content=PROTECT_CONTENT
                )
                msgs.append(cmsg)
            except:
                pass

        # Senfor msg in messages:
            if CUSTOM_CAPTION and msg.document:
                caption = CUSTOM_CAPTION.format(
                    previouscaption="" if not msg.caption else msg.caption.html,
                    filename=msg.document.file_name
                )
            else:
                caption = "" if not msg.caption else msg.caption.html

            reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None

            try:
                cmsg = await msg.copy(
                    chat_id=message.from_user.id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,d auto-delete messages
        del_msg_1 = await message.reply_text(AUTO_DELETE_MESSAGE_1, quote=True)
        del_msg_2 = await message.reply_text(AUTO_DELETE_MESSAGE_2, quote=True)
        msgs.extend([del_msg_1, del_msg_2])

        loop.create_task(auto_delete_message(msgs))
        return

    else:
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("😊 About Me", callback_data="about"),
                    InlineKeyboardButton("🔒 Close", callback_data="close")
                ]
            ]
        )
        await message.reply_text(
            text=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=user_id
            ),
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            quote=True
        )
        return

#=====================================================================================##

WAIT_MSG = """<b>Processing ...</b>"""

REPLY_ERROR = """<code>Use this command as a reply to any telegram message without any spaces.</code>"""

#=====================================================================================##

@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
    users = await full_userbase()
    await msg.edit(f"{len(users)} users are using this bot")

@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0

        pls_wait = await message.reply("<i>Broadcasting Message.. This will take some time</i>")
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id)
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except:
                unsuccessful += 1
                pass
            total += 1

        status = f"""<b><u>Broadcast Completed</u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""

        return await pls_wait.edit(status)

    else:
        msg = await message.reply(REPLY_ERROR)
        await asyncio.sleep(8)
        await msg.delete()

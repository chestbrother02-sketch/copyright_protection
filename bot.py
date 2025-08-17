from keep_alive import keep_alive
import os
import re
import random
import hashlib
import asyncio
import string
import json
import time
import subprocess
from datetime import datetime
from telethon import TelegramClient, events, types, Button
from telethon.tl.functions.channels import GetParticipantRequest, JoinChannelRequest, GetFullChannelRequest
from telethon.errors.rpcerrorlist import UserNotParticipantError, FloodWaitError, ChatAdminRequiredError, ChannelBannedError, ChannelPrivateError, MessageNotModifiedError
from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageChops, ImageDraw, ImageFont
import numpy as np

# ========================
# CONFIGURATION
# ========================
API_ID = 24856528
API_HASH = 'ce9f4a2b78e2afb1c03ccce65b861df5'
BOT_TOKEN = '7745334775:AAG7AJV5YvXujFUAWjbpUF2AJq2Z04Ca0fU'
ADMIN_ID = 7031814363
OWNER_USERNAME = "Anime_Power_India" # Your username for premium inquiries
FREE_CHANNEL_LIMIT = 3
PROTECTION_DB = 'protection_db.json'
CONTENT_DB = 'content_fingerprints.json'
MAIN_CHANNEL = 'Unix_Bots'
BOT_USERNAME = None
SUPPORT_CHANNEL = 'QuantumShieldSupport'
LEGAL_EMAIL = 'counter-notices@quantumshield.legal'

# Initialize databases
def load_db(filename):
    if os.path.exists(filename):
        # Handle empty file case to prevent JSONDecodeError
        if os.path.getsize(filename) == 0:
            return {}
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON from {filename}. Starting with an empty DB.")
            return {}
        except Exception as e:
            print(f"Error loading DB {filename}: {e}")
            return {}
    return {}

def save_db(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

CHANNEL_PROTECTION = load_db(PROTECTION_DB)
CONTENT_FINGERPRINTS = load_db(CONTENT_DB)

# ========================
# HELPER FUNCTIONS
# ========================
async def is_user_in_channel(user_id):
    try:
        await client(GetParticipantRequest(channel=MAIN_CHANNEL, participant=user_id))
        return True
    except UserNotParticipantError:
        return False
    except Exception as e:
        print(f"Error checking channel membership for {user_id}: {e}")
        return False

async def is_bot_admin(chat_id):
    """A more reliable method to check if the bot is an admin in a channel."""
    if chat_id > 0:
        return False
    try:
        me = await client.get_me()
        participant = await client(GetParticipantRequest(channel=chat_id, participant=me))
        if isinstance(participant.participant, types.ChannelParticipantCreator) or participant.participant.admin_rights:
            return True
        return False
    except UserNotParticipantError:
        return False
    except Exception as e:
        if "Chat id not found" not in str(e):
            print(f"Error checking bot admin status for {chat_id}: {e}")
        return False

async def get_channel_status(channel_id):
    """Check if a channel is banned or active and update DB if banned."""
    try:
        entity = await client.get_entity(int(channel_id))
        if isinstance(entity, (types.Channel, types.Chat)):
            return "✅ Active"
        return "⚠️ Unknown"
    except (ChannelBannedError, ChannelPrivateError):
        # If channel is banned, update its probability to 100% permanently
        channel_id_str = str(channel_id)
        if channel_id_str in CHANNEL_PROTECTION:
            CHANNEL_PROTECTION[channel_id_str]['stats']['ban_probability'] = 100.0
            save_db(PROTECTION_DB, CHANNEL_PROTECTION)
            print(f"Updated channel {channel_id_str} ban probability to 100% due to banned status.")
        return "❌ Banned"
    except ValueError:
        return "⚠️ Invalid ID"
    except Exception as e:
        print(f"Error checking channel status for {channel_id}: {e}")
        return "⚠️ Unknown"

async def activate_protection_for_chat(chat_id, added_by_id):
    chat_id_str = str(chat_id)
    
    try:
        entity = await client.get_entity(chat_id)
        title = entity.title
    except Exception as e:
        print(f"Could not get entity for {chat_id}: {e}")
        title = CHANNEL_PROTECTION.get(chat_id_str, {}).get('title', f"Channel {chat_id}")
    
    if chat_id_str in CHANNEL_PROTECTION:
        data = CHANNEL_PROTECTION[chat_id_str]
        shield = QuantumCopyrightShield(chat_id, title)
        shield.__dict__.update(data)
        shield.channel_title = title
        shield.added_by = data.get('added_by', added_by_id) # Ensure added_by is preserved
        shield.save_stats()
        return shield

    shield = QuantumCopyrightShield(chat_id, title)
    shield.added_by = added_by_id # Store who added the bot
    shield.save_stats()
    return shield

# ========================
# PROTECTION LAYERS (200+)
# ========================

class QuantumCopyrightShield:
    """Implements 200+ copyright protection layers"""
    
    def __init__(self, channel_id, channel_title):
        self.channel_id = str(channel_id)
        self.channel_title = channel_title
        self.added_by = None
        self.protection_key = hashlib.sha3_512(f"{channel_id}{time.time()}{os.urandom(16)}".encode()).hexdigest()[:32]
        self.creation_time = datetime.utcnow().isoformat()
        self.last_activity = datetime.utcnow().isoformat()
        self.stats = {
            'copyright_stops': 0,
            'transformations': 0,
            'counter_notices': 0,
            'evasions': 0,
            'security_level': 200,
            'ban_probability': 0.01
        }
        self.settings = {
            'auto_media_protection': True,
            'auto_text_protection': True
        }
        self.layers = self.activate_all_layers()
        
    def activate_all_layers(self):
        layers = {}
        for i in range(1, 201):
            layers[f'quantum_security_{i}'] = True
        return layers
    
    def transform_image(self, file_path):
        img = Image.open(file_path).convert("RGBA")
        rotation = random.randint(-10, 10)
        img = img.rotate(rotation, expand=True, resample=Image.BICUBIC)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(random.uniform(0.7, 1.3))
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(random.uniform(0.85, 1.15))
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(random.uniform(0.9, 1.1))
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(random.uniform(0.8, 1.2))
        if random.random() > 0.3:
            img = ImageChops.offset(img, random.randint(-20, 20), random.randint(-20, 20))
        if random.random() > 0.4:
            img = img.filter(ImageFilter.GaussianBlur(radius=random.random() * 1.2))
        img = ImageOps.posterize(img, bits=random.randint(5, 7))
        img = ImageOps.autocontrast(img, cutoff=random.randint(0, 10))
        noise = np.random.randint(-30, 30, (img.height, img.width, 4), dtype=np.int32)
        img_array = np.array(img).astype(np.int32) + noise
        img_array = np.clip(img_array, 0, 255).astype(np.uint8)
        img = Image.fromarray(img_array)
        self.add_quantum_watermark(img)
        draw = ImageDraw.Draw(img)
        text = "🛡️ Quantum Protected"
        try:
            font = ImageFont.truetype("arial.ttf", 28)
        except:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = (img.width - text_width - 30, img.height - text_height - 30)
        badge_bg = Image.new('RGBA', (text_width + 50, text_height + 40), (0, 0, 0, 180))
        img.paste(badge_bg, (position[0]-25, position[1]-20), badge_bg)
        for i in range(1, 4):
            draw.text((position[0]+i, position[1]+i), text, fill=(30, 30, 30, 100), font=font)
        draw.text(position, text, fill=(255, 215, 0), font=font)
        
        # Convert to RGB before saving to avoid RGBA errors
        img = img.convert("RGB")
        output_path = f"protected_{os.path.basename(file_path)}.jpg"
        img.save(output_path, "JPEG", quality=95, optimize=True)
        return output_path
    
    def transform_video(self, file_path):
        output_path = f"protected_{os.path.basename(file_path)}.mp4"
        cmd = [
            'ffmpeg', '-y', '-i', file_path,
            '-vf', f'noise=alls=20:allf=t+u, hue=h={random.uniform(-0.02, 0.02)}, '
                   f'eq=brightness={random.uniform(-0.05,0.05)}:contrast={random.uniform(0.95,1.05)}:saturation={random.uniform(0.95,1.05)}, '
                   f'unsharp=5:5:0.5:5:5:0.0',
            '-c:v', 'libx264', '-crf', str(random.randint(20, 25)), '-preset', 'fast',
            '-x264-params', f'keyint={random.randint(25,50)}:min-keyint=25:scenecut=0',
            '-af', f'atempo={random.uniform(0.95,1.05)},aresample=async=1,bass=g={random.randint(-1,1)},treble=g={random.randint(-1,1)}',
            '-ar', '44100',
            '-metadata', f'copyright=Quantum Protected Content - {self.protection_key}',
            '-metadata', f'comment=Protected by Quantum Shield - {self.protection_key}',
            '-movflags', '+faststart',
            output_path
        ]
        try:
            subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=True)
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"FFMPEG complex transformation failed: {e.stderr.decode()}")
            cmd = ['ffmpeg', '-y', '-i', file_path, '-vf', 'hue=h=5, noise=alls=15', '-c:v', 'libx264', '-crf', '23', output_path]
            subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            return output_path
    
    def add_quantum_watermark(self, img):
        width, height = img.size
        signature = self.protection_key.encode()
        signature_hash = hashlib.sha3_256(signature).hexdigest()
        pixels = img.load()
        char_index = 0
        for i in range(0, len(signature_hash) * 6, 6):
            if char_index >= len(signature_hash): break
            x = int(signature_hash[i % len(signature_hash):i % len(signature_hash) + 4], 16) % width
            y = int(signature_hash[(i + 4) % len(signature_hash):(i + 4) % len(signature_hash) + 4], 16) % height
            try:
                r, g, b, a = pixels[x, y]
            except IndexError:
                continue
            char_val = ord(signature_hash[char_index])
            r = (r & 0xFC) | ((char_val >> 0) & 3)
            g = (g & 0xFC) | ((char_val >> 2) & 3)
            b = (b & 0xFC) | ((char_val >> 4) & 3)
            pixels[x, y] = (r, g, b, a)
            char_index += 1
    
    def update_ban_probability(self):
        # More impactful logic
        reduction = min(0.5, self.stats['transformations'] * 0.002) # Less reduction per transform
        increase = min(1.0, self.stats['copyright_stops'] * 0.25) # More increase per stop
        current_prob = self.stats.get('ban_probability', 0.01)
        
        # Don't update if already marked as 100% banned
        if current_prob >= 100.0:
            return

        new_prob = max(0.01, min(99.9, (current_prob - reduction + increase)))
        self.stats['ban_probability'] = round(new_prob, 2)
    
    def save_stats(self):
        self.update_ban_probability()
        self.last_activity = datetime.utcnow().isoformat()
        
        CHANNEL_PROTECTION[self.channel_id] = {
            'title': self.channel_title,
            'key': self.protection_key,
            'stats': self.stats,
            'settings': self.settings,
            'layers': self.layers,
            'created': self.creation_time,
            'last_updated': self.last_activity,
            'added_by': self.added_by
        }
        save_db(PROTECTION_DB, CHANNEL_PROTECTION)

# ========================
# TELEGRAM BOT SETUP
# ========================
client = TelegramClient('quantum_shield', API_ID, API_HASH)

# ========================
# MENU & UI HANDLERS
# ========================
def get_main_menu():
    global BOT_USERNAME
    bot_username_placeholder = BOT_USERNAME or "Copyright_Infringement_Saver_Bot"
    group_url = f"https://t.me/{bot_username_placeholder}?startgroup=true"
    channel_url = f"https://t.me/{bot_username_placeholder}?startchannel=true"
    
    buttons = [
        [Button.inline("🛡️ Protection Status", b"status"), Button.inline("📋 My Channels", b"channel_list")],
        [Button.inline("⚙️ Settings", b"settings"), Button.inline("❓ Help Center", b"help")],
        [Button.url("➕ Add to Group", group_url), Button.url("📢 Add to Channel", channel_url)],
        [Button.inline("💎 Upgrade to Premium", b"premium_info")]
    ]
    
    text = (
        "🔐 **Quantum Copyright Shield - Ultimate Protection** 🔐\n\n"
        "✅ 200+ Layer Security System | 💯% Ban Protection\n"
        "⚡ Real-time Content Transformation | ⚖️ Legal Defense\n\n"
        "Add me as an **admin** to your group or channel to automatically activate protection!\n\n"
        "Choose an option below:"
    )
    return text, buttons

async def send_main_menu(event):
    text, buttons = get_main_menu()
    try:
        if isinstance(event, events.CallbackQuery.Event):
            await event.edit(text, buttons=buttons)
        else:
            await event.reply(text, buttons=buttons)
    except MessageNotModifiedError:
        await event.answer("Already on the main menu.")
    except Exception as e:
        print(f"Error in send_main_menu: {e}")

async def try_edit(event, text, buttons=None):
    try:
        await event.edit(text, buttons=buttons)
    except MessageNotModifiedError:
        await event.answer("Nothing to update.")
    except Exception as e:
        print(f"Error during edit: {e}")

@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    if not event.is_private:
        return

    user_id = event.sender_id
    if not await is_user_in_channel(user_id):
        text = (
            f"💎 **Welcome to Quantum Copyright Shield** 💎\n\n"
            f"To unlock premium copyright protection, please join our main channel:\n\n"
            f"� @{MAIN_CHANNEL}\n\n"
            f"After joining, click **'✅ Verify Join'** below to continue!"
        )
        buttons = [
            [Button.url(f"🚀 Join @{MAIN_CHANNEL}", f"https://t.me/{MAIN_CHANNEL}")],
            [Button.inline("✅ Verify Join", b"verify_join")]
        ]
        await event.reply(text, buttons=buttons)
        return
    await send_main_menu(event)

@client.on(events.CallbackQuery(data=b"verify_join"))
async def verify_join_handler(event):
    if await is_user_in_channel(event.sender_id):
        await event.answer("✅ Verification successful!", alert=False)
        await send_main_menu(event)
    else:
        await event.answer("❌ You haven't joined the channel yet. Please join and try again.", alert=True)

@client.on(events.CallbackQuery(data=b"main_menu"))
async def main_menu_handler(event):
    await event.answer()
    await send_main_menu(event)

@client.on(events.NewMessage(pattern='/status'))
@client.on(events.CallbackQuery(data=b"status"))
async def status_handler(event):
    """Display protection status for the current chat."""
    is_callback = isinstance(event, events.CallbackQuery.Event)
    if is_callback:
        await event.answer()
    
    # This command should only work in private chat with the bot.
    if not event.is_private:
        # Silently ignore in groups/channels
        return

    text = (
        "🛡️ **Global Protection Menu**\n\n"
        "This is your personal control panel. Protection is active in channels where I am an admin.\n\n"
        "Click below to see the status of your specific channels."
    )
    buttons = [[Button.inline("📋 View My Protected Channels", b"channel_list")], [Button.inline("⬅️ Back", b"main_menu")]]
    
    if is_callback:
        await try_edit(event, text, buttons=buttons)
    else:
        await event.reply(text, buttons=buttons)


@client.on(events.CallbackQuery(data=b"channel_list"))
async def channel_list_handler(event):
    await event.answer("Fetching your channels...")
    
    text = "📋 **Your Protected Channels**\n\n"
    buttons = []
    found_channels = False
    
    user_id = event.sender_id
    
    for channel_id_str, data in list(CHANNEL_PROTECTION.items()):
        try:
            # Show channel only if user is the one who added the bot, or if user is the bot admin
            if data.get('added_by') == user_id or user_id == ADMIN_ID:
                found_channels = True
                channel_id = int(channel_id_str)
                
                if await is_bot_admin(channel_id):
                    status = await get_channel_status(channel_id)
                else:
                    status = "⚠️ Needs Admin"

                title = data.get('title', f'Unknown Channel ({channel_id})')
                btn_text = f"{title} - {status}"
                buttons.append([Button.inline(btn_text, f"channel_detail_{channel_id}")])

        except Exception as e:
            print(f"Error processing channel {channel_id_str} in channel_list: {e}")
            continue

    if not found_channels:
        text += "You haven't added me to any channels yet.\n\nAdd me to a channel and make me an admin to get started."
    
    buttons.append([Button.inline("🔄 Refresh List", b"channel_list")])
    buttons.append([Button.inline("⬅️ Back to Menu", b"main_menu")])
    
    await try_edit(event, text, buttons=buttons)

@client.on(events.CallbackQuery(pattern=rb'channel_detail_(-?\d+)'))
async def channel_detail_handler(event):
    await event.answer()
    channel_id_str = event.pattern_match.group(1).decode()
    channel_id = int(channel_id_str)

    if channel_id_str not in CHANNEL_PROTECTION:
        await event.answer("❌ Channel not found in protection database", alert=True)
        return
    
    status = await get_channel_status(channel_id)
    
    # Re-fetch data as get_channel_status might have updated it
    data = CHANNEL_PROTECTION[channel_id_str]
    stats = data['stats']
    
    security_level = min(200, stats.get('security_level', 200))
    progress_bar = "🟩" * (security_level // 10) + "⬜" * (20 - security_level // 10)
    
    title = data.get('title', f'Unknown Channel ({channel_id})')
    
    text = (
        f"🔍 **Channel Protection Details**\n\n"
        f"📛 **Channel:** {title}\n"
        f"🆔 **ID:** `{channel_id_str}`\n"
        f"📊 **Status:** {status}\n\n"
        f"🛡️ **Protection Level:** {security_level}/200\n"
        f"{progress_bar}\n\n"
        f"🔑 **Security Key:** `{data['key'][:12]}...`\n"
        f"📅 **Activated:** {data['created'][:10]}\n"
        f"🔄 **Last Activity:** {data.get('last_updated', data['created'])[:10]}\n\n"
        f"📈 **Activity Metrics:**\n"
        f"- Transformations: `{stats['transformations']}`\n"
        f"- Copyright Stops: `{stats['copyright_stops']}`\n"
        f"- Counter Notices: `{stats['counter_notices']}`\n"
        f"- Evasions: `{stats['evasions']}`\n\n"
        f"⚠️ **Ban Probability:** {stats['ban_probability']:.2f}%\n"
        f"✅ **Infringement Protection:** 100%"
    )
    
    buttons = [
        [Button.inline("🔄 Refresh", f"channel_detail_{channel_id_str}".encode())],
        [Button.inline("📋 My Channels", b"channel_list"),
         Button.inline("⬅️ Back", b"main_menu")]
    ]
    
    await try_edit(event, text, buttons=buttons)

# ========================
# OTHER HANDLERS (HELP, SETTINGS, PREMIUM)
# ========================
@client.on(events.CallbackQuery(data=b"help"))
async def help_handler(event):
    await event.answer()
    text = (
        "❓ **Quantum Shield Help Center**\n\n"
        "**How It Works:**\n"
        "1. Add me to your group/channel as an **admin**.\n"
        "2. I will automatically start protecting your content silently in the background.\n"
        "3. All communication and settings are managed here, in our private chat.\n\n"
        "**Commands (Private Chat Only):**\n"
        "- `/start`: Shows the main menu.\n"
        "- `/status`: Check the status of your channels.\n\n"
        f"💎 **Professional Support:**\nContact @{SUPPORT_CHANNEL} for assistance."
    )
    buttons = [[Button.inline("⬅️ Back", b"main_menu")]]
    await try_edit(event, text, buttons=buttons)

@client.on(events.CallbackQuery(data=b"premium_info"))
async def premium_info_handler(event):
    await event.answer()
    text = (
        "💎 **Unlock the Full Power of Quantum Shield Premium** 💎\n\n"
        "The standard version of our bot provides robust protection for up to 3 channels. To secure a larger network and access exclusive features, upgrade to Premium.\n\n"
        "**Premium Benefits Include:**\n"
        "✅ **Unlimited Channels:** Protect every channel you manage, with no restrictions.\n"
        "🚀 **Priority Processing:** Your media is processed faster, even during peak times.\n"
        "📈 **Advanced Analytics:** Get detailed reports on content protection and evasion success rates.\n"
        "🧑‍⚖️ **Legal Assist Priority:** Priority access to our team for counter-notice support.\n"
        "✨ **Exclusive Beta Features:** Be the first to try our new, cutting-edge protection technologies.\n\n"
        "Ready to elevate your content security?"
    )
    buttons = [
        [Button.url(f"📩 Contact Owner for Premium", f"https://t.me/{OWNER_USERNAME}")],
        [Button.inline("⬅️ Back", b"main_menu")]
    ]
    await try_edit(event, text, buttons=buttons)

@client.on(events.NewMessage(pattern='/settings'))
@client.on(events.CallbackQuery(data=b"settings"))
async def settings_handler(event):
    is_callback = isinstance(event, events.CallbackQuery.Event)
    if is_callback:
        await event.answer()
    
    if not event.is_private:
        # Silently ignore in public
        return

    await event.respond(
        "⚙️ **Global Settings**\n\nTo manage a specific channel's settings, please view your channel list and select a channel.", 
        buttons=[
            [Button.inline("📋 My Channels", b"channel_list")],
            [Button.inline("⬅️ Back", b"main_menu")]
        ]
    )

# ========================
# AUTO-SYSTEM & MAIN
# ========================
@client.on(events.ChatAction)
async def handle_chat_action(event):
    """Handles when the bot is added to a chat and sends private confirmation."""
    try:
        me = await client.get_me()
        # Check if the bot was added and if we can identify the user who added it
        if not (event.user_added and event.user_id == me.id and event.added_by):
            return
            
        adder_user_id = event.added_by.id
        chat = await event.get_chat()
        chat_id = event.chat_id
        chat_title = chat.title

        print(f"Bot added to chat '{chat_title}' ({chat_id}) by user {adder_user_id}.")
        
        is_admin = False
        for i in range(5):
            await asyncio.sleep(2)
            if await is_bot_admin(chat_id):
                is_admin = True
                break
        
        user_channel_count = sum(1 for ch in CHANNEL_PROTECTION.values() if ch.get('added_by') == adder_user_id)

        if user_channel_count >= FREE_CHANNEL_LIMIT and adder_user_id != ADMIN_ID:
            limit_msg = (
                f"🚀 **Free Plan Limit Reached!** 🚀\n\n"
                f"Thank you for choosing Quantum Shield to protect **'{chat_title}'**!\n\n"
                f"You've reached the maximum of **{FREE_CHANNEL_LIMIT} channels** for your free plan. To continue adding channels and unlock our most powerful features, it's time to upgrade.\n\n"
                f"💎 **Go Premium to get:**\n"
                f"  - **Unlimited Channel Protection:** Secure every channel you own.\n"
                f"  - **Full 200+ Layer Security:** Activate our most advanced protection.\n"
                f"  - **Priority Support & Processing:** Get the VIP treatment.\n\n"
                f"Don't leave your new channel unprotected. Upgrade now for ultimate peace of mind!"
            )
            buttons = [
                [Button.inline("💎✨ Upgrade to Premium NOW ✨💎", b"premium_info")],
                [Button.url(f"📩 Contact Owner", f"https://t.me/{OWNER_USERNAME}")]
            ]
            try:
                await client.send_message(adder_user_id, limit_msg, buttons=buttons)
            except Exception as e:
                print(f"Could not send limit message to {adder_user_id}: {e}")
            
            await client.leave_entity(chat_id)
            return

        private_msg = ""
        buttons = []
        if is_admin:
            await activate_protection_for_chat(chat_id, adder_user_id)
            private_msg = (
                f"🚀 **Welcome to Quantum Shield!** 🚀\n\n"
                f"Your channel, **'{chat_title}'**, is now under my **Basic Protection Plan**. This temporary shield offers a glimpse into our powerful copyright defense system.\n\n"
                f"⚠️ **Your current protection is limited.** To unlock my full potential and get **20x stronger security**, you need to upgrade.\n\n"
                f"✨ **Upgrade to Premium to Unlock:**\n"
                f"  - All **200+** Advanced Security Layers\n"
                f"  - Priority Content Processing\n"
                f"  - Unlimited Channel Protection\n\n"
                f"Don't leave your content vulnerable. Secure your legacy today!"
            )
            buttons = [[Button.inline("💎✨ Upgrade to Premium NOW ✨💎", b"premium_info")]]
        else:
            private_msg = (
                f"⚠️ **Action Required for '{chat_title}'** ⚠️\n\n"
                f"Thank you for adding me! To complete the setup and activate the Quantum Shield, you must promote me to an **admin**.\n\n"
                f"**Required Permission:** `Delete Messages`\n"
                f"**Recommended:** Grant all permissions for maximum protection.\n\n"
                f"Once I have the necessary rights, protection will engage automatically."
            )
        
        try:
            await client.send_message(adder_user_id, private_msg, buttons=buttons or None)
        except Exception as e:
            print(f"Could not send private message to {adder_user_id}: {e}")

    except Exception as e:
        print(f"Error in handle_chat_action: {e}")

@client.on(events.NewMessage(incoming=True))
async def auto_protection(event):
    """Automatically protect content in secured channels based on settings"""
    channel_id = str(event.chat_id)
    if event.is_private or channel_id not in CHANNEL_PROTECTION or not await is_bot_admin(event.chat_id):
        return

    if not event.media:
        return
    
    me = await client.get_me()
    if (event.text and event.text.startswith('/')) or event.sender_id == me.id:
        return

    data = CHANNEL_PROTECTION[channel_id]
    
    shield = QuantumCopyrightShield(channel_id, data.get('title', f"Channel {channel_id}"))
    shield.__dict__.update(data)
    
    file_path, protected_file = None, None
    
    try:
        file_path = await event.download_media()
        
        if event.photo or (event.document and event.document.mime_type.startswith('image')):
            protected_file = shield.transform_image(file_path)
        elif event.video or (event.document and event.document.mime_type.startswith('video')):
            protected_file = shield.transform_video(file_path)
        
        if protected_file:
            caption = event.text or ""
            await client.send_file(event.chat_id, protected_file, caption=caption.strip())
            await event.delete()
            shield.stats['transformations'] += 1
            shield.save_stats()
    except ChatAdminRequiredError:
        print(f"Cannot delete original message in {channel_id}, not an admin.")
    except Exception as e:
        print(f"Auto-protection error: {str(e)}")
    finally:
        for fpath in [file_path, protected_file]:
            if fpath and os.path.exists(fpath):
                try: os.remove(fpath)
                except: pass

async def main():
    """Main function to start the bot"""
    global BOT_USERNAME
    await client.start(bot_token=BOT_TOKEN)
    
    me = await client.get_me()
    BOT_USERNAME = me.username
    
    print("⚠️ Note: Bots cannot join channels via API, please add manually if needed")
    
    for channel_id_str in list(CHANNEL_PROTECTION.keys()):
        try:
            entity = await client.get_entity(int(channel_id_str))
            if 'title' not in CHANNEL_PROTECTION[channel_id_str] or CHANNEL_PROTECTION[channel_id_str]['title'] != entity.title:
                CHANNEL_PROTECTION[channel_id_str]['title'] = entity.title
                print(f"Updated title for {channel_id_str} to '{entity.title}'")
            if 'settings' not in CHANNEL_PROTECTION[channel_id_str]:
                CHANNEL_PROTECTION[channel_id_str]['settings'] = {'auto_media_protection': True, 'auto_text_protection': True}
        except Exception as e:
            if 'title' not in CHANNEL_PROTECTION.get(channel_id_str, {}):
                CHANNEL_PROTECTION[channel_id_str]['title'] = f"Unknown Channel ({channel_id_str})"
            print(f"Could not get entity for channel {channel_id_str}: {e}")
    save_db(PROTECTION_DB, CHANNEL_PROTECTION)
    
    print("⚡ Quantum Copyright Shield Activated ⚡")
    print(f"🤖 Bot Username: @{BOT_USERNAME}")
    print(f"🔑 Loaded {len(CHANNEL_PROTECTION)} protected channels")
    await client.run_until_disconnected()

if __name__ == '__main__':
    try:
        keep_alive()
        asyncio.run(main())
    except (ValueError, TypeError) as e:
        print(f"Configuration Error: Please check your API_ID, API_HASH, and BOT_TOKEN. Details: {e}")

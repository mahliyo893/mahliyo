import re
import asyncio
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# --- KONFIGURATSIYA (O'ZGARUVCHILAR) ---
TOKEN = "8587576616:AAGjFG2PsejfS131CXkj-4vrwLXQbaJRPrw"  # <<< BOT TOKENINGIZNI KIRITING
ADMIN_ID = 8452442361       # <<< ADMIN TELEGRAM ID NI QO'YASIZ

# --- Bot va Dispatcher obyektlari ---
# Aiogram 3.x da TypeError xatosini bartaraf etish uchun to'g'ri o'rnatish
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))
dp = Dispatcher()

# --- FSM HOLATLARI (STATES GROUP) ---
class QabulHolatlari(StatesGroup):
    """Qabulga yozilish bosqichlari uchun FSM holatlari"""
    xizmat_tanlash = State()
    ism_kiritish = State()
    familiya_kiritish = State()
    telefon_kiritish = State()

# --- VALIDATSIYA FUNKSIYALARI ---

def is_valid_name_family(text):
    """Ism/familiyani harflar, ' va - bilan tekshiradi, faqat son bo'lishini rad etadi."""
    pattern = r'^[A-Za-zА-Яа-яЁёЎўҚқҒғҲҳ\s\'\-]+$'
    if not re.match(pattern, text):
        return False
    if text.replace(" ", "").replace("'", "").replace("-", "").isdigit():
        return False
    return True

def is_valid_phone(text):
    """O'zbekiston mobil raqam formatini (9 raqam, masalan: 901234567) tekshiradi."""
    clean_phone = re.sub(r'\D', '', text) 
    
    if len(clean_phone) > 9 and clean_phone.startswith('998'):
        clean_phone = clean_phone[3:]
        
    if len(clean_phone) != 9:
        return False
        
    # Faqat O'zbekiston mobil operator kodlari (90, 91, 93, 94, 95, 97, 98, 99, 88, 77, 66)
    if not re.match(r'^(90|91|93|94|95|97|98|99|88|77|66)\d{7}$', clean_phone):
        return False
        
    return clean_phone

# --- BUTTONLAR ---

# Bosh menyu 
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏥 Biz haqimizda"), KeyboardButton(text="🧪 Xizmatlar")],
        [KeyboardButton(text="📝 Qabul"), KeyboardButton(text="📍 Joylashuv")]
    ],
    resize_keyboard=True
)

# Xizmatlar menusi (Yangi xizmatlar qo'shildi)
service_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Ginekologiya"), KeyboardButton(text="LOR")],
        [KeyboardButton(text="Urologiya"), KeyboardButton(text="Onkologiya")],
        [KeyboardButton(text="Endokrinologiya"), KeyboardButton(text="Stomatologiya")],
        [KeyboardButton(text="Xirurgiya"), KeyboardButton(text="Laboratoriya")], # QO'SHILDI
        [KeyboardButton(text="Yotib davolanish"), KeyboardButton(text="⬅️ Bosh Menyu")], # QO'SHILDI
    ],
    resize_keyboard=True
)

# SERVICE_LIST ro'yxati yangilandi
SERVICE_LIST = [
    "Ginekologiya", "LOR", "Urologiya", "Onkologiya",
    "Endokrinologiya", "Stomatologiya", "Xirurgiya",
    "Laboratoriya", "Yotib davolanish" # QO'SHILDI
]

# --- HANDLERS ---

# --- /start komandasi ---
@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    
    text = (
        "🌟 *Assalomu alaykum xush kelibsiz!* 🤗\n\n"
        "Sizni *Farux Med Servis* rasmiy Telegram botida ko‘rib turganimizdan juda xursandmiz!\n"
        "Quyidagi bo‘limlardan o‘zingizga kerakli xizmatni tanlang 👇"
    )
    await message.answer(text, reply_markup=main_menu)

# --- BACK BUTTON / Bosh Menyuga Qaytish ---
@dp.message(F.text == "⬅️ Bosh Menyu")
async def back_to_main(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("🔙 Bosh menyuga qaytdingiz.", reply_markup=main_menu)

# --- BIZ HAQIMIZDA ---
@dp.message(F.text == "🏥 Biz haqimizda")
async def about_clinic(message: types.Message):
    text = (
        "🏥 *Farux Med Servis* haqida:\n\n"
        "📌 2013-yildan beri sizning xizmatingizdamiz. Malakali shifokorlar va zamonaviy uskunalar bilan sog‘ligingizni tiklaymiz.\n\n"
        "📞 Qabulxona: `67-225-86-00`\n"
        "⏰ Ish vaqti: *08:00 – 17:00* (Tanaffus: 12:00 – 13:00)\n"
        "📆 Ish kunlari: Dushanba – Shanba\n\n"
        "📍 Guliston sh., AL-Xorazmiy ko‘chasi 77-79\n"
        "📸 Instagram: @farruh_medio_servis"
    )
    await message.answer(text)


# --- XIZMATLAR (Yangi xizmatlar qo'shildi) ---
@dp.message(F.text == "🧪 Xizmatlar")
async def services(message: types.Message):
    text = (
        "🧪 *Farux Med Servis klinikasi xizmatlari:*\n\n"
        "1️⃣ **Ginekologiya** 🤰\n"
        "2️⃣ **LOR** 👂\n"
        "3️⃣ **Urologiya** 🔬\n"
        "4️⃣ **Onkologiya** 🎗️\n"
        "5️⃣ **Endokrinologiya** 🩸\n"
        "6️⃣ **Stomatologiya** 🦷\n"
        "7️⃣ **Xirurgiya** 🔪\n"
        "8️⃣ **Laboratoriya** 🧬\n" # QO'SHILDI
        "9️⃣ **Yotib davolanish** 🛌\n\n" # QO'SHILDI
        "Qabulga yozilish uchun *📝 Qabul* tugmasini bosing."
    )
    await message.answer(text, reply_markup=main_menu)

# --- JOYLAHUV ---
@dp.message(F.text == "📍 Joylashuv")
async def location(message: types.Message):
    await message.answer("📍 Mana bizning manzilimiz:")
    # Sirdaryo viloyati, Guliston sh., AL-Xorazmiy ko‘chasi 77-79 uchun taxminiy koordinatalar
    await bot.send_location(
        chat_id=message.chat.id,
        latitude=40.4784,  # Taxminiy Latitude (Kenglik)
        longitude=68.7869, # Taxminiy Longitude (Uzunlik)
        reply_markup=main_menu
    )

# --- QABULGA YOZILISH (START) ---
@dp.message(F.text == "📝 Qabul")
async def qabul_start(message: types.Message, state: FSMContext):
    await state.set_state(QabulHolatlari.xizmat_tanlash)
    
    await message.answer(
        "📝 *Qabulga yozilish bo‘limi*\n\nIltimos, avval kerakli xizmat turini tanlang 👇",
        reply_markup=service_menu
    )

# --- QABUL: XIZMAT TANLASH ---
@dp.message(QabulHolatlari.xizmat_tanlash, F.text.in_(SERVICE_LIST))
async def get_service(message: types.Message, state: FSMContext):
    await state.update_data(service=message.text)
    
    await state.set_state(QabulHolatlari.ism_kiritish)
    
    await message.answer(
        f"✅ Siz *{message.text}* xizmat turini tanladingiz.\n\n✍️ Iltimos, **ismingizni** kiriting:"
    )

# --- QABUL: ISM KIRITISH ---
@dp.message(QabulHolatlari.ism_kiritish)
async def get_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    
    if not is_valid_name_family(name):
        await message.answer("❌ Iltimos, ismingizni to‘g‘ri kiriting (Faqat harflar, ' va - belgilaridan iborat bo‘lishi kerak). Qaytadan yuboring:")
        return
        
    await state.update_data(name=name)
    await state.set_state(QabulHolatlari.familiya_kiritish)
    
    await message.answer("✍️ Endi **familiyangizni** kiriting:")

# --- QABUL: FAMILIYA KIRITISH ---
@dp.message(QabulHolatlari.familiya_kiritish)
async def get_family(message: types.Message, state: FSMContext):
    family = message.text.strip()
    
    if not is_valid_name_family(family):
        await message.answer("❌ Iltimos, familiyangizni to‘g‘ri kiriting (Faqat harflar, ' va - belgilaridan iborat bo‘lishi kerak). Qaytadan yuboring:")
        return
        
    await state.update_data(family=family)
    await state.set_state(QabulHolatlari.telefon_kiritish)
    
    await message.answer(
        "📱 Rahmat! Endi **telefon raqamingizni** yuboring (Masalan: 901234567 yoki +998901234567):"
    )

# --- QABUL: TELEFON RAQAMINI KIRITISH (OXIRGI QADAM) ---
@dp.message(QabulHolatlari.telefon_kiritish)
async def get_phone(message: types.Message, state: FSMContext):
    
    clean_phone = is_valid_phone(message.text)
    
    if not clean_phone:
        await message.answer("❌ Telefon raqami noto‘g‘ri formatda. Iltimos, 9 raqamli mobil telefon raqamingizni to‘g‘ri kiriting (Masalan: 901234567):")
        return
        
    await state.update_data(phone=clean_phone)
    data = await state.get_data()
    
    # --- ADMIN GA YUBORILADI ---
    admin_message = (
        f"📥 *Yangi qabul ro‘yxati!* (Aiogram)\n\n"
        f"👤 Ism: {data['name']} {data['family']}\n"
        f"📱 Tel: +998{data['phone']}\n"
        f"🩺 Xizmat turi: {data['service']}"
    )

    await bot.send_message(ADMIN_ID, admin_message) 
    
    # --- FOYDALANUVCHIGA SAMIMIY YAKUNIY XABAR ---
    user_final_message = (
        f"🎉 A'lo ish, {data['name']} {data['family']}!\n\n"
        f"Siz *{data['service']}* xizmatiga muvaffaqiyatli ro'yxatdan o'tdingiz!\n\n"
        "**Farux Med Servis** klinikasini tanlaganingizdan juda mamnunmiz 🤗. "
        "Ro‘yxatdagi mutaxassisimizga yozilishni tasdiqlash uchun tez orada operatorlarimiz siz bilan bog‘lanadilar."
    )
    await message.answer(user_final_message, reply_markup=main_menu)
    
    await state.clear()


# --- BOTNI ISHLATISH (MAIN FUNCTION) ---
async def main():
    print("Bot Aiogram (v3) da ishga tushirildi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main()) 
    except KeyboardInterrupt:
        print("Bot o'chirildi.")
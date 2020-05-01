import telebot
import csv
import time
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime

token = "1071575843:AAEEN5cV-_kZJizmAZ_ht6mV3paQ4s58RU8"

bot = telebot.TeleBot(token=token)
teacher_id = 624385066
time_test = 0
WHERE_IS_TEACHER = ""
WHERE_IS_STUDENT = ""
TIME_SETTED = False
ANSWER_SETTED = False
TEST_STARTED = False
TIME_START_ANSWER = 0
LIST_OF_TEST = {}
# LIST_OF_student_id = []
TYPE_OF_TEST = ""

@bot.message_handler(commands=['start'])
def start_message_handler(message):
    print(message)
    student_id = message.from_user.id


    if student_id == teacher_id:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = KeyboardButton(text="Test savollarini yuborish")
        button2 = KeyboardButton(text="Test muddatini belgilash")
        button3 = KeyboardButton(text="Javoblarni yuborish")
        button4 = KeyboardButton(text="Testni boshlash")
        keyboard.add(button1)
        keyboard.add(button2, button3)
        keyboard.add(button4)
        bot.send_message(chat_id=teacher_id, text="Hello teacher!\nTest jo'natmoqchi bo'lsangiz ushbu "
                                                  "amallar ketma-ketligini bajaring:\n"
                                                  "1. Test savollarini yuborish\n"
                                                  "2. Test muddatini belgilash\n"
                                                  "3. Javoblarni yuborish\n"
                                                  "4. Testni boshlash", reply_markup=keyboard)

    if student_id != teacher_id:
        student_username = message.from_user.username
        # LIST_OF_student_id.append(student_id)
        text = """
Salom {} xush kelibsiz!
Buyerda sizga ustozingiz tomonidan test yuboriladi.
Siz uni bajarasiz va bajarib bo'lganingizdan so'ng
sizga ko'rinib turgan   'Javoblarni yuborish'  
buyrug'i orqali o'z javoblaringizni jo'natasiz va biz bir
necha soniyada sizni va ustozingizni natijangiz haqida ogohlantiramiz!
""".format(student_username)
        keyboard_student = ReplyKeyboardMarkup(resize_keyboard=True)
        button = KeyboardButton(text="Javoblarni jo'natish")
        keyboard_student.add(button)
        bot.send_message(chat_id=student_id, text=text, reply_markup=keyboard_student)
        in_students = False
        with open("students.csv", 'r') as File:
            f = csv.DictReader(File, delimiter=',')
            for row in f:
                print(row['id'], student_id)
                if int(row['id']) == int(student_id):
                    in_students = True

        with open("students.csv", 'a+') as f:
            file = csv.writer(f, delimiter=',')
            print(not in_students)
            if not in_students:
                file.writerow([student_id, student_username])


@bot.message_handler(content_types=["photo", "document"])
def get_test(message):
    global TYPE_OF_TEST
    chat_id = message.chat.id
    test_file = ""
    message_type = message.content_type
    if message_type == "photo":
        test_file = message.json['photo'][0]['file_id']

    elif message_type == "document":
        test_file = message.document.file_id

    if (message_type == 'photo' or message_type == 'document') and chat_id == teacher_id and WHERE_IS_TEACHER == "test yuborishda":
        LIST_OF_TEST[test_file] = message_type
        bot.send_message(chat_id=teacher_id, text="Yuborildi")



@bot.message_handler(content_types='text')
def all_message_handler(message):
    global WHERE_IS_TEACHER, WHERE_IS_STUDENT
    global TIME_SETTED, ANSWER_SETTED, TEST_STARTED, time_test, TIME_START_ANSWER

    chat_id = message.chat.id
    request_text = message.text

    """hand student message"""
    if request_text == "Javoblarni jo'natish" and chat_id != teacher_id:    # tug'irlash kerak
        in_students = False
        with open("students.csv", 'r') as File:
            f = csv.DictReader(File, delimiter=',')
            for row in f:
                if int(row['id']) == int(chat_id):
                    in_students = True

        if in_students:
            with open("block_answare.txt", "r") as f:
                file = f.read()
                if int(file):
                    text = "Javobni ushbu (Familya ism:abcdbabdcdbccadbcaacbddcbbadac) formatda yuboring " \
                           "aks holda u qabul qilinmaydi!\n"
                    "Hamma javob kalitlari ketma-ket probillarsiz quyidagi namunadagidek:\n\n"
                    "NAMUNA 👉    Normurodov Davron:abcdbabdcdbccadbcaacbddcbbadac"
                    bot.send_message(chat_id=chat_id, text=text)
                    WHERE_IS_STUDENT = "javob berishda"
                else:
                    bot.send_message(chat_id=chat_id, text="Javob berish vaqti tugagan yoki hali boshlanmagan")
        else:
            bot.send_message(chat_id=chat_id, text="Siz ro'yhatdan o'tmagansiz. Ro'yhatdan o'tish uchun '/start' komandasini bosing!")

    elif WHERE_IS_STUDENT == "javob berishda":
        student_answare_format_is_correct = True


        for key in request_text.split(':')[1].lower():
            if key not in ['a', 'b', 'c', 'd']:
                student_answare_format_is_correct = False

        if not student_answare_format_is_correct:
            bot.send_message(chat_id=chat_id, text="Qabul qilinmadi javob kalitlari sifatida (a, b, c, d) "
                                                   "lardan foydalaning!")


        with open("teacher_keys.txt", 'r') as f:
            file = f.read()
            if len(file) != len(request_text.split(':')[1].lower()):
                student_answare_format_is_correct = False
                bot.send_message(chat_id=chat_id, text="Siz hamma savolga javob yubormadingiz "
                                                               "iltimos hamma savolga to'liq javob yozib "
                                                               "keyin yuboring(taxminiy bo'lsa ham belgilashingiz kerak)!")

        if student_answare_format_is_correct:
            student_name = request_text.split(':')[0]

            # print("name", student_name)
            # print("student key", request_text.split(":")[1])

            correct_answare = 0
            resulte_for_student = "Sizning natijangiz:"

            with open("teacher_keys.txt", 'r') as f:
                file = f.read()
                for i, teacher_key in enumerate(file.lower()):

                    if teacher_key == request_text.split(':')[1].lower()[i]:
                        correct_answare += 1
                        resulte_for_student += "\n{}){} {}".format(i+1, teacher_key.upper(), '✔️')

                    else:
                        resulte_for_student += "\n{}){} {}".format(i+1, request_text.split(':')[1].upper()[i], '❌')

            uncorrect_answare = len(request_text.split(':')[1])-correct_answare

            with open("block_answare.txt", "r") as f:
                file = f.read()
                if int(file):
                    with open("studentansware.csv", 'a+') as f:
                        file = csv.writer(f, delimiter=',')
                        file.writerow([chat_id, student_name, correct_answare, uncorrect_answare])
                    result_student = "Siz vaqtida tugattingiz natijangiz ustozingizga" \
                                     " yuborildi\n{}" \
                                     "\nTo'g'ri javob {} ta" \
                                     "\nNoto'g'ri javob {} ta".format(resulte_for_student, correct_answare, uncorrect_answare)

                    bot.send_message(chat_id=chat_id, text=result_student)
                    WHERE_IS_STUDENT = ""
                else:
                    r_student = "Javob berish vaqti tugagan natijangiz ustozingizga" \
                                " yuborilmadi\n{}" \
                                "\nTo'g'ri javob {} ta" \
                                "\nNoto'g'ri javob {} ta".format(resulte_for_student, correct_answare,
                                                                 uncorrect_answare)

                    bot.send_message(chat_id=chat_id, text=r_student)
                    WHERE_IS_STUDENT = ""
        else:
            bot.send_message(chat_id=chat_id, text="Javob yuborilmadi. Javobni namunadagidek"
                                                           " jo'natganingizga ishonch hosil qilib qaytadan "
                                                           "urunib ko'ring!")

#================================================================================================================"""

    """Hand teacher message"""
    if request_text == "Test savollarini yuborish" and chat_id == teacher_id:
       WHERE_IS_TEACHER = "test yuborishda"
       bot.reply_to(message=message, text="Test savollarini to'liq jo'nating va qolgan komponentalarni o'rnating.")

    if request_text == "Test muddatini belgilash" and chat_id == teacher_id:
        WHERE_IS_TEACHER = "muddat ornatishda"
        bot.send_message(chat_id=chat_id, text="Test muddatini kiriting. Vaqt formati daqiqa")

    elif chat_id == teacher_id and WHERE_IS_TEACHER == "muddat ornatishda" and not request_text.isalpha():
        try:
            time_test = float(request_text)*60
        except:
            bot.send_message(chat_id=teacher_id, text="Muddat noto'g'ri kiritildi iltimos qaytadan urunib ko'ring!")
        else:
            TIME_SETTED = True
            bot.send_message(chat_id=teacher_id, text="Muddat o'rnatildi!")
            WHERE_IS_TEACHER = ""


    if request_text == "Javoblarni yuborish" and chat_id == teacher_id:
        WHERE_IS_TEACHER = "javoblarni yuborishda"
        bot.send_message(chat_id=chat_id, text="Javobni quyidagi formatda yuboring aks holda u qabul qilinmaydi!\n"
                                               "Hamma javob kalitlari ketma-ket quyidagicha:\n\n"
                                               "NAMUNA 👉  abcdbabdcdbccadbcaacbddcbbadac")

    elif chat_id == teacher_id and WHERE_IS_TEACHER == "javoblarni yuborishda":
        teacher_keys_correct = True
        for key in request_text.lower():
            if key not in ['a', 'b', 'c', 'd']:
                teacher_keys_correct = False
        if teacher_keys_correct:
            with open("teacher_keys.txt", 'w') as f:
                f.write(request_text.lower())
            ANSWER_SETTED = True
            WHERE_IS_TEACHER = ""
            bot.send_message(chat_id=teacher_id, text="Javoblar qabul qilindi")
        else:
            bot.send_message(chat_id=teacher_id, text="Javob qabul qilinmadi jaboblarni namunadagidek"
                                                      " kiritganingizni tekshirib yana urunib ko'ring!\n"
                                                      "Namuna 👉  abcdbabdcdbccadbcaacbddcbbadac")

    if request_text == "Testni boshlash" and chat_id == teacher_id:
        if TIME_SETTED and ANSWER_SETTED and len(LIST_OF_TEST) != 0:
            TEST_STARTED = True
            bot.send_message(chat_id=teacher_id, text="Test boshlandi berilgan vaqt tugagandan so'ng natijalar yuboriladi!")
            with open("students.csv", 'r') as file:
                f = csv.DictReader(file, delimiter=',')
                for row in f:

                    for test in LIST_OF_TEST.keys():
                        if LIST_OF_TEST.get(test) == "photo":
                            bot.send_photo(chat_id=row['id'], photo=test, caption="Vaqt ketti omad!")

                        elif LIST_OF_TEST.get(test) == "document":
                            bot.send_document(chat_id=row['id'], data=test, caption="Vaqt ketti omad!")


            time.sleep(time_test)

            with open("students.csv", 'r') as file:
                f = csv.DictReader(file, delimiter=',')
                for row in f:
                    # print(row['id'])
                    bot.send_message(chat_id=row['id'], text="Test vaqti tugadi javoblarni  jonatish uchun 5 daqiqa")
                    TIME_START_ANSWER = datetime.timestamp(datetime.now())

            with open("block_answare.txt", "w") as f:
                file = f.write("1")

            time.sleep(90)


            with open("block_answare.txt", "w") as f:
                file = f.write("0")

            with open("students.csv", 'r') as file:
                f = csv.DictReader(file, delimiter=',')
                for row in f:
                    # print(row['id'])
                    # for test in LIST_OF_TEST:
                    bot.send_message(chat_id=row['id'], text="Test yakunlandi endi javoblar qabul qilinmaydi")


            with open("studentansware.csv", 'r') as file:
                f = csv.DictReader(file, delimiter=',')
                for row in f:
                    text = "Result student:\nFI: {}\nto'g'ri javob: {}\nnoto'g'ri javob: {}".format(
                        row['name'], row['cor_answare'], row['uncor_answare']
                    )
                    bot.send_message(chat_id=teacher_id, text=text)
            LIST_OF_TEST.clear()
            with open("studentansware.csv", 'w') as f:
                file = csv.writer(f, delimiter=',')
                file.writerow(['id', 'name', 'cor_answare', 'uncor_answare'])

        else:
            bot.send_message(chat_id=chat_id, text="Barcha komponentalarni to'liq o'rnatganizga ishonch "
                                                   "hosil qilib yana urunib ko'ring!")



if __name__ == '__main__':
    bot.polling()

    # numpy pandas --- organish kerak
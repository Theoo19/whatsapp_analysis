from os import listdir


def read_file(file_path):
    with open(file_path, "r") as textfile:
        return textfile.read().split("\n")


# Constants
min_word_frequency_length = 5  # characters
max_cluster_time_interval = 30  # minutes


# Character filters
alphabet = "abcdefghijklmnopqrstuvwxyz"
punctuation = ".,?!:;\"'[]{}()<>\\/|@#$%^&*-=_+€~`"
alphabet_array = list(char for char in alphabet)


class Date:
    monday = "Monday"
    tuesday = "Tuesday"
    wednesday = "Wednesday"
    thursday = "Thursday"
    friday = "Friday"
    saturday = "Saturday"
    sunday = "Sunday"

    january = "January"
    february = "February"
    march = "March"
    april = "April"
    may = "May"
    june = "June"
    july = "July"
    august = "August"
    september = "September"
    october = "October"
    november = "November"
    december = "December"

    weekdays = [monday, tuesday, wednesday, thursday, friday, saturday, sunday]
    weekdays_short = ["Mon", "Tues", "Wed", "Thur", "Fri", "Sat", "Sun"]

    months = [january, february, march, april, may, june, july, august, september, october, november, december]
    months_short = ["Jan", "Feb", "Mar", "Apr", "Jun", "Jul", "Aug", "Sept", "Oct", "Nov", "Dec"]


class Directory:
    folder_filter = "filters"
    folder_chats = "chats"
    files_messages = "messages"
    files_words = "words"


class Result:
    minute = "msg_per_min"
    hour = "msg_per_hour"
    day = "msg_per_day"
    week = "msg_per_month"
    month = "msg_per_month"
    date = "msg_per_date"
    year = "msg_per_year"
    author = "msg_per_author"

    all = [minute, hour, day, week, month, date, year, author]


class Format:
    time = "[0-9][0-9]:[0-9][0-9]"
    date_1 = "DD-MM-YYYY"
    date_2 = "MM/DD/YY"
    date_3 = "DD-MM-YY"
    all_dates = [date_1, date_2, date_3]

    regex_dates = {date_1: "[0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9]",
                   date_2: "[0-9]{1,2}/[0-9]{1,2}/[0-9][0-9],",
                   date_3: "[0-9][0-9]-[0-9][0-9]-[0-9][0-9],"}


class Filter:
    announcement = "Whatsapp Announcement"
    sentences = list()
    words = set()

    for file in listdir(Directory.folder_filter):
        if file.endswith(".txt"):
            filename = f"{Directory.folder_filter}/{file}"
            if file.startswith(Directory.files_messages):
                sentences.extend(read_file(filename))
            elif file.startswith(Directory.files_words):
                words.update(filename)
    words.update(alphabet_array)







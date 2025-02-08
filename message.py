import datetime as _datetime
import re as _re

from constants import Directory, Filter, Format, punctuation


def get_chat_file_content(filename):
    with open(f"{Directory.folder_chats}/{filename}", "r", encoding="utf-8") as file:
        return file.read()


def get_date_format(content):
    for date_format in Format.regex_dates:
        if _re.match(Format.regex_dates[date_format], content[:10]):
            return date_format


def separate_messages(content, date_format):
    """Separate the full chat text into a list of strings, where each string represents the full content of one message

    :param content: full chat text
    :type content: str
    :param date_format: DD-MM-YYYY or MM/DD/YY or DD-MM-YY
    :type date_format: str
    :return: all chat messages separated
    :rtype: list of str
    """
    messages_1 = content.split("\n")
    messages_2 = list()
    date_pattern = f"^({Format.regex_dates[date_format]} {Format.time})"

    for message in messages_1:
        if _re.match(date_pattern, message):
            messages_2.append(message)
        elif len(messages_2) > 0:
            messages_2[-1] += " " + message
    return messages_2


def get_message_array(messages, conversion_function, filter_whatsapp_announcements=True, filter_sentences=True):
    """Convert all message strings into Message objects using the specified date format

    :param messages: all chat messages separated
    :type messages: list of str
    :param conversion_function:
    :type conversion_function: function
    :param filter_whatsapp_announcements: if turned on, removes messaged made by Whatsapp instead of users
    :type filter_whatsapp_announcements: bool
    :param filter_sentences: if turned on, removes contents from messages sent by users based on custom filter list
    :type filter_sentences: bool
    :rtype: list of Message
    """
    messages = list(conversion_function(message) for message in messages)
    if filter_whatsapp_announcements:
        messages = list(message for message in messages if message.author != Filter.announcement)
    if filter_sentences:
        for message in messages:
            if message.content in Filter.sentences:
                if message.content == Filter.sentences[0]:
                    message.media = True
                message.content = ""
    return messages


def get_words(text):
    """Create list of words from a string, where each words only exists out of letters

    :param text: block of text, like a sentence
    :type text: str
    :return: words
    :rtype: list of str
    """
    text_blocks = list(text_block.strip(punctuation) for text_block in text.split())
    return list(word for word in text_blocks if word.isalpha())


def get_date_extremes(chats):
    min_date = min(chat.start_date for chat in chats)
    max_date = max(chat.end_date for chat in chats)
    return min_date, max_date


def get_date_range(min_date, max_date):
    """
    :type min_date: datetime.date
    :type max_date: datetime.date
    :rtype: list of datetime.date
    """
    delta = (max_date - min_date).days + 1
    return list(min_date + _datetime.timedelta(days=n) for n in range(delta))


def get_year_range(min_date, max_date):
    """
    :type min_date: datetime.date
    :type max_date: datetime.date
    :rtype: list of int
    """
    return range(min_date.year, max_date.year + 1)


class Message:
    def __init__(self, date_time, author, content):
        """
        :type date_time: datetime.datetime
        :type author: str
        :type content: str
        """
        self.author = author
        self.content = content
        self.datetime = date_time
        self.media = False

    def get_words(self):
        return get_words(self.content.lower())

    def __str__(self):
        return f"{self.datetime.isoformat(sep=' ', timespec='minutes')} - {self.author}: {self.content}"

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.content)

    @staticmethod
    def empty():
        return Message(_datetime.datetime.min, "Author", "Content")

    @staticmethod
    def announcement(date_time, content):
        """When a message has no author, it's sent by Whatsapp and gets a default author name assigned

        :type date_time: datetime.datetime
        :type content: str
        :rtype: Message
        """
        return Message(date_time, Filter.announcement, content)

    @staticmethod
    def date_format_1(message):
        """Converts message from str format to Message format using DD-MM-YYYY date-format

        :type message: str
        :rtype: Message
        """
        author_index = message.find(":", 19)

        date = message[:10].split("-")
        date_time = _datetime.datetime(int(date[2]),
                                       int(date[1]),
                                       int(date[0]),
                                       int(message[11:13]),
                                       int(message[14:16]))

        if author_index == -1:
            return Message.announcement(date_time, message[19:])
        author = message[19:author_index]
        content = message[author_index + 2:]
        return Message(date_time, author, content)

    @staticmethod
    def date_format_2(message):
        """Convert message from str format to Message format using MM/DD/YY date-format

        :type message: str
        :rtype: Message
        """
        date_index = message.find(",")
        author_index = message.find(":", date_index + 10)

        date = message[:date_index].split("/")
        date_time = _datetime.datetime(int(date[2]) + 2000,
                                       int(date[0]),
                                       int(date[1]),
                                       int(message[date_index + 2:date_index + 4]),
                                       int(message[date_index + 5:date_index + 7]))

        if author_index == -1:
            return Message.announcement(date_time, message[date_index + 10:])
        author = message[date_index + 10:author_index]
        content = message[author_index + 2:]
        return Message(date_time, author, content)

    @staticmethod
    def date_format_3(message):
        """Convert message from str format to Message format using DD-MM-YY date-format

        :type message: str
        :rtype: Message
        """
        author_index = message.find(":", 18)

        date = message[:8].split("-")
        date_time = _datetime.datetime(int(date[2]) + 2000,
                                       int(date[1]),
                                       int(date[0]),
                                       int(message[10:12]),
                                       int(message[13:15]))

        if author_index == -1:
            return Message.announcement(date_time, message[18:])
        author = message[18:author_index]
        content = message[author_index + 2:]
        return Message(date_time, author, content)

    @staticmethod
    def get_conversion_function(date_format):
        match date_format:
            case Format.date_1:
                return Message.date_format_1
            case Format.date_2:
                return Message.date_format_2
            case Format.date_3:
                return Message.date_format_3


class Chat:
    def __init__(self, messages, authors, start_date, end_date, name):
        """
        :type messages: list of Message
        :type authors: list of str
        :type start_date: datetime.date
        :type end_date: datetime.date
        :type name: str
        """
        self.__messages = messages
        self.authors = authors

        self.start_date = start_date
        self.end_date = end_date

        self.name = name

        self.length = len(self.__messages)

    def get_date_range(self):
        return get_date_range(self.start_date, self.end_date)

    def get_year_range(self):
        return get_year_range(self.start_date, self.end_date)

    def __len__(self):
        return self.length

    def __str__(self):
        return "\n".join(str(message) for message in self.__messages)

    def __repr__(self):
        return str(self)

    def __getitem__(self, item):
        return self.__messages[item]

    def __iter__(self):
        self.__index = 0
        return self

    def __next__(self):
        if self.__index < self.length:
            message = self.__messages[self.__index]
            self.__index += 1
            return message
        del self.__index
        raise StopIteration

    @staticmethod
    def from_message_array(messages, name=""):
        """
        :type messages: list of Message
        :type name: str
        :rtype: Chat
        """
        messages = sorted(messages, key=lambda message: message.datetime)
        authors = sorted(set(message.author for message in messages))
        min_date = messages[0].datetime.date()
        max_date = messages[-1].datetime.date()
        return Chat(messages, authors, min_date, max_date, name)

    @staticmethod
    def from_string(content, date_format, name=""):
        """Create Chat object from full chat text

        :param content: full chat text
        :type content: str
        :param date_format: DD-MM-YYYY or MM/DD/YY or DD-MM-YY
        :type date_format: str
        :type name: str
        :rtype: Chat
        """
        messages = separate_messages(content, date_format)
        conversion_function = Message.get_conversion_function(date_format)
        return Chat.from_message_array(get_message_array(messages, conversion_function), name)

    @staticmethod
    def from_filter(messages, author_filter=None, date_filter=None, time_filter=None, length_filter=None, name=""):
        """Create Chat object from message list with specified filters

        :type messages: list of Message or Chat
        :type author_filter: None or str or list
        :param date_filter: minimum and maximum date to filter
        :type date_filter: None or (datetime.datetime, datetime.datetime)
        :param time_filter: minimum and maximum time to filter
        :type time_filter: None or (datetime.datetime.time, datetime.datetime.time)
        :param length_filter: minimum and maximum message length to filter
        :type length_filter: None or (int, int)
        :type name: str
        :return: filtered chat
        :rtype: Chat
        """
        if author_filter is not None:
            if type(author_filter) is str:
                messages = list(message for message in messages if message.author == author_filter)
            else:
                messages = list(message for message in messages if message.author in author_filter)
        if date_filter is not None:
            min_date, max_date = date_filter
            messages = list(message for message in messages if min_date <= message.datetime <= max_date)
        if time_filter is not None:
            min_time, max_time = time_filter
            messages = list(message for message in messages if min_time <= message.datetime.time <= max_time)
        if length_filter is not None:
            min_len, max_len = length_filter
            messages = list(message for message in messages if min_len <= len(message.content) <= max_len)
        return Chat.from_message_array(messages, name)

    @staticmethod
    def from_file(filename, name=""):
        """Create Chat object from text file located in the folder specified in constants

        :rtype: Chat
        """
        content = get_chat_file_content(filename)
        date_format = get_date_format(content)
        return Chat.from_string(content, date_format, name)

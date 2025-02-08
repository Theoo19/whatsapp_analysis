# Default libraries
from re import findall
from itertools import chain
import pandas as pd

# Project files
from constants import *
from message import *
from visualisation import *


class ChatData:
    @staticmethod
    def _parameters(chats, data_type):
        match data_type:
            case Result.minute:
                return range(24 * 60), lambda msg: msg.datetime.time().hour * 60 + msg.datetime.time().minute
            case Result.hour:
                return range(24), lambda msg: msg.datetime.hour
            case Result.day:
                return Date.weekdays, lambda msg: Date.weekdays[msg.datetime.weekday()]
            case Result.month:
                return Date.months, lambda msg: Date.months[msg.datetime.month - 1]
            case Result.week:
                return range(1, 53), lambda msg: msg.datetime.isocalendar()[1]
            case Result.author:
                if isinstance(chats, Chat):
                    authors = chats.authors
                else:
                    authors = list(set((author for author in chat.authors) for chat in chats))
                return authors, lambda msg: msg.author
            case Result.date:
                if isinstance(chats, Chat):
                    dates = chats.get_date_range()
                else:
                    dates = get_date_range(*get_date_extremes(chats))
                return dates, lambda msg: msg.datetime.date()
            case Result.year:
                if isinstance(chats, Chat):
                    years = chats.get_year_range()
                else:
                    years = get_year_range(*get_date_extremes(chats))
                return years, lambda msg: msg.datetime.year

    @staticmethod
    def from_chat(chat, index, column, get_index_function, data=0):
        """
        :type chat: Chat or list of Message
        :type index: Any
        :type column: Any
        :type data: Any
        :type get_index_function: function
        :rtype: pd.DataFrame
        """
        results = pd.DataFrame(index=index, columns=[column], data=data)
        for message in chat:
            results.loc[get_index_function(message)][column] += 1
        return results

    @staticmethod
    def from_chats(chats, index, columns, get_index_function, data=0):
        results = pd.DataFrame(index=index, columns=columns, data=data)
        for chat, column in zip(chats, columns):
            for message in chat:
                results[column][get_index_function(message)] += 1
        return results

    @staticmethod
    def from_command_chat(chat, data_type, column="Messages"):
        index, get_index_function = ChatData._parameters(chat, data_type)
        return ChatData.from_chat(chat, index, column, get_index_function)

    @staticmethod
    def from_command_chats(chats, data_type, columns=None):
        index, get_index_function = ChatData._parameters(chats, data_type)
        if columns is None:
            columns = list(f"Messages {i+1}" for i in range(len(chats)))
        return ChatData.from_chats(chats, index, columns, get_index_function)

    @staticmethod
    def message_lengths(chat):
        """
        :type chat: Chat
        :rtype: pd.DataFrame
        """
        results = pd.DataFrame(index=range(chat.length), columns=["Length (words)", "Length (characters)"], data=0)
        for i in range(chat.length):
            results["Length (words)"][i] = len(chat[i].get_words())
            results["Length (characters)"][i] = len(chat[i])
        return results

    @staticmethod
    def chat_starters(chat, max_interval=max_cluster_time_interval):
        """
        :type chat: Chat
        :param max_interval: maximum amount of minutes between messages before a new cluster is created
        :type max_interval: int
        :rtype: pd.DataFrame
        """
        column = "Chats started"
        results = pd.DataFrame(index=chat.authors, columns=[column], data=0)
        results[column][chat[0].author] += 1

        for i in range(1, chat.length):
            time_interval = (chat[i].datetime - chat[i-1].datetime).total_seconds() / 60
            if time_interval > max_interval:
                results[column][chat[i].author] += 1
        return results

    @staticmethod
    def unique_words(chat):
        words = list(chain(*list(message.get_words() for message in chat)))
        word_index = list(set(words))
        return ChatData.from_chat(list(words), word_index, "Frequency", lambda word: word)

    @staticmethod
    def filter_unique_words(results, min_length=min_word_frequency_length):
        frequencies = results.to_dict()["Frequency"]
        for word in list(frequencies.keys()):
            if len(word) < min_length or word in Filter.words:
                del frequencies[word]
        return frequencies

    @staticmethod
    def letters(chat):
        results = pd.DataFrame(index=alphabet_array, columns=["Frequency"], data=0)
        for message in chat:
            for character in message.content.lower():
                if character in alphabet:
                    results["Frequency"][character] += 1
        return results

    @staticmethod
    def search(chat, pattern, match_case=False, words=False, regex=False):
        """
        :type chat: Chat or list of Message
        :type pattern: str
        :param match_case: match upper and lowercase
        :type match_case: bool
        :param words: only search for actual words
        :type words: bool
        :param regex: use regular expression
        :type regex: bool
        :return: number of occurrences of search
        :rtype: int
        """
        if match_case:
            texts = list(message.content for message in chat)
        else:
            pattern = pattern.lower()
            texts = list(message.content.lower() for message in chat)
        if regex:
            return sum(len(findall(pattern, text)) for text in texts)
        if words:
            texts = list(get_words(text) for text in texts)
        return sum(text.count(pattern) for text in texts)

    @staticmethod
    def search_list(chat, pattern_list, match_case=False, words=False, regex=False):
        """
        :type chat: Chat or list of Message
        :type pattern_list: list of str
        :param match_case: match upper and lowercase
        :type match_case: bool or list of bool
        :param words: only search for actual words
        :type words: bool or list of bool
        :param regex: use regular expression
        :type regex: bool or list of bool
        :return: results with number of occurrences of searches
        :rtype: pd.DataFrame
        """
        searches = len(pattern_list)
        if type(match_case) is bool:
            match_case = [match_case] * searches
        if type(words) is bool:
            words = [words] * searches
        if type(regex) is bool:
            regex = [regex] * searches

        search_data = list(ChatData.search(chat, pattern_list[i], match_case[i], words[i], regex[i]) for i in
                           range(searches))
        return pd.DataFrame(index=pattern_list, columns=["Frequency"], data=search_data)

    @staticmethod
    def word_timeline(chat, word):
        """
        :type chat: Chat
        :type word: str
        :rtype: pd.DataFrame
        """
        word = word.lower()
        dates = chat.get_date_range()
        results = pd.DataFrame(index=dates, columns=["Frequency"], data=0)

        for message in chat:
            results["Frequency"][message.datetime.date()] += message.get_words().count(word)
        return results

    @staticmethod
    def count_media(chat):
        return sum(message.media for message in chat)


def main():
    chat = Chat.from_file("Chat 4B.txt")

    data_date = ChatData.from_command_chat(chat, Result.date)
    figure = get_figure_date(data_date)[0]
    figure.savefig("fig1.pdf")
    plt.show()

    data_hour = ChatData.from_command_chat(chat, Result.hour)
    figure = get_figure_days(data_hour)[0]
    figure.savefig("fig2.pdf")


if __name__ == '__main__':
    main()

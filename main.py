import re
import os
import langdetect

def ensure_English(sentences):
    """
        Returns only English sentences from sentences that contain a combination of languages.

        Input:
            sentences (list): The list of sentences that contains different languages
        
        Output:
            english_sentences (list): The list of sentences that contains only English sentences
    """
    english_sentences = []

    for sentence in sentences:
        # getting the probability of languages in the sentence
        language_probability = langdetect.detect_langs(sentence)
        # adding the sentence if only English is detected within the sentence
        if len(language_probability) == 1 and language_probability[0].lang == "en":
            english_sentences.append(sentence)
    
    return english_sentences


def find_lists(sentences):
    """
        Takes sentences that contain a list over the next lines and breaks them into individual
        sentences for each item in the list.

        Example: 
            The following are fun programming hobbies:
                - Reading technical books
                - Doing programming challenges
            The example text will be rewritten as:
                The following are fun programming hobbies: Read technical books.
                The following are fun programming hobbies: Doing programming challenges.

        Input:
            sentences (list): A list of sentences that could contain a list
        
        Output:
            sentences (list): A reworked list that will fix the lists as shown above. If there
            no lists then sentences will not change
    """

    # split of punctuation, though not : because we still need it
    sentence_index = 0
    # Iterating through the sentences list to find all potential lists
    while sentence_index < len(sentences):
        # list detection based on : or ; starting list
        current_sentence = sentences[sentence_index]
        if current_sentence[-1] in [":", ";"]:
            # get the first non-zero character
            first_char = sentences[sentence_index+1].strip()[0]
            list_index = sentence_index + 1
            # If the first character matches the list stub then it is consider part of the list
            while(sentences[list_index][0] == first_char and list_index < len(sentences)):
                # Setting the sentence to be the pre-list stub and the list and a period
                sentences[list_index] = current_sentence + sentences[list_index] + "."
                list_index += 1
            sentence_index = list_index
        else:
            # get the next sentence if the current one doesn't include a list
            sentence_index += 1
    return sentences

def limit_section(sentences, length_limit):
    """
        Takes each sentence and limits it to the length_limit. This is done because QA models, like
        BERT and T5, have a character limit of up to 512 characters.

        Input:
            sentences (list): This is the list, where each sentence will be have its length limited
            length_limit (int): The limit of each sentence
        
        Output:
            limit_sentences (list): This is the new list where every section is less than 512 characters.
    """
    # Limiting each text section up to 512 characters before adding it to the new file
    # 512 comes from how QA models like Bert can take only upto 512 characters for its text
    limited_sentences = []
    sentence_index = 0
    while sentence_index < len(sentences):
        section = ""
        character_count = length_limit

        current_index = sentence_index
        # Continue adding sentences until the section over at most 512 characters
        while current_index < len(sentences) and character_count > 0:
            current_sentence = sentences[current_index].strip()
            # Accounting for sentences greater than 512 characters
            if character_count == length_limit and len(current_sentence) + 1 > length_limit:
                # Cut off characters up to 511 characters and then add a space at the end
                remainder_sentence = current_sentence[length_limit:]
                current_sentence = current_sentence[:length_limit - 2] + "."

            # Checking if the current section has enough characters for the next sentence
            character_count -= len(current_sentence) + 1
            if character_count >= 0:
                # Add the sentence if the section does have enough characters
                section += current_sentence + " "
                # Increment the curent index to get the next sentence
                current_index += 1
            else:
                # If the section doesn't have enough room for this sentence, start from that index
                # for the next iteration of this loop
                break

        sentence_index = current_index
        limited_sentences.append(section)
    
    return limited_sentences


def get_sentences(file_name):
    """
        Takes all the paragraphs into a file and breaks it into sentences

        Input:
            file_name (string): The name of the file containing the paragraphs
        
        Returns: 
            setences (list): A list of sentences from the file
    """

    # opening the file to split into individual sentences
    with open(file_name, "r", encoding="utf-8") as text:
        file_contents = text.read()
        line_contents = file_contents.split("\n")

        # Getting the sentences from each paragraph
        # This is done by iterating through each line from text and splitting it up at the punctuation
        sentences = []
        add_period = lambda sentence: sentence + '.' if sentence[-1] not in [";",":"] else sentence
        for line in line_contents:
            # splitting the line into a list separated by punctuation and add it to the sentences list
            new_sentences = re.split(r'[?.!\n\t]', line)
            # Additionally, the lines that contain nothing are removed
            # Every sentence is ended with a period if the last character isn't in [;, :]
            sentences += list(filter(None, new_sentences))
        
        # Fixing the sentences with lists in them
        sentences = find_lists(sentences)

        for sentence_index in range(len(sentences)):
            sentences[sentence_index] = sentences[sentence_index] + "."

        # Limiting each section to be up to 512 characters
        sentences = limit_section(sentences, 512)

        # ensuring english sentences
        sentences = ensure_English(sentences)

        base_filename = os.path.basename(file_name)
        with open("sentences_" + base_filename, "w", encoding="utf-8") as new_file:
            for sentence in sentences:
                if sentence.strip()[-1] != ".":
                    print(sentence[-1])
                    raise Exception("Bad sentence\n {}".format(sentence))
                new_file.write(sentence.strip() + "\n")


if __name__ == "__main__":
    get_sentences("texts\\privacy1.txt")
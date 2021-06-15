import nltk
import sys
import os
import math
import string

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    filesdict = dict()
    for file in os.listdir(directory):
        if file.endswith(".txt"):
            with open(os.path.join(directory, file), 'r') as ofile:
                contents = ofile.read()
            filesdict[file] = contents

    return filesdict
    # raise NotImplementedError


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.

    """

    words = nltk.word_tokenize(document.lower())
    #stop_words = set(nltk.corpus.stopwords.words("english"))
    # print(f"{words}")
    new_words = [
        x for x in words if x not in string.punctuation and x not in nltk.corpus.stopwords.words("english")]
    # print(f"{new_words}")

    return new_words
    # raise NotImplementedError


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.

"""
    idfDict = {}
    N = len(documents)
    # load up counts
    unique_words = set(sum(documents.values(), []))
    for words in unique_words:
        count = 0
        for doc in documents.values():
            if words in doc:
                count += 1

        idfDict[words] = math.log(N/count)

    # print(f"{idfDict.items()}")
    return(idfDict)
    # raise NotImplementedError


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
"""
    filescores = dict()
# for each file match each word in the query to that files content
# if present add totoal the tf_idf (count * idfs for that word)
# store in filescore for that file
    for file, words in files.items():
        total_tf_idf = 0
        for word in query:
            # print(f"count for {word} in {file} is {words.count(word)}")

            total_tf_idf += words.count(word) * idfs[word]
        # print(f"{file} has a tfid of {total_tf_idf}")
        filescores[file] = total_tf_idf
# sort the file_score by the total_tf_IDF
    rfiles = sorted(filescores.items(),
                    key=lambda x: x[1], reverse=True)
    # return the top n file names in list format
    return list(rfiles[0][:n])

    # raise NotImplementedError


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """

    topsentscores = {}
    for asent, swords in sentences.items():
        topsentscore = 0
        for aword in query:
            if aword in swords:
                topsentscore += idfs[aword]

        if topsentscore != 0:
            density = sum([swords.count(x) for x in query]) / len(swords)
            topsentscores[asent] = (topsentscore, density)

    sorted_by_score = [k for k, v in sorted(
        topsentscores.items(), key=lambda x: (x[1][0], x[1][1]), reverse=True)]

    return sorted_by_score[:n]

    raise NotImplementedError


if __name__ == "__main__":
    main()

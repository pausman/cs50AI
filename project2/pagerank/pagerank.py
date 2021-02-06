import os
import random
import re
import sys
import math

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")

    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    rdict = {}
    if corpus[page]:
        adprob = (1-damping_factor)/len(corpus)
        dprob = damping_factor/len(corpus[page])
        # get the links from the page
        for a in corpus:
            rdict[a] = adprob
        for a in corpus[page]:
            rdict[a] = rdict[a] + dprob
    else:
        # no links so every page has equal probability ie 1/len[corpse] or number
        for a in corpus:
            rdict[a] = 1/len(corpus)
    return rdict


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # setup page rank dictionary
    pagerank_dict = {}
    for a in corpus:
        pagerank_dict[a] = 0

    # Start with random page

    page = random.choice(list(corpus.keys()))

    for i in range(n - 1):
        pagerank_dict[page] = pagerank_dict[page]+1
        rdict = transition_model(corpus, page, damping_factor)
        page = random.choices(list(rdict.keys()), rdict.values())[0]

    for a in pagerank_dict:
        pagerank_dict[a] = pagerank_dict[a]/n
    return pagerank_dict


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pagerank = {}
    pagechange = {}
    lennumber = 1 / len(corpus)
    # initialize
    for page in corpus:
        pagerank[page] = lennumber
        pagechange[page] = 10

    part1 = (1-damping_factor)*lennumber

    smallestdelta = 1000
    while smallestdelta > .0005:

        for page in pagerank.keys():
            oldpr = pagerank[page]
            part2 = 0
            for page2, pagelinks in corpus.items():
                if not pagelinks:
                    pagelinks = corpus.keys()
                if page in pagelinks:
                    part2 = part2 + pagerank[page2]/len(pagelinks)
            newpr = part1 + damping_factor*part2
            pagerank[page] = newpr
            pagechange[page] = abs(newpr-oldpr)
        smallestdelta = .0005
        for page3 in pagechange:
            if smallestdelta < pagechange[page3]:
                smallestdelta = pagechange[page3]

    return pagerank


if __name__ == "__main__":
    main()

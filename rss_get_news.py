# feedparser documentation: http://pythonhosted.org/feedparser/
import feedparser


# Usage:  feed = fetch(s)
# Before: s is a valid corporation ticker
# After:  feed contains news regarding or related to the
#         desired corporation
def fetch(s):
    return feedparser.parse("http://feeds.finance.yahoo.com/rss/2.0/headline?s=%s&region=US&lang=en-US"%s)


# Usage:  news = pull_news(feed)
# Before: feed was fetched using the fetch() function
# After:  news is a list of lists where
#         news[0] is a list of titles and
#         news[1] is a corresponding list of  links
def pull_titles_and_links(feed):
    titles = []
    links = []
    for i in range(len(feed.entries)):
        titles.append(feed.entries[i].title)
        links.append(feed.entries[i].link)
    return [titles, links]



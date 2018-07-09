# Crawler

The crawler for the article retrieval system. <br>
Read our [report](https://github.com/rebryk/SPbAU-IR/blob/master/report/report.pdf).

## Installation
Python 3 is required

```
pip3 install -r requirements.txt
python -m nltk.downloader popular
```
## Structure 

### WebPage
The ```WebPage``` represents a web page.

### Website
The ```Website``` holds a queue with web pages. <br>
Also it checks ```robots.txt```.

### Frontier
The ```Frontier``` holds a queue with websites, which are allowed.

### Crawler
The ```Crawler``` works in a separate process. <br>
You can set tup ```user_agent```, ```max_pages_count```, ```max_depth```, ```delay```.

## Config structure
```
{
  "user_agent": <agent name>,
  "max_pages_count": <max pages count>,
  "max_depth": <max depth>,
  "delay": <delay in ms>
}
```

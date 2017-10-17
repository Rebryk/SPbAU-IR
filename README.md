# Crawler

The crawler for the article retrieval system.

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

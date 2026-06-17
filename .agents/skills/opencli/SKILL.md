---
name: opencli
description: Use OpenCLI (opencli) to access websites, social media, and web services from the terminal. Use this when the user wants to browse hot topics, trending content, search, or access data from websites like Bilibili, Zhihu, HackerNews, Twitter/X, Reddit, etc.
---

# OpenCLI Tool

This skill teaches you how to use the OpenCLI tool (`@jackwener/opencli`) to access websites and services directly from the terminal.

## Available Commands

### Check status
```bash
opencli doctor       # Diagnose environment
opencli list         # List all available commands
```

### Social / Content Platforms
```bash
opencli bilibili hot                     # Bilibili trending
opencli zhihu hot                        # Zhihu hot list
opencli hackernews top --limit 10        # HackerNews top stories
opencli reddit hot --subreddit reactjs   # Reddit hot posts
```

### Web Search
```bash
opencli search "your query"              # Web search
```

## Prerequisites

- **Browser Bridge**: For some platforms (Bilibili, Zhihu), the Browser Bridge Chrome/Edge extension must be installed and connected.
- Run `opencli doctor` to check connectivity.

## Notes

- OpenCLI v1.7.14 is installed globally as a Node.js CLI tool.
- For browser-dependent commands, ensure the Browser Bridge daemon is running (`opencli daemon restart`).

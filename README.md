# Kindle Bulk Downloader

Uses an existing browser session to bulk export Kindle e-books from Amazon before they disable this feature.

Start Chrome in debug mode:

On macOS:
```sh
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
```

On Windows:
```sh
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
```

Sign in to amazon.co.uk in the browser, then run the script with uv:
```sh
uv run main.py
```

If something goes wrong, you can resume from a specific page:
```sh
uv run main.py --page 6
```


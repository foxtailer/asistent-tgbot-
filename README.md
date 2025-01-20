# asistent-tgbot-

- Python
- telegram API
- SQL
- aigram 3

A bot that helps users learn a new language. It adds words and examples to a database and offers different games and tests based on these words.
You can interact with the bot using the commands. For example:

`/test10` Select ten random words from the database and ask the user for each of them, providing four variants to choose from. When the game finishes, the bot will display the results.

```
Test is over!
Nice job!
9/10
```

# Run

1. Navigate to the `asistent-tgbot-` folder.
2. Create `.env` file, with your bot token inside `TOKEN = "4806259501:oGWgcwESGV1QTnsQsBx3ABjpn8jZxM8HOBy"`
3. In docker file set file that start bot.
    - `CMD ["python", "main_pol.py"]` for poling.
    - `CMD ["python", "main_wh.py"]` for webhuck.
4. If you want use webhuck set url inside `main_wh.py`
    - `WEBHOOK_HOST = "https://bfe4-213-231-21-243.ngrok-free.app"`
2. Create a Docker image using the command: `docker build -t bot:01 .`
3. Run the container with the following command: `docker run --rm bot:01`

![Alt text](img/tg1.png)


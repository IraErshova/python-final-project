# Python final project

## How to run the project locally

1. Create local environment:

```bash
python3.12 -m venv venv
```

2. Activate local environment:

```bash
. venv/bin/activate  
```

3. Install necessary packages:

```bash
pip install -r requirements.txt
```

4. Create `.env` file

```bash
cp .env-example .env
```

5. Get API keys from:

- Spoonacular API key - https://spoonacular.com/food-api
- Telegram bot API key - https://t.me/BotFather

6. Update `.env` with your API keys

7. Run `main.py` file

```bash
python3.12 main.py
```


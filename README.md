# pmos-discord-bot

Depends on discord.py library

To parse devices:

```bash
python parse-devices.py
```

To run:

```bash
python main.py \
  --token "$(cat token)" \
  --proxy "http://127.0.0.1:8085" \
  --channel_id 1379196217371660469 \
  --devices_category_id 1379193879265411072 \
  --vendors_category_id 1379196710793777193
```

# ШилоБот

[Telegram @realShiloBot](http://telegram.me/realShiloBot).

# Установка
Загружаем трэки в `db.yaml`.

```
python -m shilobot.db --action download --artist-id 218095
```

- [ ] Семантический анализ эинт изи.

Поэтому строим список фраз в `db.yaml` ручками. По умолчанию каждая строка это фраза. Тексты не оч, поэтому нужны правки руками.

Запускаем бота.

```
TOKEN=xxxxx python -m shilobot.telegram.bot
```

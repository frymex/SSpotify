**SSpotify** — мини фреймворк для скачивания и получения информации музыки Spotify. Основан на [librespot](https://github.com/kokarare1212/librespot-python)

### # Установка

```
git clone https://github.com/frymex/SSpotify.git && cd SSpotify
pip install -r requirements.txt | pip3 install -r requirements.txt
```

### # Использование 

В файле `demo.py` есть живой пример использования этого фреймворка , поменяйте значения `email` и `password` . После успешной авторизации вы можете удалить эти параметры. 

### # Кастомизация

Пример правильной кастомизации и настройки скрипта, для этого используем класс `_Config` из client.api

```python
from client.api import _Config

_Config.MUSIC_FORMAT = 'mp3' # you can set ogg or mp3
_Config.SKIP_EXISTING_FILES = False # set true if you need skip already existsing files
```

### # Модули и требования

| Название  | Версия | Windows                           | Linux/Ubuntu                       |
| --------- | ------ | --------------------------------- | ---------------------------------- |
| librespot | 0.0.6  | `pip install -U ﻿librespot==0.0.6` | `pip3 install -U ﻿librespot==0.0.6` |
| pydub     | 0.25.1 | `pip install -U ﻿pydub==0.25.1`    | `pip3 install -U ﻿pydub==0.25.1`    |
| requests  | 2.28.1 | `pip install -U ﻿requests==2.28.1` | `pip3 install -U ﻿requests==2.28.1` |
| music-tag | 0.4.3  | pip install -U ﻿music-tag==0.4.3   | pip3 install -U ﻿music-tag==0.4.3   |


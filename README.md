# ssi_pingme

## Install 

``` sh
pip install git+https://github.com/ssi-dk/ssi_pingme.git
```

## How to use

To import and use in your python code you can do the following:

``` python
from pingme import (api, core)


core.set_env_variables(
    config_path="/path/to/config/file"
)

api.webhook_card_simple(
  title = "My title",
  text = "My text"
)

```

The config file should have the webhook url set (https://postman-echo.com/post by default). You can modify the [default config file](src/pingme/config/config.default.env) to include webhook and email smtp server details.

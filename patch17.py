import tomli
import tomli_w
with open('pyproject.toml', 'rb') as f:
    config = tomli.load(f)
config['tool']['pytest']['ini_options']['tmp_path_retention_policy'] = 'all'
config['tool']['pytest']['ini_options']['tmp_path_retention_count'] = 3
with open('pyproject.toml', 'wb') as f:
    tomli_w.dump(config, f)
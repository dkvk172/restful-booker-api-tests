import pathlib, yaml

def load_config():
    path = pathlib.Path(__file__).parent.parent / 'config'/'settings.yaml'
    with open(path, encoding='utf-8') as f:
        return yaml.safe_load(f)
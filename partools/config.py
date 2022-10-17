import yaml

with open('./config.yaml', 'r', encoding='utf8') as f:
    CONFIG = yaml.safe_load(f)

with open('./token.yml', 'r', encoding='utf8') as f:
    token = yaml.safe_load(f)['token']

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token}'
}

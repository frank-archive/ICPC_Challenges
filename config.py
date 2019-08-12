import os

JUDGE_ADDR = os.getenv('JUDGE_ADDR') or 'localhost'
JUDGE_PORT = os.getenv('JUDGE_PORT') or '5000'
JUDGE_PORT = int(JUDGE_PORT)
JUDGE_TOKEN = os.getenv('JUDGE_TOKEN') or 'set_token'

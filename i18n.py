import json
import os

CONFIG_FILE = "config.json"

TRANSLATIONS = {
    "English": {
        "check_interval": "Check Interval",
        "language": "Language",
        "quit": "Quit",
        "check_log": "Check Log",
        "5_sec": "5 seconds (Debug)",
        "1_min": "1 minute",
        "5_min": "5 minutes",
        "10_min": "10 minutes",
        "30_min": "30 minutes",
        "title": "Give my time back",
        "log_checking": "Running scheduled check... (Current interval: {current_interval}s)",
        "log_already_paused": "Leigod is ALREADY PAUSED. Doing nothing.",
        "log_leigod_on": "Leigod is ON. Checking for active games...",
        "log_game_detected": "Game detected: {game}. Will NOT pause.",
        "log_pause_sequence": "Proceeding to pause Leigod via background click...",
        "log_window_not_found": "Could not find the Leigod window!",
        "log_pause_complete": "Pause sequence complete."
    },
    "中文": {
        "check_interval": "检查间隔",
        "language": "语言 / Language",
        "quit": "退出",
        "check_log": "查看日志",
        "5_sec": "5 秒 (调试)",
        "1_min": "1 分钟",
        "5_min": "5 分钟",
        "10_min": "10 分钟",
        "30_min": "30 分钟",
        "title": "还我时长",
        "log_checking": "运行定时检查... (当前间隔: {current_interval}秒)",
        "log_already_paused": "雷神加速器已暂停。无需操作。",
        "log_leigod_on": "雷神加速器运行中。正在检查是否有游戏运行...",
        "log_game_detected": "检测到游戏: {game}。不执行暂停。",
        "log_pause_sequence": "开始通过后台点击暂停雷神加速器...",
        "log_window_not_found": "未找到雷神加速器窗口！",
        "log_pause_complete": "暂停操作完成。"
    }
}

current_lang = "English"

def load_lang():
    global current_lang
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            current_lang = config.get("language", "English")
    except Exception:
        pass

def set_lang(lang):
    global current_lang
    current_lang = lang

def get_lang():
    return current_lang

def t(key, **kwargs):
    text = TRANSLATIONS.get(current_lang, TRANSLATIONS["English"]).get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except KeyError:
            return text
    return text

# Load language initially
load_lang()

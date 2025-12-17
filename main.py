import yaml
import os
from pathlib import Path

def read_all_yaml_files(directory="users"):
    all_players = []
    
    if not os.path.exists(directory):
        print(f"Папка '{directory}' не существует")
        return all_players
    
    yaml_files = list(Path(directory).rglob("*.yaml")) + list(Path(directory).rglob("*.yml"))
    
    for filepath in yaml_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
                filename = filepath.name
                
                if data:
                    players = extract_players_from_data(data, filename)
                    all_players.extend(players)
                    
        except yaml.YAMLError as e:
            print(f"✗ Ошибка YAML в {filepath.name}: {e}")
        except Exception as e:
            print(f"✗ Ошибка чтения {filepath.name}: {e}")
    
    return all_players

def extract_players_from_data(data, filename):
    players = []
    
    if isinstance(data, list):
        for item in data:
            player = extract_player_info(item)
            if player and player['money'] is not None:
                players.append(player)
    
    elif isinstance(data, dict):
        player = extract_player_info(data)
        if player and player['money'] is not None:
            players.append(player)
    
    for player in players:
        player['source_file'] = filename
    
    return players

def extract_player_info(item):
    player = {
        'nickname': None,
        'money': None,
        'raw_data': item
    }
    
    nickname = None
    if 'last-account-name' in item:
        nickname = str(item['last-account-name']).strip()
    elif 'nickname' in item:
        nickname = str(item['nickname']).strip()
    elif 'name' in item:
        nickname = str(item['name']).strip()
    
    player['nickname'] = nickname
    
    money = None
    if 'money' in item:
        money_value = item['money']
        try:
            if isinstance(money_value, str):
                money_clean = money_value.replace(' ', '').replace(',', '.')
                money_clean = ''.join(c for c in money_clean if c.isdigit() or c == '.' or c == '-')
                if money_clean:
                    money = float(money_clean)
            else:
                money = float(money_value)
        except (ValueError, TypeError) as e:
            print(f"  Внимание: некорректное значение money: {money_value}")
            money = 0.0
    
    player['money'] = money
    
    if not player['nickname']:
        return None
    
    return player

def display_top_10_players(players, output_file="top10_players.txt"):
    """Отображение топа-10 игроков"""
    if not players:
        print("Нет данных об игроках")
        return []
    
    valid_players = [p for p in players if p['money'] is not None]
    
    if not valid_players:
        print("Нет игроков с указанным балансом")
        return []
    
    valid_players.sort(key=lambda x: x['money'], reverse=True)
    top_10 = valid_players[:10]
    
    report_lines = [
        "ТОП-10 ИГРОКОВ ПО БАЛАНСУ",
        "=" * 70,
        f"Всего игроков: {len(valid_players)}",
        f"Всего файлов: {len(set(p['source_file'] for p in valid_players))}",
        "=" * 70,
        "№  Никнейм                 Баланс       Файл",
        "-" * 70
    ]
    
    for i, player in enumerate(top_10, 1):
        line = f"{i:2}. {player['nickname'][:20]:20} {player['money']:10.2f}  {player['source_file'][:25]}"
        print(line)
        report_lines.append(line)
    
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write('\n'.join(report_lines))
            print(f"\nРезультат сохранён в: {output_file}")
        except Exception as e:
            print(f"Ошибка при записи: {e}")
    
    return top_10

def analyze_player_data(players):
    print("\n" + "="*70)
    print("АНАЛИЗ ДАННЫХ ИГРОКОВ")
    print("="*70)
    
    if not players:
        print("Нет данных для анализа")
        return
    
    files_dict = {}
    for player in players:
        filename = player['source_file']
        if filename not in files_dict:
            files_dict[filename] = []
        files_dict[filename].append(player)
def save_full_data(players, filename="all_players.txt"):
    if not players:
        return
    
    players.sort(key=lambda x: x['money'] if x['money'] is not None else -float('inf'), reverse=True)
    
    with open(filename, 'w', encoding='utf-8') as file:
        file.write("ПОЛНЫЙ СПИСОК ИГРОКОВ\n")
        file.write("=" * 80 + "\n")
        file.write("№  Никнейм                 Баланс       Файл\n")
        file.write("-" * 80 + "\n")
        
        for i, player in enumerate(players, 1):
            money = player['money'] if player['money'] is not None else 0.0
            line = f"{i:3}. {player['nickname'][:25]:25} {money:12.2f}  {player['source_file']}\n"
            file.write(line)

if __name__ == "__main__":
    input_directory = input("Введите название папки (по умолчанию 'users'): ") or "users"
    tops10_file = input("Введите название выходного файла (по умолчанию 'top10_players.txt'): ") or "top10_players.txt"
    full_data_file = input("Введите название выходного файла (по умолчанию 'all_players_data.txt'): ") or "all_players_data.txt"

    all_players = read_all_yaml_files(input_directory)
    
    if all_players:
        analyze_player_data(all_players)
        top_10 = display_top_10_players(all_players, tops10_file)
        save_full_data(all_players, full_data_file)
    else:
        print("Не найдено данных об игроках")
    
    print(f"Полные данные сохранены в: {full_data_file}")
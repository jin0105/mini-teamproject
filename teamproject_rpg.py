import random
import uuid
import sys
import time
import json


# --- 1. 한국어 조사 자동 처리 클래스 ---
class KWord:
    def __init__(self, word):
        self.word = str(word)
        last_char = self.word[-1] if self.word else ""
        self.has_batchim = (
            (ord(last_char) - ord("가")) % 28 != 0
            if "가" <= last_char <= "힣"
            else False
        )

    @property
    def 은는(self):
        return f"{self.word}{'은' if self.has_batchim else '는'}"

    @property
    def 이가(self):
        return f"{self.word}{'이' if self.has_batchim else '가'}"

    @property
    def 을를(self):
        return f"{self.word}{'을' if self.has_batchim else '를'}"

    @property
    def 과와(self):
        return f"{self.word}{'과' if self.has_batchim else '와'}"

    @property
    def 의(self):
        return f"{self.word}의"

    def __str__(self):
        return self.word


############################ 몬스터 구현
MONSTER_JSON_DATA = """
[
  {"name": "슬라임 몬스터", "hp": 100, "attack": 0, "defence": 0},
  {"name": "나무를 두른 슬라임", "hp": 100, "attack": 0, "defence": 10},
  {"name": "오거", "hp": 150, "attack": 0, "defence": 0},
  {"name": "뿅망치를 든 오거", "hp": 150, "attack": 10, "defence": 0},
  {"name": "나무를 두른 오거", "hp": 150, "attack": 0, "defence": 10},
  {"name": "철갑을 두른 오거", "hp": 150, "attack": 0, "defence": 20}
]
"""


class Monster:
    def __init__(self, name, hp=100, attack=0, defence=0):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.defence = defence


class Monster_Manage:
    def __init__(self):
        self.M_list = []

    def add(self, Mon):
        if any(i for i in self.M_list if i.name == Mon.name):
            raise ValueError("이미 등록되어있는 이름의 몬스터 입니다")
        self.M_list.append(Mon)

    def load_from_json_string(self, json_string):
        data = json.loads(json_string)
        for m in data:
            monster_obj = Monster(m["name"], m["hp"], m["attack"], m["defence"])
            self.add(monster_obj)

    def list(self):
        return [i.name for i in self.M_list]


# --- 몬스터 매니저 초기화 및 데이터 로드 ---
mon = Monster_Manage()
mon.load_from_json_string(MONSTER_JSON_DATA)


# --- 4. 플레이어 관리 구현 ---
DATA_FILE = "players.json"


class ManagePlayer:
    def __init__(
        self,
        name,
        hp=100,
        potions=3,
        attack=0,
        defence=0,
        coin=0,
        kill_cnt=0,
        id_str=None,
    ):
        self.name = name
        self.hp = hp
        self.potions = potions
        self.attack = attack
        self.defence = defence
        self.coin = coin
        self.kill_cnt = kill_cnt
        self.id = id_str or str(uuid.uuid4())

    @staticmethod
    def load_data():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    @staticmethod
    def save_data(data):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "hp": self.hp,
            "potions": self.potions,
            "attack": self.attack,
            "defence": self.defence,
            "coin": self.coin,
            "kill_cnt": self.kill_cnt,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            hp=data["hp"],
            potions=data["potions"],
            attack=data["attack"],
            defence=data["defence"],
            id_str=data["id"],
            coin=data["coin"],
            kill_cnt=data["kill_cnt"],
        )

    def add_player(self):
        players = self.load_data()
        players.append(self.to_dict())
        self.save_data(players)
        start_game(self)

    def save_player(self):
        players = self.load_data()
        for idx, p in enumerate(players):
            if p["id"] == self.id:
                players[idx] = self.to_dict()
                break
        self.save_data(players)
        choice = input("""저장이 완료되었습니다. 게임으로 돌아가시겠습니까?
(예 / 아니오) """)
        if choice == "예":
            return
        else:
            sys.exit()

    def kill_player(self):
        players = [p for p in self.load_data() if p["id"] != self.id]
        self.save_data(players)

    @classmethod
    def list_player(cls):
        players = cls.load_data()
        if not players:
            print("등록된 캐릭터가 없습니다.")
            return []

        for idx, p in enumerate(players, 1):
            print(
                f"{idx}. {p['name']} (ID: {p['id']})\n"
                f"   체력: {p['hp']} | 포션: {p['potions']}개 | 공격력: {p['attack']} | 방어력: {p['defence']}"
            )
        return players

    @classmethod
    def del_player(cls):
        players = cls.list_player()
        if not players:
            return

        try:
            choice = int(input("삭제할 캐릭터 번호를 입력하세요: "))
            if 1 <= choice <= len(players):
                deleted = players.pop(choice - 1)
                cls.save_data(players)
                print(f"'{deleted['name']}' 캐릭터가 삭제되었습니다.")
            else:
                print("올바른 번호 범위가 아닙니다.")
        except ValueError:
            print("숫자만 입력해 주세요.")

    @classmethod
    def load_player(cls):
        players = cls.list_player()
        if not players:
            return

        try:
            choice = int(input("플레이할 캐릭터 번호를 입력하세요: "))
            if 1 <= choice <= len(players):
                selected = players[choice - 1]
                player_obj = cls.from_dict(selected)
                start_game(player_obj)
                return player_obj
            print("올바른 번호 범위가 아닙니다.")
        except ValueError:
            print("숫자만 입력해 주세요.")


def start_new():
    player_name = input("이름 입력: ").strip()
    if not player_name:
        player_name = "무명 용사"
    player = ManagePlayer(player_name)
    player.add_player()


def start_game(player):
    p_name = KWord(player.name)
    while True:
        print("=" * 40)
        print(f"🏰 [시스템] {p_name.이가} 게임에 접속했습니다.")
        print("=" * 40)
        print("""
    1. 동굴 탐험
    2. 상점
    3. 사우나
    4. 저장
    """)
        choice = input("실행할 번호를 선택하세요: ")

        if choice == "1":
            walk(player)
        elif choice == "2":
            store(player)
        elif choice == "3":
            sauna(player)
        elif choice == "4":
            player.save_player()


# --- 탐험 및 전투 시스템 ---


def heal(player, max_heal):
    before_hp = player.hp
    heal = random.randint(max_heal - 10, max_heal)
    player.hp += heal
    player.hp = min(100, player.hp)
    heal_amount = player.hp - before_hp
    return player.hp, heal_amount


def stop(player):
    action = input("뭘 할까? 1. 동굴 안으로 들어가기  2. 동굴 밖으로 나가기: ")
    if action == "1":
        walk(player)


def walk(player):
    print("동굴 속을 걷는 중.")
    time.sleep(1)
    print("동굴 속을 걷는 중..")
    time.sleep(1)
    print("동굴 속을 걷는 중...")
    time.sleep(1)

    a = random.randint(1, 100)
    if a > 80:
        walk(player)
    elif a > 60:
        nothing(player)
    elif a > 50:
        pond(player)
    elif a > 40:
        chest(player)
    else:
        join(player)


def nothing(player):
    print("=" * 40)
    time.sleep(1)
    print("아무 일도 없었다...")
    print("=" * 40)
    time.sleep(1)
    stop(player)


def chest(player, max_potion=10):
    playerName = KWord(player.name)
    print("=" * 40)
    time.sleep(1)
    print("보물 상자를 발견했다!")
    print("=" * 40)
    time.sleep(1)
    choice = input("상자를 여시겠습니까? \n(예/아니오)")
    if choice == "예":
        treasure(player)
    else:
        print(f"{playerName.은는} 상자를 열지 않기로 했다...")
        stop(player)

#-------------보물상자 이벤트-------------
def treasure(player):
    print("=" * 40)
    a = random.randint(1, 100)
    if a > 60:
        coin = random.randint(1, 10)
        print(f"상자 속에서 {coin}G가 나왔다!")
        player.coin += coin
        print(f"현재 코인: {player.coin}G")
        print("=" * 40)
        walk(player)
    elif a > 20:
        print("상자 속에서 포션이 나왔다!")
        if player.potions == 10:
            print("그러나 포션 가방이 가득 차서 더는 얻을 수 없었다...")
            print(f"현재 포션 수: {player.potions}개")
            print("=" * 40)
            stop(player)
        else:
            player.potions += 1
            print(f"현재 포션 수: {player.potions}개")
            print("=" * 40)
            stop(player)
    elif a > 10:
        print("상자 속에서 몬스터가 나왔다!")
        print("=" * 40)
        join(player)
    else:
        print("빈 상자였다...")
        print("=" * 40)
        stop(player)

#-------------연못 이벤트-------------
def pond(player):
    playerName = KWord(player.name)
    print("=" * 40)
    print("작은 연못을 발견했다!")
    print("=" * 40)
    time.sleep(1)
    player.hp, heal_amount = heal(player, 15)
    print(
        f"{playerName.은는} 연못에서 잠시 휴식했다. 체력이 {heal_amount}만큼 회복되었다."
    )
    print(f"현재 체력: {player.hp}")
    time.sleep(1)
    stop(player)


def join(player):
    target = random.choice(mon.M_list)
    # 전투용 독립 객체 생성
    c_mon = Monster(target.name, target.hp, target.attack, target.defence)

    p_word = KWord(player.name)
    m_word = KWord(c_mon.name)

    print("=" * 40)
    print(f"{m_word.word.과와} 마주쳤다!")
    print("=" * 40)
    time.sleep(1)

    while player.hp > 0 and c_mon.hp > 0:
        action = input("어떻게 할까? 1. 싸운다  2. 도망간다  3. HP를 회복한다: ")
        if action == "1":
            print("=" * 40)
            print(f"{p_word.은는} 전투를 시작했다.")
            time.sleep(1)
            print(
                f"{m_word.의} 체력: {c_mon.hp}"
                if hasattr(m_word, "의")
                else f"{m_word.word}의 체력: {c_mon.hp}"
            )
            print("=" * 40)
            time.sleep(0.5)
            base_damage = random.randint(5, 15) + int(player.attack)
            is_critical = random.random() < 0.1
            if is_critical:
                damage = base_damage * 2
                print(" Critical!!! 2배의 데미지를 입혔습니다!")
            else:
                damage = base_damage
            print(f"{p_word.word}의 차례 : {damage}만큼의 공격을 했다!")
            time.sleep(0.5)
            time.sleep(1)

            c_mon.hp -= damage
            print(
                f'{m_word.의 if hasattr(m_word, "의") else m_word.word + "의"} 남은 체력 : {max(0, c_mon.hp)}'
            )
            time.sleep(1)

        elif action == "2":
            success = random.choice([True, False])
            if success:
                print("=" * 40)
                print("도망에 성공했다!")
                time.sleep(1)
                print("=" * 40)
                stop(player)
                return
            else:
                print("=" * 40)
                print("도망치지 못했다...!")
                time.sleep(1)
                print(f"우왕좌왕 하는 사이 {m_word.이가} 공격한다!")
                print("=" * 40)
                time.sleep(1)

        elif action == "3":
            if player.potions > 0:
                print("=" * 40)
                print(f"가방에 {player.potions}개의 포션이 있다.")
                use = input("포션을 사용하시겠습니까? 1. 예 2. 아니오: ")
                if use == "1":
                    player.potions -= 1
                    player.hp, heal_amount = heal(player, 20)
                    print(f"{p_word.은는} {heal_amount}만큼의 체력을 회복했다!")
                    time.sleep(1)
                    print(
                        f'{p_word.의 if hasattr(p_word, "의") else p_word.word + "의"} 현재 체력 : {player.hp}'
                    )
                elif use == "2":
                    print("포션을 마시지 않기로 했다.")
            else:
                print("포션이 없습니다!")
        else:
            print(f"잘못된 입력입니다. 당황하는 사이 {m_word.이가} 공격합니다.")
            time.sleep(1)

        # 몬스터의 반격
        if c_mon.hp > 0:
            print("=" * 40)
            dm = random.randint(5, 15) + int(c_mon.attack)
            # 플레이어 방어력 반영
            actual_damage = max(1, dm - player.defence)
            player.hp -= actual_damage
            print(
                f'{m_word.의 if hasattr(m_word, "의") else m_word.word + "의"} 공격! : {actual_damage}만큼의 데미지를 받았다.'
            )
            time.sleep(1)
            print(
                f'현재 {p_word.의 if hasattr(p_word, "의") else p_word.word + "의"} 체력 : {max(0, player.hp)}'
            )
            print("=" * 40)
            time.sleep(1)

    print("=" * 40)
    if player.hp > 0:
        print("=" * 40)
        print(f"당신의 멋진 승리! {m_word.을를} 물리쳤습니다!")
        time.sleep(1)
        coin = random.randint(1, 10)
        print(f"전리품으로 금화 {coin}개를 얻었다!")
        player.coin += coin
        player.kill_cnt += 1
        print(f"현재 처치한 몬스터 수: {player.kill_cnt}/10")
        print("=" * 40)
        time.sleep(2)

        if player.kill_cnt >= 10:  # 엔딩 조건 (10마리 처치)
            print("\n" + "=" * 80)
            print("🎉 🎉 🎉 🎉 🎉 🎉 CONGRATULATION !! 🎉 🎉 🎉 🎉 🎉 🎉")
            print(" 축하합니다, 당신은 동굴 내부의 모든 몬스터를 무찔렀습니다 !!")
            time.sleep(1)
            print("         '동굴의 지배자' 훈장을 획득합니다.")
            time.sleep(1)
            print(" 마물들이 가득했던 동굴이 다시 평범한 동굴로 돌아갑니다.")
            print(" 당신은 또 다른 마물들을 찾아 여행을 떠납니다....The End...")
            print("=" * 80 + "\n")
            sys.exit()
        stop(player)
    else:
        print(f"체력이 바닥났습니다... {p_word.이가} 죽었습니다.")
        time.sleep(1)
        player.kill_player()
        print("=" * 40)
        time.sleep(1)
        main()


# --- 상점 ---
def store(player, max_potion=10):
    print("\n" + "=" * 40)
    print("상점입니다.")
    print("=" * 40)
    time.sleep(1)

    item_list = {
        "1": ["포션", 5, "potion", 1],
        "2": ["검", 20, "attack", 10],
        "3": ["방패", 15, "defence", 5],
        "4": ["갑옷", 30, "defence", 15],
        "5": ["신발", 10, "defence", 3],
    }

    while True:
        print(
            f"\n[현재 골드: {player.coin}G | 포션: {player.potions}개 | 공격력: {player.attack} | 방어력: {player.defence}]"
        )
        print("-" * 40)

        for key, (name, price, stat_type, stat_val) in item_list.items():
            print(f"{key}. {name} 구매 {price}G")
        print("6. 상점 나가기")

        choice = input("선택: ")

        if choice == "6":
            print("상점을 나갑니다.")
            break

        elif choice in item_list:
            for key, (name, price, stat_type, stat_val) in item_list.items():
                if choice == key:
                    item_word = KWord(name)
                    if choice == "1" and player.potions >= max_potion:
                        print("포션을 더 이상 소지할 수 없습니다.")
                    elif player.coin < price:
                        print("골드가 부족합니다.")
                    else:
                        player.coin -= price
                        if choice == "1":
                            player.potions += 1
                            print(
                                f"{item_word.을를} 구매했습니다. (현재 포션: {player.potions}개)"
                            )
                        else:
                            if stat_type == "attack":
                                player.attack += stat_val
                                print(
                                    f"{item_word.을를} 구매 및 장착하여 공격력이 {stat_val} 증가했습니다. (현재 공격력: {player.attack})"
                                )
                            elif stat_type == "defence":
                                player.defence += stat_val
                                print(
                                    f"{item_word.을를} 구매 및 장착하여 방어력이 {stat_val} 증가했습니다. (현재 방어력: {player.defence})"
                                )
        else:
            print("잘못된 입력입니다.")


# --- 사우나 ---
def sauna(player, max_hp=100):
    price = 50
    sauna_heal = 30

    print("\n" + "=" * 40)
    print("사우나입니다.")
    print("=" * 40)
    time.sleep(1)

    while True:
        print(
            f"\n[현재 체력: {player.hp}/{max_hp} | 보유 골드: {player.coin}G]"
        )
        print(f"1. 입장하기 ({price}G - 체력 최대 {sauna_heal} 회복)")
        print("2. 사우나 나가기")
        choice = input("선택: ")

        if choice == "1":
            if player.hp >= max_hp:
                print("이미 체력이 가득 차 있습니다.")
            elif player.coin >= price:
                player.coin -= price
                player.hp, heal_amount = heal(player, sauna_heal)
                print(
                    f"{heal_amount}만큼 체력이 회복되어 현재 체력은 {player.hp}입니다."
                )
            else:
                print("골드가 부족합니다.")

        elif choice == "2":
            print("사우나를 나갑니다.")
            break
        else:
            print("잘못된 입력입니다.")


# --- 메인 루프 ---
def main():
    while True:
        print("=" * 40)
        print("미니 RPG 게임")
        print("=" * 40)
        print("""1. 새로운 시작
2. 플레이어 삭제
3. 플레이어 로드
4. 게임 종료""")
        print("=" * 40)
        choice = input("실행할 번호를 입력하세요: ")
        if choice == "1":
            start_new()
        elif choice == "2":
            ManagePlayer.del_player()
        elif choice == "3":
            ManagePlayer.load_player()
        elif choice == "4":
            print("게임을 종료합니다.")
            sys.exit()
        else:
            pass


if __name__ == "__main__":
    main()

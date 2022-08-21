from flask import Flask, render_template, request
from random import choice, randint

app = Flask(__name__)

difficulty = {"Easy": 1.2, "Very Easy": 1, "Extremely Easy": 0.8}
current_difficulty = "Easy"

enemies_defeated = 0
boss = False
boss_dead = False

weapons = ("Iron Sword", "Iron Axe", "Steel Sword", "Steel Axe", "Hammer", "Katana", "Dagger", "Pure Nail", "Gun")
weapons_stats = {
    "None": 0,
    "Iron Sword": 5,
    "Iron Axe": 7,
    "Steel Sword": 8,
    "Steel Axe": 10,
    "Hammer": 12,
    "Katana": 11,
    "Dagger": 4,
    "Pure Nail": 9,
    "Gun": 999
}

armor = ("Leather Armor", "Iron Armor", "Steel Armor", "Golden Pot")
armor_stats = {
    "None": 0,
    "Leather Armor": 2,
    "Iron Armor": 4,
    "Steel Armor": 6,
    "Golden Pot": 0
    }

equipment = {
        "weapon1": "Iron Sword",
        "weapon2": "None",
        "armor": "None",
        "cheese": 3
    }

stats = {
        "health": 50,
        "resistance": armor_stats[equipment["armor"]],
        "attack1": weapons_stats[equipment["weapon1"]],
        "attack2": weapons_stats[equipment["weapon2"]]
    }

enemies = ("Goblin", "Bandit", "Golem", "Stone", "Werewolf")
enemies_stats = {
    "Goblin":{
        "hp": 20,
        "attk": 4,
        "description": "Little mischievous annoying creature."
    },
    "Bandit":{
        "hp": 30,
        "attk": 10,
        "description": "They could have become a hero but had chosen path of evil."
    },
    "Golem":{
        "hp": 50,
        "attk": 8,
        "description": "Big boulder. Brother of stone. Hopefully you didn't hurt his little brother."
    },
    "Stone":{
        "hp": 5,
        "attk": 0,
        "description": "It's a stone. Just a stone. You have decided to attack stone. How heroic..." 
    },
    "Werewolf":{
        "hp": 25,
        "attk": 6,
        "description": "Maybe if he wouldn't be angry. He would be cute puppy."
    }
}

boss = {
    "hp": 150,
    "attk": 15,
    "description": "to be"
}


class Actions():
    def __init__(self):
        self.equipment = equipment
        self.stats = stats

    def create_enemy(self):
        if boss == True:
            self.current_enemy = "Boss"
            self.enemy = {
                "Hp": 150,
                "Attk": 15,
                "Description": "to be"
            }
        else:
            self.current_enemy = choice(enemies)
            self.enemy = {
                "Hp": int(enemies_stats[self.current_enemy]["hp"] * difficulty[current_difficulty]),
                "Attk": int(enemies_stats[self.current_enemy]["attk"] * difficulty[current_difficulty]),
                "Description": enemies_stats[self.current_enemy]["description"]
            }

    def attack1(self):
        self.enemy["Hp"] = self.enemy["Hp"] - self.stats["attack1"]

        if (self.enemy["Attk"] - self.stats["resistance"]) > 1:
            self.stats["health"] = self.stats["health"] - (self.enemy["Attk"] -self.stats["resistance"])
        else:
            self.stats["health"] = self.stats["health"]

        if equipment["weapon1"] == "Gun":
            equipment["weapon1"] = "None"
            self.stats["attack1"] = weapons_stats[self.equipment["weapon1"]]


    def attack2(self):
        self.enemy["Hp"] = self.enemy["Hp"] - self.stats["attack2"]

        if (self.enemy["Attk"] - self.stats["resistance"]) > 1:
            self.stats["health"] = self.stats["health"] - (self.enemy["Attk"] -self.stats["resistance"])
        else:
            self.stats["health"] = self.stats["health"]

        if equipment["weapon2"] == "Gun":
            equipment["weapon2"] = "None"
            self.stats["attack2"] = weapons_stats[self.equipment["weapon2"]]

    def heal(self):
        global warning_message
        if self.equipment["cheese"] != 0 and self.stats["health"] != 50:
            self.stats["health"] = self.stats["health"] + 20
            self.equipment["cheese"] = self.equipment["cheese"] - 1

            if self.stats["health"] > 50:
                self.stats["health"] = 50
                
        else:
            warning_message = "You cannot heal"
    
    def text_(self):
        self.name = self.current_enemy
        self.description = "Health: {}       Attack: {}<br><br>{}".format(self.enemy["Hp"], self.enemy["Attk"], self.enemy["Description"])
        return self.name, self.description
    
    def is_dead(self):
        if self.enemy["Hp"] <= 0:
            return True
        else:
            return False

    def loot(self):
        self.cheese = randint(0,3)
        self.equipment["cheese"] = self.equipment["cheese"] + self.cheese
        self.weapon = choice(weapons)
        self.armor = choice(armor)

    def equip1(self):
        self.equipment["weapon1"] = self.weapon
        self.stats["attack1"] = weapons_stats[self.equipment["weapon1"]]

    def equip2(self):
        self.equipment["weapon2"] = self.weapon
        self.stats["attack2"] = weapons_stats[self.equipment["weapon2"]]

    def equip_armor(self):
        self.equipment["armor"] = self.armor
        self.stats["resistance"] = armor_stats[self.equipment["armor"]]

    def loot_weapon_text(self):
        self.text = "You have defeated {}. <br> You found {} cheese and {} ({} dmg).".format(self.current_enemy, self.cheese, self.weapon, weapons_stats[self.weapon]) 
        return self.text

    def loot_armor_text(self):
        self.text = "You have defeated {}. <br> You found {} cheese and {} ({}).".format(self.current_enemy, self.cheese, self.armor, armor_stats[self.armor]) 
        return self.text

actions = Actions()



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/prologue")
def prologue():
    global boss, boss_dead, enemies_defeated, stats, equipment
    boss = False
    boss_dead = False
    enemies_defeated = 0

    equipment = {
            "weapon1": "Iron Sword",
            "weapon2": "None",
            "armor": "None",
            "cheese": 3
    }

    stats = {
            "health": 50,
            "resistance": armor_stats[equipment["armor"]],
            "attack1": weapons_stats[equipment["weapon1"]],
            "attack2": weapons_stats[equipment["weapon2"]]
    }
    actions.__init__()
    return render_template("prologue.html")

@app.route("/settings", methods=["GET", "POST"])
def settings():
    global current_difficulty

    if request.method == "POST":
        if request.form.get("Easy") == "Easy":
            current_difficulty = "Easy"
        elif request.form.get("Very Easy") == "Very Easy":
            current_difficulty = "Very Easy"
        elif request.form.get("Extremely Easy") == "Extremely Easy":
            current_difficulty = "Extremely Easy"

    elif request.method == "GET":
        return render_template("settings.html", difficulty="Difficulty: {}".format(current_difficulty))
    
    return render_template("settings.html", difficulty="Difficulty: {}".format(current_difficulty))


@app.route("/game", methods=["GET", "POST"])
def game():
    global warning_message, equipment, stats, enemies_defeated, boss, enemies, enemies_stats, boss_dead, current_difficulty
    warning_message = ""

    if request.method == "POST":
        if request.form.get("Attack1") == "Attack1":
            actions.attack1()           

        elif request.form.get("Attack2") == "Attack2":
            actions.attack2()

        elif request.form.get("Placeholder2") == "Placeholder2":
           pass

        elif request.form.get("Heal") == "Heal":
            actions.heal()
        

        #checking for players low health
        if stats["health"] <= 15:
            warning_message = "Your health is low"


        #checking if player is dead
        if stats["health"] <= 0:
            #creating new enemy
            if "Lost Soul" in enemies:
                #updating dmg
                enemies_stats["Lost Soul"].update({"attk": int((stats["attack1"]+stats["attack2"])/2)})
            else:
                enemies = enemies + ("Lost Soul",)
                enemies_stats["Lost Soul"] = {"hp":25, "attk":int((stats["attack1"]+stats["attack2"])/2), "description": "Rumor says, it is a soul of a previous hero who decided to take this path but failed."}

            end_message = "You died"
            return render_template("game_over.html", end_message=end_message)
        

        #checking if enemy is dead
        if actions.is_dead() == True:
            enemies_defeated = enemies_defeated + 1

            if boss == True:
                boss_dead =True

            if enemies_defeated == (20 * difficulty[current_difficulty]):
                boss = True
                if current_difficulty == "Extremely Easy":
                    return render_template("false-ending.html")
                else:
                    return render_template ("pre-boss.html")

            if boss_dead == True:
                return render_template ("post-boss.html")

            else:
                actions.loot()
                if choice(("weapon","armor")) == "weapon":
                    text = actions.loot_weapon_text()
                    return render_template("loot-weapon.html", text=text, health=stats["health"],
                                        resistance=stats["resistance"], attack1=stats["attack1"],
                                        attack2=stats["attack2"], difficulty=current_difficulty, weapon1=equipment["weapon1"],
                                        weapon2=equipment["weapon2"], armor=equipment["armor"], cheese=equipment["cheese"])
                else:
                    text = actions.loot_armor_text()
                    return render_template("loot-armor.html", text=text, health=stats["health"],
                                        resistance=stats["resistance"], attack1=stats["attack1"],
                                        attack2=stats["attack2"], difficulty=current_difficulty, weapon1=equipment["weapon1"],
                                        weapon2=equipment["weapon2"], armor=equipment["armor"], cheese=equipment["cheese"])


    elif request.method == "GET":
        actions.create_enemy()
        name, description = actions.text_()
        return render_template("game.html", name=name, description=description, warning_message=warning_message,
                        health=stats["health"], resistance=stats["resistance"], attack1=stats["attack1"],
                        attack2=stats["attack2"], difficulty=current_difficulty, weapon1=equipment["weapon1"],
                        weapon2=equipment["weapon2"], armor=equipment["armor"], cheese=equipment["cheese"])

    name, description = actions.text_()
    return render_template("game.html", name=name, description=description, warning_message=warning_message,
                        health=stats["health"], resistance=stats["resistance"], attack1=stats["attack1"],
                        attack2=stats["attack2"], difficulty=current_difficulty, weapon1=equipment["weapon1"],
                        weapon2=equipment["weapon2"], armor=equipment["armor"], cheese=equipment["cheese"])


@app.route("/loot-weapon", methods=["GET", "POST"])
def loot_weapon():
    if request.method == "POST":
        if request.form.get("Equip as Weapon1") == "Equip as Weapon1":
            actions.equip1()

        elif request.form.get("Equip as Weapon2") == "Equip as Weapon2":
            actions.equip2()    

        elif request.form.get("Continue") == "Continue":
            pass


        actions.create_enemy()
        name, description = actions.text_()
        return render_template("game.html", name=name, description=description, warning_message=warning_message,
                            health=stats["health"], resistance=stats["resistance"], attack1=stats["attack1"],
                            attack2=stats["attack2"], difficulty=current_difficulty, weapon1=equipment["weapon1"],
                            weapon2=equipment["weapon2"], armor=equipment["armor"], cheese=equipment["cheese"])

    elif request.method == "GET":
        return render_template("index.html")

@app.route("/loot-armor", methods=["GET", "POST"])
def loot_armor():
    if request.method == "POST":
        if request.form.get("Equip armor") == "Equip armor":
            actions.equip_armor()

        elif request.form.get("Continue") == "Continue":
            pass


        actions.create_enemy()
        name, description = actions.text_()
        return render_template("game.html", name=name, description=description, warning_message=warning_message,
                            health=stats["health"], resistance=stats["resistance"], attack1=stats["attack1"],
                            attack2=stats["attack2"], difficulty=current_difficulty, weapon1=equipment["weapon1"],
                            weapon2=equipment["weapon2"], armor=equipment["armor"], cheese=equipment["cheese"])
        
    elif request.method == "GET":
        return render_template("index.html")

@app.route("/game-over")
def game_over():
    global boss_dead
    if boss_dead == False:
        end_message = "Ending: Coward" 
    else:
        if equipment["armor"] == "Golden Pot":
            end_message = "Ending: Madlad"
        else:
            end_message = "Ending: Merciful"    

    return render_template("game_over.html", end_message=end_message)

@app.route("/epilogue")
def epilogue():
    return render_template("epilogue.html")


if __name__ == "__main__":
    app.run(debug=True)
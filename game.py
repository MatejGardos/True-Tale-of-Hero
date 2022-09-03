from flask import Flask, render_template, request
from random import choice, randint
import json

app = Flask(__name__)

difficulty = {"Easy": 1.2, "Very Easy": 1, "Extremely Easy": 0.8}
current_difficulty = "Easy"

enemies_defeated = 0
boss = False
boss_dead = False

boss = {
    "hp": 150,
    "attk": 15,
    "description": "to be"
}


class Actions():
    def __init__(self):
        with open("stats_and_stuff.json", "r") as json_file:
            content = json.load(json_file)
            self.equipment = content["equipment"]
            self.stats = content["stats"]
            self.melee_weapons = content["melee_weapons"]
            self.ranged_weapons = content["ranged_weapons"]
            self.armor = content["armor"]
            self.enemies = content["enemies"]

            stats = {
                "resistance": int(self.armor[self.equipment["armor"]]),
                "melee_attack": int(self.melee_weapons[self.equipment["melee_weapon"]]),
                "ranged_attack": int(self.ranged_weapons[self.equipment["ranged_weapon"]])
            }
            self.stats.update(stats)

            self.warning_message = ""

    def create_enemy(self):
        if boss == True:
            self.current_enemy = "Boss"
            self.enemy = {
                "Hp": 150,
                "Attk": 15,
                "Description": "to be"
            }
        else:
            self.current_enemy = choice(tuple(self.enemies.keys()))
            self.enemy = {
                "Hp": int(self.enemies[self.current_enemy]["hp"] * difficulty[current_difficulty]),
                "Attk": int(self.enemies[self.current_enemy]["attk"] * difficulty[current_difficulty]),
                "Description": self.enemies[self.current_enemy]["description"]
            }

    def melee_attack(self):
        self.enemy["Hp"] = self.enemy["Hp"] - self.stats["melee_attack"]

        if (self.enemy["Attk"] - self.stats["resistance"]) > 1:
            self.stats["health"] = self.stats["health"] - (self.enemy["Attk"] -self.stats["resistance"])
        else:
            self.stats["health"] = self.stats["health"]

        self.warning_message = ""


    def ranged_attack(self):
        if self.equipment["arrows"] > 0:
            self.enemy["Hp"] = self.enemy["Hp"] - self.stats["ranged_attack"]
            self.equipment["arrows"] = self.equipment["arrows"] - 1

            self.warning_message = ""

        else:
            self.warning_message = "Not enough arrows"

    def heal(self):
        if self.equipment["cheese"] != 0 and self.stats["health"] != 50:
            self.stats["health"] = self.stats["health"] + 20
            self.equipment["cheese"] = self.equipment["cheese"] - 1
            self.warning_message = ""

            if self.stats["health"] > 50:
                self.stats["health"] = 50
                
        else:
            self.warning_message = "You cannot heal"
    
    def text_(self):
        self.name = self.current_enemy
        self.description = "Health: {}       Attack: {}<br><br>{}".format(self.enemy["Hp"], self.enemy["Attk"], self.enemy["Description"])
        return self.name, self.description, self.warning_message, self.stats["health"], self.equipment["cheese"], self.equipment["arrows"]
    
    def is_dead(self):
        if self.enemy["Hp"] <= 0:
            return True
        else:
            return False

    def loot(self):
        self.loot_items = ""
        self.item_out = choice(("cheese","arrows","gold"))

        if self.item_out != "cheese":
            self.cheese = randint(0,3)
            self.equipment["cheese"] = self.equipment["cheese"] + self.cheese
            self.loot_items = str(self.cheese) + " cheese"

        if self.item_out != "arrows":
            self.arrows = randint(0,4)
            self.equipment["arrows"] = self.equipment["arrows"] + self.arrows
            if self.loot_items != "":
                self.loot_items = self.loot_items + ", "
            self.loot_items = self.loot_items + str(self.arrows) + " arrows"

        if self.item_out != "gold":
            self.gold = randint(0,5)
            self.equipment["gold"] = self.equipment["gold"] + self.gold
            if self.loot_items != "":
                self.loot_items = self.loot_items + ", "
            self.loot_items = self.loot_items + str(self.gold) + " gold"

        self.item = choice(("melee","ranged","armor"))
        if self.item == "melee":
            self.loot_item = choice(tuple(self.melee_weapons.keys()))
        elif self.item == "ranged":
            self.loot_item = choice(tuple(self.ranged_weapons.keys()))
        elif self.item == "armor":
            self.loot_item = choice(tuple(self.armor.keys()))

    def equip_melee_weapon(self):
        self.equipment["melee_weapon"] = self.loot_item
        self.stats["melee_attack"] = self.melee_weapons[self.equipment["melee_weapon"]]

    def equip_ranged_weapon(self):
        self.equipment["ranged_weapon"] = self.loot_item
        self.stats["ranged_attack"] = self.ranged_weapons[self.equipment["ranged_weapon"]]

    def equip_armor(self):
        self.equipment["armor"] = self.loot_item
        self.stats["resistance"] = self.armor[self.equipment["armor"]]

    def loot_text(self):
        if self.item == "melee":
            self.item_stats = self.melee_weapons[self.loot_item]
            self.cur_item = self.equipment["melee_weapon"]
            self.cur_item_stats = self.stats["melee_attack"]
        elif self.item == "ranged":
            self.item_stats = self.ranged_weapons[self.loot_item]
            self.cur_item = self.equipment["ranged_weapon"]
            self.cur_item_stats = self.stats["ranged_attack"]
        elif self.item == "armor":
            self.item_stats = self.armor[self.loot_item]
            self.cur_item = self.equipment["armor"]
            self.cur_item_stats = self.stats["resistance"]
            
        self.text = "You have defeated {}. <br> You found {} <br> and {} ({}). Now you have equiped {} ({}).".format(self.current_enemy, self.loot_items, self.loot_item, self.item_stats, self.cur_item, self.cur_item_stats) 
        return self.text, self.item

    def player_health(self):
        if self.stats["health"] <= 15:
            self.warning_message = "Your health is low"

    def player_dead(self):
        if self.stats["health"] <= 0:
            return True
        return False

    def inventory(self):
        return self.stats["health"], self.equipment["melee_weapon"], self.stats["melee_attack"], self.equipment["ranged_weapon"], self.stats["ranged_attack"], self.equipment["arrows"], self.equipment["armor"], self.stats["resistance"], self.equipment["cheese"], self.equipment["gold"]

actions = Actions()



@app.route("/")
def menu():
    return render_template("menu.html")

@app.route("/prologue")
def prologue():
    global boss, boss_dead, enemies_defeated
    boss = False
    boss_dead = False
    enemies_defeated = 0
    actions.__init__()
    actions.create_enemy()
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
    global enemies_defeated, boss, boss_dead, current_difficulty

    if request.method == "POST":
        if request.form.get("Strike") == "Strike":
            actions.melee_attack()           

        elif request.form.get("Shoot") == "Shoot":
            actions.ranged_attack()

        elif request.form.get("Heal") == "Heal":
           actions.heal()

        elif request.form.get("Inventory") == "Inventory":
            health, melee_weapon, melee_attack, ranged_weapon, ranged_attack, arrows, armor, resistance, cheese, gold = actions.inventory()
            return render_template("inventory.html", health=health, melee_weapon=melee_weapon, melee_attack=melee_attack,
                                    ranged_weapon=ranged_weapon, ranged_attack=ranged_attack, arrows=arrows, armor=armor,
                                    resistance=resistance, cheese=cheese, gold=gold, difficulty=current_difficulty)
        

        actions.player_health()

        if actions.player_dead() == True:
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
                text,item = actions.loot_text()
                return render_template("loot.html", text=text)

    elif request.method == "GET":
        name, description, warning_message, health, cheese, arrows = actions.text_()
        return render_template("game.html", name=name, description=description, warning_message=warning_message, health=health, cheese=cheese, arrows=arrows)

    name, description, warning_message, health, cheese, arrows = actions.text_()
    return render_template("game.html", name=name, description=description, warning_message=warning_message, health=health, cheese=cheese, arrows=arrows)


@app.route("/loot", methods=["GET", "POST"])
def loot():
    text,item = actions.loot_text()
    if request.method == "POST":
        if request.form.get("Equip") == "Equip":
            if item == "melee":
                actions.equip_melee_weapon()
            elif item == "ranged":
                actions.equip_ranged_weapon()
            elif item == "armor":
                actions.equip_armor

        elif request.form.get("Continue") == "Continue":
            pass

        actions.create_enemy()
        name, description, warning_message, health, cheese, arrows = actions.text_()
        return render_template("game.html", name=name, description=description, warning_message=warning_message, health=health, cheese=cheese, arrows=arrows)

    elif request.method == "GET":
        return render_template("menu.html")


@app.route("/game-over")
def game_over():
    global boss_dead
    if boss_dead == False:
        end_message = "Ending: Coward" 
    else:
        end_message = "Ending: Merciful"    

    return render_template("game_over.html", end_message=end_message)

@app.route("/epilogue")
def epilogue():
    return render_template("epilogue.html")

@app.route("/how-to-play")
def how_to_play():
    return render_template("how-to-play.html")

@app.route("/feedback")
def feedback():
    return render_template("feedback.html")

if __name__ == "__main__":
    app.run(debug=True)
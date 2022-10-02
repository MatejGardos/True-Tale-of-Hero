from email import message
from flask import Flask, render_template, request
from random import choice, randint
import json

app = Flask(__name__)

difficulty = {"Easy": 1.2, "Very Easy": 1, "Extremely Easy": 0.8}
current_difficulty = "Easy"

enemies_defeated = 0
boss = False
boss_dead = False


class Actions():
    def __init__(self):
        with open("stats-and-stuff\stats_and_stuff.json", "r") as json_file:
            content = json.load(json_file)
            self.equipment = content["equipment"]
            self.stats = content["stats"]
            self.melee_weapons_types = tuple(content["melee_weapons_types"])
            self.melee_weapons = content["melee_weapons"]
            self.ranged_weapons_types = tuple(content["ranged_weapons_types"])
            self.ranged_weapons = content["ranged_weapons"]
            self.armor_types = tuple(content["armor_types"])
            self.armor = content["armor"]
            self.enemies = content["enemies"]
            self.events = content["events"]

        stats = {
            "resistance": int(self.armor[self.equipment["armor"]]),
            "melee_attack": int(self.melee_weapons[self.equipment["melee_weapon"]]),
            "ranged_attack": int(self.ranged_weapons[self.equipment["ranged_weapon"]])
        }
        self.stats.update(stats)

        self.warning_message = ""
        self.durability = "Sharp"

    def create_enemy(self):
        if boss == True:
            self.current_enemy = "Boss"
            self.enemy = {
                "Hp": int(1000 * difficulty[current_difficulty]),
                "Attk": int(20 * difficulty[current_difficulty]),
                "Description": "Man, who has been treatening all villages around - at least that is what legend says."
            }
            
        # creating ordinary enemy
        else:
            self.current_enemy = choice(tuple(self.enemies.keys()))
            self.enemy = {
                "Hp": int(self.enemies[self.current_enemy]["hp"] * difficulty[current_difficulty]),
                "Attk": int(self.enemies[self.current_enemy]["attk"] * difficulty[current_difficulty]),
                "Description": self.enemies[self.current_enemy]["description"]
            }

    def melee_attack(self):
        if self.stats["melee_durability"] >= 30:
            self.enemy["Hp"] = self.enemy["Hp"] - self.stats["melee_attack"]
        else:
            self.enemy["Hp"] = self.enemy["Hp"] - int(self.stats["melee_attack"]/2)
            self.durability = "Dull"

        self.stats["health"] = self.stats["health"] - int(self.enemy["Attk"] - (self.enemy["Attk"]*(self.stats["resistance"]/100)))
        self.stats["melee_durability"] = self.stats["melee_durability"] - randint(0,2)

        self.warning_message = ""


    def ranged_attack(self):
        if self.equipment["arrows"] > 0:
            self.enemy["Hp"] = self.enemy["Hp"] - self.stats["ranged_attack"]
            self.equipment["arrows"] = self.equipment["arrows"] - 1

            self.warning_message = ""

        else:
            self.warning_message = "Not enough arrows"


    def heal(self):
        if self.equipment["cheese"] != 0 and self.stats["health"] != self.stats["max_health"]:
            self.stats["health"] = self.stats["health"] + 20
            self.equipment["cheese"] = self.equipment["cheese"] - 1
            self.warning_message = ""

            if self.stats["health"] > self.stats["max_health"]:
                self.stats["health"] = self.stats["max_health"]
                
        else:
            self.warning_message = "You cannot heal"

    def sleep(self):
        if self.stats["health"] != self.stats["max_health"]:
            self.stats["health"] = self.stats["health"] + 10

            if self.stats["health"] > self.stats["max_health"]:
                self.stats["health"] = self.stats["max_health"]

        self.warning_message = ""
    
    def text_(self):
        self.name = self.current_enemy
        self.description = "Health: {}       Attack: {}<br><br>{}".format(self.enemy["Hp"], self.enemy["Attk"], self.enemy["Description"])

        if boss == False:
            self.image = self.enemies[self.current_enemy]["image"]
        else:
            self.image = "https://i.pinimg.com/736x/36/b7/ef/36b7ef7f01965aeb6b4639ef4aa5fdda.jpg"
        
        return self.name, self.description, self.image, self.warning_message, self.stats["health"], self.equipment["cheese"], self.equipment["arrows"], self.equipment["gold"]

    def text_stats(self):
        return self.stats["health"], self.equipment["cheese"], self.equipment["arrows"], self.equipment["gold"]
    
    # checking if enemy is dead
    def is_dead(self):
        if self.enemy["Hp"] <= 0:
            return True
        else:
            return False

    def player_health(self):
        if self.stats["health"] <= 15:
            self.warning_message = "Your health is low"

    def player_dead(self):
        if self.stats["health"] <= 0:
            return True
        return False

    def inventory(self):
        return self.stats["health"], self.equipment["melee_weapon"], self.durability, self.stats["melee_attack"], self.equipment["ranged_weapon"], self.stats["ranged_attack"], self.equipment["arrows"], self.equipment["armor"], self.stats["resistance"], self.equipment["cheese"], self.equipment["gold"]


    #Loot stuff
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
            self.loot_item = choice(self.melee_weapons_types)
        elif self.item == "ranged":
            self.loot_item = choice(self.ranged_weapons_types)
        elif self.item == "armor":
            self.loot_item = choice(self.armor_types)

    def equip_melee_weapon(self):
        self.equipment["melee_weapon"] = self.loot_item
        self.stats["melee_attack"] = self.melee_weapons[self.equipment["melee_weapon"]]
        self.stats["melee_durability"] = 100

    def equip_ranged_weapon(self):
        self.equipment["ranged_weapon"] = self.loot_item
        self.stats["ranged_attack"] = self.ranged_weapons[self.equipment["ranged_weapon"]]

    def equip_armor(self):
        self.equipment["armor"] = self.loot_item
        self.stats["resistance"] = self.armor[self.equipment["armor"]]

    def loot_text(self):
        if self.item == "melee":
            self.item_stats = str(self.melee_weapons[self.loot_item]) + " damage"
            self.cur_item = self.equipment["melee_weapon"]
            self.cur_item_stats = str(self.stats["melee_attack"]) + " damage"
        elif self.item == "ranged":
            self.item_stats = str(self.ranged_weapons[self.loot_item]) + " damage"
            self.cur_item = self.equipment["ranged_weapon"]
            self.cur_item_stats = str(self.stats["ranged_attack"]) + " damage"
        elif self.item == "armor":
            self.item_stats = str(self.armor[self.loot_item]) + "%" + " resistance"
            self.cur_item = self.equipment["armor"]
            self.cur_item_stats = str(self.stats["resistance"]) + "%" + " resistance"
            
        self.text = "You have defeated {}. <br> You found {} <br> and {} ({}). Now you have equiped {} ({}).".format(self.current_enemy, self.loot_items, self.loot_item, self.item_stats, self.cur_item, self.cur_item_stats) 
        return self.text, self.item


    #Event stuff
    def event(self):
        self.event_type = choice(tuple(self.events.keys()))

    def text_event(self):
        self.text_event_ = self.events[self.event_type]["text"]
        self.image = self.events[self.event_type]["image"]
        return self.event_type, self.text_event_, self.image

    def yes(self, event):
        self.yes_ = self.events[event]["yes"]
        self.image = self.events[self.event_type]["image_y"]
        return self.yes_, self.image

    def yes_fail(self, event):
        self.yes_fail_ = self.events[event]["yes-fail"]
        self.image = self.events[self.event_type]["image_yf"]
        return self.yes_fail_, self.image

    def no(self, event):
        self.no_ = self.events[event]["no"]
        self.image = self.events[self.event_type]["image_n"]
        return self.no_, self.image

    def beggar(self):
        if self.equipment["gold"] >= 20:
            self.equipment["gold"] = self.equipment["gold"] - 20
            self.stats["max_health"] = self.stats["max_health"] + 5
            return True
        else:
            return False

    def bandit_camp(self):
        if randint(0,100) > 75:
            self.stats["max_health"] = self.stats["max_health"] - 5
            if self.stats["health"] >= self.stats["max_health"]:
                self.stats["health"] = self.stats["max_health"]
            return False
        else:
            self.equipment["gold"] = self.equipment["gold"] + randint(4,10)
            return True

    #Village stuff
    def steal(self):
        if randint(0,100) > 30:
            self.sentence = randint(4,10)
            return False
        else:
            self.equipment["cheese"] = self.equipment["cheese"] + 1
            return True
    
    def jail_text(self):
        return self.sentence

    def serve_time(self):
        self.sentence = self.sentence - 1
        if self.sentence <= 0:
            return True

    def bribe(self):
        if self.equipment["gold"] >= 20:
            self.equipment["gold"] = self.equipment["gold"] - 20
            return True

    def upgrade_melee(self):
        if self.equipment["gold"] >= 25:
            self.equipment["gold"] = self.equipment["gold"] - 25
            self.stats["melee_attack"] = int(self.stats["melee_attack"] * 1.4)
            return True

    def sharpen_melee(self):
        if self.equipment["gold"] >= 5:
            self.equipment["gold"] = self.equipment["gold"] - 5
            self.stats["melee_durability"] = 100
            self.durability = "Sharp"
            return True

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
            health, melee_weapon, durability, melee_attack, ranged_weapon, ranged_attack, arrows, armor, resistance, cheese, gold = actions.inventory()
            return render_template("inventory.html", health=health, melee_weapon=melee_weapon, durability=durability, melee_attack=melee_attack,
                                    ranged_weapon=ranged_weapon, ranged_attack=ranged_attack, arrows=arrows, armor=armor,
                                    resistance=resistance, cheese=cheese, gold=gold, difficulty=current_difficulty)
        

        actions.player_health()

        if actions.player_dead() == True:
            return render_template("game_over.html")
        
        #checking if enemy is dead
        if actions.is_dead() == True:
            enemies_defeated = enemies_defeated + 1

            if boss == True:
                boss_dead = True

            if boss_dead == True:
                return render_template("post-boss.html")

            else:
                if randint(0,100) > 50:
                    actions.loot()
                    text, item = actions.loot_text()
                    return render_template("loot.html", text=text)
                else:
                    health, cheese, arrows, gold = actions.text_stats()
                    return render_template("camp.html", health=health, cheese=cheese, arrows=arrows, gold=gold)

    elif request.method == "GET":
        name, description, image, warning_message, health, cheese, arrows, gold = actions.text_()
        return render_template("game.html", name=name, description=description, image=image, warning_message=warning_message, health=health, cheese=cheese, arrows=arrows, gold=gold)

    name, description, image, warning_message, health, cheese, arrows, gold = actions.text_()
    return render_template("game.html", name=name, description=description, image=image, warning_message=warning_message, health=health, cheese=cheese, arrows=arrows, gold=gold)


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
                actions.equip_armor()

        elif request.form.get("Continue") == "Continue":
            pass
        
        health, cheese, arrows, gold = actions.text_stats()
        return render_template("camp.html", health=health, cheese=cheese, arrows=arrows, gold=gold)
        
    elif request.method == "GET":
        return render_template("menu.html")


@app.route("/event", methods=["GET", "POST"])
def event():
    if request.method == "POST":
        event, text, image = actions.text_event()

        if request.form.get("Yes") == "Yes":
            #event Beggar
            if event == "Beggar":
                if actions.beggar():
                    post_event_text, image = actions.yes(event)
                else:
                    event_warning_message = "Not enough gold"
                    return render_template("event.html", title=event, text=text, image=image, warning_message=event_warning_message)
            
            #event Bandit camp
            if event == "Bandit Camp":
                if actions.bandit_camp():
                    post_event_text, image = actions.yes(event)
                else:
                    post_event_text, image = actions.yes_fail(event)

        elif request.form.get("No") == "No":
            post_event_text, image = actions.no(event)
            
        return render_template("post_event.html", post_event_text=post_event_text, image=image)

    elif request.method == "GET":
        return render_template("menu.html")


@app.route("/camp", methods=["GET", "POST"])
def camp():
    if request.method == "POST":
        if request.form.get("Adventure") == "Adventure":
            #25% of time there will be event
            if randint(0,100) < 25:
                actions.event()
                title, text, image = actions.text_event()
                return render_template("event.html",title=title, text=text, image=image)
            else:
                actions.create_enemy()
                name, description, image, warning_message, health, cheese, arrows, gold = actions.text_()
                return render_template("game.html", name=name, description=description, image=image, warning_message=warning_message, health=health, cheese=cheese, arrows=arrows, gold=gold)       

        elif request.form.get("Village") == "Village":
            health, cheese, arrows, gold = actions.text_stats()
            return render_template("village.html", health=health, cheese=cheese, arrows=arrows, gold=gold)

        elif request.form.get("Sleep") == "Sleep":
            actions.sleep()

        elif request.form.get("Castle") == "Castle":
            return render_template("challenge_the_boss.html")

        health, cheese, arrows, gold = actions.text_stats()
        return render_template("camp.html", health=health, cheese=cheese, arrows=arrows, gold=gold)

    elif request.method == "GET":
        health, cheese, arrows, gold = actions.text_stats()
        return render_template("camp.html", health=health, cheese=cheese, arrows=arrows, gold=gold)


@app.route("/village", methods=["GET", "POST"])
def village():
    if request.method == "POST":
        if request.form.get("Blacksmith") == "Blacksmith":
            health, cheese, arrows, gold = actions.text_stats()
            return render_template("blacksmith.html", health=health, cheese=cheese, arrows=arrows, gold=gold)

        elif request.form.get("Royal Quest") == "Royal Quest":
            pass

        elif request.form.get("Steal Food") == "Steal Food":
            if actions.steal():
                return render_template("steal_success.html")
            else:
                return render_template("steal_unsuccess.html")

        elif request.form.get("Camp") == "Camp":
            health, cheese, arrows, gold = actions.text_stats()
            return render_template("camp.html", health=health, cheese=cheese, arrows=arrows, gold=gold)

        health, cheese, arrows, gold = actions.text_stats()
        return render_template("village.html", health=health, cheese=cheese, arrows=arrows, gold=gold)

    elif request.method == "GET":
        health, cheese, arrows, gold = actions.text_stats()
        return render_template("village.html", health=health, cheese=cheese, arrows=arrows, gold=gold)


@app.route("/blacksmith", methods=["GET", "POST"])
def blacksmith():
    if request.method == "POST":
        message = ""
        warning_message = ""

        if request.form.get("Upgrade") == "Upgrade":
            if actions.upgrade_melee():
                message = "Blacksmith upgraded your weapon."
            else:
                warning_message = "Not enough gold."

        elif request.form.get("Fix") == "Fix":
            if actions.sharpen_melee():
                message = "Blacksmith fixed your weapon."
            else:
                warning_message = "Not enough gold."

        elif request.form.get("Village") == "Village":
            health, cheese, arrows, gold = actions.text_stats()
            return render_template("village.html", health=health, cheese=cheese, arrows=arrows, gold=gold)

        health, cheese, arrows, gold = actions.text_stats()
        return render_template("blacksmith.html", health=health, cheese=cheese, arrows=arrows, gold=gold, message=message, warning_message=warning_message)

    elif request.method == "GET":
        health, cheese, arrows, gold = actions.text_stats()
        return render_template("blacksmith.html", health=health, cheese=cheese, arrows=arrows, gold=gold)


@app.route("/jail", methods=["GET", "POST"])
def jail():
    if request.method == "POST":
        if request.form.get("Bribe") == "Bribe":
            if actions.bribe():
                health, cheese, arrows, gold = actions.text_stats()
                return render_template("village.html", health=health, cheese=cheese, arrows=arrows, gold=gold)
            else:
                warning_message = "Not enough gold"
                health, cheese, arrows, gold = actions.text_stats()
                sentence = actions.jail_text()
                return render_template("jail.html", health=health, cheese=cheese, arrows=arrows, gold=gold, sentence=sentence, warning_message=warning_message)

        elif request.form.get("Spend a Night") == "Spend a Night":
            if actions.serve_time():
                health, cheese, arrows, gold = actions.text_stats()
                return render_template("village.html", health=health, cheese=cheese, arrows=arrows, gold=gold)

        health, cheese, arrows, gold = actions.text_stats()
        sentence = actions.jail_text()
        return render_template("jail.html", health=health, cheese=cheese, arrows=arrows, gold=gold, sentence=sentence)


    elif request.method == "GET":
        health, cheese, arrows, gold = actions.text_stats()
        sentence = actions.jail_text()
        return render_template("jail.html", health=health, cheese=cheese, arrows=arrows, gold=gold, sentence=sentence)

        

@app.route("/game-over")
def game_over():
    return render_template("game_over.html")


@app.route("/challenge-the-boss", methods=["GET", "POST"])
def challenge_the_boss():
    global boss, enemies_defeated

    if request.method == "POST":
        if request.form.get("Challenge") == "Challenge":
            boss = True
            actions.create_enemy()
            name, description, image, warning_message, health, cheese, arrows, gold = actions.text_()
            return render_template("game.html", name=name, description=description, image=image, warning_message=warning_message, health=health, cheese=cheese, arrows=arrows, gold=gold)       

        elif request.form.get("Not yet") == "Not yet":
            enemies_defeated = 0
            health, cheese, arrows, gold = actions.text_stats()
            return render_template("camp.html", health=health, cheese=cheese, arrows=arrows, gold=gold)

    elif request.method == "GET":
        return render_template("menu.html")
    

@app.route("/epilogue")
def epilogue():
    return render_template("epilogue.html")


@app.route("/how-to-play")
def how_to_play():
    return render_template("how-to-play.html")


@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if request.method == "POST":
        text = request.form["feedback"]
        with open("stats-and-stuff/feedback.txt", "w")as file:
            file.write(text)

    if request.method == "GET":
        return render_template("feedback.html")

    return render_template("feedback.html")

if __name__ == "__main__":
    app.run(debug=True)
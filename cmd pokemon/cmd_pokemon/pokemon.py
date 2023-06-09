from math import sqrt, floor, log10
from random import randint, shuffle, choice, random
from time import sleep
from pokemonStrengthChart import typeAdantages, typeDisadantages
from pokeworld import pokemonWorld


def pprint(*args, **kwargs):
    print('\t\t', *args, **kwargs)


class Pokemon(object):
	__slots__ = 'name', 'categories', 'level', 'health', 'maxHealth', 'experience', 'nextLevelAt', 'attacks', 'learnableAttacks', 'defence', 'speed', 'evolveAt', 'evolveTo', 'newAttackAt', 'basedef', 'baseSpeed'
	experienceChart = [0] + [5 + 2 * (i + 1) ** 2 for i in range(100)]
	learningCheckpoints = [2, 7, 10, 15, 18, 23, 30, 39, 46, 55, 60, 64, 67, 72, 78, 89, 95, 100]

	def __init__(self, name, pokedata, level=0, *args, **kwargs):
		self.name = name
		self.newAttackAt = 0
		self.categories = pokedata['type']
		self.level = level
		self.maxHealth = 15 + floor(log10(self.level * 23 + 1) * self.level ** 1.7)
		self.health = self.maxHealth
		self.basedef = pokedata['baseDef']
		self.baseSpeed = pokedata['baseSpeed']
		self.defence = pokedata['baseDef']
		self.speed = pokedata['baseSpeed']
		self.evolveAt = pokedata['evolveAt']
		self.evolveTo = pokedata['evolveTo']
		self.experience = 0
		self.nextLevelAt = self.experienceChart[self.level + 1]
		self.attacks = pokedata['startAttacks'][:]
		self.learnableAttacks = pokedata['learnableAttacks'][:]
		
	def updateLevel(self, playertype=None):
		self.level += 1
		self.maxHealth = 15 + floor(log10(self.level * 23 + 1) * self.level ** 1.7)
		self.health = self.maxHealth
		self.defence += randint(0, 5)
		self.speed += randint(0, 5)
		self.basedef = self.defence
		self.baseSpeed = self.speed
		if playertype is None:
			self.experience = self.experience - self.nextLevelAt
		else: self.experience = randint(0, self.nextLevelAt)
		self.nextLevelAt = self.experienceChart[self.level + 1] if self.level < 100 else None
		if playertype is None:
			pprint(f"{self.name} levelled up...\n"); sleep(0.3)
			pprint(f"Current level: {self.level}"); sleep(0.3)
			pprint(f"Max Health increased to {self.maxHealth}"); sleep(0.3)
			pprint(f"Defence increased to {self.defence}"); sleep(0.3)
			pprint(f"Speed increased to {self.speed}\n"); sleep(0.3)

    
    
		if self.evolveAt is not None:
			if self.level >= self.evolveAt:
				self.evolvePokemon(playertype)

		if len(self.learnableAttacks) != 0:
			if self.level >= self.learningCheckpoints[self.newAttackAt]:
				self.newAttackAt += 1
				self.learnNewAttack(playertype)

		for attack in self.attacks:
			if attack is not None:
				if attack.heal == 0 and attack.recoil == 0:
					attack.updateAttack(self.level)
				if attack.heal != 0:
					attack.updateAttack(self.level, newHeal=5)
				if attack.recoil != 0:
					attack.updateAttack(self.level, newRecoil=5)


	def learnNewAttack(self, playertype=None):
		attackToLearn = self.learnableAttacks.pop()
		if not all(self.attacks):
			if playertype is None:
				sleep(0.5)			
				pprint(f"{self.name} learnt {attackToLearn.name}"); sleep(0.5)
			indNone = self.attacks.index(None)
			self.attacks[indNone] = attackToLearn
		else:
			if playertype is None:
				sleep(0.5)
				pprint(self.name, 'wants to learn', attackToLearn.name, end='\n')
				sleep(0.5)
				pprint('CURRENT ATTACKS: '); sleep(0.5)
				i=0
				for attack in self.attacks:
					pprint(f"{i+1}) {attack.name}")
					i+=1
					sleep(0.2)
				pprint()
				pprint("New Attack Stats: \n")
				attackToLearn.printAttack()
				pprint()
				sleep(0.2)
				discard = input('\t\tWhich attack would you like to replace?\n\t\t(Choose 1, 2, 3, 4. Any other choice will result in not learning the attack): ')
				if discard in ['1', '2', '3', '4']:
					self.attacks[int(discard)-1] = attackToLearn
			else:
				idiscard = randint(0, len(self.attacks)-1)
				self.attacks[idiscard] = attackToLearn


	def evolvePokemon(self, playertype=None):
		if self.name == 'nidoran':
			dice = random()
			self.evolveTo = 'nidorino' if dice >= 0.4 else 'nidorina'
      
		evolveform = pokemonWorld[self.evolveTo]

		if playertype is None:
			sleep(0.2)
			pprint()
			pprint("What is happening !!!!")
			sleep(2.5)
			pprint(self.name, 'is evolving....')
			sleep(2)
			pprint(self.name, 'has evolved into', self.evolveTo)
			sleep(2.2)
			pprint()

		self.name = self.evolveTo
		self.evolveTo = evolveform['evolveTo']
		self.evolveAt = evolveform['evolveAt']
		self.categories = evolveform['type']
		self.defence += randint(10, 15)
		self.speed += randint(8, 15)

		if evolveform.get('learnableAttacks', None) is not None:
			self.learnableAttacks = evolveform['learnableAttacks'] + self.learnableAttacks
		

	def attack(self, enemyPokemon, attackUsedInd):
		attackUsed = self.attacks[attackUsedInd]
		pprint()
		pprint(f"{self.name} used {attackUsed.name}")
		sleep(0.2)
		attackType = attackUsed.attCategory
		enemyType = enemyPokemon.categories

		chanceToMiss = random()
		if attackUsed.name == 'agility':
			if self.speed < self.baseSpeed + 10:
				self.speed += floor(random()*2 + random()*1)
				pprint(f"{self.name}'s speed increased to {self.speed}"); sleep(0.2)
			else:
				pprint("Can't increase speed anymore at this level..."); sleep(0.2)
		elif attackUsed.name == 'howl':
			if chanceToMiss < attackUsed.accuracy:
				initialHealth = enemyPokemon.health
				enemyPokemon.health -= 0.95*enemyPokemon.health
				enemyPokemon.health = max(0, enemyPokemon.health)
				pprint(f"Health reduced by {initialHealth - enemyPokemon.health}"); sleep(0.2)
			else:
				pprint(f"{self.name} missed..."); sleep(0.2)
		elif attackUsed.name == 'harden':
			if self.defence < self.basedef + 9:
				self.defence += floor(random()*2 + random()*1)
				pprint(f"{self.name}'s defence increased to {self.defence}"); sleep(0.2)	
			else:
				pprint("Can't increase defence anymore at this level..."); sleep(0.2)

		elif chanceToMiss < attackUsed.accuracy:

			if attackUsed.name != 'Heal':
				criticalChance = random()
				initialHealth = enemyPokemon.health

				if criticalChance >= 0.92:
					pprint("Critical Hit...")
					sleep(0.2)
					enemyPokemon.health -= floor((0.3+random()*0.2)*attackUsed.damage)

				if enemyType in typeAdantages[attackType]:
					pprint("It's Super Effective !!")
					sleep(0.2)
					enemyPokemon.health -= floor((0.6+random()*0.8)*attackUsed.damage)

				elif enemyType in typeDisadantages[attackType]:
					pprint("It's not very effective !!")
					sleep(0.2)
					enemyPokemon.health += floor((0.2+random()*0.5)*attackUsed.damage)

				enemyPokemon.health -= floor(attackUsed.damage*((2.71823)**(-0.0056*enemyPokemon.defence)))
				enemyPokemon.health = max(0, enemyPokemon.health)
				pprint(f"Health reduced by {initialHealth - enemyPokemon.health}")

				if attackUsed.recoil != 0:
					sleep(0.2)
					pprint(f"{self.name} got a recoil of {-floor(attackUsed.recoil)}"); sleep(0.2)
					self.health += floor(attackUsed.recoil)
					self.health = max(0, self.health)
     
				if attackUsed.heal != 0:
					sleep(0.2)
					self.health = min(self.maxHealth, self.health + attackUsed.heal)
					pprint(f"{self.name} healed some portion of it's health..."); sleep(0.2)

			else:
				self.health = min(self.maxHealth, self.health + attackUsed.heal)
				pprint(f"{self.name} healed some portion of it's health..."); sleep(0.2)

		else:
			pprint(f"{self.name} missed...\n"); sleep(0.2)


		self.attacks[attackUsedInd].count -= 1
		# sleep(0.2); pprint(f"{self.attacks[attackUsedInd].name}'s count decreased to {self.attacks[attackUsedInd].count}"); sleep(0.2)


	def printPokemon(self):
		pprint(f"Name: {self.name}\tLevel: {self.level}\tHP: {self.health}/{self.maxHealth}"); sleep(0.5)
	
	
	def displayStats(self, trainer="player's", detailed=False):
		if trainer == "player's":
			pprint(f"+---------------------------------------------+"); sleep(0.3); pprint()
			pprint(f"{trainer} {self.name}"); sleep(0.3)
			pprint(f"PokemonType: {self.categories}  Level: {self.level}"); sleep(0.3)
			pprint(f"Health: {self.health}  MaxHealth: {self.maxHealth}"); sleep(0.3)
			pprint(f"Defense: {self.defence}  Speed: {self.speed}"); sleep(0.3)
			pprint(f"Experience: {self.experience}/{self.nextLevelAt}"); sleep(0.3)
			pprint(f"Attacks: "); sleep(0.4)
			i=0
			for attack in self.attacks:
				if attack != None:
					pprint(f"{i+1}) {attack.name:20} :  {attack.count} left"); sleep(0.2)
					if detailed: 
						pprint()
						attack.printAttack()
						pprint()
				else:
					pprint(f"{i+1}) {attack}")
				i+=1
				sleep(0.4)
			pprint()
			pprint(f"+---------------------------------------------+"); sleep(0.5); pprint()
   
		else:
			pprint(f"+---------------------------------------------+"); sleep(0.4); pprint()
			pprint(f"{trainer} {self.name}"); sleep(0.4)
			pprint(f"PokemonType: {self.categories}  Level: {self.level}"); sleep(0.4)
			pprint(f"Health: {self.health}  MaxHealth: {self.maxHealth}"); sleep(0.4)
			pprint()
			pprint(f"+---------------------------------------------+"); sleep(0.5); pprint()
	
	
	def gain_exp(self, enemyPok, battletype='wild'):
		enemyType = enemyPok.categories
		multiplier = 1
  
		ExpIncrease = 3*(self.level*4 + 1)
  
		if enemyType in typeAdantages[self.categories]:
			multiplier = 0.4 + random()*0.5
		elif enemyType in typeDisadantages[self.categories]:
			multiplier = 1.3 + random()*0.7
   
		if battletype == 'gym': multiplier += 7
		elif battletype == 'duel': multiplier += 2
   
		enemylvl = enemyPok.level
		if enemylvl >= self.level:
			ExpIncrease += 6*(enemylvl-self.level)**2.8
		else:
			ExpIncrease -= 5*(self.level-enemylvl)**1.75
   
		ExpIncrease = floor(max(7, ExpIncrease)*multiplier)
	
		pprint(f"{self.name}'s Experience increased by {ExpIncrease}")
		self.experience += ExpIncrease
		# pprint(f"{self.experience} <- Total exp\n")
		sleep(0.8)
		if self.nextLevelAt is not None:
			if self.experience > self.nextLevelAt:
				while self.experience > self.nextLevelAt:
					self.updateLevel()
			

	def visitPokemonCentre(self):
		self.health = self.maxHealth
		for attack in self.attacks:
			if attack is not None:
				attack.count = attack.maxcount

 
	def npcPokemonReady(self, maxlevel):
		for _ in range(maxlevel):
			self.updateLevel(playertype='npc')
	# 	self.updateLevel(playertype='npc')
	# 	self.updateLevel(playertype='npc')
 
 
	def useStone(self, stonetype, playertype=None):
		sleep(0.5)
		if self.name == 'pikachu':
			if self.level >= 18: 
				if stonetype == 'thunderstone':
					if playertype is None:
						pprint(f"You used {stonetype} to evolve {self.name} into {self.evolveTo}"); sleep(0.2)
					self.evolvePokemon(playertype)
				else: pprint(f"{stonetype} can't be used on {self.name}"); sleep(0.2)
			else: pprint(f"{self.name} can't be evolved at this level. Train it more..."); sleep(0.2)
		elif self.name == 'eevee':
			if self.level >= 10:
				if stonetype == 'thunderstone':
					self.evolveTo = 'jolteon'
					
					if playertype is None:
						pprint(f"You used {stonetype} to evolve {self.name} into {self.evolveTo}")
      	
					self.evolvePokemon(playertype)
     
				elif stonetype == 'waterstone':
					self.evolveTo = 'vaporeon'
					
					if playertype is None:
						pprint(f"You used {stonetype} to evolve {self.name} into {self.evolveTo}")
      
					self.evolvePokemon(playertype)

				elif stonetype == 'firestone':
					self.evolveTo = 'flareon'
					
					if playertype is None:
						pprint(f"You used {stonetype} to evolve {self.name} into {self.evolveTo}")
      
					self.evolvePokemon(playertype)

				else: pprint(f"{stonetype} can't be used on {self.name}."); sleep(0.2)
    
			else: pprint(f"{self.name} can't be evolved at this level. Train it more..."); sleep(0.2)
				
 

# for i in range(100):
#     p = Pokemon('jabba', pokemonWorld['pikachu'], i)
#     pprint(p.maxHealth)
# p = Pokemon('eevee', pokemonWorld['eevee'], 10)
# p.useStone('waterstone')

# pprint(p.experienceChart)

# for i in range(3,20):
# 	for j in range(3,20):
# 		p1 = Pokemon('jabba', pokemonWorld['charmander'], i)
# 		p2 = Pokemon('dabba', pokemonWorld['charmander'], j)
# 		pprint(f"p1 lvl: {i} | p2 lvl: {j}", end=' ')
# 		p1.gain_exp(p2)	
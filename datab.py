import sqlite3
import random


async def sql_start():
	global db, cur
	db = sqlite3.connect('database/db.db')
	cur = db.cursor()
	db.execute('CREATE TABLE IF NOT EXISTS users(user_id int, pet_name str, dead BOOL DEFAULT(1), feed INT, happy INT, energy INT)')
	db.commit()

async def get_ids():
	ids = cur.execute("SELECT user_id FROM users").fetchall()
	return ids

async def add(user_id):
	cur.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)",(user_id, 'TGochi', 1, 0, 0, 0))
	db.commit()	

async def check_dead(user_id):
	result = cur.execute("SELECT dead FROM users WHERE user_id = ?",(user_id,)).fetchall()
	return bool(result[0][0])

async def check(user_id):
	result = cur.execute("SELECT * FROM users WHERE user_id = ?",(user_id,)).fetchall()
	return bool(len(result))

async def kill(user_id):
	
	cur.execute(f'UPDATE users SET dead=1 WHERE user_id = ?',(user_id,))
	cur.execute(f'UPDATE users SET feed=0 WHERE user_id = ?',(user_id,))
	cur.execute(f'UPDATE users SET happy=0 WHERE user_id = ?',(user_id,))
	cur.execute(f'UPDATE users SET energy=0 WHERE user_id = ?',(user_id,))
	db.commit()	

async def alive(user_id):
	
	cur.execute(f'UPDATE users SET dead=0 WHERE user_id = ?',(user_id,))
	cur.execute(f'UPDATE users SET feed=10 WHERE user_id = ?',(user_id,))
	cur.execute(f'UPDATE users SET happy=10 WHERE user_id = ?',(user_id,))
	cur.execute(f'UPDATE users SET energy=10 WHERE user_id = ?',(user_id,))
	db.commit()


def live_time(user_id):

	result2 = cur.execute("SELECT happy FROM users WHERE user_id = ?",(user_id,)).fetchall()
	happy = result2[0][0]
	new_happy = happy + random.randint(-2, 0)
	cur.execute(f'UPDATE users SET happy={new_happy} WHERE user_id = ?', (user_id,))
	db.commit()

	result = cur.execute("SELECT energy FROM users WHERE user_id = ?",(user_id,)).fetchall()
	energy = result[0][0]
	new_energy = energy + random.randint(-2, 0)
	cur.execute(f'UPDATE users SET energy={new_energy} WHERE user_id = ?', (user_id,))
	db.commit()

	result1 = cur.execute("SELECT feed FROM users WHERE user_id = ?",(user_id,)).fetchall()
	feed = result1[0][0]
	new_feed = feed + random.randint(-2, 0)
	cur.execute(f'UPDATE users SET feed={new_feed} WHERE user_id = ?', (user_id,))
	db.commit()

async def feed(user_id):
	result = cur.execute("SELECT feed FROM users WHERE user_id = ?",(user_id,)).fetchall()
	feed = result[0][0]
	new_feed = feed + random.randint(1, 3)
	cur.execute(f'UPDATE users SET feed={new_feed} WHERE user_id = ?', (user_id,))
	db.commit()
async def happy(user_id):
	result = cur.execute("SELECT happy FROM users WHERE user_id = ?",(user_id,)).fetchall()
	happy = result[0][0]
	new_happy = happy + random.randint(1, 3)
	cur.execute(f'UPDATE users SET happy={new_happy} WHERE user_id = ?', (user_id,))
	db.commit()
async def energy(user_id):
	result = cur.execute("SELECT energy FROM users WHERE user_id = ?",(user_id,)).fetchall()
	energy = result[0][0]
	new_energy = energy + random.randint(1, 3)
	cur.execute(f'UPDATE users SET energy={new_energy} WHERE user_id = ?', (user_id,))
	db.commit()

def check_stats(user_id):
	result = cur.execute("SELECT energy FROM users WHERE user_id = ?",(user_id,)).fetchall()
	energy = result[0][0]
	result1 = cur.execute("SELECT feed FROM users WHERE user_id = ?",(user_id,)).fetchall()
	feed = result1[0][0]
	result2 = cur.execute("SELECT happy FROM users WHERE user_id = ?",(user_id,)).fetchall()
	happy = result2[0][0]
	stats = [energy, feed, happy]
	return stats
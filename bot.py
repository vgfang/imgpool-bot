# bot.py
import os
import random
import requests
import asyncio
import uuid
import shutil
import discord
import string
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents=intents=discord.Intents.all()
intents = discord.Intents()
intents.members = True

bot = commands.Bot(command_prefix='!')

imgPath = './img_pools/'
imageFormats = ("image/png", "image/jpeg", "image/jpg", "image/gif", "image/webp")
uploadRole = os.getenv('UPLOAD_ROLE')
adminRole = os.getenv('ADMIN_ROLE')
bot.imgRunTasks = []
bot.maxImgRunTasks = 6

# returns filenames within a given directory, excluding hidden unix files
def listdir_no_hidden(path):
    return list(filter(lambda x: not x.startswith('.'), os.listdir(path)))

# checks if filename is a safe input
def check_filename(filename):
	illegalChars = ['..','\\',' ','/']
	if filename is None:
		return f"Error: Filename is empty."
		
	for x in illegalChars:
		if x in filename:
			return f"Error: Unsafe filename for deletion."
	return "Success"

# checks if poolname is valid and if the pool already exists
def check_poolname_and_exists(validPools, pool):
	check = check_poolname(pool)
	if check != "Success":
		return check
	if pool not in validPools:
		return f"Error: poolname {pool} does not exist.\nUse `!imgop` to list pools."
	return "Success"

# checks if poolname is valid and if the pool does not exist
def check_poolname_and_not_exists(validPools, pool):
	check = check_poolname(pool)
	if check != "Success":
		return check
	if pool in validPools:
		return f"Error: poolname {pool} already exists.\nUse `!imgop` to list pools."
	return "Success"

# checks if poolname is valid
def check_poolname(pool):
	illegalChars = ['/','\'','\"',' ','\t','\n','.','\\','..']
	illegalPools = ['misc']
	minPoolLen = 3
	maxPoolLen = 12

	if pool in illegalPools:
		return f"Error: poolname `{pool}` is illegal."
	for x in illegalChars:
		if x in pool:
			return f"Error: poolname `{pool}` contains an invalid character: `{illegalChars}`."
	if len(pool) > maxPoolLen:
		return f"Error: poolname `{pool}` is longer than `{maxPoolLen}` characters."
	if len(pool) < minPoolLen:
		return f"Error: poolname `{pool}` is shorter than `{minPoolLen}` characters."

	return "Success"

@bot.event
async def on_ready():
	for guild in bot.guilds:
		print(
			f'{bot.user} is connected to the following guild:\n'
			f'{guild.name}(id: {guild.id})'
		)

# PUBLIC COMMANDS
# Commands available to any role.

@bot.command(name='imgop', help='Lists possible pool options.')
async def imgop(ctx):
	validPools = listdir_no_hidden(imgPath)
	await ctx.send(f"Valid image pools: `{validPools}`")
	return

@bot.command(name='imgcn', help='Sends Message with Pool Image Count.')
async def imgcn(ctx, pool=None):
	validPools = listdir_no_hidden(imgPath)
	if pool not in validPools and pool is not None:
		await ctx.send("Error: Invalid pool for image count.\nUse `!imgop` to list pools.")
		return

	if pool is None: # return total image count
		imgCount = 0
		for vPool in validPools: # choose random from all directories
			imgCount += len(listdir_no_hidden(f"{imgPath}{vPool}"))
		await ctx.send(f"Total image count: `{imgCount}`")
	else: # return pool image count
		imgCount = len(listdir_no_hidden(f"{imgPath}{pool}"))
		await ctx.send(f"Image count for `{pool}` pool: `{imgCount}`")
	return

@bot.command(name='img', help='Responds with random image.')
async def img(ctx, pool=None):
	validPools = listdir_no_hidden(imgPath)
	filename = ''
		
	if pool is not None and pool not in validPools:
		await ctx.send("Error: Improper pool input.\nUse `!imgop` to see valid image pools.")
		return

	if pool is None:
		pool = ''
		allImgs = []
		for vPool in validPools: # choose random from all directories
			vPoolImgs = listdir_no_hidden(f"{imgPath}{vPool}")
			allImgs += list(map(lambda x: os.path.join(str(vPool),x),vPoolImgs))
		if len(allImgs) == 0:
			await ctx.send("Error: no images.")
			return
		filename = f"{imgPath}{random.choice(allImgs)}"
	else:
		imgs = listdir_no_hidden(imgPath+pool)
		if len(imgs) == 0:
			await ctx.send(f"Error: Empty pool `{pool}`.")
			return
		filename = f"{imgPath}{pool}/{random.choice(imgs)}"

	# add to ctx.send for filename: filename[len(imgPath):],
	await ctx.send(file=discord.File(filename))
	return filename

# UPLOAD COMMANDS
# Commands available to upload and admin roles.

@bot.command(name='imgin', help='Upload Image into Pool.')
@commands.has_any_role(uploadRole, adminRole)
async def imgin(ctx, pool=None):
	validPools = listdir_no_hidden(imgPath)
	if pool is None:
		pool = "misc"

	if pool not in validPools:
		await ctx.send("Error: Invalid pool for upload.\nUse `!imgop` to list pools.")
		return

	if len(ctx.message.attachments) == 0:
		await ctx.send("Error: Need to upload one (1) image file.")

	for attachment in ctx.message.attachments:
		url = attachment.url
		if url[0:26] != "https://cdn.discordapp.com":
			await ctx.send("Error: Bad URL.")
			return

		r = requests.get(url, stream=True)
		if r.headers['content-type'] not in imageFormats:
			await ctx.send(f"Error: File must be of types: `{imageFormats}`")
			return
		filename = f"{uuid.uuid4()}.{r.headers['content-type'][6:]}"
		filedirname = f"{imgPath}{pool}/{filename}"
		with open(filedirname, 'wb') as outFile:
			shutil.copyfileobj(r.raw, outFile)
			await ctx.send(f"Success: uploaded `{pool}`/`{filename}`")


# ADMIN COMMANDS
# Commands available to admin role.
@bot.command(name='imgrm', help='Removes image using filename')
@commands.has_any_role(adminRole)
async def imgrm(ctx, filename=None):
	check = check_filename(filename)
	if check != "Success":
		await ctx.send(check)
		return

	validPools = listdir_no_hidden(imgPath)
	for vPool in validPools: # choose random from all directories
		vPoolImgs = listdir_no_hidden(f"{imgPath}{vPool}")
		if filename in vPoolImgs:
			os.remove(f"{imgPath}{vPool}/{filename}")
			await ctx.send(f"Success: removed `{vPool}`/`{filename}`")
			return
	await ctx.send(f"Error: File not found.")


@bot.command(name='imgpadd', help='Adds a new pool if available.')
@commands.has_any_role(adminRole)
async def imgpadd(ctx, pool=None):
	validPools = listdir_no_hidden(imgPath)
	check = check_poolname_and_not_exists(validPools, pool)
	if check != "Success":
		await ctx.send(check)
		return
	try:
		os.mkdir(f"{imgPath}{pool}")
	except:
	    ctx.send(f"Internal Error: Could not make pool `{pool}`.")
	    raise

	await ctx.send(f"Success: new pool `{pool}` created.")

@bot.command(name='imgpmod', help='Renames a pool.')
@commands.has_any_role(adminRole)
async def imgpmod(ctx, oldPool=None, newPool=None):
	if oldPool == 'misc' or newPool == 'misc':
		await ctx.send("Error: `misc` pool selected.")
		return

	validPools = listdir_no_hidden(imgPath)
	
	oldCheck = check_poolname_and_exists(validPools, oldPool)
	if oldCheck != "Success":
		await ctx.send(oldCheck)
		return

	newCheck = check_poolname_and_not_exists(validPools, newPool)
	if newCheck != "Success":
		await ctx.send(newCheck)
		return


	os.rename(f"{imgPath}{oldPool}", f"{imgPath}{newPool}")
	await ctx.send(f"Success: pool `{oldPool}` renamed to `{newPool}`.")

@bot.command(name='imgpmov', help='Moves all images from a pool')
@commands.has_any_role(adminRole)
async def imgpmov(ctx, oldPool=None, newPool=None):
	if oldPool == 'misc':
		await ctx.send("Error: `misc` pool selected as oldPool")
		return
	
	validPools = listdir_no_hidden(imgPath) 
	oldCheck = check_poolname_and_exists(validPools, oldPool)
	if oldCheck != "Success":
		await ctx.send(oldCheck)
		return

	imgs = listdir_no_hidden(imgPath+oldPool)
	if len(imgs) == 0:
		await ctx.send(f"Error: Empty oldPool `{oldPool}`.")
		return

	newCheck = check_poolname_and_exists(validPools, newPool)
	# exception that newPool can be misc
	if newCheck != "Success" and not newPool == 'misc':
		await ctx.send(newCheck)
		return

	oldFiles = os.listdir(f"{imgPath}{oldPool}")
	for fileName in oldFiles:
		shutil.move(os.path.join(f"{imgPath}{oldPool}", fileName), f"{imgPath}{newPool}")
	await ctx.send(f"Success: pool `{oldPool}` contents moved  to `{newPool}`.")

@bot.command(name='imgpdel', help='Deletes a pool and its contents.')
@commands.has_any_role(adminRole)
async def imgpdel(ctx, pool=None):
	validPools = listdir_no_hidden(imgPath)
	check = check_poolname_and_exists(validPools, pool)
	if check != "Success":
		await ctx.send(check)
		return
	try:
		shutil.rmtree(f"{imgPath}{pool}")
	except:
		await ctx.send(f"Internal Error: Pool `{pool}` deletion failure.")
		return
	await ctx.send(f"Success: Pool `{pool}` has been deleted.")

# internal coroutine for imgtrun
async def imgrun(ctx, taskId, minutes, pool=None): # coroutine to send images to a channel
	counter = 1
	if pool is None:
		await ctx.send(f"Success: initialized imgtrun task `{taskId}` with `{minutes}` minute timer.")
	else:
		await ctx.send(f"Success: initialized imgtrun task `{taskId}` with pool `{pool}` and `{minutes}` minute timer.")
	try:
		while True:
			await ctx.send(f"Image: imgtrun taskId=`{taskId}` counter: `{counter}`")
			await img(ctx, pool)
			await asyncio.sleep(minutes * 60)
			counter += 1
	except asyncio.CancelledError:
		await ctx.send(f"Success: canceled imgtrun task `{taskId}`")

@bot.command(name='imgtrun', help='Start imgtrun tasks for automatical image posting based on a time interval.')
@commands.has_any_role(adminRole)
async def imgtrun(ctx, minutes=1, pool=None):
	if not isinstance(minutes,int) or minutes < 1:
		await ctx.send(f"Error: minutes must be an integer greater than `0`.")
		return
	
	validPools = listdir_no_hidden(imgPath)
	if pool is not None and pool not in validPools:
		await ctx.send("Error: Improper pool input.\nUse `!imgop` to see valid image pools.")
		return

	# id for stopping
	taskId = random.choice(string.ascii_lowercase) + random.choice(string.ascii_lowercase) + random.choice(string.ascii_lowercase) + str(random.randint(0,9)) + str(random.randint(0,9)) + str(random.randint(0,9))

	if len(bot.imgRunTasks) > bot.maxImgRunTasks:
		await ctx.send("Error: Maximum number of imgtrun tasks (`6`) have been exceeded. Stop tasks using `!imgpstp` or `!imgpstpall`")
	# add to global list of current imgtrun, tuple with (id, minutes, pool, coroutine)
	bot.imgRunTasks.append((taskId, minutes, pool,(asyncio.create_task(imgrun(ctx, taskId, minutes, pool)))))

@bot.command(name='imgtstop', help='Stop a imgtrun task')
@commands.has_any_role(adminRole)
async def imgtstop(ctx, taskId=None):
	if taskId is None:
		await ctx.send(f"Error: Inter a valid imgtrun taskId. List options with `!imgtlist`")
		return
	if bot.imgRunTasks == []:
		await ctx.send(f"Error: There are no imgtruns to cancel.")
		return
	for task in bot.imgRunTasks:
		print(task[0])
		if task[0] == taskId:
			task[3].cancel()
			return
	await ctx.send(f"Error: Inter a valid imgtrun taskId. List options with `!imgtlist`")
	return

@bot.command(name='imgtstopall', help='Stop all imgtrun tasks.')
@commands.has_any_role(adminRole)
async def imgtstopall(ctx, taskId=None):
	if bot.imgRunTasks == []:
		await ctx.send(f"Error: There are no imgtruns to cancel.")
		return
	for task in bot.imgRunTasks:
		task[3].cancel()
	await ctx.send(f"Success: All imgtrun tasks are cancelled")
	return

@bot.command(name='imgtlist', help='List imgtrun Tasks.')
@commands.has_any_role(adminRole)
async def imgtlist(ctx):
	print(bot.imgRunTasks)
	if bot.imgRunTasks == []:
		await ctx.send(f"There are no imgtruns currently running.")
	message = f"Current imgtrun tasks:\n"
	for task in bot.imgRunTasks:
		message += f"\ttaskId: `{task[0]}` pool: `{task[1]}` minutes: `{task[2]}`\n"
	await ctx.send(message)

# ERROR CHECKING
@imgin.error
async def imgin_error(ctx, error):
	if isinstance(error, commands.MissingAnyRole):
		await ctx.send(f"Error: Need role `{uploadRole}` to upload images.")

@imgrm.error
@imgpadd.error
@imgpmod.error
@imgpdel.error
@imgtrun.error
@imgtstop.error
@imgtstopall.error
@imgtlist.error
async def on_pool_fn_error(ctx, error):
	if isinstance(error, (commands.MissingAnyRole)):
		await ctx.send(f"Error: Need role `{adminRole}` for image deletion and image pool management.")

bot.run(TOKEN)

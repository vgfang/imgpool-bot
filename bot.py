# bot.py
import os
import random
import requests
import uuid
import shutil
import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents=intents=discord.Intents.all()
intents = discord.Intents()
intents.members = True

bot = commands.Bot(command_prefix='!')

imgPath = './img_pools/'
imageFormats = ("image/png", "image/jpeg", "image/jpg", "image/gif")
uploadRole = os.getenv('UPLOAD_ROLE')

@bot.event
async def on_ready():
	for guild in bot.guilds:
		print(
			f'{bot.user} is connected to the following guild:\n'
			f'{guild.name}(id: {guild.id})'
		)

@bot.command(name='imgcn', help='Sends Message with Pool Image Count.')
async def imgcn(ctx, pool=None):
	validPools = os.listdir(imgPath)
	if pool not in validPools and pool is not None:
		await ctx.send("Error: Invalid pool for image count.\nUse `!img opt` to list pools.")
		return

	if pool is None: # return total image count
		imgCount = 0
		for vPool in validPools: # choose random from all directories
			imgCount += len(listdir_no_hidden(f"{imgPath}{vPool}"))
		await ctx.send(f"Total Image Count: {imgCount}")
	else: # return pool image count
		imgCount = len(listdir_no_hidden(f"{imgPath}{pool}"))
		await ctx.send(f"Image Count for {pool} pool: {imgCount}")
	return

@bot.command(name='imgin', help='Upload Image into Pool.')
@commands.has_role(uploadRole)
async def imgin(ctx, pool=None):
	validPools = os.listdir(imgPath)
	if pool is None:
		pool = "misc"

	if pool not in validPools:
		await ctx.send("Error: Invalid pool for upload.\nUse `!img opt` to list pools.")
		return

	for attachment in ctx.message.attachments:
		try:
			url = attachment.url
		except IndexError:
			print("Error: No Image.")
			await ctx.send("Error: Need to upload one (1) image file.")
			return
		else:
			if url[0:26] != "https://cdn.discordapp.com":
				await ctx.send("Error: Bad URL.")
				return
	
			r = requests.get(url, stream=True)
			#if r.headers['content-length'] > ImageSizeCap:
			#	await ctx.send(f"Error. File exceeded cap: {imageSizeCap} B")
			#	return
			if r.headers['content-type'] not in imageFormats:
				await ctx.send(f"Error: File must be of types: {imageFormats}")
				return
			print(2)
			imageName = f"{uuid.uuid4()}.{r.headers['content-type'][6:]}"
			imageName = f"{imgPath}{pool}/{imageName}"
			with open(imageName, 'wb') as outFile:
				print('Saving image: ' + imageName)
				shutil.copyfileobj(r.raw, outFile)
				await ctx.send(f"Success: Image uploaded to pool: {pool}")

@imgin.error
async def imgin_error(ctx, error):
	if isinstance(error, commands.MissingRole):
		await ctx.send(f"Need role: {uploadRole} to upload images.")

def listdir_no_hidden(path):
    return list(filter(lambda x: not x.startswith('.'), os.listdir(path)))

@bot.command(name='img', help='Responds with random image.')
async def img(ctx, pool='all'):
	validPools = os.listdir(imgPath)
	filename = ''
	
	if pool == 'opt': # return directory options
		await ctx.send("Valid image pools: " + str(validPools))
		return
	if pool != 'all' and not pool in validPools:
		await ctx.send("Improper pool input.\nUse `!img opt` to see valid image pools.")
		return

	if pool == 'all':
		pool = ''
		allImgs = []
		for vPool in validPools: # choose random from all directories
			vPoolImgs = listdir_no_hidden(f"{imgPath}{vPool}")
			allImgs += list(map(lambda x: os.path.join(str(vPool),x),vPoolImgs))
		filename = f"{imgPath}{random.choice(allImgs)}"
	else:
		filename = f"{imgPath}{pool}/{random.choice(listdir_no_hidden(imgPath+pool))}"

	await ctx.send(file=discord.File(filename))
	return filename

bot.run(TOKEN)

# imgpool bot
Imgpool bot is a discord bot for randomly selecting from image pools and uploading images to image pools on a server. There are 3 levels of permissions in the form of an upload role for uploading images, and an admin role for removing images and modifying image pools. 

## Commands
- any role
   + `!img`: returns a random image from any pool
   + `!img poolname`: returns a random image from `poolname` pool
   + `!imgop`: returns existing poolnames
   + `!imgcn`: returns the total image count
   + `!imgcn poolname`: returns the image count of `poolname` pool
- upload role
   + `!imgin`: uploads attached image(s) to `misc` pool 
   + `!imgin poolname`: uploads attached image(s) to `poolname` pool
      * supports multiple image uploads (up to 10) on mobile 
- admin role
   + `!imgrm filename`:
      * get filename by pressing `Open original` on an imgbot uploaded image
      * then select the only the image filename
      * eg. filename: `aabbdd1d-5873-40b7-b7c1-6bdb5ba2356e.png`
   + `!imgpadd poolname`: adds a new `poolname` pool
   + `!imgpmod oldPoolName newPoolName`: renames `oldPoolName` pool to `newPoolName`
   + `!imgpdel poolname`: delete `poolname` pool and all of its contents
      * cannot delete `misc`

## Deployment on GNU/Linux
1. `git clone` the repository
2. Install `tmux` on your distribution for running the bot 24/7. eg. `sudo apt install tmux`
3. Create a Discord bot at the Discord Developer Portal and add the bot to your desired server
4. Use your Discord Bot Token to fill in the `.env` variable
5. Fill out the roles for `UPLOAD_ROLE` and `ADMIN_ROLE` in `.env`
6. Activate the virtualenv: `source env/bin/activate`
7. Run the bot using `tmux` so that it does not terminate on logout: 
   - `tmux`
   - `source env/bin/activate`
   - `python3 bot.py`
   - `Ctrl+b`, `d`
8. To shut down the bot:
   - `tmux`
   - `Ctrl+b`, `s`
   - select tmux session with the running bot
   - `x`, `y`
# imgpool bot
Imgpool bot is a discord bot for uploading images to image pools on a server and randomly selecting from them with commands. There are 3 levels of permissions in the form of an upload role for uploading images, and an admin role for removing images and modifying image pools. Automatic image posting tasks can started and stopped be run synchonously.

## Commands
- any role
   + `!img`: returns a random image from any pool
      * `!img poolName`: returns a random image from `poolName` pool
   + `!imgop`: returns existing poolNames
   + `!imgcn`: returns the total image count
      * `!imgcn poolName`: returns the image count of `poolName` pool
   + `!imghp`: returns list of commands
- upload role
   + `!imgin`: uploads attached image(s) to `misc` pool 
   + `!imgin poolName`: uploads attached image(s) to `poolName` pool
      * supports multiple image uploads (up to 10) on mobile 
- admin role
   + `!imgrm filename`:
      * get filename by pressing `Open original` on an imgbot uploaded image
      * then select the only the image filename
      * eg. filename: `aabbdd1d-5873-40b7-b7c1-6bdb5ba2356e.png`
   + `!imgpadd poolName`: adds a new `poolName` pool
   + `!imgpmod oldPoolName newPoolName`: renames `oldPoolName` pool to `newPoolName`
   + `!imgpmov oldPoolName newPoolName`: moves `oldPoolName` images to `newPoolname`
   + `!imgpdel poolName`: delete `poolName` pool and all of its contents
   + `!imgtrun`: starts automatic image-posting task at a fixed time interval
      * `!imgtrun numOfMinutes`: with user-specified time interval
      * `!imgtrun numOfMinutes poolName`: user-specified time interval and pool
   + `imgtlist`: list all automatic image-posting tasks
   + `imgtstop taskId`: stop automatic image-posting task using its taskId
   + `imgtstopall`: stop all automatic image-posting tasks

## Deployment on GNU/Linux
1. `git clone` the repository
2. Install `tmux` on your distribution for running the bot 24/7. eg. `sudo apt install tmux`
3. Create a Discord bot at the Discord Developer Portal and add the bot to your desired server
4. Use your Discord Bot Token to fill in the `.env` variable
5. Fill out the roles for `UPLOAD_ROLE` and `ADMIN_ROLE` in `.env`
6. Run the bot using `tmux` so that it does not terminate on logout: 
   - `tmux`
   - `source env/bin/activate`
   - `python3 bot.py`
   - `Ctrl+b`, `d`
7. To shut down the bot:
   - `tmux`
   - `Ctrl+b`, `s`
   - select tmux session with the running bot
   - `x`, `y`
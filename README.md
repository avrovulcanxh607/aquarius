# Aquarius
## TV Playout Controller for OBS

This is a terrible bit of software which remotes controls OBS via Websockets to create a live TV stream. It is offered here in the hope that it might inspire someone to do something similar, only better.

Essentially the idea is that you have a library of "programme lists". Then you create a playlist explaining what time slot you'd like each series to be put into. listings_creator creates a list of OBS commands from this playlist, and then aquarius.py plays them out.

Listings_creator will try to fill time between episodes with a clock, ident, text bulletin or Pages From Ceefax. These are all just scences in OBS, you can put whatever you want there, or better yet customise the program to do what you need.

**Disclaimer: the software is offered completely as-is, with no warranty of any kind. I will no longer be offering support or assistance on this project, if you want to use it you must figure it out from the resources provided here.**

If you do decide to do something cool with this design, please consider posting photos of it to Bluesky and tagging "@nmsni.co.uk", I would love to see it!
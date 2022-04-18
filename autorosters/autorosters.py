from mwrogue.esports_client import EsportsClient
from rivercogutils import utils
from redbot.core import commands

from autorosters.autorosters_main import AutoRostersRunner


class AutoRosters(commands.Cog):
    """Automatically generates Team Rosters for Leaguepedia, using scoreboard data"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def autorosters(self, ctx, overview_page):
        await ctx.send('Okay, starting now!')
        credentials = await utils.get_credentials(ctx, self.bot)
        site = EsportsClient('lol', credentials=credentials,
                             max_retries_mwc=0,
                             max_retries=2, retry_interval=10)
        AutoRostersRunner(site, overview_page).run()
        await ctx.send('Okay, done!')

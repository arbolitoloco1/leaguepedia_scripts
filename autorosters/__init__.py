from .autorosters import AutoTeamRosters


def setup(bot):
    bot.add_cog(AutoTeamRosters(bot))

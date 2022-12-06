from discord import app_commands, Interaction
import json

config = json.load(open("./config.json"))
lower_regions = [r.lower() for r in config['supported_regions']]


class Region(app_commands.Transformer):
    async def autocomplete(self, interaction: Interaction, current):
        # not using lower regions since we want to display uppercase
        return [app_commands.Choice(name=region, value=region)
                for region in config['supported_regions']
                if current.lower() in region.lower()]

    async def transform(self, interaction: Interaction, value):
        if value.lower() not in lower_regions:
            return None
        else:
            return value.upper()

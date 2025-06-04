import discord, argparse, json, os

class MyClient(discord.Client):
    def __init__(self, cache, proxy, channel_id, devices_category_id, vendors_category_id):
        self.message_id = message_id
        self.channel_id = channel_id
        self.devices_category_id = devices_category_id
        self.vendors_category_id = vendors_category_id

        self.devices = json.load(open("devices.json","r"))
        self.cache = json.load(open("cache.json","r")) \
            if os.path.exists("cache.json") \
            else {"devices": {}, "vendors": {}}
        
        super().__init__(intents=discord.Intents.all(), proxy=proxy)

    async def save_cache(self):
        with open("cache.json","w") as file:
            json.dump(self.cache, file)
            file.close()

    async def update_navigation(self):
        # TODO: create devices' channels and write to cache (to devices and vendors)
        # TODO: update or create navigation message and write to cache (to message_id)
        
        await self.save_cache()

    async def on_ready(self):
        print(f'We have logged in as {self.user}')
        
        self.channel = await self.fetch_channel(self.channel_id)
        self.devices_category = await self.fetch_channel(self.devices_category_id)
        self.vendors_category = await self.fetch_channel(self.vendors_category_id)

        await self.update_navigation()

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--proxy', type=str)
    parser.add_argument('--token', type=str)
    parser.add_argument('--channel_id', type=int)
    parser.add_argument('--devices_category_id', type=int)
    parser.add_argument('--vendors_category_id', type=int)

    args = parser.parse_args()

    MyClient(
        args.proxy, 
        args.channel_id, 
        args.devices_category_id, 
        args.vendors_category_id
    ).run(args.token)

if __name__ == "__main__":
    main()

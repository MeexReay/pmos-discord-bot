import discord, argparse, json, os, copy

class MyClient(discord.Client):
    def __init__(self, proxy, channel_id):
        self.channel_id = channel_id

        self.devices = json.load(open("devices.json","r"))
        self.cache = json.load(open("cache.json","r")) \
            if os.path.exists("cache.json") \
            else {"devices": {}}
        
        super().__init__(intents=discord.Intents.all(), proxy=proxy)

    async def save_cache(self):
        with open("cache.json","w") as file:
            json.dump(self.cache, file)
            file.close()

    async def create_nonexistent_channels(self):
        print("Creating nonexistent device and vendor channels...")
        for vendor, devices in self.devices.items():
            if vendor not in self.cache["devices"]:
                channel = await self.channel.guild.create_text_channel(vendor.lower())
                message = await channel.send("# "+vendor+"\nThis chat is about "+vendor+" devices.")

                await message.pin()
                
                self.cache["devices"][vendor] = {
                    "channel_id": channel.id,
                    "message_id": message.id,
                    "devices": {}
                }

            vendor_channel = await self.fetch_channel(self.cache["devices"][vendor]["channel_id"])
            
            for codename, name in devices.items():
                if name not in self.cache["devices"][vendor]["devices"]:
                    channel = await vendor_channel.create_thread(name=codename, type=discord.ChannelType.public_thread)
                    message = await channel.send("# "+name+"\nThis thread is about "+name+".\nWiki page: https://wiki.postmarketos.org/wiki/"+(name.replace(" ", "_")))
                    
                    await message.pin()
                
                    self.cache["devices"][vendor]["devices"][name] = {
                        "channel_id": channel.id,
                        "message_id": message.id
                    }

                print(name)

    async def update_navigation_message(self):
        print("Upading navigation messages...")
        
        guild_id = self.channel.guild.id
        
        init_message_ids = copy.deepcopy(self.cache["message_ids"]) if "message_ids" in self.cache else []
        message_ids = copy.deepcopy(init_message_ids)
        index = 0

        async def request_message():
            nonlocal index, message_ids, init_message_ids
            
            if index < len(init_message_ids):
                message = await self.channel.fetch_message(init_message_ids[index])
            else: 
                message = await self.channel.send(".")
                message_ids.append(message.id)
            index += 1
            return message

        vendors_list_content = ["# Choose your vendor:"]
    
        for vendor, vdata in self.cache["devices"].items():
            vendor_channel_id = vdata["channel_id"]
            vendor_message_id = vdata["message_id"]
            
            message = await request_message()
            
            vendor_content = f"- [{vendor}](https://discord.com/channels/{guild_id}/{self.channel.id}/{message.id})"
            if len(vendors_list_content[-1]) + len(vendor_content) >= 2000:
                vendors_list_content += [vendor_content]
            else:
                vendors_list_content[-1] += "\n"+vendor_content
            
            content = f"# [{vendor}](https://discord.com/channels/{guild_id}/{vendor_channel_id}/{vendor_message_id})"
            
            for device, ddata in sorted(vdata["devices"].items()):
                device_channel_id = ddata["channel_id"]
                device_message_id = ddata["message_id"]
                device_content = f"- [{device}](https://discord.com/channels/{guild_id}/{device_channel_id}/{device_message_id})"

                if len(content) + len(device_content) >= 2000:
                    await message.edit(content=content)
                    message = await request_message()
                    content = device_content
                else:
                    content += "\n" + device_content
                
            await message.edit(content=content)
            
        for content in vendors_list_content:
            message = await request_message()
            await message.edit(content=content)

        message = await request_message()
        await message.edit(content="""# How to use this channel

1. Choose your device vendor in the message above
2. Choose your device name in the appeared message
3. That's it, now you are in the right topic, it will be pinned to your channel list if you write any messages

You can also simply click on the vendor name in Step 2 to go to the general channel about that vendor's devices.
Although the easiest way is to simply use Ctrl+F with the device code name""")
        
        self.cache["message_ids"] = message_ids
    
    async def update_navigation(self):
        await self.create_nonexistent_channels()
        await self.save_cache()
        await self.update_navigation_message()
        await self.save_cache()
        print("Navigation updated!!")

    async def on_ready(self):
        print(f'We have logged in as {self.user}')
        
        self.channel = await self.fetch_channel(self.channel_id)

        if not os.path.exists("cache.json"):
            for i in self.channel.guild.text_channels:
                if i.category_id == None:
                    await i.delete()
        if len(self.cache["message_ids"]) == 0:
            await self.channel.purge(limit=len(self.devices))

        await self.update_navigation()

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--proxy', type=str)
    parser.add_argument('--token', type=str)
    parser.add_argument('--channel_id', type=int)

    args = parser.parse_args()

    MyClient(
        args.proxy, 
        args.channel_id, 
    ).run(args.token)

if __name__ == "__main__":
    main()

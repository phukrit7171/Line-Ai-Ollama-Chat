# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.
from dotenv import load_dotenv
load_dotenv()
from ai import generate_response
import os
import sys
from argparse import ArgumentParser

import asyncio
from aiohttp import web

import logging

from aiohttp.web_runner import TCPSite

from linebot import LineBotApi
from linebot.v3 import WebhookParser
from linebot.v3.messaging import (
    Configuration,
    AsyncApiClient,
    AsyncMessagingApi,
    TextMessage,
    ReplyMessageRequest,
    ShowLoadingAnimationRequest,
    MessagingApiBlob
)
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    ImageMessageContent,
    StickerMessageContent,
)


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

configuration = Configuration(access_token=channel_access_token)


class Handler:
    def __init__(self, line_bot_api: AsyncMessagingApi, parser: WebhookParser):
        self.line_bot_api = line_bot_api
        self.parser = parser

    async def echo(self, request):
        signature = request.headers["X-Line-Signature"]
        body = await request.text()

        try:
            events = self.parser.parse(body, signature)
        except InvalidSignatureError:
            return web.Response(status=400, text="Invalid signature")

        for event in events:
            await self.line_bot_api.show_loading_animation(
                ShowLoadingAnimationRequest(
                    chatId=event.source.user_id, loadingSeconds=30
                )
            )
            if not isinstance(event, MessageEvent):
                continue
            if isinstance(event.message, TextMessageContent):
                print("TextMessageContent")
                await self.line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[
                            TextMessage(
                                text=await generate_response(
                                    event.source.user_id, event.message.text
                                )
                            )
                        ],
                    )
                )
            if isinstance(event.message, ImageMessageContent):
                print("ImageMessageContent")
                print(event)
                image_object = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN")).get_message_content(event.message.id)
                image_binary = image_object.content
                await self.line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token, messages=[TextMessage(text=await generate_response(event.source.user_id, image_data=image_binary))]
                        )
                    )
                
                
                pass
            if isinstance(event.message, StickerMessageContent):
                print("StickerMessageContent")
                try :
                    text = ("(sticker) "+(", ".join(event.message.keywords))+" (/sticker)")
                    print(text)
                    await self.line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token, messages=[TextMessage(text=await generate_response(event.source.user_id, text))]
                        )
                    )
                except Exception as e:
                    await self.line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token, messages=[TextMessage(text="Sorry, I don't understand the meaning of this sticker.")]
                        )
                    )
                    
                pass

        return web.Response(text="OK\n")


async def main(port=8000):
    async_api_client = AsyncApiClient(configuration)
    line_bot_api = AsyncMessagingApi(async_api_client)
    parser = WebhookParser(channel_secret)

    handler = Handler(line_bot_api, parser)

    app = web.Application()
    app.add_routes([web.post("/callback", handler.echo)])

    runner = web.AppRunner(app)
    await runner.setup()
    site = TCPSite(runner=runner, port=port)
    await site.start()
    while True:
        await asyncio.sleep(3600)  # sleep forever


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

    arg_parser = ArgumentParser(
        usage="Usage: python " + __file__ + " [--port <port>] [--help]"
    )
    arg_parser.add_argument("-p", "--port", type=int, default=8000, help="port")
    options = arg_parser.parse_args()
    print(f"Starting on port {options.port} ...")
    asyncio.run(main(options.port))

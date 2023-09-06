# You, pretty much, have to just paste in the MongoDB URL. The code will do the rest itself.
# Or at least it should. If you need help, contact me on Discord; voidable_method.
# Remember, a license applies to this code, so be cautious, because you can be sued.
# Read it before using this.

import string
import time
import random
import datetime

from sanic import Sanic
from pymongo import MongoClient
from sanic.response import text, html, json
from sanic.exceptions import SanicException
from os import system as cmd

server = Sanic("VoidKeygen")
dbClient = MongoClient(
    "yourURL"
)
keysdb = dbClient.keysdb
keys = keysdb.get_collection("keys")

# Functions
def generateKey():
    return "".join(
        random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)
        for _ in range(26)
    )


def sendLog(message):
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime(
        "[%Y-%m-%d %H:%M:%S %z]"
    )
    logMessage = f"{timestamp} [LOG] {message}"
    print(logMessage)


# Main route
@server.route("/")
async def main(request):
    with open("./public/index.html") as file:
        content = file.read()
    return html(content)


# API Routes
@server.route("/api/status")
async def status(request):
    return json({"status": "online"})


@server.route("/api/generate/<hwid>")
async def generate(request, hwid):
    hwidExists = keys.find_one({"hwid": hwid})
    if hwidExists is None:
        key = generateKey()
        expirationTime = time.time() + 60
        keys.update_one(
            {"hwid": hwid},
            {"$set": {"key": key, "expiration_time": expirationTime}},
            upsert=True,
        )
        sendLog(f"A new key has been generated for HWID: {hwid}")
        return text(key)
    else:
        return text("used")


@server.route("/api/check/<hwid>/<key>")
async def checkKey(request, hwid, key):
    keyExists = keys.find_one({"hwid": hwid, "key": key})
    if keyExists is not None:
        expirationTime = keyExists.get("expiration_time", 0)
        currentTime = time.time()

        if expirationTime >= currentTime:
            return text("valid")
        else:
            keys.delete_one({"hwid": hwid, "key": key})
            return text("expired")
    else:
        return text("invalid")


if __name__ == "__main__":
    cmd("cls")
    server.run(host="0.0.0.0", port=80)
    sendLog(f"Server shut down.")

import asyncio
import hashlib

import bcrypt

DEFAULT_EXECUTOR = None


async def check_password(password: str, hashed: str) -> bool:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(DEFAULT_EXECUTOR,
                                      bcrypt.checkpw,
                                      password.encode('utf-8'),
                                      hashed.encode('utf-8'),
                                      )


async def hash_password(password: str) -> str:
    loop = asyncio.get_event_loop()

    # NOTE: osu! hashes passwords with md5 before passing them to bcrypt.
    password = hashlib.md5(password.encode('utf-8')).hexdigest()

    return (await loop.run_in_executor(DEFAULT_EXECUTOR,
                                       bcrypt.hashpw,
                                       password.encode('utf-8'),
                                       bcrypt.gensalt(),
                                       )).decode()

import os
import gzip
import shutil
import asyncio
from pathlib import Path

import aiohttp


def download(url: str, to: str) -> None:
    Path(to).parent.mkdir(parents=True, exist_ok=True)

    tmp = to + '.tmp'
    tar = to + '.gz.tmp'

    async def do_download() -> None:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(url, timeout=None) as resp:
                with open(tar, 'wb') as fd:
                    # TODO: read and write in chunks
                    fd.write(await resp.read())

        # decompress to a tmp file before replacing the original
        with gzip.open(tar, 'rb') as f_in:
            with open(tmp, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        # chmod +x
        status = os.stat(tmp)
        os.chmod(tmp, status.st_mode | 0o111)

        # override the original
        shutil.copy(tmp, to)

        # remove temporary files
        os.remove(tar)
        os.remove(tmp)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(do_download())

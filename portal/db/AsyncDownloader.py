
import asyncio, aiohttp, aiofiles
import uvloop
import json
import gns


class DefaultDownloader():
    """ Takes a url, downloads it, reads json """
    def __init__(self, url, method='get', params=dict(), path=None):
        self.url = url
        self.path = path  # writes to location if not None
        self.method = method
        self.params = params
        self.path = path
        self.json_dumps_kwargs = dict(indent=4)

    async def write(self, res_json, path):
        txt_contents = json.dumps(res_json, **self.json_dumps_kwargs);
        async with aiofiles.open(path, 'w') as f:
            await f.write(txt_contents)
            self.did_write(path)

    async def download(self, session):
        self.will_download(self.url)
        async with session.request(self.method, self.url, params=self.params) as response:
            response_json = await response.json()
            self.did_download(self.url)

        if self.path:
            asyncio.ensure_future( self.write(response_json, self.path) ) #! await
        return response_json

    def did_write(self, path):
        pass

    def will_download(self, url):
        pass

    def did_download(self, url):
        pass

class PagingDownloader(DefaultDownloader):
    """
    For use when there is a 'since_id' or other paging counter and 
    getting the full resource requires paging
    """
    def __init__(self, *args, **kwargs):
        self._json = self.initial_json_value()
        super().__init__(*args, **kwargs)

    def initial_json_value(self):
        raise NotImplemented

    def update_json(self, response_json):
        """ Add to json here, as needed """
        raise NotImplemented

    def needs_next_page(self, response_json):
        """ Determine whether or not """
        raise NotImplemented

    def update_params_for_page(self, response_json):
        """ Allows you to send new parameters in url to get the next page """
        raise NotImplemented

    async def download(self, session):
        self.will_download(self.url)
        async with session.request(self.method, self.url, params=self.params) as response:
            response_json = await response.json()
            self.did_download(self.url)
            self.update_json(response_json)

        if self.needs_next_page(response_json):
            self.update_params_for_page(response_json)
            asyncio.ensure_future( self.download(session) ) #! await
        else:
            if self.path:
                asyncio.ensure_future( self.write(self._json, self.path) ) #! await
            return self._json

class DiscoveryDownloader(DefaultDownloader):
    """
    For use when information inside the response leads to another url
    which represents a seperate resource to be downloaded
    """
    klass = DefaultDownloader

    def __init__(self, *args, **kwargs):
        self._kwargs = kwargs
        super().__init__(*args, **kwargs)

    def discover_urls(self, resp_json):
        """ Return the urls to follow """
        raise NotImplemented

    def discover_path(self, url, resp_json):
        """ Return the path to save it to, if applicable; returning None means we want the result """
        raise NotImplemented

    async def download(self, session):
        self.will_download(self.url)
        async with session.request(self.method, self.url, params=self.params) as response:
            response_json = await response.json()
            self.did_download(self.url)

        url = self.discover_urls(response_json)

        if url:
            if not isinstance(url, list):
                url = [url]
            if 'path' in self._kwargs:
                del self._kwargs['path']
            for u in url:
                path = self.discover_path(response_json, u)
                downloader = self.klass(u, path=path, **self._kwargs)
                asyncio.ensure_future( downloader.download(session) ) #! await

        if self.path:
            asyncio.ensure_future( self.write(response_json, self.path) ) #! await
        return response_json

class AsyncDownloaderHelper():
    """
    Helper to create the instances and run the machinery to download asyncronously
    """ 

    def __init__(self):
        """
        """
        self._loop = None
        self._downloaders = []

    def add_downloader(self, klass, *args, **kwargs):
        self._downloaders.append( klass(*args, **kwargs) )

    async def download_all(self):
        """ Drives the event loop, etc """
        ret = []
        async with aiohttp.ClientSession() as session:
            pending = []

            for downloader in self._downloaders:
                pending.append( asyncio.ensure_future( downloader.download(session) ) )

            while pending:
                dne, pnding= await asyncio.wait(pending)
                ret.extend( [d.result() for d in dne] )

                # Get all the tasks, including those that were scheduled with ensure_future
                tasks = asyncio.Task.all_tasks()
                pending = [tks for tks in tasks if not tks.done()]
                pending = [t for t in pending if not t._coro.__name__ == self.download_all.__name__]
        return ret

    def download(self):
        """ Set up state, launch the downloads """
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy()) # makes thing much faster
        self._loop = asyncio.get_event_loop()
        self._loop.slow_callback_duration = 3

        main_task = asyncio.ensure_future(self.download_all())
        return self._loop.run_until_complete( main_task )



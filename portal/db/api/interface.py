"""
The file lets me sort out the model for myself
1) Downloads info that is available via API into files
2) Puts it into database

Excuse the mess, it works well enough but isn't exactly clear what's happening
In particular errors aren't handled (FIXME)
"""
from portal.db.AsyncDownloader import AsyncDownloaderHelper, DefaultDownloader, DiscoveryDownloader, PagingDownloader
import gns
import click

class Outputter:
    def will_download(self, url):
        click.echo("Q: {}".format(click.style(url, fg='yellow')))

    def did_download(self, url):
        click.echo("S: {}".format(click.style(url, fg='green')))

    def did_write(self, path):
        click.echo("P: {}".format(click.style(path, fg='magenta')))

class MyDefaultDownloader(Outputter, DefaultDownloader):
    pass

class PathURLHelper():
    mb_api_base = gns.config.managebac.api_url
    oa_api_base = gns.config.openapply.api_url
    jsons_base = gns.config.paths.jsons

    @classmethod
    def build_json_entrypoint_path(cls, filename):
        return "{base}/{filename}.json".format(base=cls.jsons_base, filename=filename)

    @classmethod
    def build_entrypoint_url(cls, section):
        return "{base}/{section}".format(base=cls.mb_api_base, section=section)

    @classmethod
    def build_members_url(cls, path, id_):
        return "{base}/{path}".format(base=cls.mb_api_base, path=path.format(id=id_))

    @classmethod
    def build_oa_entrypoint_url(cls, section):
        return "{base}/{section}".format(base=cls.oa_api_base, section=section)

class MBSectionDiscovery(Outputter, DiscoveryDownloader):
    klass = MyDefaultDownloader

    def __init__(self, section, api_path, *args, **kwargs):
        self.section = section
        self.api_path = api_path
        super().__init__(*args, **kwargs)

    def discover_urls(self, resp_json):
        ret = []
        section = resp_json.get(self.section)
        for i, group in enumerate(section):
            group_id = group.get('id')
            ret.append( PathURLHelper.build_members_url(self.api_path, group_id) )
        return ret

    def discover_path(self, resp, url):
        tailend = url.split('/')[-2:]
        tailend.insert(0, self.section)  # differentiate between classes and ibgroups this way
        return PathURLHelper.build_json_entrypoint_path("-".join(tailend))

class OpenApplyPaging(Outputter, PagingDownloader):

    def will_download(self, url):
        click.echo("Q: {} (since_id={})".format(click.style(url, fg='yellow'), self.params['since_id']))

    def did_download(self, url):
        click.echo("S: {}".format(click.style(url, fg='green'), self.params['since_id']))

    def initial_json_value(self):
        return {'students':[], 'parents':[]}

    def update_json(self, response_json):
        students = response_json.get('students')
        links = response_json.get('links')
        if students:
            self._json['students'].extend(students)
        if links:
            parents = links.get('parents')
            self._json['parents'].extend(parents)

    def needs_next_page(self, response_json):
        """ Determine whether or not """
        return bool(response_json.get('students'))

    def update_params_for_page(self, response_json):
        """ Allows you to send new parameters in url to get the next page """
        self.params['since_id'] = response_json['students'][-1].get('id')

class AsyncAPIDownloader(AsyncDownloaderHelper):
    """
    Downloads all the user, classes, ib_groups information provided by ManageBac/OpenApply APIs
    """

    def __init__(self, *args, **kwargs):
        """
        Sets up the downloaders, using the class structure
        """
        mb_api_token = gns.config.managebac.api_token
        oa_api_token = gns.config.openapply.api_token

        super().__init__(*args, **kwargs)

        urls_to_traverse = [
            PathURLHelper.build_entrypoint_url('users'),
            PathURLHelper.build_entrypoint_url('ib_groups'),
            PathURLHelper.build_entrypoint_url('classes'),
            PathURLHelper.build_oa_entrypoint_url('students'),
        ]
        gns.tutorial(self.__doc__, edit=(urls_to_traverse, '.pretty'), banner=True)

        # These appear in order of how long it takes to download, each
        self.add_downloader( 
            OpenApplyPaging, 
            urls_to_traverse[3],
            params=dict(since_id=0, count=200, auth_token=oa_api_token), 
            path=PathURLHelper.build_json_entrypoint_path("open_apply_users")
        )

        self.add_downloader( 
            MBSectionDiscovery, 
            'classes',              # section
            'classes/{id}/members', # url after api/   
            urls_to_traverse[2], 
            params=dict(auth_token=mb_api_token), 
            path=PathURLHelper.build_json_entrypoint_path('classes')
        )

        self.add_downloader( 
            MBSectionDiscovery, 
            'ib_groups',            # section
            'groups/{id}/members',  # url after api/
            urls_to_traverse[1], 
            params=dict(auth_token=mb_api_token), 
            path=PathURLHelper.build_json_entrypoint_path('ib_groups')
        )

        self.add_downloader( 
            MyDefaultDownloader,
            urls_to_traverse[0], 
            params=dict(auth_token=mb_api_token),
            path=PathURLHelper.build_json_entrypoint_path('users')
        )

        # In case you want users-users-{id} jsons available
        # but there doesn't seem to be much useful information in full profile

        # self.add_downloader( 
        #     MBSectionDiscovery,
        #     'users',       # section
        #     'users/{id}',  # url after api/
        #     urls_to_traverse[0], 
        #     params=dict(auth_token=mb_api_token),
        #     path=PathURLHelper.build_json_entrypoint_path('users')
        # )



if __name__ == "__main__":

    go = APIDownloader()
    go.download()






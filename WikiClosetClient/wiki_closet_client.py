import json
from typing import Optional, Union, List, Iterable

from mwcleric import WikiClient, AuthCredentials, WikiggClient
from requests.exceptions import HTTPError
from mwclient.errors import APIError


class WikiClosetClient:
    def __init__(self, credentials: Optional[AuthCredentials] = None, client: Optional[WikiClient] = None):
        if credentials is None and client is None:
            raise ValueError("Must provide either credentials to log into Confluence or your own client")
        if credentials is not None:
            self.credentials = credentials
        if client is not None:
            self.confluence = client
            return
        self.confluence = WikiggClient('confluence', credentials=credentials)
        with open('skip_wikis.json', 'r') as f:
            data = json.load(f)
            if wikis := data['skip']:
                self.wikis_to_skip = wikis
            else:
                self.wikis_to_skip = []

    def all_wikis(self, wcstatus: str = 'all', lang: Optional[str] = None,
                  startat: Optional[str] = None,
                  do_skips: bool = True,
                  extensions: Union[str, List[str]] = None,
                  credentials: AuthCredentials = None) -> Iterable["WikiggClient"]:
        wikis = self.confluence.client.api('wikicloset', do='listwikis',
                                           wcprop='wikiid|name|status|flags|url', wcstatus=wcstatus
                                           )
        if type(extensions) is str:
            extensions = [extensions]

        # if you provide your own instance of confluence in the constructor then
        # it's possible that credentials will be None here and you won't log into the individual wikis
        # that should be fine
        passed_startat = startat is None
        credentials = self.credentials if credentials is None else credentials
        for wiki, info in wikis['query']['listwikis'].items():
            if do_skips and wiki in self.wikis_to_skip:
                continue
            if wiki == startat:
                passed_startat = True
            if not passed_startat:
                continue
            if lang is not None:
                # return only the language the user wants
                if info['languages'].get(lang) is not None:
                    yield from self._filter_extensions(wiki, credentials, lang, extensions)
                continue
            for language in info['languages'].keys():
                yield from self._filter_extensions(wiki, credentials, language, extensions)

    @staticmethod
    def _filter_extensions(wiki, credentials, lang, extensions) -> Iterable["WikiClient"]:
        if extensions is None:
            try:
                yield WikiggClient(wiki, credentials=credentials, lang=lang)
            except (HTTPError, APIError):
                return
            return
        try:
            fs = WikiggClient(wiki, credentials=credentials, lang=lang)
        except (HTTPError, APIError):
            return
        valid = True

        for ext in extensions:
            if ext not in fs.extensions:
                valid = False
                break
        if valid:
            yield fs

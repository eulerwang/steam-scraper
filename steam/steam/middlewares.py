import logging
import os
import re
from w3lib.url import url_query_cleaner

from scrapy import Request
from scrapy.downloadermiddlewares.redirect import RedirectMiddleware
from scrapy.extensions.httpcache import FilesystemCacheStorage
from scrapy.utils.request import request_fingerprint

logger = logging.getLogger(__name__)


class SteamCacheStorage(FilesystemCacheStorage):
    def _get_request_path(self, spider, request):
        # For the purposes of caching we wish to discard the
        # unstable 'snr' query field.
        url = url_query_cleaner(request.url, ['snr'], remove=True)
        request = request.replace(url=url)
        key = request_fingerprint(request)
        return os.path.join(self.cachedir, spider.name, key[0:2], key)


class CircumventAgeCheckMiddleware(RedirectMiddleware):
    def _redirect(self, redirected, request, spider, reason):
        if not self.is_age_check_url(redirected.url):
            return super()._redirect(redirected, request, spider, reason)

        logger.debug(f"Age check triggered for {request.url}.")
        return Request(url=request.url,
                       cookies={'mature_content': '1'},
                       meta={'dont_cache': True})

    def is_age_check_url(self, url):
        return True if re.findall('app/(.*)/agecheck', url) else False

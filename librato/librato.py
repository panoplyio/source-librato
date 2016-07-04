import time
import json
import base64
import urllib2
import panoply
import datetime

MINUTE = 60
DAY = 24 * 60 * MINUTE
RESOLUTION = 5 * MINUTE
BASE_URL = "https://metrics-api.librato.com/v1/metrics"

class Librato(panoply.DataSource):
    
    # constructor
    def __init__(self, source, options):
        super(Librato, self).__init__(source, options)
        start = int(time.time() - 7 * DAY)
        # self._url = build_url(source.get("user"), source.get("token"))
        self._meta_page = 0
        self._current_metric = 0
        self._auth = base64.encodestring("%(user)s:%(token)s" % source).strip()

        # create the list of metrics along with their start timestamp
        self._metrics = map(lambda metric: {
            "name": metric, 

             # the ._read() method may change that timestamp in order to 
             # paginate over the results
            "start": start
        }, source.get("metrics", []))

        # progress counters
        self._total = len(self._metrics)


    # returns all of the metrics available for this source
    def get_metrics(self):
        body = self._request(BASE_URL)
        metrics = body.get("metrics", [])
        return map(lambda metric: metric.get("name"), metrics)


    # reads the next batch of data
    def read(self, n = None):
        if len(self._metrics) == 0:
            return None # we are done here.

        # build the URL for the next metric
        metric = self._metrics[0]
        url = "%s/%s?resolution=%d&start_time=%d" % (
            BASE_URL, 
            metric["name"],
            RESOLUTION,
            metric["start"]
        )

        # read the API response for the next metric
        body = self._request(url)

        # constrcut the results list per source, per measurement
        results = []
        for source, measures in body.get("measurements", {}).iteritems():
            for measure in measures:
                results.append({
                    "source": source,
                    "metric": metric["name"],
                    "time": measure.get("measure_time"),
                    "value": measure.get("value"),
                    "count": measure.get("count")
                })

        # paginate to the next start time
        start = body.get("query", {}).get("next_time")
        if start is not None:
            metric["start"] = start
        else:

            # no more results for this metric, remove it
            self._metrics.pop(0)

            # report the progress
            loaded = self._total - len(self._metrics)
            msg = "%s of %s metrics loaded" % (loaded, self._total)
            # self.progress(loaded, self._total, msg)
        
        return results

    # helper function for issuing GET requests against the Librato API
    def _request(self, url):
        req = urllib2.Request(url)
        req.add_header("Authorization", "Basic %s" % self._auth)

        self.log("GET", url)
        try:
            res = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            raise LibratoError.from_http_error(e)

        self.log("RESPONSE", url)

        body = res.read()
        return json.loads(body)


# Librato API exception class
class LibratoError(Exception):

    # unavailable time range is indicative that the requested time range 
    # contains not results
    def isEmptyTimeRange(self):
        return str(self) == "unavailable for the given time range"

    @classmethod
    def from_http_error(cls, err):
        """
        Librato's REST API returns appropriate HTTP error codes on failure, 
        which are raised as generic urllib2.HTTPError instances. These error
        responses also contain a JSON with a descriptive explanation of the 
        error, one that's more readable than the generic HTTP message like
        "400 Bad Request". This method transforms this generic error to an 
        instance of the LibratoError class with the descriptive message from the
        response body
        """

        try:
            # "an HTTPError can also function as a non-exceptional file-like
            # return value" -- urllib2 docs
            # see: https://docs.python.org/2/library/urllib2.html#urllib2.HTTPError
            body = err.read()
            parsed = json.loads(body)
            errors = parsed["errors"]

            # extract the error details from the http body
            # Librato supports request and params errors. the latter is a key-
            # value map of params and their validation error message
            # see: https://www.librato.com/docs/api/#error-messages
            if "request" in errors:
                return cls(errors["request"][0])
            elif "params" in errors:
                param = errors["params"].keys()[0]
                msg = errors["params"][param][0]
                return cls(param + " " + msg)
        except Exception, e:
            # unable to read a structured error from the response, just
            # return the original error
            pass

        # no descriptive error message was extracted, just return the original
        # generic error.
        return err




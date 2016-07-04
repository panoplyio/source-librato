import io
import json
import librato
import urllib2
import unittest
import urlparse

OPTIONS = {
    "logger": lambda *msgs: None # no-op logger
}

orig_urlopen = urllib2.urlopen

class TestLibrato(unittest.TestCase):


    def tearDown(self):
        urllib2.urlopen = orig_urlopen


    def test_auth(self):
        "user and token are encoded correclty in HTTP authorization header"

        auths = []
        def urlopen(req):
            auths.append(req.get_header("Authorization"))
            return io.BytesIO("{}")

        urllib2.urlopen = urlopen
        l = librato.Librato({
            "user": "Aladdin", 
            "token": "OpenSesame",
            "metrics": [ "cpu_time" ]
        }, OPTIONS)
        l.read()

        self.assertEqual(auths[0], "Basic QWxhZGRpbjpPcGVuU2VzYW1l")


    def test_url(self):
        "valid url suffixed with the metric name"

        urls = []
        def urlopen(req):
            urls.append(req.get_full_url())
            return io.BytesIO("{}")

        urllib2.urlopen = urlopen
        l = librato.Librato({
            "user": "Aladdin", 
            "token": "OpenSesame",
            "metrics": [ "cpu_time", "cpu_idle" ]
        }, OPTIONS)
        l.read() # first metric
        l.read() # second metric

        expected = "https://metrics-api.librato.com/v1/metrics/cpu_time?"
        self.assertTrue(urls[0].startswith(expected))

        expected = "https://metrics-api.librato.com/v1/metrics/cpu_idle?"
        self.assertTrue(urls[1].startswith(expected))


    def test_get_metrics(self):
        "retrieves the full list of available metrics"

        urls = []
        def urlopen(req):
            urls.append(req.get_full_url())
            res = {
                "metrics": [
                    {"name": "cpu_time", "display_name": "hello"},
                    {"name": "cpu_idle", "display_name": "world"},
                ]
            }
            return io.BytesIO(json.dumps(res))

        urllib2.urlopen = urlopen
        l = librato.Librato({
            "user": "Aladdin", 
            "token": "OpenSesame",
        }, OPTIONS)

        metrics = l.get_metrics()
        self.assertEqual(metrics, ["cpu_time", "cpu_idle"])
        self.assertEqual(urls,["https://metrics-api.librato.com/v1/metrics"])


    def test_done(self):
        "_read() returns None when all results where consumed"

        def urlopen(req):
            return io.BytesIO("{}")

        urllib2.urlopen = urlopen
        l = librato.Librato({
            "user": "Aladdin", 
            "token": "OpenSesame",
            "metrics": [ "cpu_time", "cpu_idle" ]
        }, OPTIONS)

        self.assertIsNotNone(l.read()) # first metric
        self.assertIsNotNone(l.read()) # second metric
        self.assertIsNone(l.read()) # should be done by now


    def test_pagination(self):
        "_read() continues to read the same metric with the new start time"

        times = [ 100, 200 ]
        urls = []
        def urlopen(req):
            urls.append(req.get_full_url())
            nexttime = times.pop(0) if len(times) > 0 else None
            res = { "query": { "next_time": nexttime } }
            return io.BytesIO(json.dumps(res))

        urllib2.urlopen = urlopen
        l = librato.Librato({
            "user": "Aladdin", 
            "token": "OpenSesame",
            "metrics": [ "cpu_time" ]
        }, OPTIONS)

        self.assertIsNotNone(l.read()) # first start time
        self.assertIsNotNone(l.read()) # 100
        self.assertIsNotNone(l.read()) # 200; last
        self.assertIsNone(l.read()) # done.

        # urls[0] has the default start time; irrelevant for pagination

        qs = parseqs(urls[1])
        self.assertEqual(qs["start_time"], ["100"])

        qs = parseqs(urls[2])
        self.assertEqual(qs["start_time"], ["200"])


    def test_progress(self):
        "test that the progress notifications are fired"
        pass


    def test_results(self):
        "parse results json and breakdown all measurements to a list of results"
        def urlopen(req):
            return io.BytesIO(json.dumps(RESULTS))

        urllib2.urlopen = urlopen
        l = librato.Librato({
            "user": "Aladdin", 
            "token": "OpenSesame",
            "metrics": [ "cpu_time" ]
        }, OPTIONS)
        res = l.read()
        self.assertEqual(res, EXPECTED)


    def test_request_err(self):
        "parses request errors and returns the descriptive message"

        def urlopen(req):
            url = req.get_full_url()
            body = io.BytesIO(json.dumps({
                "errors": {
                    "request": [
                        "one two",
                        "three four"
                    ]
                }
            }))
            raise urllib2.HTTPError(url, 400, "Bad Request", {}, body)

        urllib2.urlopen = urlopen
        l = librato.Librato({
            "user": "Aladdin", 
            "token": "OpenSesame",
            "metrics": [ "cpu_time", "cpu_idle" ]
        }, OPTIONS)

        try:
            l.read()
        except librato.LibratoError, e:
            self.assertEqual(str(e), "one two")


    def test_params_err(self):
        "parses params errors and returns the descriptive message"

        def urlopen(req):
            url = req.get_full_url()
            body = io.BytesIO(json.dumps({
                "errors": {
                    "params": {
                        "name": ["is missing", "is required"],
                        "value": ["is not a number", "is too big"]
                    }
                }
            }))
            raise urllib2.HTTPError(url, 400, "Bad Request", {}, body)

        urllib2.urlopen = urlopen
        l = librato.Librato({
            "user": "Aladdin", 
            "token": "OpenSesame",
            "metrics": [ "cpu_time", "cpu_idle" ]
        }, OPTIONS)

        try:
            l.read()
        except librato.LibratoError, e:
            self.assertEqual(str(e), "name is missing")


    def test_unknown_err(self):
        "forwards all other errors as-is"

        raised = {}
        def urlopen(req):
            url = req.get_full_url()
            body = io.BytesIO(json.dumps({}))
            e = urllib2.HTTPError(url, 400, "Bad Request", {}, body)
            raised["error"] = e
            raise e

        urllib2.urlopen = urlopen
        l = librato.Librato({
            "user": "Aladdin", 
            "token": "OpenSesame",
            "metrics": [ "cpu_time", "cpu_idle" ]
        }, OPTIONS)

        try:
            l.read()
        except Exception, e:
            self.assertEqual(e, raised["error"])




# test data that returns from the API
RESULTS = {
    "resolution": 60,
    "measurements": {
        "server1.acme.com": [
            {
                "measure_time": 1234567890,
                "value": 84.5,
                "count": 1
            },
            {
                "measure_time": 1234567950,
                "value": 86.7,
                "count": 1
            }
        ],
        "server2.acme.com": [
            {
                "measure_time": 1234567890,
                "value": 94.5,
                "count": 1
            },
            {
                "measure_time": 1234567890,
                "value": 96.7,
                "count": 1
            }
        ]
    }
}

# the expected parsed output data from the previous RESULTS variable
EXPECTED = [
    {
        "count": 1,
        "source": "server2.acme.com",
        "metric": "cpu_time",
        "value": 94.5,
        "time": 1234567890
    },
    {
        "count": 1,
        "source": "server2.acme.com",
        "metric": "cpu_time",
        "value": 96.7,
        "time": 1234567890
    },
    {
        "count": 1,
        "source": "server1.acme.com",
        "metric": "cpu_time",
        "value": 84.5,
        "time": 1234567890
    },
    {
        "count": 1,
        "source": "server1.acme.com",
        "metric": "cpu_time",
        "value": 86.7,
        "time": 1234567950
    }
]


# -- helper functions
def parseqs(url):
    "parses a url and returns its parsed query string"
    return urlparse.parse_qs(urlparse.urlparse(url).query)


# fire it up.
if __name__ == "__main__":
    unittest.main()

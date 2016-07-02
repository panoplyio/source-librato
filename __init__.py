params = [
    {
        "name": "user",
        "title": "Email",
        "placeholder": "Email address"
    },
    {
        "name": "token",
        "title": "API Token",
        "help": "Your Librato API token. [Learn more](https://metrics.librato.com/tokens)"
    },
    {
        "name": "metrics",
        "required": True,
        "title": "Metrics",
        "type": "list",
        "values": load_metrics,
        "dependencies": [ "user", "token" ]
    }
]

def load_metrics(source):
    pass
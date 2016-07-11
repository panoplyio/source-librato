from librato import *

Stream = Librato # alias

TITLE = "Librato"
ICON = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAMAAAD04JH5AAAAsVBMVEUPgKr///8PgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKoPgKo5cNJPAAAAOnRSTlMAAOEM5wk2FQb2Zmwb2/nze8wDhA855KUzz5O37UW9yYr8h0uBck606iqfeDCuP2kSoh5R8LFUwI2oFsEihgAAAcdJREFUeF7t2Fdu4zAUheFjU1SxarETuXenT693/wsbYB4GCEbSQwDxIMn9V/AB7MQIbX04fS5TGbwxRi0Ae7m/lb9RAMkiEhEawOwyESLgOBYhAsKDCBNgNkIFBKVQAWYrVEC1ES6gFi5gLVxAmJIBtXABn3Iy4CRcQLgiA74KGfBEBlQrMsAXMiBmAxZswJINmLMBKRswlpelAAUoQAEKUIACFKAABShgvzz7TVU1/nm5JwC8yRT/mk48x4CoMHiWKSKXAM/Hf/meO8D8C1pK5q4AXoLWEs8NIPPRkZ85ARTorHABuDLozFw5AMToKR4ekFv0ZPPBAdfo7XpwwAS9TQYHzNDbbHBAgN6CwQEhegvpAPoQ0CchfRnSN6K3vxXLR+5hxD+O+RcSie7Q0V3kBCBpgNaCVNwApEzQUlK+n4eJSPRg8Sz7EL3Fx2l/2U3cPAKPTXyTvdYPCgUoQAEKUIACFKAABShAASkbMGcDlmzAgg2I2YAZGfCtIgO+gwz4QQasLBlQgwvIAzLgAC4gtWTAGlxADS5gU3EB2ymogDIAFfDTgAr4FYIJGB8BIiDbGRAB0SIBaIDb+4sFOACv/F2v0dboDwpU3suqbEhHAAAAAElFTkSuQmCC"
PARAMS = [
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
        "values": [],
        "dependencies": [ "user", "token" ]
    }
]
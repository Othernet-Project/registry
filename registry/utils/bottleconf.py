import json
import datetime

import bottle


class DateTimeCapableEncoder(json.JSONEncoder):
    EPOCH = datetime.datetime(1970, 1, 1)

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return self.totimestamp(obj)

        return super(DateTimeCapableEncoder, self).default(obj)

    def totimestamp(self, dt):
        # Drop offset awareness
        dt = dt.replace(tzinfo=None)
        td = dt - self.EPOCH
        return td.total_seconds()


def json_dumps(s):
    return json.dumps(s, cls=DateTimeCapableEncoder)


def pre_init(app, config):
    app.install(bottle.JSONPlugin(json_dumps=json_dumps))
    bottle.debug(config['server.debug'])

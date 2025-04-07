from urllib.parse import urlencode, quote_plus

class FilterArgs:
    def __init__(self, request_args):
        # if request_args: # TODO still set default values if request_args was null?
        self.search = request_args.get('search', '')
        self.hide_children = request_args.get('hide_children', True)
        self.show_future = request_args.get('show_future', False)
        self.priority = request_args.get('priority', None)
        if self.priority:
            self.priority = int(self.priority)

    def to_url_params(self):
        params = {}
        if self.search:
            params['search'] = self.search
        if self.show_future:
            params['show_future'] = 'on'
        if self.priority:
            params['priority'] = self.priority
        return '?' + urlencode(params, quote_via=quote_plus) if params else ''
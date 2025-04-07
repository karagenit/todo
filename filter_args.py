class FilterArgs:
    def __init__(self, request_args):
        # if request_args: # TODO still set default values if request_args was null?
        self.search = request_args.get('search', '')
        self.hide_children = request_args.get('hide_children', True)
        self.hide_future = request_args.get('hide_future', False)
    
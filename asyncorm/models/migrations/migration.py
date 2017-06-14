class Migration(object):
    operations = []
    models = []


class ModelState(object):

    def __init__(self, model_name, orig_state, end_state):
        self.model_name = model_name
        self.orig_state = orig_state
        self.end_state = end_state

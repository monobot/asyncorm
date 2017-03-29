from ..fields import Field


class Inspector():

    @classmethod
    def jsonify(cls, model):
        inspected_model = {}
        for n, f in model.__dict__.items():
            if not n == 'Meta':
                inspected_model[n] = f
                if isinstance(f, Field):
                    inspected_model[n] = f.__dict__

        return inspected_model

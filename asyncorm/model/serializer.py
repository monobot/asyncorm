from ..exceptions import SerializerError


class SerializerMeta(type):

    def __new__(cls, clsname, bases, clsdict):
        base_class = super().__new__(cls, clsname, bases, clsdict)

        defined_meta = clsdict.pop('Meta', None)

        if defined_meta:
            if hasattr(defined_meta, 'model'):
                base_class.model = getattr(defined_meta, 'model')
            else:
                raise SerializerError(
                    'The serializer has to define it refeers to'
                )
            if hasattr(defined_meta, 'fields'):
                base_class._fields = getattr(defined_meta, 'fields')
            else:
                raise SerializerError(
                    'The serializer has to define it refeers to'
                )

        return base_class


class ModelSerializer(object, metaclass=SerializerMeta):

    def __init__(self):
        self.validate_fields()

    def validate_fields(self):
        for f in self._fields:
            if not hasattr(self.model, f):
                raise SerializerError(
                    '{} is not a correct argument for model {}'.format(
                        f, self.model
                    )
                )

    def serialize(self, instanced_model):
        return_dict = {}

        if not isinstance(instanced_model, self.model):
            raise SerializerError(
                'That model is not an instance of {}'.format(self.model)
            )

        for f in self._fields:
            return_dict[f] = getattr(instanced_model, f)

        return return_dict

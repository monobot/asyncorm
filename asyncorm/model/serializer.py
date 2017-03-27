from ..exceptions import SerializerError


class Serializer():
    pass


class ModelSerializerMeta(type):

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


class SerializerMethod(Serializer):
    pass


class ModelSerializer(Serializer, metaclass=ModelSerializerMeta):

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

    @classmethod
    def serialize(cls, instanced_model):
        return_dict = {}

        if not isinstance(instanced_model, cls.model):
            raise SerializerError(
                'That model is not an instance of {}'.format(cls.model)
            )

        for f in cls._fields:
            if hasattr(cls, f):
                serializer = getattr(cls, f)
                if isinstance(serializer, SerializerMethod):
                    try:
                        serializer_method = getattr(cls, 'get_{}'.format(f))
                        return_dict[f] = serializer_method(
                            serializer, instanced_model
                        )
                    except AttributeError:
                        raise SerializerError(
                            ('The serializer does not defines the method '
                             'for attribute {}').format(f)
                        )
            else:
                return_dict[f] = getattr(instanced_model, f)

        return return_dict

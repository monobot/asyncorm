from asyncorm.exceptions import AsyncOrmSerializerError


class Serializers:
    pass


class ModelSerializerMeta(type):
    def __new__(cls, clsname, bases, clsdict):
        base_class = super().__new__(cls, clsname, bases, clsdict)

        defined_meta = clsdict.pop("Meta", None)

        if defined_meta:
            # For a modelserializer when check that has it correctly defined
            # has a model
            if hasattr(defined_meta, "model"):
                base_class.model = getattr(defined_meta, "model")
            else:
                raise AsyncOrmSerializerError("The serializer has to define the model it's serializing")
            # has fields
            if hasattr(defined_meta, "fields"):
                base_class._fields = getattr(defined_meta, "fields")
            else:
                raise AsyncOrmSerializerError("The serializer has to define the fields's to serialize")

        return base_class


class SerializerMethod(Serializers):
    def __init__(self, method_name=""):
        self.method_name = method_name


class ModelSerializer(Serializers, metaclass=ModelSerializerMeta):
    def __init__(self):
        self.validate_fields()

    def validate_fields(self):
        for f in self._fields:
            if not hasattr(self.__class__, f) and not hasattr(self.model, f):
                raise AsyncOrmSerializerError("{} is not a correct argument for model {}".format(f, self.model))

    @classmethod
    def serialize(cls, instanced_model):
        return_dict = {}

        if not isinstance(instanced_model, cls.model):
            raise AsyncOrmSerializerError("That object is not an instance of {}".format(cls.model))

        for f in cls._fields:
            # if the serializer class has an specific serializer for that field
            if hasattr(cls, f):
                serializer = getattr(cls, f)
                if isinstance(serializer, SerializerMethod):
                    method_name = serializer.method_name
                    if not method_name:
                        serializer_method = getattr(cls, "get_{}".format(f))
                    else:
                        serializer_method = getattr(cls, method_name)
                    return_dict[f] = serializer_method(instanced_model)
                # here we have to add subserializers when posible
            else:
                field_class = getattr(instanced_model.__class__, f)
                return_dict[f] = field_class.serialize_data(getattr(instanced_model, f))

        return return_dict

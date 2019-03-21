from asyncpg.exceptions import UniqueViolationError

from asyncorm.exceptions import AsyncOrmModelDoesNotExist, AsyncOrmModelError
from asyncorm.manager.queryset import Queryset
from asyncorm.models.fields import AutoField


class ModelManager(Queryset):
    def __init__(self, model, field=None):
        self.model = model
        self.field = field
        super().__init__(model)

    def _copy_me(self):
        queryset = ModelManager(self.model)
        queryset.set_orm(self.orm)
        queryset.query = self.query_copy()

        return queryset

    async def get_or_create(self, **kwargs):
        try:
            return await self.get(**kwargs), False
        except AsyncOrmModelDoesNotExist:
            return await self.create(**kwargs), True

    async def save(self, instanced_model):
        # performs the database save
        fields, field_data = [], []

        for k, data in instanced_model.data.items():
            f_class = getattr(instanced_model.__class__, k)

            field_name = f_class.db_column or k

            data = f_class.sanitize_data(data)

            fields.append(field_name)
            field_data.append(data)

        for field in instanced_model.fields.keys():
            if field not in fields:
                f_class = getattr(instanced_model.__class__, field)

                field_name = f_class.db_column or field
                data = getattr(instanced_model, field)
                field_has_default = hasattr(instanced_model.fields[field], "default")
                default_not_none = instanced_model.fields[field].default is not None
                not_auto_field = not isinstance(f_class, AutoField)
                if data is None and field_has_default and default_not_none and not_auto_field:
                    data = instanced_model.fields[field].default

                    data = f_class.sanitize_data(data)

                    fields.append(field_name)
                    field_data.append(data)

        db_request = [
            {
                "action": getattr(instanced_model, instanced_model.orm_pk) and "_db__update" or "_db__insert",
                "id_data": "{}={}".format(instanced_model.db_pk, getattr(instanced_model, instanced_model.orm_pk)),
                "field_names": ", ".join(fields),
                "field_values": field_data,
                "field_schema": ", ".join(["${}".format(value + 1) for value in range(len(field_data))]),
                "condition": "{}={}".format(instanced_model.db_pk, getattr(instanced_model, instanced_model.orm_pk)),
            }
        ]
        try:
            response = await self.db_request(db_request)
        except UniqueViolationError:
            raise AsyncOrmModelError("The model violates a unique constraint")

        self.modelconstructor(response, instanced_model)

        # now we have to save the m2m relations: m2m_data
        fields, field_data = [], []
        for k, data in instanced_model.m2m_data.items():
            # for each of the m2m fields in the model, we have to check
            # if the table register already exists in the table otherwise
            # and delete the ones that are not in the list
            # first get the table_name
            cls_field = getattr(instanced_model.__class__, k)
            table_name = cls_field.table_name
            foreign_column = cls_field.foreign_key

            model_column = instanced_model.cls_tablename()

            model_id = getattr(instanced_model, instanced_model.orm_pk)

            db_request = [
                {
                    "table_name": table_name,
                    "action": "_db__insert",
                    "field_names": ", ".join([model_column, foreign_column]),
                    "field_values": [model_id, data],
                    "field_schema": ", ".join(["${}".format(value + 1) for value in range(len([model_id, data]))]),
                }
            ]

            if isinstance(data, list):
                for d in data:
                    db_request[0].update(
                        {
                            "field_values": [model_id, d],
                            "field_schema": ", ".join(
                                ["${}".format(value + 1) for value in range(len([model_id, d]))]
                            ),
                        }
                    )
                    await self.db_request(db_request)
            else:
                await self.db_request(db_request)

    async def delete(self, instanced_model):
        db_request = [
            {
                "action": "_db__delete",
                "id_data": "{}={}".format(instanced_model.db_pk, getattr(instanced_model, instanced_model.db_pk)),
            }
        ]
        return await self.db_request(db_request)

    async def create(self, **kwargs):
        n_object = self.model(**kwargs)
        await self.model.objects.save(n_object)
        return n_object

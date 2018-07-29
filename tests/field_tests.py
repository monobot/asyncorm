from datetime import date, datetime, time

from uuid import UUID
from netaddr import EUI, IPNetwork, mac_eui48

from asyncorm.exceptions import FieldError
from asyncorm import models
from tests.testapp.models import Book, Publisher, Reader, Author
from tests.testapp2.models import Organization, Client, Appointment, Skill, Developer
from tests.test_helper import AioTestCase


class FieldTests(AioTestCase):
    def test_class_definition(self):
        with self.assertRaises(NotImplementedError) as exc:
            models.Field()

        self.assertEqual(
            exc.exception.args[0],
            'Missing "internal_type" attribute from class definition',
        )

    def test_required_kwargs_not_sent(self):

        with self.assertRaises(FieldError) as exc:
            models.CharField()

        self.assertEqual(exc.exception.args[0], '"CharField" field requires max_length')

    def test_required_kwargs_wrong_value(self):
        with self.assertRaises(FieldError) as exc:
            models.CharField(max_length="gt")

        self.assertEqual(exc.exception.args[0], "Wrong value for max_length")

    def test_now_correcly_valuates(self):
        # correctly valuates if max_length correctly defined
        self.assertTrue(models.CharField(max_length=45))

    def test_db_column_validation_wrong_start(self):
        with self.assertRaises(FieldError) as exc:
            models.CharField(max_length=35, db_column="_oneone")

        self.assertEqual(exc.exception.args[0], 'db_column can not start with "_"')

    def test_db_column_validation_wrong_ending(self):
        with self.assertRaises(FieldError) as exc:
            models.CharField(max_length=35, db_column="oneone_")

        self.assertEqual(exc.exception.args[0], 'db_column can not end with "_"')

    def test_db_column_validation_wrong_characters(self):
        with self.assertRaises(FieldError) as exc:
            models.CharField(max_length=35, db_column="one__one")

        self.assertEqual(exc.exception.args[0], 'db_column can not contain "__"')

    def test_db_column_correctly_validates(self):
        # this is an allowed fieldname
        self.assertTrue(models.CharField(max_length=35, db_column="one_one"))

    async def test_field_max_length(self):
        reader = Reader(size="M", name="name bigger than max")

        with self.assertRaises(FieldError) as exc:
            await reader.save()

        self.assertEqual(
            exc.exception.args[0],
            'The string entered is bigger than the "max_length" defined (15)',
        )

    async def test_choices_display(self):
        book = Book(content="hard cover")

        self.assertEqual(book.content_display(), "hard cover book")

    async def test_choices_content_not_in_choices(self):
        # choices defined as lists or tuples
        with self.assertRaises(FieldError) as exc:
            book = Book(content="telomero")
            await book.save()

        self.assertEqual(exc.exception.args[0], '"telomero" not in model choices')

    async def test_dictionary_choices_content_not_in_choices(self):
        # choices defined as dictionaries
        with self.assertRaises(FieldError) as exc:
            read = Reader(power="flower")
            await read.save()

        self.assertEqual(exc.exception.args[0], '"flower" not in model choices')

    async def test_default_callable(self):
        # when the fields with default value are not esecifically defined
        reader = Reader(size="M")

        await reader.save()

        # they get the default value
        self.assertEqual(reader.name, "pepito")
        self.assertEqual(reader.weight, 85)

    async def test_jsonfield_saving_dictionary(self):
        publisher = Publisher(name="Oliver", json={"last_name": "Gregory"})

        await publisher.save()

        self.assertEqual(publisher.json.__class__, dict)

    async def test_jsonfield_saving_list(self):
        publisher = Publisher(name="Oliver", json=["last_name", "Gregory"])

        await publisher.save()

        self.assertEqual(publisher.json.__class__, list)

    async def test_jsonfield_saving_wrong_string(self):
        # you can also save an string as json
        publisher = Publisher(name="Oliver", json='{"last_name": "Gregory", 67: 6}')

        with self.assertRaises(FieldError) as exc:
            await publisher.save()

        self.assertEqual(
            exc.exception.args[0], "The data entered can not be converted to json"
        )

    async def test_jsonfield_saving_over_max_length(self):
        # if not bigger than max_length
        publisher = Publisher(
            name="Oliver",
            json='{"last_name": "Gregory", "67": 6, "totorota": "of course"}',
        )

        with self.assertRaises(FieldError) as exc:
            await publisher.save()

        self.assertEqual(
            exc.exception.args[0],
            'The string entered is bigger than the "max_length" defined (50)',
        )

    async def test_jsonfield_correct_format(self):
        # only if its correctly formated
        publisher = Publisher(name="Oliver", json={"last_name": "Gregory", "67": 6})

        await publisher.save()

        self.assertEqual(publisher.json["last_name"], "Gregory")
        self.assertEqual(publisher.json["67"], 6)

    async def test_booleanfield_validate(self):
        models.BooleanField(default=False).validate(True)

    async def test_booleanfield_validate_wrong_value(self):
        with self.assertRaises(FieldError) as exc:
            models.BooleanField(default=False).validate("laadio@svgvgvcom")

        self.assertEqual(
            "laadio@svgvgvcom is a wrong datatype for field BooleanField",
            exc.exception.args[0],
        )

    async def test_booleanfield_correct(self):
        org = await Organization.objects.create(**{"name": "chapulin", "active": True})

        self.assertTrue(org.active)

    def test_emailfield_no_domain_period(self):
        models.EmailField(max_length=35).validate("laadio@s.com")

        with self.assertRaises(FieldError) as exc:
            models.EmailField(max_length=35).validate("laadio@svgvgvcom")

        self.assertTrue("not a valid email address" in exc.exception.args[0])

    def test_emailfield_wrong_starting_char(self):
        with self.assertRaises(FieldError) as exc:
            models.EmailField(max_length=35).validate("@laadio@svgvgv.com")

        self.assertTrue("not a valid email address" in exc.exception.args[0])

    def test_emailfield_wrong_starting_char_2(self):
        with self.assertRaises(FieldError) as exc:
            models.EmailField(max_length=35).validate(".laadio@svgv@gv.com")

        self.assertTrue("not a valid email address" in exc.exception.args[0])

    def test_emailfield_wrong_starting_char_3(self):
        with self.assertRaises(FieldError) as exc:
            models.EmailField(max_length=35).validate("_laadio@svgv@gv.com")

        self.assertTrue("not a valid email address" in exc.exception.args[0])

    def test_emailfield_too_many_ats(self):
        with self.assertRaises(FieldError) as exc:
            models.EmailField(max_length=35).validate("laadio@svgv@gv.com")

        self.assertTrue("not a valid email address" in exc.exception.args[0])

    def test_emailfield_correct(self):
        self.assertEqual(
            models.EmailField(max_length=35).validate("laadio@s.com"), None
        )

    async def test_datetimefield_correct(self):
        org = await Organization.objects.create(
            date=datetime.now(), name="nonameneeded"
        )

        self.assertTrue(isinstance(org.date, datetime))

    async def test_datefield_correct(self):
        appmnt = await Appointment.objects.create(
            date=date.today(), name="nonameneeded"
        )

        self.assertTrue(isinstance(appmnt.date, date))

    async def test_timefield_correct(self):
        appmnt = await Appointment.objects.create(
            date=date.today(), time=datetime.now().timetz(), name="nonameneeded2"
        )

        self.assertTrue(isinstance(appmnt.time, time))

    async def test_uuidv1field_correct(self):
        org = await Organization.objects.create(name="nonamen22")

        self.assertTrue(isinstance(org.uuid, UUID))
        self.assertEqual(len(str(org.uuid).split("-")), 5)
        self.assertTrue(len(str(org.uuid)), 36)

    async def test_uuidv4field_correct(self):
        appmnt = await Appointment.objects.create(
            date=date.today(), time=datetime.now().timetz(), name="nonam34"
        )

        self.assertTrue(isinstance(appmnt.uuid, UUID))
        self.assertEqual(len(str(appmnt.uuid).split("-")), 5)
        self.assertEqual(len(str(appmnt.uuid)), 36)

    async def test_uuidv4field(self):
        with self.assertRaises(FieldError) as exc:
            models.Uuid4Field(uuid_type="mn")

        self.assertEqual(
            exc.exception.args[0], "{} is not a recognized type".format("mn")
        )

    async def test_arrayfield_correct(self):
        dev = Developer(name="oldscholl", age=38)
        await dev.save()
        skill = await Skill.objects.create(
            dev=dev.id, name="Python", specialization=["backend", "frontend"]
        )

        self.assertIsInstance(skill.specialization, list)
        self.assertIn("backend", skill.specialization)
        self.assertIn("frontend", skill.specialization)
        self.assertEqual(2, len(skill.specialization))

    async def test_arrayfield_multidimensional(self):
        dev = Developer(name="multitalent", age=22)
        await dev.save()

        skill = await Skill.objects.create(
            dev=dev.id,
            name="Rust",
            specialization=[["backend", "web"], ["sql", "postgres"]],
        )

        self.assertIsInstance(skill.specialization, list)
        self.assertIsInstance(skill.specialization[0], list)
        self.assertIn("backend", skill.specialization[0])
        self.assertIn("web", skill.specialization[0])
        self.assertIn("sql", skill.specialization[1])
        self.assertIn("postgres", skill.specialization[1])

    async def test_arrayfield_wrong_dimensions_size(self):
        with self.assertRaises(FieldError) as exc:
            models.ArrayField().validate([["backend", "nodejs"], ["frontend"]])

        self.assertEqual(
            exc.exception.args[0],
            "Multi-dimensional arrays must have items of the same size",
        )

    async def test_arrayfield_wrong_dimensions_type(self):
        with self.assertRaises(FieldError) as exc:
            models.ArrayField().validate([["backend", "nodejs"], "frontend"])

        self.assertEqual(
            exc.exception.args[0], "Array elements are not of the same type"
        )

    async def test_arrayfield_empty_array(self):
        dev = Developer(name="walkie", age=43)
        await dev.save()

        skill = await Skill.objects.create(dev=dev.id, name="C/CPP", specialization=[])

        self.assertIsInstance(skill.specialization, list)
        self.assertEqual(skill.specialization, [])

    async def test_textfield_correct(self):
        dev = Developer(name="talkie", age=33)
        await dev.save()

        skill = await Skill.objects.create(
            dev=dev.id,
            name="Ruby",
            specialization=["Rails"],
            notes="Wish I could help you developing something cool",
        )

        self.assertIsInstance(skill.notes, str)

    async def test_check_all_indices_were_created(self):
        for m in (
            Book,
            Publisher,
            Reader,
            Author,
            Organization,
            Client,
            Appointment,
            Skill,
            Developer,
        ):
            for field in m.fields.values():
                if field.db_index:
                    field_index = "idx_{}_{}".format(
                        field.table_name, field.orm_field_name
                    ).lower()[:30]
                    self.assertTrue(
                        await Developer.objects.db_manager.request(
                            "SELECT * FROM pg_indexes WHERE indexname = '{}'".format(
                                field_index
                            )
                        )
                    )

    async def test_model_with_macadressfield_field_ok(self):
        mac = "00-1B-77-49-54-FD"
        pub = Publisher(name="Linda", json={"last_name": "Olson"}, mac=mac)
        await pub.save()

        # diferent dialects
        self.assertNotEqual(pub.mac, mac)
        # equal when converted on same dialect
        self.assertEqual(str(EUI(pub.mac, dialect=mac_eui48)), mac)
        # equal before representation
        self.assertEqual(EUI(pub.mac), EUI(mac))

    async def test_model_with_macadressfield_field_error(self):
        with self.assertRaises(FieldError) as exc:
            pub = Publisher(
                name="Linda", json={"last_name": "Olson"}, mac="00-1B-77-49-54"
            )
            await pub.save()

        self.assertEqual(exc.exception.args[0], "Not a correct MAC address")

    def test_macadressfield_field_validation_error(self):
        dialect = "wrong"
        with self.assertRaises(FieldError) as exc:
            models.MACAdressField(dialect=dialect)

        self.assertEqual(
            exc.exception.args[0], '"{}" is not a correct mac dialect'.format(dialect)
        )

    def test_macadressfield_field_ok(self):
        models.MACAdressField().validate("00-1B-77-49-54-FD")

    def test_macadressfield_field_error(self):
        with self.assertRaises(FieldError) as exc:
            models.MACAdressField().validate("00-1B-77-49-54")

        self.assertEqual(exc.exception.args[0], "Not a correct MAC address")

    def test_genericipaddressfield_validation_ipv4_error(self):
        with self.assertRaises(FieldError) as exc:
            models.GenericIPAddressField(protocol="ipv4", unpack_protocol="ipv4")

        self.assertEqual(
            exc.exception.args[0],
            "if the protocol is restricted the output will always be in the same protocol version, "
            'so unpack_protocol should be default value, "same"',
        )

    def test_genericipaddressfield_validation_protocol_error_option(self):
        protocol = "ipv9"
        with self.assertRaises(FieldError) as exc:
            models.GenericIPAddressField(protocol=protocol)

        self.assertEqual(
            exc.exception.args[0], '"{}" is not a recognized protocol'.format(protocol)
        )

    def test_genericipaddressfield_validation_unpack_protocol_error_option(self):
        unpack_protocol = "ipv9"
        with self.assertRaises(FieldError) as exc:
            models.GenericIPAddressField(unpack_protocol=unpack_protocol)

        self.assertEqual(
            exc.exception.args[0],
            '"{}" is not a recognized unpack_protocol'.format(unpack_protocol),
        )

    def test_genericipaddressfield_validation_protocol_correct_options(self):
        protocol = ("both", "ipv4", "ipv6")
        for prot in protocol:
            models.GenericIPAddressField(protocol=prot)

    def test_genericipaddressfield_validation_unpack_protocol_correct_options(self):
        unpack_protocol = ("same", "ipv4", "ipv6")
        for prot in unpack_protocol:
            models.GenericIPAddressField(unpack_protocol=prot)

    def test_genericipaddressfield_validation_ipv6_error(self):
        with self.assertRaises(FieldError) as exc:
            models.GenericIPAddressField(protocol="ipv6", unpack_protocol="ipv4")

        self.assertEqual(
            exc.exception.args[0],
            "if the protocol is restricted the output will always be in the same protocol version, "
            'so unpack_protocol should be default value, "same"',
        )

    def test_genericipaddressfield_validation_ok(self):
        models.GenericIPAddressField(protocol="ipv6", unpack_protocol="same")

    async def test_model_with_genericipaddressfield_ok(self):
        pub = Publisher(name="Linda", json={"last_name": "Olson"}, inet="1.1.1.1")
        await pub.save()

    async def test_model_with_genericipaddressfield_error(self):
        with self.assertRaises(FieldError) as exc:
            pub = Publisher(name="Linda", json={"last_name": "Olson"}, inet="300.3.3.3")
            await pub.save()

        self.assertEqual(exc.exception.args[0], "Not a correct IP address")

    async def test_model_with_genericipaddressfield_unpack(self):
        ip = "::ffff:1.2.3.0/120"
        pub = Publisher(name="Linda", json={"last_name": "Olson"}, inet=ip)

        await pub.save()

        self.assertNotEqual(pub.inet, ip)
        self.assertEqual(pub.inet, "1.2.3.0/24")
        self.assertEqual(pub.inet, str(IPNetwork(ip).ipv4()))

    def test_genericipaddressfield_ok(self):
        correct_formats = (
            "192.168.100.128/25",
            "192.168/24",
            "192.168/25",
            "192.168.1",
            "192.168",
            "128.1",
            "128",
            "128.1.2",
            "10.1.2",
            "10.1",
            "10",
            "10.1.2.3/32",
            "2001:4f8:3:ba::/64",
            "2001:4f8:3:ba:2e0:81ff:fe22:d1f1/128",
            "::ffff:1.2.3.0/120",
            "::ffff:1.2.3.0/128",
        )

        for ip_address in correct_formats:
            models.GenericIPAddressField().validate(ip_address)

    def test_genericipaddressfield_ok_ipv4(self):
        correct_formats = (
            "192.168.100.128/25",
            "192.168/24",
            "192.168/25",
            "192.168.1",
            "192.168",
            "128.1",
            "128",
            "128.1.2",
            "10.1.2",
            "10.1",
            "10",
            "10.1.2.3/32",
        )

        for ip_address in correct_formats:
            models.GenericIPAddressField(protocol="ipv4").validate(ip_address)

    def test_genericipaddressfield_ok_ipv6(self):
        correct_formats = (
            "2001:4f8:3:ba::/64",
            "2001:4f8:3:ba:2e0:81ff:fe22:d1f1/128",
            "::ffff:1.2.3.0/120",
            "::ffff:1.2.3.0/128",
        )

        for ip_address in correct_formats:
            models.GenericIPAddressField(protocol="ipv6").validate(ip_address)

    def test_genericipaddressfield_ipv4_error(self):
        value = "::ffff:1.2.3.0/128"
        protocol = "ipv4"
        with self.assertRaises(FieldError) as exc:
            models.GenericIPAddressField(protocol=protocol).validate(value)

        self.assertEqual(
            exc.exception.args[0],
            "{} is not a correct {} IP address".format(value, protocol),
        )

    def test_genericipaddressfield_ipv6_error(self):
        value = "1.1.1.1"
        protocol = "ipv6"
        with self.assertRaises(FieldError) as exc:
            models.GenericIPAddressField(protocol=protocol).validate(value)

        self.assertEqual(
            exc.exception.args[0],
            "{} is not a correct {} IP address".format(value, protocol),
        )

    def test_genericipaddressfield_error(self):
        with self.assertRaises(FieldError) as exc:
            models.GenericIPAddressField().validate("1.1.1.1000")

        self.assertEqual(exc.exception.args[0], "Not a correct IP address")

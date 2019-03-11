from datetime import date, datetime, time
from uuid import UUID

import pytest
from astroid.node_classes import Assert
from netaddr import EUI, IPNetwork, mac_eui48

from asyncorm import models
from asyncorm.exceptions import AsyncormException, AsyncOrmFieldError
from tests.app_1.models import Author, Book, Publisher, Reader
from tests.app_2.models import Appointment, Client, Developer, Organization, Skill
from tests.conftest import event_loop, orm_setup
from tests.helper_tests import AioTestCase

pytestmark = pytest.mark.integration


def test_class_definition(orm_setup, event_loop):
    with pytest.raises(NotImplementedError) as exc:
        models.Field()

    assert 'Missing "internal_type" attribute from class definition' in str(exc)


def test_required_kwargs_not_sent(orm_setup, event_loop):
    with pytest.raises(AsyncOrmFieldError) as exc:
        models.CharField()

    assert '"CharField" field requires max_length' in str(exc)


def test_required_kwargs_wrong_value(orm_setup, event_loop):
    with pytest.raises(AsyncOrmFieldError) as exc:
        models.CharField(max_length="gt")

    assert "Wrong value for max_length" in str(exc)


def test_now_correcly_valuates(orm_setup, event_loop):
    assert models.CharField(max_length=45)


def test_db_column_validation_wrong_start(orm_setup, event_loop):
    with pytest.raises(AsyncOrmFieldError) as exc:
        models.CharField(max_length=35, db_column="_oneone")

    assert 'db_column can not start with "_"' in str(exc)


def test_db_column_validation_wrong_ending(orm_setup, event_loop):
    with pytest.raises(AsyncOrmFieldError) as exc:
        models.CharField(max_length=35, db_column="oneone_")

    assert 'db_column can not end with "_"' in str(exc)


def test_db_column_validation_wrong_characters(orm_setup, event_loop):
    with pytest.raises(AsyncOrmFieldError) as exc:
        models.CharField(max_length=35, db_column="one__one")

    assert 'db_column can not contain "__"' in str(exc)


def test_db_column_correctly_validates(orm_setup, event_loop):
    # this is an allowed fieldname
    assert models.CharField(max_length=35, db_column="one_one")


@pytest.mark.asyncio
async def test_field_max_length(orm_setup, event_loop):
    reader = Reader(size="M", name="name bigger than max")

    with pytest.raises(AsyncOrmFieldError) as exc:
        await reader.save()

    assert 'The string entered is bigger than the "max_length" defined (15)' in str(exc)


@pytest.mark.asyncio
async def test_choices_display(orm_setup, event_loop):
    book = Book(content="hard cover")

    assert book.content_display() == "hard cover book"


@pytest.mark.asyncio
async def test_choices_content_not_in_choices(orm_setup, event_loop):
    # choices defined as lists or tuples
    with pytest.raises(AsyncOrmFieldError) as exc:
        book = Book(content="telomero")
        await book.save()

    assert '"telomero" not in field choices' in str(exc)


@pytest.mark.asyncio
async def test_dictionary_choices_content_not_in_choices(orm_setup, event_loop):
    # choices defined as dictionaries
    with pytest.raises(AsyncOrmFieldError) as exc:
        read = Reader(power="flower")
        await read.save()

    assert '"flower" not in field choices' in str(exc)


@pytest.mark.asyncio
async def test_default_callable(orm_setup, event_loop):
    # when the fields with default value are not esecifically defined
    reader = Reader(size="M")

    await reader.save()

    # they get the default value
    assert reader.name == "pepito"
    assert reader.weight == 85


@pytest.mark.asyncio
async def test_jsonfield_saving_dictionary(orm_setup, event_loop):
    publisher = Publisher(name="Oliver", json={"last_name": "Gregory"})

    await publisher.save()

    assert isinstance(publisher.json, dict)


@pytest.mark.asyncio
async def test_jsonfield_saving_list(orm_setup, event_loop):
    publisher = Publisher(name="Oliver", json=["last_name", "Gregory"])

    await publisher.save()

    assert isinstance(publisher.json, dict)


@pytest.mark.asyncio
async def test_jsonfield_saving_wrong_string(orm_setup, event_loop):
    # you can also save an string as json
    publisher = Publisher(name="Oliver", json='{"last_name": "Gregory", 67: 6}')

    with pytest.raises(AsyncOrmFieldError) as exc:
        await publisher.save()

    assert "The data entered can not be converted to json" in str(exc)


@pytest.mark.asyncio
async def test_jsonfield_saving_over_max_length(orm_setup, event_loop):
    # if not bigger than max_length
    publisher = Publisher(name="Oliver", json='{"last_name": "Gregory", "67": 6, "totorota": "of course"}')

    with pytest.raises(AsyncOrmFieldError) as exc:
        await publisher.save()

    assert 'The string entered is bigger than the "max_length" defined (50)' in str(exc)


@pytest.mark.asyncio
async def test_jsonfield_correct_format(orm_setup, event_loop):
    # only if its correctly formated
    publisher = Publisher(name="Oliver", json={"last_name": "Gregory", "67": 6})

    await publisher.save()

    assert publisher.json["last_name"] == "Gregory"
    assert publisher.json["67"] == 6


@pytest.mark.asyncio
async def test_booleanfield_validate(orm_setup, event_loop):
    models.BooleanField(default=False).validate(True)


@pytest.mark.asyncio
async def test_booleanfield_validate_wrong_value(orm_setup, event_loop):
    with pytest.raises(AsyncOrmFieldError) as exc:
        models.BooleanField(default=False).validate("laadio@svgvgvcom")

    assert "laadio@svgvgvcom is a wrong datatype for field BooleanField" in str(exc)


@pytest.mark.asyncio
async def test_booleanfield_correct(orm_setup, event_loop):
    org = await Organization.objects.create(**{"name": "chapulin", "active": True})

    assert org.active is True


def test_emailfield_no_domain_period(orm_setup, event_loop):
    models.EmailField(max_length=35).validate("laadio@s.com")

    with pytest.raises(AsyncOrmFieldError) as exc:
        models.EmailField(max_length=35).validate("laadio@svgvgvcom")

    assert "not a valid email address" in str(exc)


def test_emailfield_wrong_starting_char(orm_setup, event_loop):
    with pytest.raises(AsyncOrmFieldError) as exc:
        models.EmailField(max_length=35).validate("@laadio@svgvgv.com")

    assert "not a valid email address" in str(exc)


def test_emailfield_wrong_starting_char_2(orm_setup, event_loop):
    with pytest.raises(AsyncOrmFieldError) as exc:
        models.EmailField(max_length=35).validate(".laadio@svgv@gv.com")

    assert "not a valid email address" in str(exc)


def test_emailfield_wrong_starting_char_3(orm_setup, event_loop):
    with pytest.raises(AsyncOrmFieldError) as exc:
        models.EmailField(max_length=35).validate("_laadio@svgv@gv.com")

    assert "not a valid email address" in str(exc)


def test_emailfield_too_many_ats(orm_setup, event_loop):
    with pytest.raises(AsyncOrmFieldError) as exc:
        models.EmailField(max_length=35).validate("laadio@svgv@gv.com")

    assert "not a valid email address" in str(exc)


def test_emailfield_correct(orm_setup, event_loop):
    assert models.EmailField(max_length=35).validate("laadio@s.com") is None


@pytest.mark.asyncio
async def test_datetimefield_correct(orm_setup, event_loop):
    org = await Organization.objects.create(date=datetime.now(), name="nonameneeded")

    assert isinstance(org.date, datetime)


@pytest.mark.asyncio
async def test_datefield_correct(orm_setup, event_loop):
    appmnt = await Appointment.objects.create(date=date.today(), name="nonameneeded")

    assert isinstance(appmnt.date, date)


@pytest.mark.asyncio
async def test_timefield_correct(orm_setup, event_loop):
    appmnt = await Appointment.objects.create(date=date.today(), time=datetime.now().timetz(), name="nonameneeded2")

    assert isinstance(appmnt.time, time)


@pytest.mark.asyncio
async def test_uuidv1field_correct(orm_setup, event_loop):
    org = await Organization.objects.create(name="nonamen22")

    assert isinstance(org.uuid, UUID)
    assert len(str(org.uuid).split("-")) == 5
    assert len(str(org.uuid)) == 36


@pytest.mark.asyncio
async def test_uuidv4field_correct(orm_setup, event_loop):
    appmnt = await Appointment.objects.create(date=date.today(), time=datetime.now().timetz(), name="nonam34")

    assert isinstance(appmnt.uuid, UUID)
    assert len(str(appmnt.uuid).split("-")) == 5
    assert len(str(appmnt.uuid)) == 36


@pytest.mark.asyncio
async def test_uuidv4field(orm_setup, event_loop):
    with pytest.raises(AsyncOrmFieldError) as exc:
        models.Uuid4Field(uuid_type="mn")

    assert "{} is not a recognized type".format("mn") in str(exc)


@pytest.mark.asyncio
async def test_arrayfield_correct(orm_setup, event_loop):
    dev = Developer(name="oldscholl", age=38)
    await dev.save()

    skill = await Skill.objects.create(dev=dev.id, name="Python", specialization=["backend", "frontend"])

    assert isinstance(skill.specialization, list)
    assert "backend" in skill.specialization
    assert "frontend" in skill.specialization
    assert 2 == len(skill.specialization)


@pytest.mark.asyncio
async def test_arrayfield_multidimensional(orm_setup, event_loop):
    dev = Developer(name="multitalent", age=22)
    await dev.save()

    skill = await Skill.objects.create(
        dev=dev.id, name="Rust", specialization=[["backend", "web"], ["sql", "postgres"]]
    )

    assert isinstance(skill.specialization, list)
    assert isinstance(skill.specialization[0], list)
    assert "backend" in skill.specialization[0]
    assert "web" in skill.specialization[0]
    assert "sql" in skill.specialization[1]
    assert "postgres" in skill.specialization[1]


@pytest.mark.asyncio
async def test_arrayfield_wrong_dimensions_size(orm_setup, event_loop):
    with pytest.raises(AsyncOrmFieldError) as exc:
        models.ArrayField().validate([["backend", "nodejs"], ["frontend"]])

    assert "Multi-dimensional arrays must have items of the same size" in str(exc)


@pytest.mark.asyncio
async def test_arrayfield_wrong_dimensions_type(orm_setup, event_loop):
    with pytest.raises(AsyncOrmFieldError) as exc:
        models.ArrayField().validate([["backend", "nodejs"], "frontend"])

    assert str(exc) == "Array elements are not of the same type"


@pytest.mark.asyncio
async def test_arrayfield_empty_array(orm_setup, event_loop):
    dev = Developer(name="walkie", age=43)
    await dev.save()

    skill = await Skill.objects.create(dev=dev.id, name="C/CPP", specialization=[])

    assert isinstance(skill.specialization, list)
    assert skill.specialization == []


@pytest.mark.asyncio
async def test_textfield_correct(orm_setup, event_loop):
    dev = Developer(name="talkie", age=33)
    await dev.save()

    skill = await Skill.objects.create(
        dev=dev.id, name="Ruby", specialization=["Rails"], notes="Wish I could help you developing something cool"
    )

    assert isinstance(skill.notes, str)


@pytest.mark.asyncio
async def test_check_all_indices_were_created(orm_setup, event_loop):
    for m in (Book, Publisher, Reader, Author, Organization, Client, Appointment, Skill, Developer):
        for field in m.fields.values():
            if field.db_index:
                field_index = "idx_{}_{}".format(field.table_name, field.orm_field_name).lower()[:30]
                assert await Developer.objects.db_backend.request(
                    "SELECT * FROM pg_indexes WHERE indexname = '{}'".format(field_index)
                )


@pytest.mark.asyncio
async def test_model_with_macadressfield_field_ok(orm_setup, event_loop):
    mac = "00-1B-77-49-54-F6"
    # remove existing
    previous = await Publisher.objects.get(mac=mac)
    await previous.delete()

    pub = await Publisher(name="Linda", json={"last_name": "Olson"}, mac=mac).save()

    assert pub.mac != mac
    assert str(EUI(pub.mac, dialect=mac_eui48)) == mac
    assert EUI(pub.mac) == EUI(mac)


@pytest.mark.asyncio
async def test_model_with_macadressfield_field_error(orm_setup, event_loop):
    with pytest.raises(AsyncOrmFieldError) as exc:
        pub = Publisher(name="Linda", json={"last_name": "Olson"}, mac="00-1B-77-49-54")
        await pub.save()

    assert "Not a correct MAC address" in str(exc)


def test_macadressfield_field_validation_error(orm_setup, event_loop):
    dialect = "wrong"
    with pytest.raises(AsyncOrmFieldError) as exc:
        models.MACAdressField(dialect=dialect)

    assert '"{}" is not a correct mac dialect'.format(dialect) in str(exc)


def test_macadressfield_field_ok(orm_setup, event_loop):
    try:
        models.MACAdressField().validate("00-1B-77-49-54-FD")
    except AsyncOrmFieldError:
        pytest.fail("unexpectedly exception raised!")


def test_macadressfield_field_error(orm_setup, event_loop):
    with pytest.raises(AsyncOrmFieldError) as exc:
        models.MACAdressField().validate("00-1B-77-49-54")

    assert "Not a correct MAC address" in str(exc)


def test_genericipaddressfield_validation_ipv4_error(orm_setup, event_loop):
    with pytest.raises(AsyncOrmFieldError) as exc:
        models.GenericIPAddressField(protocol="ipv4", unpack_protocol="ipv4")

    assert (
        "if the protocol is restricted the output will always be in the same protocol version, "
        'so unpack_protocol should be default value, "same"' in str(exc)
    )


def test_genericipaddressfield_validation_protocol_error_option(orm_setup, event_loop):
    protocol = "ipv9"
    with pytest.raises(AsyncOrmFieldError) as exc:
        models.GenericIPAddressField(protocol=protocol)

    assert '"{}" is not a recognized protocol'.format(protocol) in str(exc)


def test_genericipaddressfield_validation_unpack_protocol_error_option(orm_setup, event_loop):
    unpack_protocol = "ipv9"
    with pytest.raises(AsyncOrmFieldError) as exc:
        models.GenericIPAddressField(unpack_protocol=unpack_protocol)

    assert '"{}" is not a recognized unpack_protocol'.format(unpack_protocol) in str(exc)


def test_genericipaddressfield_validation_protocol_correct_options(orm_setup, event_loop):
    protocol = ("both", "ipv4", "ipv6")
    for prot in protocol:
        try:
            models.GenericIPAddressField(protocol=prot)
        except AsyncOrmFieldError:
            pytest.fail("Unexpectedly not recognized ip address")


def test_genericipaddressfield_validation_unpack_protocol_correct_options(orm_setup, event_loop):
    unpack_protocol = ("same", "ipv4", "ipv6")
    for prot in unpack_protocol:
        try:
            models.GenericIPAddressField(unpack_protocol=prot)
        except AsyncOrmFieldError:
            pytest.fail("Unexpectedly not a recognized protocol")


def test_genericipaddressfield_validation_ipv6_error(orm_setup, event_loop):
    with pytest.raises(AsyncOrmFieldError) as exc:
        models.GenericIPAddressField(protocol="ipv6", unpack_protocol="ipv4")

    assert (
        "if the protocol is restricted the output will always be in the same protocol version, "
        'so unpack_protocol should be default value, "same"' in str(exc)
    )


def test_genericipaddressfield_validation_ok(orm_setup, event_loop):
    try:
        models.GenericIPAddressField(protocol="ipv6", unpack_protocol="same")
    except AsyncOrmFieldError:
        pytest.fail("Unexpectedly not correctly matched")


@pytest.mark.asyncio
async def test_model_with_genericipaddressfield_ok(orm_setup, event_loop):
    try:
        pub = Publisher(name="Linda", json={"last_name": "Olson"}, inet="1.1.1.1")
        await pub.save()
    except AsyncormException:
        pytest.fail("Unexpectedly could not save.")


@pytest.mark.asyncio
async def test_model_with_genericipaddressfield_error(orm_setup, event_loop):
    with pytest.raises(AsyncOrmFieldError) as exc:
        pub = Publisher(name="Linda", json={"last_name": "Olson"}, inet="300.3.3.3")
        await pub.save()

    assert "Not a correct IP address" in str(exc)


@pytest.mark.asyncio
async def test_model_with_genericipaddressfield_unpack(orm_setup, event_loop):
    ip = "::ffff:1.2.3.0/120"
    pub = Publisher(name="Linda", json={"last_name": "Olson"}, inet=ip)

    await pub.save()

    assert pub.inet != ip
    assert pub.inet == "1.2.3.0/24"
    assert pub.inet == str(IPNetwork(ip).ipv4())


def test_genericipaddressfield_ok(orm_setup, event_loop):
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
        try:
            models.GenericIPAddressField().validate(ip_address)
        except AsyncOrmFieldError:
            pytest.fail("unexpectedly not valid IP address")


def test_genericipaddressfield_ok_ipv4(orm_setup, event_loop):
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
        try:
            models.GenericIPAddressField(protocol="ipv4").validate(ip_address)
        except AsyncOrmFieldError:
            pytest.fail("unexpectedly not valid IP address")


def test_genericipaddressfield_ok_ipv6(orm_setup, event_loop):
    correct_formats = (
        "2001:4f8:3:ba::/64",
        "2001:4f8:3:ba:2e0:81ff:fe22:d1f1/128",
        "::ffff:1.2.3.0/120",
        "::ffff:1.2.3.0/128",
    )

    for ip_address in correct_formats:
        try:
            models.GenericIPAddressField(protocol="ipv6").validate(ip_address)
        except AsyncOrmFieldError:
            pytest.fail("Unexpectedly not a correct format")


def test_genericipaddressfield_ipv4_error(orm_setup, event_loop):
    value = "::ffff:1.2.3.0/64"
    protocol = "ipv4"
    with pytest.raises(AsyncOrmFieldError) as exc:
        models.GenericIPAddressField(protocol=protocol).validate(value)

    assert "{} is not a correct {} IP address".format(value, protocol) in str(exc)


def test_genericipaddressfield_ipv6_error(orm_setup, event_loop):
    value = "1.1.1.1"
    protocol = "ipv6"
    with pytest.raises(AsyncOrmFieldError) as exc:
        models.GenericIPAddressField(protocol=protocol).validate(value)

    assert "{} is not a correct {} IP address".format(value, protocol) in str(exc)


def test_genericipaddressfield_error(orm_setup, event_loop):
    with pytest.raises(AsyncOrmFieldError) as exc:
        models.GenericIPAddressField().validate("1.1.1.1000")

    assert "Not a correct IP address" in str(exc)

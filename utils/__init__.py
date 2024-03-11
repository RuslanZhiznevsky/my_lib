from django.db.models.fields import CharField, TextField, EmailField
from django.core.exceptions import ValidationError

from sys import _getframe


class ModelTestUtils():
    '''Adds functions to TestCase to achieve DRY

    To work with this add-on class
    define default_obj(usually inside setUpTestData).
    It represents model object that is correctrly initialized(valid).
    Its fields shouldn't change during testing.
    '''
    ATTRIBS_TO_UNDERSOCRE = ["related_name"]
    ATTRIBS_TO_CALL = ["related_query_name"]

    STRING_FIELDS = (CharField, TextField, EmailField)

    class assertNotRaises():
        '''Is like TestCase.assertRaises, but checks that code inside
        "with assertNotRaises:" does not raise expected exception.

        Used by calling "with" statement.

        If any other exception occures, it is just raised and test returns an
        error.'''

        def __init__(self, expected_exc):
            self.expected_exc = expected_exc

        def __enter__(self):
            return self.expected_exc

        def __exit__(self, exc_type, exc_value, exc_traceback):
            if exc_type is None:
                return
            elif isinstance(exc_type, type(self.expected_exc)):
                assert False, f"{self.expected_exc} was raised.\n{exc_value}"

    def field_meta_attrib_eq(self, q):
        '''Compares field meta attribute to q. Field and meta attribute names
        are retrieved from outer function name, which should be like:

        test_<field_name>__<meta_attrib_name>

        q is any object, usually string
        '''
        outer_func_name = _getframe(1).f_code.co_name

        field, attrib = outer_func_name.removeprefix("test_").split("__")

        obj = self.__getattribute__("default_obj")
        field = obj._meta.get_field(field)
        if attrib in self.ATTRIBS_TO_UNDERSOCRE:
            attrib = f"_{attrib}"

        meta_attrib = field.__getattribute__(attrib)

        if attrib in self.ATTRIBS_TO_CALL:
            meta_attrib = meta_attrib()

        self.assertEqual(first=meta_attrib, second=q)

    @staticmethod
    def _is_blank_and_null_true(field):
        return field.null is True and field.blank is True

    def test_modelobj_string_fields_have_blank_and_null_true(self):
        '''Assert that there are NO blank=True and null=True on the fields that
        are in STRING_FIELDS

        This function starts with test_... so django will automaticly find and
        call it when running tests
        '''
        for field in self.__getattribute__("default_obj")._meta.fields:
            if isinstance(field, self.STRING_FIELDS):
                self.assertFalse(
                    self._is_blank_and_null_true(field),
                    f"{field} model field has blank=True and null=True",
                )

    def _test_max_length(self, unsaved_obj, field_name, length):
        '''Tests longest option of string, which should succeed
        and an one over option, which should fail

        unsaved_obj is a Model object that has not yet been saved to db.
        field_name is this object's string field name
        for which the length will be tested
        '''

        # check string that is too long
        with self.assertRaises(ValidationError):
            unsaved_obj.__dict__[field_name] = (length+1) * "z"
            unsaved_obj.full_clean()

        # check the longest possible string
        with self.assertNotRaises(ValidationError):
            unsaved_obj.__dict__[field_name] = length * "z"
            unsaved_obj.full_clean()

    def test_max_lengths(self):
        '''Tests Field.max_length attribute for all the fields of the model
        on wich this test case will be performed.

        TestCase class should have an "unsaved_obj" attribute. Unsaved_obj is
        a model instance on wich model tests are being performed.

        TestCase class should also have "max_lengths" dict with field names
        of the model and their corresponding max_length.

        If one or both attributes are missing this test will not run
        '''

        try:
            max_lengths = self.__getattribute__("max_lengths")
            unsaved_obj = self.__getattribute__("unsaved_obj")
        except AttributeError:
            return

        for field, max_length in max_lengths.items():
            self._test_max_length(
                unsaved_obj=unsaved_obj,
                field_name=field,
                length=max_length
            )

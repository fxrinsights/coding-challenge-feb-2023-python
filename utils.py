import random
import string


def get_name_parser(component_keys, separator="_"):
    """
    factory to get a method which extracts components from a name string.
    """

    def parse_name(name):
        return dict(
            zip(
                component_keys,
                str(name).split(separator),
            )
        )

    return parse_name


def get_name_formatter(component_keys, schematic, separator="_"):
    """
    factory to get a method which formats name components into a string.
    """

    def format_name(obj={}, forced_components={}, **kwargs):
        # we allow user to either pass the object in as the first argument, or
        # as kwargs, and we merge these; on top of that come the
        # forced_components.
        components_raw = {**obj, **kwargs, **forced_components}

        # validate and convert the components
        components = schematic.validate(components_raw)

        # turn into a string
        return separator.join(
            [components[component] for component in component_keys]
        )

    return format_name


def get_random_alphanumeric_string(length):
    """
    Generate a random alphanumeric string of the given length
    """
    return "".join(
        random.choice(
            string.ascii_lowercase + string.ascii_uppercase + string.digits
        )
        for _ in range(length)
    )

import pandas as pd


class BaseNamer(object):
    """
    abstract implementation for a namer which can both parse structured names
    and format name components, for any name which is composed out of multiple
    components.

    example usage::

        In [1]: DirectoryNamer('active_22ghosts_...').components
        Out[1]: { 'status': 'active', 'client_slug': '22ghosts', ... }
        In [2]: DirectoryNamer({ 'status': 'archived', ... }).name
        Out[2]: 'archived_...'

    a child implementation needs to set the following attributes:

        - cls._schematic: the schema.Schema which validates a dict of
          components.

        - cls.component_keys: a list of the keys of the components.

        - self._name_parser (as @property): the function which takes a name
          string and returns the extracted components dict.

        - self._name_formatter (as @property): the function which takes a
          components dict and returns the correct name string.
    """

    _forced_components = {}

    def _validate_required_attrs_on_child_implementation(self):
        """
        validates whether the child implementation (in the code) has set the
        correct attributes.
        """
        for attr in [
            "_schematic",
            "component_keys",
            "_name_parser",
            "_name_formatter",
        ]:
            if not hasattr(self, attr):
                raise NotImplementedError(
                    "the child implementation of BaseNamer you "
                    "are trying to use has not set the required attribute "
                    f"{attr}."
                )

    def __init__(self, name_or_components, skip_forced_components=False):
        """
        initialize the namer class with an arg which holds the information
        about the name to be formatted or parsed.

        :param name_or_components: either the name as a string, or the
            dictionary of the components of the name.
        :param skip_forced_components: if True, self._forced_components are not
            taken into account when formatting components, which should only be
            enabled if you explicitly need to circumvent this behaviour
            (default: False).
        """
        self._validate_required_attrs_on_child_implementation()
        self._skip_forced_components = skip_forced_components

        if isinstance(name_or_components, str):
            # if it's the name, we parse it to the components
            self._components = self._name_parser(name_or_components)
        elif isinstance(name_or_components, dict):
            # we only perform validation if it's the components, because this
            # performs necessary type conversions and you should only be able
            # to name something from valid components.
            self._components = self._schematic.validate(
                # here, forced_components are used as defaults so that
                # validation doesn't fail. however, we don't force them because
                # we should parse exactly what was given in init.
                {**self.forced_components, **name_or_components}
            )
        else:
            raise TypeError(
                "needs to be initialized with either the name as "
                "string, or a dict of the name components."
            )

    @property
    def forced_components(self):
        if self._skip_forced_components:
            return {}
        return self._forced_components

    @classmethod
    def rename(cls, name: str, components: dict):
        """
        rename the given name using the given (dict of) components.

        :returns: the new name, as a string.
        """
        dname = cls(name)
        dname.update(components)
        return dname.name

    @classmethod
    def format(cls, *args, **kwargs):
        """
        convenience method to immediately return the formatted name.

        params are equivalent to the initialization args of this class.

        :returns: the formatted name as a string.
        """
        return cls(*args, **kwargs).name

    @classmethod
    def parse(cls, *args, **kwargs):
        """
        convenience method to immediately return the parsed components.

        params are equivalent to the initialization args of this class.

        :returns: the parsed components dict.
        """
        return cls(*args, **kwargs).components

    @classmethod
    def format_components_df(
        cls,
        components_df,
        default_components={},
        existing_column_prefix=None,
        **kwargs,
    ):
        """
        given a df whose columns are the various components, returns a series
        with the formatted name strings.

        each component key for this namer needs to be present either in the
        components_df.columns, in the default_components, or in the
        cls.forced_components.

        :param components_df: the df containing the name components as columns.
        :param default_components: default components to use for every row.
            will be overwritten by the components_df values.  default: {}.
        :param existing_column_prefix: if the df columns are prefixed with some
            common prefix (like when registering data from a manager), pass
            that prefix and this method will deal with it (default: None).
        """
        if existing_column_prefix is not None:
            # remove that prefix
            components_df = components_df.rename(
                columns={
                    f"{existing_column_prefix}{key}": key
                    for key in cls.component_keys
                }
            )

        forced_component_keys = (
            []
            if kwargs.get("skip_forced_components")
            else list(cls._forced_components.keys())
        )
        present_keys_in_components_df = [
            key for key in cls.component_keys if key in components_df
        ]
        present_component_keys = (
            present_keys_in_components_df
            + list(default_components.keys())
            + forced_component_keys
        )

        if (
            len(
                missing_keys := (
                    set(cls.component_keys) - set(present_component_keys)
                )
            )
            > 0
        ):
            raise ValueError(
                "the following keys are not specified in the df nor "
                "in the default_components: "
                f"{', '.join(missing_keys)}"
            )

        def _format_row(row):
            return cls.format(
                {**default_components, **row},
                **kwargs,
            )

        return components_df[
            present_keys_in_components_df
        ].fxr_utils.apply_rows_unique(_format_row)

    @classmethod
    def parse_names_series(cls, names, **kwargs):
        """
        parse all name strings in the given series (or list-like), and return a
        dataframe where each extracted component is a column.

        :param names: a pd.Series (or list-like) containing the name strings
            that should be parsed.

        :returns: a pd.DataFrame with the same index as `names`, where each
                  extracted component is a column.
        """
        if not isinstance(names, pd.Series):
            names = pd.Series(names)

        return pd.DataFrame(
            names.apply(cls.parse, **kwargs).tolist(),
            columns=cls.component_keys,
            index=names.index,
        )

    @property
    def components(self):
        """
        the name's components.
        """
        return self._components

    @property
    def name(self):
        """
        the formatted name string.
        """
        return self._name_formatter(
            self._components, forced_components=self.forced_components
        )

    def update(self, new_components_partial: dict):
        """
        update the current name components with the given updated dict.
        """
        # not using self._components.update because we want to validate the
        # full new dict
        new_components = {**self._components, **new_components_partial}
        self._components = self._schematic.validate(new_components)

    def __str__(self):
        return self.name

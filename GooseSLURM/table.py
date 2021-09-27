from . import rich


def print_long(lines):
    r"""
    Print full data without much formatting. The output looks as follows:

    .. code-block:: none

      +------------------+
      | line 1, column 1 |
      | line 1, column 2 |
      | ...              |
      +-----------------+
      | line 2, column 1 |
      | line 2, column 2 |
      | ...              |
      +------------------+

    :arguments:

      **lines** (``[ {'JOBID': '1234', ...}, ...]``)
        List of lines, with each line stored as a dictionary.
        Note that all data has to be stored as one as string,
        or as one the GooseSLURM.rich classes (no rich printing is used though).
    """

    # width of the field-names
    # - initialize
    width = 0
    # - compute
    for line in lines:
        for key in sorted(line):
            width = max(width, len(key))

    # print format
    head = "{{key:<{width:d}.{width:d}s}}".format(width=width + 1)
    fmt = "{{key:<{width:d}.{width:d}s}}: {{data:s}}".format(width=width + 1)

    # print header
    print(head.format(key="-" * 100, data=""))

    # print data
    for line in lines:
        for key in sorted(line):
            print(fmt.format(key=key, data=str(line[key])))
        print(head.format(key="-" * 100, data=""))


def print_columns(
    lines, columns, header, no_truncate=False, sep=", ", cols=None, print_header=True
):
    r"""
    Print table to fit the screen. This function can show data truncated, or even suppress columns
    if there is insufficient room.

    :arguments:

      **lines** (``[ {'JOBID': '1234', ...}, ...]``)
        List of lines, with each line stored as a dictionary.
        Note that all data has to be stored as one of the GooseSLURM.rich classes
        (to customize the color, precision, ...) or as string.

      **columns** (``[ {'key': 'JOBID', 'width': 7, 'align': '>', 'priority': True}, ...]``)
        List with print settings of each column:
        - 'key'     : the key-name used to store each line (see ``lines`` below)
        - 'width'   : minimum print width (expanded as much as possible to fit the data)
        - 'align'   : alignment of the column
        - 'priority': priority of column expansion, columns marked ``True`` are expanded first

      **header** (``{'JOBID': 'JobID', ...}``)
        Header name for each column.

    :options:

      **no_truncate** ([``False``] | ``True``)
        Disable truncation of columns. In this case each column is expanded to fit the data.

      **sep** ([``', '``] | ``<str>``)
        Separator between columns.

      **cols** ([``None``] | ``<int>``)
        Number of characters on one line. If ``None`` the current terminal's width is used.

      **print_header** ([``True``] | ``False``)
        Optionally skip printing of header.
    """

    # check available data
    # --------------------

    # function to check if a "key" present in all lines
    def inlines(lines, key):
        # - check all lines
        for line in lines:
            if key not in line:
                return False
        # - all lines passed: return True
        return True

    # select columns based on data availability
    columns = [column for column in columns if inlines(lines, column["key"])]

    # select header based on columns
    header = {column["key"]: header[column["key"]] for column in columns}

    # convert to GooseSLURM.rich
    # --------------------------

    for line in lines:
        for key in line:
            if not isinstance(line[key], rich.String):
                line[key] = rich.String(line[key])

    for key in header:
        if not isinstance(header[key], rich.String):
            header[key] = rich.String(header[key])

    # compute column-width, based on data
    # -----------------------------------

    # initialize
    for column in columns:
        column["real"] = 0

    # get actual width
    # - header
    for column in columns:
        column["real"] = max(column["real"], len(str(header[column["key"]])))
    # - data
    for line in lines:
        for column in columns:
            column["real"] = max(column["real"], len(str(line[column["key"]])))

    # auto-limit columns, auto-adjust their width
    # -------------------------------------------

    if no_truncate:

        # set all columns to the real width
        for line in lines:
            for column in columns:
                column["width"] = column["real"]

    else:

        # get the terminal size
        if cols is None:
            import shutil

            cols, _ = shutil.get_terminal_size()

        # get the cumulative minimum size of the columns (+ spacing between the columns)
        # - first entry
        columns[0]["total"] = columns[0]["width"]
        # - all other entries
        for i in range(1, len(columns)):
            columns[i]["total"] = (
                columns[i - 1]["total"] + columns[i]["width"] + len(sep)
            )

        # truncate at terminal size
        columns = [column for column in columns if column["total"] <= cols]

        # get the available size to expand
        room = cols - columns[-1]["total"]

        # expand minimum width, as long there is room
        # - distinguish priorities for expanding
        low = [column["key"] for column in columns if not column.get("priority", False)]
        high = [column["key"] for column in columns if column["key"] not in low]
        # - expand
        for prio in [high, low]:
            for column in columns:
                if column["key"] not in prio:
                    continue
                if room <= 0:
                    break
                dw = min(column["real"] - column["width"], room)
                if dw <= 0:
                    continue
                column["width"] += dw
                room -= dw

    # apply width
    for line in lines:
        for column in columns:
            line[column["key"]].width = column["width"]
            line[column["key"]].align = column["align"]

    # print to screen
    # ---------------

    # select header based on columns
    header = {column["key"]: header[column["key"]] for column in columns}

    # apply width to header
    for column in columns:
        header[column["key"]].width = column["width"]

    # separator
    # - copy from header
    hline = {key: rich.String(**value.__dict__) for key, value in header.items()}
    # - convert from header (print format retained)
    for key in hline:
        hline[key].data = "=" * hline[key].width

    # header
    if print_header:
        print(sep.join(hline[column["key"]].format() for column in columns))
        print(sep.join(header[column["key"]].format() for column in columns))
        print(sep.join(hline[column["key"]].format() for column in columns))
    # data
    for line in lines:
        print(sep.join(line[column["key"]].format() for column in columns))


def print_list(lines, key, sep=" "):
    r"""
    Print a single column as a list.

    :arguments:

      **lines** (``[ {'JOBID': '1234', ...}, ...]``)
        List of lines, with each line stored as a dictionary.
        Note that all data has to be stored as one as string,
        or as one the GooseSLURM.rich classes (no rich printing is used though).

      **key** (``'JOBID'``)
        Column to print.

    :options:

      **sep** ([``' '``] | ``<str>``)
        Separator between columns.
    """

    for line in lines:
        print(line[key], end=sep)

    print("")

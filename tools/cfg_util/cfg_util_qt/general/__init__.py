from tools.cfg_util.cfg_util_qt.layout import window, TABLE_KEYS


def btn_all(table, selected):
    if table in TABLE_KEYS["table"]:
        if len(selected) == len(window[table].Values):
            window[table].update(select_rows=())
        else:
            window[table].update(
                select_rows=([row for row in range(len(window[table].Values))])
            )

    if table in TABLE_KEYS["tree"]:
        if len(selected) == len(window[table].Widget.get_children()):
            _tree = window[table]
            _tree.Widget.selection_set([])
        else:
            _tree = window[table]
            rows_to_select = [i for i in _tree.Widget.get_children()]
            _tree.Widget.selection_set(rows_to_select)

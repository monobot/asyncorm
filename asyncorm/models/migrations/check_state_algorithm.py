old_state = {
    'fields': {
        'date_created': {
            'db_column': 'date_created',
            'strftime': '%Y-%m-%d',
            'choices': None,
            'null': False,
            'default': None,
            'auto_now': True,
            'unique': False,
        },
        'book_type': {
            'db_column': 'book_type',
            'choices': {
                'paperback': 'paperback book',
                'hard cover': 'hard cover book',
            },
            'null': True,
            'default': None,
            'max_length': 15,
            'unique': False,
        },
        'id': {
            'db_column': 'id',
            'unique': True,
            'null': False,
        },
        'name': {
            'db_column': 'name',
            'choices': None,
            'null': False,
            'default': None,
            'max_length': 50,
            'unique': False,
        },
        'synopsis': {
            'db_column': 'synopsis',
            'choices': None,
            'null': False,
            'default': None,
            'max_length': 255,
            'unique': False,
        },
    },
    'meta': {
        'ordering': ('-id', ),
        'viejos': 1,
    },
}

new_state = {
    'fields': {
        'date_created': {
            'db_column': 'date_created',
            'strftime': '%Y-%m-%d',
            'choices': None,
            'null': False,
            'default': None,
            'auto_now': True,
            'unique': False,
        },
        'book_type': {
            'db_column': 'book_type',
            'choices': {
                'paperback': 'paperback book',
                'hard cover': 'hard cover book',
            },
            'null': True,
            'default': None,
            'max_length': 15,
            'unique': False,
        },
        'id': {
            'db_column': 'id',
            'unique': True,
            'null': True,
        },
        'name': {
            'db_column': 'name',
            'choices': None,
            'null': False,
            'default': None,
            'max_length': 50,
            'unique': False,
        },
        'pages': {
            'db_column': 'pages',
            'default': None,
            'choices': None,
            'null': True,
            'unique': False,
        },
    },
    'meta': {
        'ordering': ('-date', ),
        'otro': ('-id', ),
    },
}

if old_state != new_state:
    # model has differences
    if old_state['fields'] != new_state['fields']:
        # fields are different

        # we walk on he old state fields and compare
        for f_n, f_v in old_state['fields'].items():
            if new_state['fields'].get(f_n, False):
                if new_state['fields'][f_n] != f_v:
                    print('Field "{}" has changed'.format(f_n))
            else:
                print('Field "{}" was deleted'.format(f_n))

        # we walk on he new state fields but only check if there are new fields
        for f_n, f_v in new_state['fields'].items():
            if not old_state['fields'].get(f_n, False):
                print('Field "{}" is new'.format(f_n))

    if old_state['meta'] != new_state['meta']:
        # meta is different

        # we walk on he old state meta and compare
        for m_n, m_v in old_state['meta'].items():
            if new_state['meta'].get(m_n, False):
                if new_state['meta'][m_n] != m_v:
                    print('Meta "{}" has changed'.format(m_n))
            else:
                print('Meta "{}" was deleted'.format(m_n))

        # we walk on he new state meta but only check if there are new attrs
        for m_n, m_v in new_state['meta'].items():
            if not old_state['meta'].get(m_n, False):
                print('Meta "{}" is new'.format(m_n))

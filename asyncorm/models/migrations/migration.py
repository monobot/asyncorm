class MigrationBase(object):
    depends = []
    fw_operations = {
        'stage1': [],
        'stage2': [],
        'stage3': [],
        'stage4': [],
    }
    models = {}

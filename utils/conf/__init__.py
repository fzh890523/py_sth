# encoding: utf-8

__author__ = 'yonka'


def fill_config_to_global(g, config, section, arg_names):
    for arg_name in arg_names:
        converter = None
        if type(arg_name) == tuple:
            if len(arg_name) > 2:
                converter = arg_name[2]
            arg_name, var_name = arg_name[0], arg_name[1]
        else:
            var_name = arg_name
        arg_value = config.get(section, arg_name)
        g[var_name] = converter(arg_value) if converter else arg_value

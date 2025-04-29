import re
from collections import defaultdict

def parse_proguard_mapping(file_path):
    class_pattern = re.compile(r'^(\S+) -> (\S+):$')
    method_line_pattern = re.compile(r'^\s+(\d+):(\d+):(.+?) (.+?)\((.*?)\) -> (\S+)$')
    field_line_pattern = re.compile(r'^\s+(\d+):(\d+):(.+?) (.+?) -> (\S+)$')
    method_pattern = re.compile(r'^\s+(.+?) (.+?)\((.*?)\) -> (\S+)$')
    field_pattern = re.compile(r'^\s+(.+?) (.+?) -> (\S+)$')

    mapping = defaultdict(lambda: {
        'original_name': '',
        'fields': {},
        'methods': {}
    })
    current_class = None

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip('\n')
            class_match = class_pattern.match(line)
            if class_match:
                original_class, obfuscated_class = class_match.groups()
                current_class = obfuscated_class
                mapping[current_class]['original_name'] = original_class
            elif current_class:
                method_line_match = method_line_pattern.match(line)
                if method_line_match:
                    orig_start, orig_end, return_type, method_name, params, obf_name = method_line_match.groups()
                    mapping[current_class]['methods'][obf_name] = {
                        'original': f'{method_name}({params})',
                        'return_type': return_type,
                        'params': params,
                        'original_lines': (int(orig_start), int(orig_end))
                    }
                elif method_match := method_pattern.match(line):
                    return_type, method_name, params, obf_name = method_match.groups()
                    mapping[current_class]['methods'][obf_name] = {
                        'original': f'{method_name}({params})',
                        'return_type': return_type,
                        'params': params
                    }
                elif field_line_match := field_line_pattern.match(line):
                    orig_start, orig_end, field_type, field_name, obf_name = field_line_match.groups()
                    mapping[current_class]['fields'][obf_name] = {
                        'original': field_name,
                        'type': field_type,
                        'original_lines': (int(orig_start), int(orig_end))
                    }
                elif field_match := field_pattern.match(line):
                    field_type, field_name, obf_name = field_match.groups()
                    mapping[current_class]['fields'][obf_name] = {
                        'original': field_name,
                        'type': field_type
                    }

    return dict(mapping)

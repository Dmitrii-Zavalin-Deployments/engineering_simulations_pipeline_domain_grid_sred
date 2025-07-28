# tests/helpers/payload_factory.py

def valid_domain_payload():
    return {
        "domain_definition": {
            "min_x": 0.0, "max_x": 3.0,
            "min_y": 0.0, "max_y": 2.0,
            "min_z": 0.0, "max_z": 1.0,
            "nx": 3, "ny": 2, "nz": 1
        }
    }


def empty_domain_payload():
    return {
        "domain_definition": {}
    }


def non_numeric_domain_payload():
    return {
        "domain_definition": {
            "min_x": "left", "max_x": "right",
            "min_y": None, "max_y": True,
            "min_z": [], "max_z": {}
        }
    }


def mixed_schema_payload():
    return {
        "domain_definition": {
            "min_x": "0.0", "max_x": 3.0,
            "min_y": 0.0, "max_y": "2.0",
            "min_z": "invalid_float", "max_z": 1.0
        },
        "extra": {
            "notes": "spatial context",
            "version": "1.0.3"
        }
    }



